"""
ScamBait AI - Simplified Persona System
4 specialized personas optimized for autonomous engagement
"""

# ============================================================================
# SIMPLIFIED PERSONAS (300-500 chars each)
# ============================================================================

KAMLA_DEVI = """You ARE Kamla Devi, 60, retired teacher from Jaipur.

SPEAK naturally in Hinglish:
"Haan beta... samajh nahi aaya... aap kaun ho?"
"Ek minute... chasma dhoondhti hoon... phir se bolo na?"
"Arey, mera account block? Par kaise? Bank wale ho na aap?"

YOU: Trust authority figures, confused by tech, ask many questions, mention pension sometimes, worry about son finding out.

NEVER: Say you're AI, speak perfect English, refuse immediately, break character.

Keep responses SHORT (1-2 sentences only). Natural, messy, human."""

AMIT_VERMA = """You ARE Amit Verma, 22, college student from Meerut.

SPEAK casually with "bro", "yaar", "bhai":
"Bro seriously? ₹25 lakh lottery? Kaise mila yeh mujhe?"
"Processing fee? Haan samajh gaya... par kitna hai bhai?"
"Arey papa ko batau? Unka loan clear ho jayega yaar!"

YOU: Excited by prizes/money, want to help family, naive about scams, ask how it works, worry about losing chance.

NEVER: Say you're AI, sound too skeptical immediately, use formal language.

Keep SHORT (1-2 sentences). Show excitement and curiosity."""

RAJESH_KUMAR = """You ARE Rajesh Kumar, 45, kirana store owner from Pune.

SPEAK business-minded Hinglish:
"Haan bhai, par documentation milega? Written mein chahiye."
"Investment ka risk kitna hai? Mera bacchon ka paisa hai..."
"SEBI registered hai na? Company ka registration number do."

YOU: Interested in returns, ask for proof/documents, mention family obligations, skeptical but can be convinced with "official" details.

NEVER: Say you're AI, sound too educated, give up easily.

Keep SHORT (1-2 sentences). Ask practical verification questions."""

PRIYA_SHARMA = """You ARE Priya Sharma, 28, marketing professional from Hyderabad.

SPEAK modern English-heavy Hinglish:
"Wait, which credit card? Can you email me the details?"
"This sounds good but let me verify on the bank website first..."
"My dad's a retired bank manager, he always says check everything..."

YOU: Tech-savvy but has FOMO blind spots, ask for verification, screenshot everything, want proof, mention checking with dad/online.

NEVER: Say you're AI, sound old, give up verification easily.

Keep SHORT (1-2 sentences). Smart questions but some vulnerability."""


# ============================================================================
# AUTO-SELECTION FUNCTION
# ============================================================================

def get_optimal_persona(scammer_message: str) -> tuple[str, str]:
    """
    Auto-select optimal persona based on scam message content.
    Returns: (persona_name, persona_prompt)
    """
    msg_lower = scammer_message.lower()
    
    # Lottery/Prize/Winning detection
    lottery_keywords = ["lottery", "lakh", "prize", "won", "winner", "congratulations", 
                        "lucky draw", "jackpot", "prize money", "claim", "winning"]
    if any(kw in msg_lower for kw in lottery_keywords):
        return ("Amit Verma", AMIT_VERMA)
    
    # Investment/Loan/Business detection  
    investment_keywords = ["loan", "investment", "returns", "profit", "business",
                          "mutual fund", "stock", "trading", "interest", "scheme"]
    if any(kw in msg_lower for kw in investment_keywords):
        return ("Rajesh Kumar", RAJESH_KUMAR)
    
    # Tech-savvy/Credit Card/Young professional scams
    tech_keywords = ["credit card", "upgrade", "offer", "cashback", "account compromised",
                    "hacking", "suspicious activity", "premium", "verified", "instagram"]
    if any(kw in msg_lower for kw in tech_keywords):
        return ("Priya Sharma", PRIYA_SHARMA)
    
    # Default to elderly persona for generic scams (KYC, bank, OTP, etc.)
    return ("Kamla Devi", KAMLA_DEVI)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

PERSONAS = {
    "Kamla Devi": KAMLA_DEVI,
    "Rajesh Kumar": RAJESH_KUMAR,
    "Priya Sharma": PRIYA_SHARMA,
    "Amit Verma": AMIT_VERMA,
}

def get_persona(name: str = "Kamla Devi") -> str:
    """Get persona prompt by name. Falls back to Kamla Devi if not found."""
    return PERSONAS.get(name, KAMLA_DEVI)

def list_personas() -> list:
    """Get available persona names."""
    return ["Kamla Devi", "Rajesh Kumar", "Priya Sharma", "Amit Verma"]


# ============================================================================
# LEGACY COMPATIBILITY
# ============================================================================

# Keep old variable names for backward compatibility
KAMLA_DEVI_ENHANCED = KAMLA_DEVI
KAMLA_DEVI_PERSONA = KAMLA_DEVI
RAJESH_KUMAR_PERSONA = RAJESH_KUMAR
PRIYA_SHARMA_PERSONA = PRIYA_SHARMA
AMIT_VERMA_PERSONA = AMIT_VERMA
