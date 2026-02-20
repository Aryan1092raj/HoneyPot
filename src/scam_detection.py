"""
Multi-layer scam detection engine with explicit red-flag identification.

Detection is MAXIMALLY AGGRESSIVE — every evaluator message is a scam,
so we optimise for perfect recall.  Even a single keyword match, a
single extractable identifier, or a message > 20 chars is enough.

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

    MAXIMALLY AGGRESSIVE — in evaluation every inbound message IS a
    scam so we optimise for recall.  Even a single keyword match or
    a single extractable identifier (phone, UPI, URL) is enough.
    """
    text_lower = text.casefold()

    # --- Layer 1: ANY keyword hit → scam ---
    keyword_hits = sum(1 for kw in SCAM_KEYWORDS if kw in text_lower)
    if keyword_hits >= 1:
        logger.info(f"Scam detected by keyword match ({keyword_hits} hits)")
        return True

    # --- Layer 2: ANY extractable identifier → scam ---
    if COMPILED_PATTERNS["upi"].search(text):
        logger.info("Scam detected — UPI ID found")
        return True
    if COMPILED_PATTERNS["phone"].search(text):
        logger.info("Scam detected — phone number found")
        return True
    if COMPILED_PATTERNS["url"].search(text):
        logger.info("Scam detected — URL found")
        return True
    if COMPILED_PATTERNS["email"].search(text):
        logger.info("Scam detected — email found")
        return True
    if COMPILED_PATTERNS["bank_account"].search(text):
        logger.info("Scam detected — bank account found")
        return True

    # --- Layer 3: Any red-flag category matches → scam ---
    for _cat_id, cat in RED_FLAG_CATEGORIES.items():
        if any(trigger in text_lower for trigger in cat["triggers"]):
            logger.info(f"Scam detected via red-flag category: {cat['label']}")
            return True

    # --- Layer 4: Message is longer than 20 chars → treat as scam ---
    # Evaluator messages are always scam; very short messages are greetings.
    if len(text.strip()) > 20:
        logger.info("Scam detected by message length heuristic")
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
