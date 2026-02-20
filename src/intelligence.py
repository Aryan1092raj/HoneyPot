"""
Regex-based intelligence extraction module.

Extracts and deduplicates the following from scammer messages:
    - UPI IDs      (e.g. scam@paytm)
    - Phone numbers (Indian +91 format, both original and cleaned)
    - Phishing URLs (http:// and www. patterns)
    - Bank accounts (10–18 digit numbers, excluding known phones)
    - Email addresses (full TLD validation)
    - Suspicious keywords from the SCAM_KEYWORDS list

All extraction is idempotent — calling multiple times on the same text
will not produce duplicates.
"""

from __future__ import annotations

import re

from src.config import COMPILED_PATTERNS, KNOWN_UPI_HANDLES, SCAM_KEYWORDS, logger


def extract_intelligence_from_history(conversation_history: list, session: dict) -> None:
    """
    Aggressively scan ALL conversation history turns for intelligence.
    Extracts from both scammer and user messages.
    """
    if not conversation_history:
        return
    for msg in conversation_history:
        if isinstance(msg, dict):
            text = msg.get("text", "") or msg.get("content", "")
            if text:
                extract_intelligence(text, session)


def extract_intelligence(text: str, session: dict) -> None:
    """
    Extract actionable intelligence from *text* and store in *session*.

    Extraction order matters:
    1. Emails first (to prevent UPI regex from eating email fragments)
    2. UPI IDs (skip anything already captured as email)
    3. Phone numbers (both cleaned and original format)
    4. URLs (trailing punctuation stripped)
    5. Bank accounts (deduplicated against phone digits)
    6. Suspicious keywords
    """
    intel = session["extracted_intelligence"]

    # 1. Emails ----------------------------------------------------------
    for match in COMPILED_PATTERNS["email"].findall(text):
        if match not in intel["emailAddresses"]:
            intel["emailAddresses"].append(match)
            logger.info(f"Extracted email: {match}")

    # 2. UPI IDs ---------------------------------------------------------
    # Build set of all email matches in text for cross-referencing
    all_email_matches = set(COMPILED_PATTERNS["email"].findall(text))
    all_emails_lower = {e.lower() for e in (all_email_matches | set(intel["emailAddresses"]))}

    for match in COMPILED_PATTERNS["upi"].findall(text):
        match_lower = match.lower()
        domain_part = match_lower.split("@", 1)[-1] if "@" in match_lower else ""

        # Case-insensitive dedup
        existing_lower = {u.lower() for u in intel["upiIds"]}
        if match_lower in existing_lower:
            continue

        # ALWAYS check: skip if this match is a prefix/fragment of a full email
        # e.g. "support@sbi" is a fragment of "support@sbi-fraud-dept.fake.com"
        is_email_fragment = any(
            (match_lower in email and match_lower != email)
            or email.startswith(match_lower)
            for email in all_emails_lower
        )
        if is_email_fragment:
            logger.debug(f"Skipped UPI candidate '{match}' — fragment of email")
            continue

        # Positive match: domain is a known UPI handle → definitely UPI
        is_known_upi = domain_part in KNOWN_UPI_HANDLES
        if is_known_upi:
            intel["upiIds"].append(match)
            logger.info(f"Extracted UPI ID (known handle): {match}")
            continue

        # Skip if it looks like a full email (has a dot-separated TLD after @)
        has_tld = bool(re.match(r"[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", domain_part))
        if not has_tld:
            intel["upiIds"].append(match)
            logger.info(f"Extracted UPI ID: {match}")

    # 3. Phone numbers ---------------------------------------------------
    for match in COMPILED_PATTERNS["phone"].findall(text):
        original = match.strip()
        clean = re.sub(r"[\s.\-]", "", original)
        if clean not in intel["phoneNumbers"]:
            intel["phoneNumbers"].append(clean)
            logger.info(f"Extracted phone: {clean}")
        if original != clean and original not in intel["phoneNumbers"]:
            intel["phoneNumbers"].append(original)
            logger.info(f"Extracted phone (original format): {original}")

    # 4. URLs ------------------------------------------------------------
    for match in COMPILED_PATTERNS["url"].findall(text):
        clean_url = match.rstrip(".,;:!?)")
        if clean_url not in intel["phishingLinks"]:
            intel["phishingLinks"].append(clean_url)
            logger.info(f"Extracted URL: {clean_url}")

    # 5. Bank accounts ---------------------------------------------------
    phone_digits: set[str] = set()
    for pn in intel["phoneNumbers"]:
        digits = re.sub(r"[^0-9]", "", pn)
        phone_digits.add(digits)
        phone_digits.add(digits[-10:])

    for match in COMPILED_PATTERNS["bank_account"].findall(text):
        if match not in intel["bankAccounts"] and match not in phone_digits:
            intel["bankAccounts"].append(match)
            logger.info(f"Extracted bank account: {match}")

    # 5b. Spaced bank accounts (e.g., "1234 5678 9012 34") ---------------
    if "bank_account_spaced" in COMPILED_PATTERNS:
        for match in COMPILED_PATTERNS["bank_account_spaced"].findall(text):
            clean = re.sub(r"[\s.\-]", "", match)
            if clean not in intel["bankAccounts"] and clean not in phone_digits:
                intel["bankAccounts"].append(clean)
                logger.info(f"Extracted bank account (spaced): {clean}")

    # 6. IFSC codes -------------------------------------------------------
    if "ifsc" in COMPILED_PATTERNS:
        for match in COMPILED_PATTERNS["ifsc"].findall(text):
            if match not in intel.get("ifscCodes", []):
                if "ifscCodes" not in intel:
                    intel["ifscCodes"] = []
                intel["ifscCodes"].append(match)
                logger.info(f"Extracted IFSC code: {match}")

    # 7. Suspicious keywords ---------------------------------------------
    text_lower = text.casefold()
    for kw in SCAM_KEYWORDS:
        if kw in text_lower and kw not in intel["suspiciousKeywords"]:
            intel["suspiciousKeywords"].append(kw)
