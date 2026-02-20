"""
Configuration constants and logging setup for ScamBait AI.

Centralizes all tunable parameters, API keys, keyword lists,
and compiled regex patterns used across the application.
"""

import os
import re
import logging
from dotenv import load_dotenv

# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("scambait-api")

# ============================================================
# API KEYS & URLS
# ============================================================

VALID_API_KEY = os.getenv("HONEYPOT_API_KEY", "scambait-secure-key-2026-hackathon")
CALLBACK_URL = os.getenv(
    "HACKATHON_CALLBACK_URL",
    "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ============================================================
# SESSION PARAMETERS
# ============================================================

MIN_MESSAGES = 1   # Send callback from first turn for maximum coverage
MAX_MESSAGES = 10  # Hard cap — evaluator sends at most 10 turns

# ============================================================
# SCAM DETECTION KEYWORDS
# ============================================================

SCAM_KEYWORDS: tuple[str, ...] = (
    # Banking / Finance
    "urgent", "blocked", "suspended", "verify", "otp", "kyc", "pan",
    "aadhaar", "account", "bank", "upi", "transfer", "payment",
    "immediately", "click", "link", "update", "expire", "freeze",
    "locked", "compromised", "share", "identity", "security",
    "prevent", "suspension", "digit", "minutes", "hours",
    # Lottery / Prize
    "lottery", "prize", "winner", "won", "congratulations", "claim",
    "lakh", "crore", "rupees", "jackpot", "lucky", "draw",
    # Threats
    "police", "arrest", "court", "legal", "case", "crime", "fraud",
    # Offers
    "refund", "cashback", "reward", "bonus", "offer", "limited",
    # Extended: more scam indicators
    "unauthorized", "transaction", "debit", "credit",
    "pin", "cvv", "password", "credential", "login",
    "selected", "chosen", "allocation", "approved",
    "fee", "charge", "tax", "processing", "registration",
    "hurry", "fast", "quick", "deadline", "today",
    "complaint", "penalty", "fine", "warning", "notice",
    "whatsapp", "telegram", "call", "contact", "helpline",
    "investment", "returns", "profit", "guaranteed", "scheme",
    "crypto", "bitcoin", "forex", "trading", "stock",
    "insurance", "loan", "emi", "interest", "installment",
    "deliver", "package", "courier", "customs", "shipping",
    # Scenario: Electricity Bill scam
    "electricity", "bill", "disconnect", "disconnection", "meter",
    "overdue", "outstanding", "bijli", "power cut", "supply",
    "reconnection", "ebill", "bses", "tata power", "discom",
    # Scenario: Job Scam
    "job", "hiring", "salary", "resume", "interview",
    "vacancy", "placement", "work from home", "freelance",
    "recruitment", "hr", "joining", "offer letter", "stipend",
    # Scenario: Income Tax scam
    "income tax", "itr", "tax refund", "tax notice", "assessment",
    "e-filing", "tax department", "it department", "tds",
    "challan", "demand notice", "outstanding tax", "rectification",
    # Scenario: Insurance scam
    "policy", "premium", "maturity", "nomination", "lic",
    "health insurance", "life insurance", "endowment", "surrender",
    "claim settlement", "insurance renewal", "policy lapse",
    # Scenario: Refund scam
    "refund", "reimbursement", "excess payment", "overpaid",
    "reversal", "credit back", "return amount", "refund process",
    # Scenario: Tech Support scam
    "virus", "malware", "hacked", "remote access", "anydesk",
    "teamviewer", "tech support", "computer", "laptop",
    "antivirus", "license", "subscription", "renewal",
    # Scenario: Customs / Parcel scam
    "detained", "seized", "contraband", "narcotics", "illegal",
    "clearance", "duty", "import", "export", "consignment",
)

# ============================================================
# RED-FLAG CATEGORIES
# ============================================================
# Each category maps to a list of trigger phrases and a human-readable label.
# Used by scam_detection.identify_red_flags().

RED_FLAG_CATEGORIES: dict[str, dict] = {
    "URGENCY_PRESSURE": {
        "label": "Urgency / pressure tactics",
        "triggers": [
            "urgent", "immediately", "act now", "expire", "last chance",
            "right now", "act fast", "hurry", "quick", "limited time",
            "within minutes", "within hours", "today only", "don't delay",
            "minutes", "hours", "seconds",
        ],
    },
    "AUTHORITY_IMPERSONATION": {
        "label": "Impersonation of authority / institution",
        "triggers": [
            "bank", "rbi", "sbi", "government", "police", "court",
            "reserve bank", "income tax", "sebi", "customs", "telecom",
            "officer", "manager", "department", "ministry", "aadhaar",
        ],
    },
    "FINANCIAL_REQUEST": {
        "label": "Request for money / financial transaction",
        "triggers": [
            "send money", "transfer", "pay", "upi", "payment",
            "processing fee", "registration fee", "advance amount",
            "deposit", "invest", "amount", "rupees", "rs.",
        ],
    },
    "PERSONAL_INFO_REQUEST": {
        "label": "Request for sensitive personal information",
        "triggers": [
            "otp", "password", "pin", "cvv", "card number",
            "aadhaar", "pan", "kyc", "verify identity", "share details",
            "bank details", "account number", "login", "credentials",
        ],
    },
    "TOO_GOOD_TO_BE_TRUE": {
        "label": "Too-good-to-be-true offer",
        "triggers": [
            "lottery", "won", "prize", "congratulations", "winner",
            "guaranteed returns", "double", "triple", "jackpot",
            "lakh", "crore", "free", "lucky draw", "cashback", "reward",
        ],
    },
    "THREATENING_LANGUAGE": {
        "label": "Threatening / fear-based language",
        "triggers": [
            "arrest", "court", "legal action", "case filed", "jail",
            "warrant", "crime", "fraud", "suspend", "block", "freeze",
            "locked", "compromised", "terminate", "penalty", "fine",
        ],
    },
    "SUSPICIOUS_LINKS": {
        "label": "Contains suspicious links or redirects",
        "triggers": [
            "http://", "https://", "www.", "click here", "click link",
            ".xyz", ".tk", ".ml", "bit.ly", "tinyurl",
        ],
    },
    "UPFRONT_PAYMENT": {
        "label": "Upfront payment required before benefit",
        "triggers": [
            "processing fee", "registration fee", "tax amount",
            "claim charge", "advance", "fee before", "pay to receive",
            "pay first", "token amount",
        ],
    },
    "SECRECY_REQUEST": {
        "label": "Request for secrecy",
        "triggers": [
            "don't tell", "keep secret", "confidential", "private",
            "between us", "do not share", "alone",
        ],
    },
    "IDENTITY_THEFT": {
        "label": "Identity theft / credential harvesting",
        "triggers": [
            "otp", "pin", "cvv", "password", "login", "credential",
            "card number", "expiry", "security code", "mother's maiden",
            "date of birth", "social security", "ssn",
            "verify identity", "confirm identity", "authenticate",
        ],
    },
    "FAKE_DEADLINE": {
        "label": "Artificial deadline / time pressure",
        "triggers": [
            "today only", "last chance", "final warning", "24 hours",
            "48 hours", "within minutes", "within hours", "expires today",
            "before midnight", "deadline", "closing", "last date",
            "time is running out", "hurry up", "don't delay",
        ],
    },
    "IMPERSONATION_TECH": {
        "label": "Impersonation of tech company / service",
        "triggers": [
            "google", "amazon", "flipkart", "paytm", "phonepe",
            "microsoft", "apple", "whatsapp", "facebook", "instagram",
            "netflix", "gpay", "google pay", "razorpay",
            "customer care", "helpline", "support team", "technical support",
        ],
    },
    "DELIVERY_SCAM": {
        "label": "Fake delivery / package scam",
        "triggers": [
            "package", "parcel", "delivery", "courier", "customs",
            "shipment", "tracking", "dispatch", "warehouse",
            "customs duty", "import tax", "delivery charge",
            "detained", "seized", "contraband", "narcotics",
            "clearance", "consignment",
        ],
    },
    "JOB_SCAM": {
        "label": "Fake job / recruitment scam",
        "triggers": [
            "job", "hiring", "salary", "resume", "interview",
            "vacancy", "placement", "work from home", "freelance",
            "recruitment", "offer letter", "joining", "stipend",
            "data entry", "part time", "full time", "hr department",
        ],
    },
    "UTILITY_SCAM": {
        "label": "Fake utility bill / disconnection threat",
        "triggers": [
            "electricity", "bill", "disconnect", "disconnection",
            "meter", "overdue", "outstanding", "bijli", "power cut",
            "supply", "reconnection", "ebill", "bses", "tata power",
            "gas bill", "water bill", "utility",
        ],
    },
    "INSURANCE_SCAM": {
        "label": "Fake insurance / policy scam",
        "triggers": [
            "policy", "premium", "maturity", "nomination", "lic",
            "health insurance", "life insurance", "endowment",
            "surrender", "claim settlement", "policy lapse",
            "insurance renewal", "bonus amount", "annuity",
        ],
    },
    "TAX_SCAM": {
        "label": "Fake income tax / government notice scam",
        "triggers": [
            "income tax", "itr", "tax refund", "tax notice",
            "assessment", "e-filing", "tax department", "it department",
            "tds", "challan", "demand notice", "outstanding tax",
            "rectification", "pan verification",
        ],
    },
    "TECH_SUPPORT_SCAM": {
        "label": "Fake tech support / remote access scam",
        "triggers": [
            "virus", "malware", "hacked", "remote access", "anydesk",
            "teamviewer", "tech support", "computer", "laptop",
            "antivirus", "license", "subscription", "renewal",
            "software update", "system compromised",
        ],
    },
}

# ============================================================
# LLM FORBIDDEN PATTERNS (reasoning leakage)
# ============================================================

FORBIDDEN_PATTERNS: tuple[str, ...] = (
    "the user", "the scammer", "user wants", "scammer wants",
    "training data", "output format", "instructions",
    "i will", "i need to", "let me", "i should",
    "as an ai", "as a language model", "i'm an ai",
    "the victim", "the agent", "honeypot",
    "generate", "scenario", "realistic", "respond with",
    "here is", "here's the", "the response",
    "i am calling from", "this is bank", "i am from bank",
    "we need your", "please provide your", "share your",
)

# ============================================================
# NAIVE / FALLBACK RESPONSES
# ============================================================
# Every fallback actively probes for intelligence.

NAIVE_RESPONSES: tuple[str, ...] = (
    # Phase 1: Initial confusion + ask for PHONE NUMBER
    "Haan ji? Kaun bol raha hai? Aapka phone number kya hai... main call back karungi verify karne ke liye?",
    "Arey arey... blocked matlab? Aap pakka bank se ho? Aapka direct number do na, main khud call karungi.",
    # Phase 2: Ask for UPI ID and ACCOUNT NUMBER
    "Acha acha... par kahan bhejoon paisa? Woh UPI ID phir se bolo na slowly... likhti hoon... @ ke baad kya aata hai?",
    "Account number chahiye aapko? Woh passbook mein likha hai... par pehle aapka account number bolo jismein bhejoon? IFSC code bhi dena.",
    # Phase 3: Ask for LINK and EMAIL
    "Woh link wala message phir se bhejo... phone pe chhota likha hai dikha nahi. Pura URL bolo na http se?",
    "Email pe bhej do details beta... mera beta padhega. Aapka email ID kya hai? Gmail hai ya office wala?",
    # Phase 4: Repeat intelligence probes (multi-ask)
    "Haan haan main bhejti hoon... par UPI ID kya tha aapka? Woh @ wala phir se bolo na? Aur phone number bhi do backup ke liye.",
    "Aap branch ka phone number do na... landline hoga na? Aur woh website ka link bhi bhejo, main beta se check karwaungi.",
    # Phase 5: Deeper probing (ask for everything missing)
    "Theek hai... aapka website kya hai? Link bhejo WhatsApp pe. Aur email bhi do, main documents forward karungi.",
    "Padosan fraud fraud bol rahi thi... aapka official email bhejo, phone number do, aur UPI ID bhi — mera beta sab verify karega.",
    # Phase 6: Extra aggressive probing rounds
    "Main confuse ho gayi... ek kaam karo — apna phone number, UPI ID, aur bank account number sab ek saath bol do. Main likh leti hoon.",
    "Arey sun nahi paya... woh link phir se bolo? Aur email pe bhi bhej do. Mera beta aayega toh check karega.",
)

# ============================================================
# KNOWN UPI HANDLES (used for positive UPI identification)
# ============================================================

KNOWN_UPI_HANDLES: frozenset[str] = frozenset({
    # --- Bank-issued UPI handles ---
    "sbi",             # SBI
    "okhdfcbank",      # HDFC Bank
    "okicici",         # ICICI Bank
    "axisb", "axl",    # Axis Bank
    "kotak",           # Kotak Mahindra Bank
    "yes", "yescred",  # Yes Bank
    "federal",         # Federal Bank
    "cnrb",            # Canara Bank
    "pnb",             # Punjab National Bank
    "bob",             # Bank of Baroda
    "uboi",            # Union Bank of India
    "boi",             # Bank of India
    "iob",             # Indian Overseas Bank
    "indianbank",      # Indian Bank
    "idbi",            # IDBI Bank
    "indus",           # IndusInd Bank
    "rbl",             # RBL Bank
    "dbs",             # DBS Bank
    "hsbc",            # HSBC
    "citi",            # Citi Bank
    "sc",              # Standard Chartered
    "bandhan",         # Bandhan Bank
    "jkb",             # J&K Bank
    "kvb",             # KVB
    "tmb",             # TMB
    "cub",             # City Union Bank
    "dlb",             # Dhanlaxmi Bank
    "equitas",         # Equitas
    "fino",            # Fino Payments Bank
    "paytm",           # Paytm Payments Bank
    "airtel",          # Airtel Payments Bank
    "jio",             # Jio Payments Bank
    # --- Non-bank / app UPI handles ---
    "ptaxis", "ptyes", "ptsbi",   # Paytm
    "ybl", "ibl",                  # PhonePe
    "apl", "yapl",                 # Amazon Pay
    "upi",                         # BHIM UPI
    "okaxis",                      # Google Pay via Axis
    "oksbi",                       # Google Pay via SBI
    "jupiteraxis",                 # Jupiter
    "freecharge",                  # Freecharge
    "mbk",                         # Mobikwik
    "paytm",                       # Paytm
    "waaxis", "wasbi",             # WhatsApp Pay
    "slice",                       # Slice
    "niyoicici",                   # Niyo
    "ikwik",                       # mPokket
})

# ============================================================
# COMPILED REGEX PATTERNS
# ============================================================

COMPILED_PATTERNS: dict[str, re.Pattern] = {
    # UPI: handle dotted bank handles like user@ok.bank, user@okicici, user@ybl
    "upi": re.compile(r"[a-zA-Z0-9._-]+@[a-zA-Z][a-zA-Z0-9.]*[a-zA-Z]"),
    # Phone: handle +91-9876543210, +91 98765 43210, +91-98765-43210, bare 10-digit
    # Also handle 0-prefixed like 09876543210, and with parens/dots, and toll-free 1800
    "phone": re.compile(
        r"\+91[\s.\-()]*\d[\d\s.\-()]{7,14}\d"
        r"|\b0?[6-9]\d{9}\b"
        r"|\b0?[6-9]\d[\s.\-]\d{4}[\s.\-]\d{4}\b"
        r"|\b1800[\s.\-]?\d{3}[\s.\-]?\d{4,5}\b"
        r"|\b1800\d{7,10}\b"
    ),
    # URL: handle http, https, www, common shortened URLs, naked domains, IP addresses
    "url": re.compile(
        r"https?://[^\s]+"
        r"|www\.[^\s]+"
        r"|bit\.ly/[^\s]+"
        r"|tinyurl\.com/[^\s]+"
        r"|t\.co/[^\s]+"
        r"|[a-zA-Z0-9-]+\.(?:in|com|org|net|co\.in|info|xyz|online|site|live|app|io)/[^\s]*"
        r"|\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?::\d+)?(?:/[^\s]*)?\b",
        re.IGNORECASE,
    ),
    # Bank account: 9-18 digits (bare), or with spaces between groups
    "bank_account": re.compile(r"\b\d{9,18}\b"),
    # Bank account with spaces: like "1234 5678 9012 34"
    "bank_account_spaced": re.compile(r"\b\d{4}[\s.\-]\d{4}[\s.\-]\d{4}(?:[\s.\-]\d{2,6})?\b"),
    # Email: standard format with TLD validation
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    # IFSC code: 4 alpha + 0 + 6 alphanumeric
    "ifsc": re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b"),
}
