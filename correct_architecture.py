# ============================================================
# CORRECT ARCHITECTURE FOR SCAMBAIT AI
# 5-Layer System as per Competition Requirements
# ============================================================

from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
import re
from pydantic import BaseModel

# ============================================================
# LAYER 1: SCAM DETECTION MODULE (Hybrid Rule + Pattern)
# ============================================================

class ScamIntent(Enum):
    """Scam type classification"""
    FINANCIAL_FRAUD = "financial_fraud"
    UPI_SCAM = "upi_scam"
    FAKE_PRIZE = "fake_prize"
    JOB_SCAM = "job_scam"
    KYC_FRAUD = "kyc_fraud"
    PHISHING = "phishing"
    NONE = "none"

class ScamDetector:
    """Layer 1: Rule-based + pattern matching scam detection"""
    
    # Keyword sets for different scam types
    FINANCIAL_KEYWORDS = {"urgent", "blocked", "account", "bank", "verify", "otp"}
    PRIZE_KEYWORDS = {"lottery", "won", "prize", "congratulations", "claim", "lakh", "crore"}
    JOB_KEYWORDS = {"job", "vacancy", "hiring", "salary", "work from home", "earn"}
    KYC_KEYWORDS = {"kyc", "pan", "aadhaar", "update", "incomplete", "expire"}
    
    # Regex patterns (compiled for performance)
    UPI_PATTERN = re.compile(r'[a-zA-Z0-9._-]+@[a-zA-Z]+')
    PHONE_PATTERN = re.compile(r'\+91[\s-]?\d{10}|\b\d{10}\b')
    URL_PATTERN = re.compile(r'https?://[^\s]+|www\.[^\s]+', re.IGNORECASE)
    AMOUNT_PATTERN = re.compile(r'₹|lakh|crore|rupees|rs\.?\s*\d+')
    
    def detect(self, text: str) -> tuple[bool, List[ScamIntent]]:
        """
        Hybrid detection: Rule-based + Pattern matching
        Returns: (is_scam, list_of_intents)
        """
        text_lower = text.lower()
        signals = 0
        intents = []
        
        # Signal 1: Check keyword categories
        if any(kw in text_lower for kw in self.PRIZE_KEYWORDS):
            intents.append(ScamIntent.FAKE_PRIZE)
            signals += 1
        
        if any(kw in text_lower for kw in self.FINANCIAL_KEYWORDS):
            intents.append(ScamIntent.FINANCIAL_FRAUD)
            signals += 1
        
        if any(kw in text_lower for kw in self.JOB_KEYWORDS):
            intents.append(ScamIntent.JOB_SCAM)
            signals += 1
        
        if any(kw in text_lower for kw in self.KYC_KEYWORDS):
            intents.append(ScamIntent.KYC_FRAUD)
            signals += 1
        
        # Signal 2: Pattern matching
        if self.UPI_PATTERN.search(text):
            intents.append(ScamIntent.UPI_SCAM)
            signals += 1
        
        if self.URL_PATTERN.search(text):
            intents.append(ScamIntent.PHISHING)
            signals += 1
        
        if self.PHONE_PATTERN.search(text):
            signals += 1
        
        # Special case: Lottery scam (keyword + amount = instant detection)
        has_prize = any(kw in text_lower for kw in self.PRIZE_KEYWORDS)
        has_amount = self.AMOUNT_PATTERN.search(text) is not None
        if has_prize and has_amount:
            return True, [ScamIntent.FAKE_PRIZE]
        
        # General rule: 2+ signals = scam
        is_scam = signals >= 2
        
        return is_scam, intents if intents else [ScamIntent.NONE]


# ============================================================
# LAYER 2: AGENT CONTROLLER (State Machine) - THE CORE
# ============================================================

class EngagementState(Enum):
    """Conversation states"""
    INITIAL = "initial"
    TRUST_BUILDING = "trust_building"
    PROBING = "probing"
    EXTRACTION = "extraction"
    WINDING_DOWN = "winding_down"
    TERMINATED = "terminated"

class SessionController:
    """
    Layer 2: Core state machine
    This is BACKEND LOGIC, not LLM decision-making
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state = EngagementState.INITIAL
        self.message_count = 0
        self.scam_confirmed = False
        self.intents: List[ScamIntent] = []
        self.extracted_intel = {
            "upiIds": [],
            "bankAccounts": [],
            "phoneNumbers": [],
            "phishingLinks": [],
            "suspiciousKeywords": []
        }
        self.conversation_history = []
        self.callback_sent = False
        self.created_at = datetime.now()
    
    def should_continue(self) -> bool:
        """
        BACKEND LOGIC: Decide if engagement continues
        This is NOT an LLM job
        """
        # Hard cap
        if self.message_count >= 20:
            return False
        
        # Already terminated
        if self.state == EngagementState.TERMINATED:
            return False
        
        # Callback already sent
        if self.callback_sent:
            return False
        
        # Minimum engagement + sufficient intel
        if self.message_count >= 8:
            intel_count = sum(len(v) for v in self.extracted_intel.values())
            if intel_count >= 3:
                # Enough data collected
                return False
        
        return True
    
    def transition_state(self) -> None:
        """
        BACKEND LOGIC: Deterministic state transitions
        Based on message count, not LLM output
        """
        if self.message_count <= 3:
            self.state = EngagementState.TRUST_BUILDING
        elif self.message_count <= 8:
            self.state = EngagementState.PROBING
        elif self.message_count <= 15:
            self.state = EngagementState.EXTRACTION
        else:
            self.state = EngagementState.WINDING_DOWN
    
    def get_phase_instruction(self) -> str:
        """
        Return instruction for Persona Engine based on current state
        """
        instructions = {
            EngagementState.INITIAL: "Show confusion. Ask who they are.",
            EngagementState.TRUST_BUILDING: "Be curious and somewhat trusting. Ask basic questions.",
            EngagementState.PROBING: "Show interest. Ask for details (payment method, steps, verification).",
            EngagementState.EXTRACTION: "Almost comply. Ask for their contact details to 'send money' or 'verify'.",
            EngagementState.WINDING_DOWN: "Show doubt. Mention checking with family/friend. Stall naturally."
        }
        return instructions.get(self.state, "Respond naturally.")
    
    def increment_message(self) -> None:
        """Update message count and transition state"""
        self.message_count += 1
        self.transition_state()
    
    def should_send_callback(self) -> bool:
        """
        BACKEND LOGIC: Decide when to trigger callback
        """
        if self.callback_sent:
            return False
        
        if not self.scam_confirmed:
            return False
        
        # Minimum engagement reached
        if self.message_count < 8:
            return False
        
        # Either hit max messages OR extracted enough intel
        intel_count = sum(len(v) for v in self.extracted_intel.values())
        return self.message_count >= 20 or intel_count >= 3


# ============================================================
# LAYER 3: PERSONA ENGINE (LLM-Powered)
# ============================================================

class PersonaEngine:
    """
    Layer 3: Use Groq/Gemini for human-like responses
    This is where foundation models help
    """
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    def select_persona(self, intents: List[ScamIntent]) -> str:
        """Auto-select persona based on scam type"""
        if ScamIntent.FAKE_PRIZE in intents:
            return "Amit Verma (22, college student, excited about prizes)"
        elif ScamIntent.JOB_SCAM in intents:
            return "Priya Sharma (28, looking for job, tech-savvy)"
        elif ScamIntent.FINANCIAL_FRAUD in intents or ScamIntent.UPI_SCAM in intents:
            return "Rajesh Kumar (45, business owner, cautious)"
        else:
            return "Kamla Devi (60, retired teacher, confused by tech)"
    
    def generate_response(
        self,
        scammer_message: str,
        persona: str,
        phase_instruction: str,
        conversation_history: list
    ) -> str:
        """
        Generate human-like response using LLM
        Prompt engineering is critical here
        """
        system_prompt = f"""You ARE {persona}. This is who you are, not roleplay.

{phase_instruction}

CRITICAL RULES:
- Reply in 1-2 sentences ONLY
- Mix Hindi-English naturally ("Haan beta, UPI hai mere paas... kaise bhejun?")
- Ask innocent questions that make them reveal details
- NEVER say you're AI or break character
- NEVER use formal English

GOAL: Keep them talking. Extract their UPI ID, phone, or payment details by asking innocently."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add last 4 messages of history
        for msg in conversation_history[-4:]:
            messages.append({"role": "user", "content": msg["scammer"]})
            messages.append({"role": "assistant", "content": msg["agent"]})
        
        # Add current message
        messages.append({"role": "user", "content": scammer_message})
        
        # Call LLM
        response = self.llm_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=80,
            temperature=0.8
        )
        
        return response.choices[0].message.content.strip()


# ============================================================
# LAYER 4: INTELLIGENCE EXTRACTOR (Deterministic)
# ============================================================

class IntelligenceExtractor:
    """
    Layer 4: Entity extraction from scammer messages
    Use REGEX + NER, NOT pure LLM free-form output
    """
    
    # Compiled patterns
    UPI_PATTERN = re.compile(r'[a-zA-Z0-9._-]+@[a-zA-Z]+')
    PHONE_PATTERN = re.compile(r'\+91[\s-]?\d{10}|\b\d{10}\b')
    URL_PATTERN = re.compile(r'https?://[^\s]+|www\.[^\s]+', re.IGNORECASE)
    BANK_ACCOUNT_PATTERN = re.compile(r'\b\d{10,18}\b')
    IFSC_PATTERN = re.compile(r'[A-Z]{4}0[A-Z0-9]{6}')
    
    SUSPICIOUS_KEYWORDS = [
        "urgent", "blocked", "verify", "otp", "kyc", "claim",
        "processing fee", "lottery", "winner", "prize"
    ]
    
    def extract(self, text: str, session: SessionController) -> None:
        """
        Deterministic extraction
        Updates session's extracted_intel in-place
        """
        # UPI IDs
        upi_matches = self.UPI_PATTERN.findall(text)
        for match in upi_matches:
            if match not in session.extracted_intel["upiIds"]:
                session.extracted_intel["upiIds"].append(match)
        
        # Phone numbers
        phone_matches = self.PHONE_PATTERN.findall(text)
        for match in phone_matches:
            clean = re.sub(r'[\s-]', '', match)
            if clean not in session.extracted_intel["phoneNumbers"]:
                session.extracted_intel["phoneNumbers"].append(clean)
        
        # URLs
        url_matches = self.URL_PATTERN.findall(text)
        for match in url_matches:
            if match not in session.extracted_intel["phishingLinks"]:
                session.extracted_intel["phishingLinks"].append(match)
        
        # Bank accounts (excluding phone numbers)
        acc_matches = self.BANK_ACCOUNT_PATTERN.findall(text)
        for match in acc_matches:
            if (match not in session.extracted_intel["bankAccounts"] and
                match not in session.extracted_intel["phoneNumbers"]):
                session.extracted_intel["bankAccounts"].append(match)
        
        # Keywords
        text_lower = text.lower()
        for keyword in self.SUSPICIOUS_KEYWORDS:
            if keyword in text_lower:
                if keyword not in session.extracted_intel["suspiciousKeywords"]:
                    session.extracted_intel["suspiciousKeywords"].append(keyword)


# ============================================================
# LAYER 5: CALLBACK ENGINE (Non-blocking, Reliable)
# ============================================================

import httpx
import asyncio
from typing import Callable

class CallbackEngine:
    """
    Layer 5: Reliable callback delivery
    Non-blocking background task
    """
    
    CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    TIMEOUT = 10.0  # seconds
    MAX_RETRIES = 3
    
    async def send_callback(
        self,
        session: SessionController,
        logger: Optional[Callable] = None
    ) -> bool:
        """
        Send final results to GUVI endpoint
        Non-blocking, with retries
        """
        if session.callback_sent:
            return True
        
        # Mark as sent immediately (prevent duplicate sends)
        session.callback_sent = True
        
        payload = {
            "sessionId": session.session_id,
            "scamDetected": session.scam_confirmed,
            "totalMessagesExchanged": session.message_count,
            "extractedIntelligence": session.extracted_intel,
            "agentNotes": self._generate_notes(session)
        }
        
        # Retry logic
        for attempt in range(self.MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                    response = await client.post(self.CALLBACK_URL, json=payload)
                    
                    if response.status_code == 200:
                        if logger:
                            logger(f"Callback sent successfully for session {session.session_id}")
                        return True
                    else:
                        if logger:
                            logger(f"Callback failed: HTTP {response.status_code}")
                
            except Exception as e:
                if logger:
                    logger(f"Callback attempt {attempt + 1} failed: {e}")
                
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return False
    
    def _generate_notes(self, session: SessionController) -> str:
        """Generate summary notes for law enforcement"""
        intel_count = sum(len(v) for v in session.extracted_intel.values())
        
        return (
            f"AI agent engaged suspected scammer for {session.message_count} exchanges. "
            f"Scam type: {', '.join(i.value for i in session.intents)}. "
            f"Extracted {intel_count} intelligence items including "
            f"{len(session.extracted_intel['upiIds'])} UPI IDs, "
            f"{len(session.extracted_intel['phoneNumbers'])} phone numbers, "
            f"and {len(session.extracted_intel['phishingLinks'])} suspicious links."
        )


# ============================================================
# ORCHESTRATOR: Putting It All Together
# ============================================================

class HoneypotOrchestrator:
    """
    Main orchestrator that coordinates all 5 layers
    """
    
    def __init__(self, llm_client):
        self.detector = ScamDetector()
        self.persona_engine = PersonaEngine(llm_client)
        self.extractor = IntelligenceExtractor()
        self.callback_engine = CallbackEngine()
        
        # Session storage (in-memory for prototype)
        self.sessions: Dict[str, SessionController] = {}
    
    def get_or_create_session(self, session_id: str) -> SessionController:
        """Get existing session or create new one"""
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionController(session_id)
        return self.sessions[session_id]
    
    async def process_message(
        self,
        session_id: str,
        scammer_message: str
    ) -> dict:
        """
        Main processing pipeline
        Input: session_id + scammer_message
        Output: agent_response + metadata
        """
        # Get session
        session = self.get_or_create_session(session_id)
        
        # Check if should continue
        if not session.should_continue():
            return {
                "status": "success",
                "reply": "Thank you. I need to go now.",
                "session_ended": True
            }
        
        # LAYER 1: Detect scam
        if not session.scam_confirmed:
            is_scam, intents = self.detector.detect(scammer_message)
            session.scam_confirmed = is_scam
            session.intents = intents
        
        # LAYER 4: Extract intelligence (silent)
        self.extractor.extract(scammer_message, session)
        
        # LAYER 2: Update state machine
        session.increment_message()
        phase_instruction = session.get_phase_instruction()
        
        # LAYER 3: Generate response
        if session.scam_confirmed:
            persona = self.persona_engine.select_persona(session.intents)
            reply = self.persona_engine.generate_response(
                scammer_message,
                persona,
                phase_instruction,
                session.conversation_history
            )
        else:
            # Not confirmed as scam yet
            reply = "Hello. How can I help you?"
        
        # Update conversation history
        session.conversation_history.append({
            "scammer": scammer_message,
            "agent": reply,
            "timestamp": datetime.now().isoformat()
        })
        
        # LAYER 5: Check if should send callback
        if session.should_send_callback():
            # Non-blocking background task
            asyncio.create_task(
                self.callback_engine.send_callback(session, print)
            )
        
        return {
            "status": "success",
            "reply": reply,
            "session_ended": False
        }


# ============================================================
# USAGE EXAMPLE
# ============================================================

"""
# In your api.py:

from groq import Groq
from correct_architecture import HoneypotOrchestrator

# Initialize
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
orchestrator = HoneypotOrchestrator(groq_client)

# In your endpoint:
@app.post("/api/honeypot")
async def honeypot(request: HoneypotRequest):
    result = await orchestrator.process_message(
        session_id=request.sessionId,
        scammer_message=extract_message_text(request.message)
    )
    return HoneypotResponse(
        status=result["status"],
        reply=result["reply"]
    )
"""
