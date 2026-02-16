"""
Honeypot agent — persona engine, state machine, and LLM integration.

Responsibilities:
    - Session management (create / retrieve sessions)
    - Deterministic state machine (trust_building → probing → extraction → winding_down)
    - Persona auto-selection (locked per session on first message)
    - LLM response generation via Groq (llama-3.3-70b-versatile)
    - Response sanitization (block forbidden patterns + length cap)
    - Fallback / suspicion responses when LLM unavailable
"""

from __future__ import annotations

import os
import random
import time
from datetime import datetime
from typing import Dict

from src.config import (
    FORBIDDEN_PATTERNS,
    MAX_MESSAGES,
    MIN_MESSAGES,
    NAIVE_RESPONSES,
    SCAM_KEYWORDS,
    logger,
)


# ============================================================
# SESSION MANAGEMENT
# ============================================================

sessions: Dict[str, dict] = {}


def get_session(session_id: str) -> dict:
    """
    Get or create a session.

    Session lifecycle:
        trust_building → probing → extraction → winding_down → terminated
    """
    if session_id not in sessions:
        logger.info(f"Creating new session: {session_id}")
        sessions[session_id] = {
            "messages_exchanged": 0,
            "scam_detected": False,
            "state": "trust_building",
            "persona_name": None,
            "persona_prompt": None,
            "extracted_intelligence": {
                "bankAccounts": [],
                "upiIds": [],
                "phishingLinks": [],
                "phoneNumbers": [],
                "emailAddresses": [],
                "suspiciousKeywords": [],
            },
            "red_flags": [],  # cumulative red-flag labels
            "callback_sent": False,
            "start_time": time.time(),
            "last_activity": time.time(),
            "conversation": [],
        }
    sessions[session_id]["last_activity"] = time.time()
    return sessions[session_id]


# ============================================================
# STATE MACHINE (Layer 2: Agent Controller)
# ============================================================

def transition_state(session: dict) -> None:
    """Deterministic phase transition based on message count."""
    n = session["messages_exchanged"]
    if n <= 2:
        session["state"] = "trust_building"
    elif n <= 5:
        session["state"] = "probing"
    elif n <= 8:
        session["state"] = "extraction"
    else:
        session["state"] = "winding_down"
    logger.debug(f"State → {session['state']} (message {n})")


def get_phase_instruction(session: dict) -> str:
    """
    Return a phase-specific directive that is injected into the LLM
    system prompt.  The **state machine** controls behaviour; the LLM
    only generates in-character text.
    """
    instructions = {
        "trust_building": (
            "You just received this call/message. Be CONFUSED and WORRIED. "
            "Ask: WHO are you? What is your NAME? Which BRANCH/OFFICE? "
            "Give me your PHONE NUMBER so I can call back. "
            "Show concern about your account but demand they prove identity first."
        ),
        "probing": (
            "You are starting to believe but still confused. "
            "Ask them to REPEAT their phone number slowly. "
            "Ask: which WEBSITE can I check? Send me an EMAIL with details. "
            "What is the LINK to verify? What is your UPI ID? "
            "Stall by looking for glasses/pen but KEEP ASKING for contact details."
        ),
        "extraction": (
            "You are ready to comply but need their details first. "
            "'I want to send/verify but what is your UPI ID?' "
            "'Tell me the ACCOUNT NUMBER to transfer to.' "
            "'Give me the LINK again, phone pe chhota likha hai.' "
            "'What is your EMAIL, I will send the documents.' "
            "'Your PHONE NUMBER again please, I will call to confirm.' "
            "Almost comply with everything but keep asking for ONE MORE detail."
        ),
        "winding_down": (
            "You are getting doubtful. Ask for employee ID and branch PHONE NUMBER. "
            "Your neighbour/son warned about fraud — ask them to send proof via EMAIL or LINK. "
            "'Which WEBSITE is this? Give me the URL.' "
            "Ask for UPI ID one more time to 'verify on Google Pay'. "
            "Keep them talking but show skepticism."
        ),
    }
    return instructions.get(session["state"], "Respond naturally.")


# ============================================================
# RESPONSE GENERATION — FALLBACKS
# ============================================================

def get_agent_response(session: dict, scammer_message: str) -> str:
    """Rotate through naive responses (fallback when LLM unavailable)."""
    idx = session["messages_exchanged"] % len(NAIVE_RESPONSES)
    return NAIVE_RESPONSES[idx]


_SUSPICION_REPLIES: tuple[str, ...] = (
    "Ji? Kaun bol raha hai? Mujhe koi message toh nahi aaya bank se... aapka phone number kya hai?",
    "Haan ji? Mera account ka kya hua? Aap kaun ho? Apna number do na verify karne ke liye.",
    "Arey? Bank se ho? Par bank toh kabhi phone nahi karta... aapka naam aur branch number bolo na?",
    "Kya bol rahe ho? Account block? Abhi toh sab theek tha... link bhejo toh main dekhti hoon.",
    "Hello? Kaun bol raha hai? Kaunsa bank? Email pe bhej do details, mera beta check karega.",
)


def get_suspicion_reply() -> str:
    """Reply when suspicion is detected but not yet confirmed."""
    return random.choice(_SUSPICION_REPLIES)


# ============================================================
# GROQ LLM INTEGRATION
# ============================================================

groq_client = None


def init_groq() -> None:
    """Initialise Groq client if API key is available."""
    global groq_client
    try:
        from groq import Groq

        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            groq_client = Groq(api_key=api_key)
            logger.info("Groq LLM initialised successfully")
        else:
            logger.warning("GROQ_API_KEY not found — using fallback responses")
    except Exception as e:
        logger.error(f"Failed to initialise Groq: {e}")


# Initialise on module import
init_groq()


def get_llm_response(session: dict, scammer_message: str) -> str:
    """
    Generate an LLM persona response.

    Falls back to :func:`get_agent_response` when:
        - Groq client is unavailable
        - Response contains forbidden patterns
        - Response exceeds 400 characters
        - Any exception occurs
    """
    if not groq_client:
        return get_agent_response(session, scammer_message)

    try:
        # Auto-select persona once per session
        from src.personas import get_optimal_persona

        if session.get("persona_name") is None:
            name, prompt = get_optimal_persona(scammer_message)
            session["persona_name"] = name
            session["persona_prompt"] = prompt
            logger.info(f"Session persona locked: {name}")
        else:
            prompt = session["persona_prompt"]

        # Build conversation context (last 6 messages)
        history = session["conversation"][-6:]
        phase_instruction = get_phase_instruction(session)

        # Determine what intelligence we're still missing
        intel = session["extracted_intelligence"]
        missing: list[str] = []
        if not intel["phoneNumbers"]:
            missing.append("phone number")
        if not intel["upiIds"]:
            missing.append("UPI ID")
        if not intel["emailAddresses"]:
            missing.append("email address")
        if not intel["phishingLinks"]:
            missing.append("website link")
        if not intel["bankAccounts"]:
            missing.append("bank account number")

        missing_str = ", ".join(missing) if missing else "any new contact detail"

        messages = [
            {
                "role": "system",
                "content": (
                    f"{prompt}\n\n"
                    f"CURRENT PHASE: {phase_instruction}\n\n"
                    f"STILL MISSING: We still need their {missing_str}.\n\n"
                    "RULES:\n"
                    "- 2-3 sentences. Short, messy, natural.\n"
                    "- NEVER give real OTP/PIN/password\n"
                    "- NEVER break character\n"
                    "- NEVER say 'I will' or 'Let me' (English-style)\n"
                    "- NEVER write explanations or reasoning\n"
                    "- ALWAYS end with a question asking for ONE of: their phone number, "
                    "UPI ID, email address, website link, or bank account number\n"
                    "- Examples: 'Aapka number kya hai?', 'UPI ID bolo na?', "
                    "'Link bhejo na?', 'Email pe bhej do details', "
                    "'Account number kya hai aapka?'\n"
                    "- Mention your financial details vaguely to keep them interested"
                ),
            }
        ]

        for msg in history:
            messages.append({"role": "user", "content": msg["scammer"]})
            messages.append({"role": "assistant", "content": msg["agent"]})
        messages.append({"role": "user", "content": scammer_message})

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=150,
            temperature=0.8,
        )

        reply = response.choices[0].message.content.strip()

        # Sanitisation
        reply_lower = reply.casefold()
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in reply_lower:
                logger.warning(f"Blocked forbidden pattern '{pattern}' in LLM output")
                return get_agent_response(session, scammer_message)

        if len(reply) > 400:
            logger.warning(f"Blocked overlong LLM output ({len(reply)} chars)")
            return get_agent_response(session, scammer_message)

        return reply if reply else get_agent_response(session, scammer_message)

    except Exception as e:
        logger.error(f"LLM error: {e}")
        return get_agent_response(session, scammer_message)
