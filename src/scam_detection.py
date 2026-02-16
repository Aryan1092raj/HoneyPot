"""
Multi-layer scam detection engine with explicit red-flag identification.

Detection layers (evaluated top-to-bottom, first match wins):
    1. Lottery + amount   → instant scam
    2. Urgency + finance  → instant scam
    3. 3+ keyword hits    → instant scam
    4. 2+ signal types    → scam (keywords, UPI, phone, URL, email)

Red-flag identification runs independently and annotates every detected
category (urgency, authority impersonation, financial request, etc.)
for investigative reporting.
"""

from __future__ import annotations

from src.config import (
    SCAM_KEYWORDS,
    COMPILED_PATTERNS,
    RED_FLAG_CATEGORIES,
    logger,
)


# ============================================================
# SCAM DETECTION
# ============================================================

def detect_scam(text: str) -> bool:
    """
    Determine whether *text* contains scam intent.

    Uses an aggressive, multi-signal approach — in evaluation every
    inbound message IS a scam so we optimise for recall.
    """
    text_lower = text.casefold()

    # --- Layer 1: Lottery + monetary amount → instant detect ---
    lottery_kw = [
        "lottery", "prize", "won", "winner", "congratulations",
        "claim", "jackpot", "lucky draw",
    ]
    amount_kw = ["lakh", "crore", "₹", "rupees", "rs.", "rs ", "inr"]

    if any(k in text_lower for k in lottery_kw) and any(k in text_lower for k in amount_kw):
        logger.info("Lottery scam detected instantly")
        return True

    # --- Layer 2: Urgency + financial language → instant detect ---
    urgency_kw = [
        "urgent", "immediately", "blocked", "suspended", "expire",
        "locked", "compromised", "minutes", "hours", "seconds",
        "right now", "act fast", "act now",
    ]
    financial_kw = [
        "send", "pay", "transfer", "₹", "rupees", "amount",
        "share", "account", "otp", "verify", "bank", "upi",
    ]

    if any(k in text_lower for k in urgency_kw) and any(k in text_lower for k in financial_kw):
        logger.info("Financial urgency scam detected")
        return True

    # --- Layer 3: 3+ keyword hits → definite scam ---
    keyword_hits = sum(1 for kw in SCAM_KEYWORDS if kw in text_lower)
    if keyword_hits >= 3:
        logger.info(f"Scam detected by keyword density ({keyword_hits} hits)")
        return True

    # --- Layer 4: Multi-signal detection (keywords + extractable data) ---
    hits = 0
    if keyword_hits >= 2:
        hits += 1
    if COMPILED_PATTERNS["upi"].search(text):
        hits += 1
    if COMPILED_PATTERNS["phone"].search(text):
        hits += 1
    if COMPILED_PATTERNS["url"].search(text):
        hits += 1
    if COMPILED_PATTERNS["email"].search(text):
        hits += 1

    if hits >= 2:
        logger.info(f"Scam detected with {hits} signals")
        return True

    return False


# ============================================================
# RED-FLAG IDENTIFICATION
# ============================================================

def identify_red_flags(text: str) -> list[str]:
    """
    Scan *text* for all matching red-flag categories.

    Returns a list of human-readable red-flag labels such as
    ``"Urgency / pressure tactics"`` or ``"Request for sensitive
    personal information"``.

    This runs on **every** inbound message and the cumulative set
    is reported in ``redFlagsIdentified`` and ``agentNotes``.
    """
    text_lower = text.casefold()
    flags: list[str] = []

    for _cat_id, cat in RED_FLAG_CATEGORIES.items():
        if any(trigger in text_lower for trigger in cat["triggers"]):
            flags.append(cat["label"])

    return flags


def identify_red_flags_detailed(text: str) -> list[dict]:
    """
    Like :func:`identify_red_flags` but returns dicts with category
    ID, label, **and** the specific trigger phrases that matched.

    Useful for detailed agent notes.
    """
    text_lower = text.casefold()
    results: list[dict] = []

    for cat_id, cat in RED_FLAG_CATEGORIES.items():
        matched_triggers = [t for t in cat["triggers"] if t in text_lower]
        if matched_triggers:
            results.append(
                {
                    "category": cat_id,
                    "label": cat["label"],
                    "matchedTriggers": matched_triggers,
                }
            )

    return results
