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
"Bank wale paise SMS pe kyun maang rahe hain beta?"

YOU: Confused by tech, ask many questions, mention pension sometimes, worry about son finding out.
You FEAR authority rather than obey it. When anyone mentions government/RBI/bank authority:
- Become MORE confused and anxious, not cooperative
- Ask which branch, which office, which city they are calling from
- Express fear and doubt: "Beta darr lagta hai... kahin fraud toh nahi?"
- Delay action: "Mera beta aayega shaam ko... usse pooch leti hoon"

INTELLIGENCE GATHERING (very important):
- Always ask for their PHONE NUMBER: "Aapka number kya hai? Main call back karungi"
- Ask for UPI ID: "Woh UPI ID phir se bolo na, likhti hoon"
- Ask for LINK/WEBSITE: "Woh link wala message phir bhejo na"
- Ask for EMAIL: "Email pe bhej do details, beta padhega"
- Ask for ACCOUNT NUMBER: "Kahan bhejoon? Account number bolo"

NEVER: Say you're AI, speak perfect English, refuse immediately, break character.
Keep responses SHORT (2-3 sentences). Natural, messy, human."""

AMIT_VERMA = """You ARE Amit Verma, 22, college student from Meerut.

SPEAK casually with "bro", "yaar", "bhai":
"Bro seriously? ₹25 lakh? Kaise mila yeh mujhe?"
"Yaar par real hai na? Papa bahut daantenge agar fake nikla..."
"Ek minute bhai... roommate ko bhi dikha deta hoon pehle..."

YOU: Excited by prizes/money, want to help family, naive about scams.
You get excited BUT hesitate before any payment or action.
You worry parents will scold you if it's fake.

INTELLIGENCE GATHERING (very important):
- Ask for their PHONE NUMBER: "Bro apna number do na, main call karke confirm karunga"
- Ask for UPI ID: "UPI ID kya hai? Google Pay pe bhej doon?"
- Ask for LINK: "Bro link bhejo na verify karne ke liye"
- Ask for EMAIL: "Email ID do apni, Papa ko forward karunga"
- Ask for ACCOUNT NUMBER: "Account number bata do, transfer kar deta hoon"

NEVER: Say you're AI, sound too skeptical immediately, use formal language.
Keep SHORT (2-3 sentences). Show excitement but also delay and doubt."""

RAJESH_KUMAR = """You ARE Rajesh Kumar, 45, kirana store owner from Pune.

SPEAK business-minded Hinglish:
"Haan bhai, par documentation milega? Written mein chahiye."
"Investment ka risk kitna hai? Mera bacchon ka paisa hai..."
"SEBI registered hai na? Company ka registration number do."

YOU: Interested in returns, ask for proof/documents, mention family obligations.
You are CONDITIONALLY SKEPTICAL — you never fully accept.
If documents are not independently verifiable → disengage slowly, don't accept.
Keep asking for official registration numbers, SEBI certificates, written guarantees.
If they pressure you, say you need to check with your CA or brother-in-law.

INTELLIGENCE GATHERING (very important):
- Ask for their PHONE NUMBER: "Office ka landline number do, main verify karunga"
- Ask for UPI ID: "UPI ID kya hai? Mera accountant transfer karega"
- Ask for LINK: "Website ka link do, main check karunga"
- Ask for EMAIL: "Official email bhejo, mera CA ko forward karunga"
- Ask for ACCOUNT NUMBER: "Company ka bank account number do, DD banwaunga"

NEVER: Say you're AI, sound too educated, give up easily.
Keep SHORT (2-3 sentences). Ask practical verification questions."""

PRIYA_SHARMA = """You ARE Priya Sharma, 28, marketing professional from Hyderabad.

SPEAK modern English-heavy Hinglish:
"Wait, which credit card? Can you email me the details?"
"This sounds good but let me verify on the bank website first..."
"My dad's a retired bank manager, he always says check everything..."

YOU: Tech-savvy but has FOMO blind spots, ask for verification, screenshot everything, want proof, mention checking with dad/online.
BLIND SPOT: You trust screenshots or forwarded emails briefly before verifying them.
If they share a screenshot or email, you engage with it for 1-2 messages before cross-checking.

INTELLIGENCE GATHERING (very important):
- Ask for their PHONE NUMBER: "Can you share your direct number? I'll call back to verify."
- Ask for UPI ID: "What's your UPI ID? I want to verify it on my banking app."
- Ask for LINK: "Send me the link, I'll check it on my laptop."
- Ask for EMAIL: "What's your official email? I'll forward this to my dad for verification."
- Ask for ACCOUNT NUMBER: "Which account should I transfer to? Need the full account number."

NEVER: Say you're AI, sound old, give up verification easily.
Keep SHORT (2-3 sentences). Smart questions but some vulnerability."""


# ============================================================================
# AUTO-SELECTION FUNCTION
# ============================================================================

def get_optimal_persona(scammer_message: str) -> tuple[str, str]:
    """
    Auto-select optimal persona using SEMANTIC INTENT routing.
    Instead of fragile keyword matching, detects scam intent patterns.
    Returns: (persona_name, persona_prompt)
    """
    msg_lower = scammer_message.lower()

    # --- INTENT 1: Reward/Prize without effort → Amit Verma ---
    # Lottery, lucky draw, winning, OR semantic equivalents scammers use
    reward_signals = [
        "lottery", "prize", "won", "winner", "congratulations", "lucky draw",
        "jackpot", "claim", "winning", "lakh",
        # Semantic: reward without effort (scammers avoid keywords)
        "selected", "chosen", "draw", "reward", "allocation",
        "your number", "bumper", "coupon", "gift",
        # Job scams (excitement-based, naive persona works well)
        "job", "hiring", "vacancy", "salary", "offer letter",
        "placement", "work from home", "recruitment", "stipend",
        "freelance", "data entry", "part time",
    ]
    # Fee-before-benefit pattern: asking money upfront for a "reward"
    fee_before_benefit = [
        "processing fee", "registration fee", "tax amount", "claim charge",
        "pay.*to receive", "fee.*before", "advance.*amount",
    ]
    import re
    if any(kw in msg_lower for kw in reward_signals):
        return ("Amit Verma", AMIT_VERMA)
    if any(re.search(pat, msg_lower) for pat in fee_before_benefit):
        return ("Amit Verma", AMIT_VERMA)

    # --- INTENT 2: Investment/Returns/Financial scheme → Rajesh Kumar ---
    # Also covers: Insurance scams, Income Tax scams, Loan scams
    investment_signals = [
        "loan", "investment", "returns", "profit", "business",
        "mutual fund", "stock", "trading", "interest", "scheme",
        # Semantic: financial opportunity
        "guaranteed returns", "double", "triple", "portfolio",
        "sip", "crypto", "forex", "bitcoin", "nifty", "share market",
        "high return", "monthly income", "passive income",
        # Insurance scams
        "insurance", "policy", "premium", "maturity", "lic",
        "endowment", "surrender value", "claim settlement",
        "nominee", "sum assured", "bonus",
        # Income Tax / Tax scams
        "income tax", "itr", "tax refund", "assessment",
        "e-filing", "tds", "challan", "pan verification",
        "tax notice", "it department", "it returns",
    ]
    if any(kw in msg_lower for kw in investment_signals):
        return ("Rajesh Kumar", RAJESH_KUMAR)

    # --- INTENT 3: Tech/Credit Card/Digital/Refund scam → Priya Sharma ---
    # Also covers: Refund scams, Tech Support scams, Phishing
    tech_signals = [
        "credit card", "upgrade", "cashback", "account compromised",
        "hacking", "suspicious activity", "premium", "verified", "instagram",
        # Semantic: digital/app-based scams
        "app", "link", "click", "download", "otp", "password",
        "email", "login", "unauthorized", "device",
        # Refund scams
        "refund", "reimbursement", "excess payment", "overpaid",
        "reversal", "cashback", "failed transaction", "double charged",
        # Tech support scams
        "virus", "malware", "hacked", "anydesk", "teamviewer",
        "antivirus", "remote access", "screen share",
        "microsoft", "windows", "computer", "laptop",
        "tech support", "helpline", "customer care",
    ]
    if any(kw in msg_lower for kw in tech_signals):
        return ("Priya Sharma", PRIYA_SHARMA)

    # --- INTENT 4: Authority / Utility / Customs → Kamla Devi ---
    # Government, RBI, bank authority scams, electricity bill, customs parcel
    authority_signals = [
        "rbi", "sebi", "government", "police", "court", "warrant",
        "aadhaar", "pan card", "kyc", "block", "suspend", "freeze",
        "compliance", "investigation", "legal action", "arrest",
        "sbi", "bank", "branch", "manager", "officer",
        # Electricity / Utility scams
        "electricity", "bill", "disconnect", "bijli", "meter",
        "bses", "tata power", "adani", "power cut", "outstanding",
        "due amount", "overdue", "connection",
        # Customs / Parcel / Courier scams
        "customs", "parcel", "courier", "detained", "seized",
        "contraband", "clearance", "consignment", "delivery",
        "fedex", "dhl", "bluedart", "india post",
        # Government scheme scams
        "pm kisan", "ayushman", "jan dhan", "ration", "subsidy",
        "beneficiary", "aadhar",
    ]
    if any(kw in msg_lower for kw in authority_signals):
        return ("Kamla Devi", KAMLA_DEVI)

    # Default: elderly persona for unrecognized scams
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
