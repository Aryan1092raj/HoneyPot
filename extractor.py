import re
from typing import Dict, List


class IndianFinancialExtractor:
    """
    Extracts Indian financial data from scammer messages.
    Detects: UPI IDs, Account Numbers, IFSC Codes, Phone Numbers, Links
    """

    def __init__(self):
        # --- UPI Patterns ---
        self.upi_patterns = [
            r'\b[a-zA-Z0-9][a-zA-Z0-9.\-_]{2,29}@(okaxis|okhdfcbank|oksbi|okicici|okkotak|paytm|ybl|upi|gpay|phonepe|slice|bincl|freecharge|airmoney|jiopay|idfcfirst|airtel|vi|bsnl)\b',
            r'\bUPI\s*(?:ID|id|Id)[:\s]*([a-zA-Z0-9.\-_]+@[a-zA-Z0-9]+)\b',
            r'\bupi://pay\?pa=([^&\s]+)',
            r'\b[a-zA-Z0-9][a-zA-Z0-9.\-_]{2,29}@[a-zA-Z]{2,15}\b'  # Generic fallback
        ]

        # --- Bank Account Number Patterns ---
        self.account_patterns = [
            r'(?:account|a/c|acct|acc)\s*(?:no|number|num|\.)[:\s]*(\d[\d\s\-]{7,17}\d)',
            r'(?:account|a/c)\s*[:\s]*(\d{9,18})',
            r'\b(\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{0,6})\b'  # XXXX-XXXX-XXXX format
        ]

        # --- IFSC Code Patterns ---
        self.ifsc_patterns = [
            r'\b([A-Z]{4}0[A-Z0-9]{6})\b',
            r'(?:IFSC|ifsc)\s*(?:code|Code)?\s*[:\s]*([A-Z]{4}0[A-Z0-9]{6})'
        ]

        # --- Indian Phone Number Patterns ---
        self.phone_patterns = [
            r'(?:\+91[\s\-]?)?(?:0)?([6789]\d{9})\b',
            r'\b(\+91[\s\-]?[6789]\d{9})\b',
            r'(?:call|number|no|mobile|phone|whatsapp)\s*(?:me\s*)?(?:on\s*)?[:\s]*(\+?91?[\s\-]?[6789]\d{9})'
        ]

        # --- Suspicious Link Patterns ---
        self.link_patterns = [
            r'(https?://[^\s<>"{}|\\^`\[\]]+)',
            r'(www\.[^\s<>"{}|\\^`\[\]]+)',
            r'(bit\.ly/[^\s]+)',
            r'(tinyurl\.com/[^\s]+)',
            r'(t\.co/[^\s]+)'
        ]

        # --- Known scam UPI suffixes to flag ---
        self.suspicious_upi_domains = [
            'paytm', 'ybl', 'gpay', 'phonepe',
            'slice', 'bincl', 'freecharge'
        ]

        # --- Known suspicious link keywords ---
        self.suspicious_link_keywords = [
            'verify', 'confirm', 'update', 'login', 'secure',
            'bank', 'sbi', 'hdfc', 'icici', 'npci',
            'kyc', 'otp', 'reward', 'prize', 'claim'
        ]

    # ============================================================
    # EXTRACTION METHODS
    # ============================================================

    def extract_upi(self, text: str) -> List[str]:
        """Extract UPI IDs from text"""
        results = []
        for pattern in self.upi_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            results.extend(matches)

        # Deduplicate + filter out common emails
        cleaned = []
        for item in results:
            item = item.strip()
            # Skip obvious emails
            if any(email in item.lower() for email in ['gmail', 'yahoo', 'hotmail', 'outlook']):
                continue
            if item and item not in cleaned:
                cleaned.append(item)

        return cleaned

    def extract_account_numbers(self, text: str) -> List[str]:
        """Extract bank account numbers"""
        results = []
        for pattern in self.account_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean: remove spaces and dashes
                cleaned = re.sub(r'[\s\-]', '', match)
                # Valid Indian account: 9-18 digits
                if 9 <= len(cleaned) <= 18 and cleaned.isdigit():
                    if cleaned not in results:
                        results.append(cleaned)

        return results

    def extract_ifsc(self, text: str) -> List[str]:
        """Extract IFSC codes"""
        results = []
        for pattern in self.ifsc_patterns:
            matches = re.findall(pattern, text)
            results.extend(matches)

        return list(set(results))

    def extract_phone_numbers(self, text: str) -> List[str]:
        """Extract Indian phone numbers"""
        results = []
        for pattern in self.phone_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                cleaned = re.sub(r'[\s\-]', '', match)
                # Normalize: remove +91 prefix for comparison
                normalized = cleaned.replace('+91', '')
                if len(normalized) == 10 and normalized[0] in '6789':
                    # Store with +91 prefix
                    formatted = f"+91 {normalized}"
                    if formatted not in results:
                        results.append(formatted)

        return results

    def extract_links(self, text: str) -> List[str]:
        """Extract URLs/links"""
        results = []
        for pattern in self.link_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            results.extend(matches)

        return list(set(results))

    # ============================================================
    # MAIN EXTRACTION + ANALYSIS
    # ============================================================

    def extract_all(self, text: str) -> Dict:
        """
        Run all extractors on text.
        Returns structured dict with all findings.
        """
        return {
            "upi_ids": self.extract_upi(text),
            "account_numbers": self.extract_account_numbers(text),
            "ifsc_codes": self.extract_ifsc(text),
            "phone_numbers": self.extract_phone_numbers(text),
            "links": self.extract_links(text)
        }

    def analyze_links(self, links: List[str]) -> List[Dict]:
        """Flag suspicious links based on keywords"""
        analyzed = []
        for link in links:
            suspicious = any(
                keyword in link.lower()
                for keyword in self.suspicious_link_keywords
            )
            analyzed.append({
                "url": link,
                "suspicious": suspicious,
                "reason": "Contains suspicious keyword" if suspicious else "No flags"
            })
        return analyzed

    def get_summary(self, text: str) -> Dict:
        """
        Full extraction + risk analysis summary.
        This is what the dashboard calls.
        """
        extracted = self.extract_all(text)
        link_analysis = self.analyze_links(extracted["links"])

        # Count total findings
        total_findings = sum(len(v) for v in extracted.values())

        # Risk level
        if total_findings >= 3:
            risk = "🔴 HIGH"
        elif total_findings >= 1:
            risk = "🟡 MEDIUM"
        else:
            risk = "🟢 LOW"

        return {
            "extracted": extracted,
            "link_analysis": link_analysis,
            "total_findings": total_findings,
            "risk_level": risk
        }


# ============================================================
# QUICK TEST (run: python extractor.py)
# ============================================================

if __name__ == "__main__":
    extractor = IndianFinancialExtractor()

    # --- Test Messages (realistic scammer messages) ---
    test_messages = [
        "Send the amount to my UPI: fraudster123@paytm and my account number is 4523119876543210 with IFSC HDFC0004021",
        "Call me back on +91 9876543210. Transfer to rajesh.kumar@ybl. My WhatsApp is 8765432109",
        "Click this link to verify: https://secure-sbi-login.com/verify?token=abc123. Your KYC update link: https://bit.ly/kyc-update",
        "My account number is 123456789 at SBI. IFSC code is SBIN0001234. Send money to priya@okicici",
        "Transfer ₹5000 to 9876543210@gpay. If not working, call 7654321098. Link: https://www.reward-claim.com/prize"
    ]

    print("=" * 60)
    print("  INDIAN FINANCIAL DATA EXTRACTOR - TEST")
    print("=" * 60)

    for i, msg in enumerate(test_messages, 1):
        print(f"\n📨 Test Message {i}:")
        print(f"   \"{msg[:80]}...\"" if len(msg) > 80 else f"   \"{msg}\"")
        print("-" * 40)

        summary = extractor.get_summary(msg)

        print(f"   Risk Level: {summary['risk_level']}")
        print(f"   Total Findings: {summary['total_findings']}")

        ext = summary["extracted"]
        if ext["upi_ids"]:
            print(f"   💳 UPI IDs: {ext['upi_ids']}")
        if ext["account_numbers"]:
            print(f"   🏦 Accounts: {ext['account_numbers']}")
        if ext["ifsc_codes"]:
            print(f"   🏦 IFSC: {ext['ifsc_codes']}")
        if ext["phone_numbers"]:
            print(f"   📞 Phones: {ext['phone_numbers']}")
        if ext["links"]:
            print(f"   🔗 Links: {ext['links']}")
            for la in summary["link_analysis"]:
                if la["suspicious"]:
                    print(f"      ⚠️  {la['url']} → {la['reason']}")

    print("\n" + "=" * 60)
    print("  ALL TESTS COMPLETE")
    print("=" * 60)