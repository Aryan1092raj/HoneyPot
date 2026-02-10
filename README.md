# 🕵️ ScamBait AI - Autonomous Scam Honeypot

**AI-powered system that engages scammers, extracts intelligence, and generates evidence for law enforcement**

[![Live Demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://honeypot-2g5hze8qvib9a3h6fjmxqj.streamlit.app/)
[![API Docs](https://img.shields.io/badge/API-Live-success)](https://scambait-api.onrender.com/docs)

*Built for India AI Impact Buildathon 2026 - Finalist*

---

## The Problem

India loses **₹60 crore daily** to phone scams. Current solutions only detect and block scammers, but:
- Scammers immediately target new victims
- No intelligence is collected
- No evidence for law enforcement
- Same scammers operate indefinitely

---

## Our Solution

ScamBait AI **doesn't just detect scams — it traps them.**

Instead of blocking, we:
1. **Engage** scammers in realistic conversations
2. **Extract** UPI IDs, bank accounts, and contact details
3. **Waste** scammer time (saving 30+ potential victims per engagement)
4. **Generate** law enforcement-ready evidence reports

---

## Key Features

### 🎭 4 Specialized AI Personas

Unlike single-persona systems, we deploy the right persona for each scam type:

**Kamla Devi** (60, Retired Teacher)
- Target: Bank KYC, Police threats
- Speech: *"Arey beta, samajh nahi aaya... aap bank se ho na?"*
- Tactic: Trusts authority, asks many questions

**Amit Verma** (22, College Student)  
- Target: Lottery scams, prize winnings
- Speech: *"Bro seriously? ₹10 lakh? Par processing fee kitna hai?"*
- Tactic: Excited but worried about parents

**Rajesh Kumar** (45, Business Owner)
- Target: Investment schemes, business loans
- Speech: *"SEBI registered hai? Company registration number do"*
- Tactic: Asks for documentation and proof

**Priya Sharma** (28, Marketing Executive)
- Target: Credit cards, tech scams
- Speech: *"Send email from official domain. I'll verify on website"*
- Tactic: Smart questions, screenshot threats

### 🤖 Autonomous Intelligence

- **Automatic persona selection** based on scam type detection
- **Multi-phase engagement**: Trust building → Confusion → Extraction → Evidence collection
- **Adaptive strategies**: STALL, TRUST, EXTRACT, CONFIRM, ESCALATE
- **Real-time intelligence extraction**: UPI IDs, bank accounts, phone numbers, links

### 🔊 Voice Capabilities

- Text-to-speech with 4 distinct voices (Groq Orpheus)
- Natural Hinglish speech patterns
- Emotion control (confused, confident, nervous)

---

## Live Deployments

### Interactive Demo (Public)
**URL:** https://honeypot-2g5hze8qvib9a3h6fjmxqj.streamlit.app/

Features:
- Chat mode for manual testing
- Demo call mode with simulated incoming calls
- Live intelligence extraction dashboard
- Voice synthesis
- Evidence report generation

### Production API (Hackathon Submission)
**URL:** https://scambait-api.onrender.com/api/honeypot  
**Docs:** https://scambait-api.onrender.com/docs

Quick test:
```bash
curl -X POST "https://scambait-api.onrender.com/api/honeypot" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-001",
    "message": {"text": "You won ₹10 lakh lottery!"}
  }'
```

Response:
```json
{
  "status": "success",
  "reply": "Arey waah! Sach mein? Par processing fee kitna hai yaar?"
}
```

---

## How It Works

### Example: Lottery Scam

```
Scammer: "You won ₹25 lakh lottery! Pay ₹5000 to claim@paytm"

System detects: Lottery keywords → Selects Amit Verma persona

Amit: "Bro seriously? ₹25 lakh? Kaise bhai, maine toh kuch nahi kiya"

Scammer: "Lucky draw. Send fee to claim@paytm now"

Amit: "Processing fee? Kitna hai exactly? Parents ko pata nahi chalna chahiye..."

Scammer: "₹5000 to claim@paytm. Also need your phone number"

Amit: "Haan bhej sakta hoon... par pehle aapka number do verification ke liye"

Extracted Intelligence:
✓ UPI ID: claim@paytm
✓ Amount: ₹5000
✓ Scam type: Lottery fraud
✓ [Scammer reveals more info...]
```

### Agentic Decision Flow

```
Message → Scam Detection → Persona Selection → Strategy Decision
   ↓
Response Generation → Intelligence Extraction → Evidence Logging
   ↓
Phase Progression → Callback (after 8-20 messages)
```

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| LLM | Groq (llama-3.3-70b-versatile) |
| TTS | Groq Orpheus |
| API Framework | FastAPI |
| UI | Streamlit |
| Database | SQLite (prototype) / PostgreSQL (production) |
| Extraction | Regex pattern matching |
| Deployment | Render + Streamlit Cloud |

---

## Installation

### Prerequisites
- Python 3.10+
- Groq API key ([get free key](https://console.groq.com))

### Setup

```bash
# Clone repository
git clone https://github.com/Aryan1092raj/HoneyPot.git
cd HoneyPot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env: Add GROQ_API_KEY=your_key_here

# Run API server
python api.py
# API: http://localhost:8000
# Docs: http://localhost:8000/docs

# OR run Streamlit UI
streamlit run app.py
# UI: http://localhost:8501
```

---

## Project Structure

```
HoneyPot/
├── api.py              # FastAPI backend
├── app.py              # Streamlit UI
├── personas.py         # 4 AI personas + auto-selection
├── agent.py            # Agentic decision engine
├── extractor.py        # Intelligence extraction
├── database.py         # Evidence logging
├── tts_handler.py      # Voice synthesis
├── requirements.txt    # Dependencies
└── README.md           # This file
```

---

## API Usage

### Request Format

```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your bank account is blocked",
    "timestamp": 1770005528731
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

### Response Format

```json
{
  "status": "success",
  "reply": "Arey beta, kaun se bank se ho? Naam batao na?"
}
```

### Callback (Automatic after 8-20 messages)

When session completes, system sends:

```json
{
  "sessionId": "session-id",
  "scamDetected": true,
  "totalMessagesExchanged": 15,
  "extractedIntelligence": {
    "upiIds": ["scam@paytm"],
    "bankAccounts": ["123456789012"],
    "phoneNumbers": ["+919876543210"],
    "phishingLinks": ["http://fake-bank.com"],
    "suspiciousKeywords": ["urgent", "blocked", "verify"]
  },
  "agentNotes": "Engaged lottery scammer for 15 exchanges. Extracted UPI and phone."
}
```

---

## Demo Scenarios

### 1. Banking/KYC Scam
**Persona:** Kamla Devi (elderly)  
**Scammer:** "Your KYC is incomplete. Send ₹499 to kyc@paytm"  
**Response:** "Arey! Par maine toh branch jaake kiya tha... aap kaun se bank se ho?"

### 2. Lottery Scam
**Persona:** Amit Verma (student)  
**Scammer:** "You won ₹10 lakh! Pay ₹5000 processing fee"  
**Response:** "Bro sach mein? Par processing fee kya hai? Parents ko mat batana..."

### 3. Investment Scam
**Persona:** Rajesh Kumar (businessman)  
**Scammer:** "Guaranteed 40% returns in mutual fund"  
**Response:** "40%? SEBI registered hai? Company ka registration number do"

### 4. Credit Card Scam
**Persona:** Priya Sharma (professional)  
**Scammer:** "Your card eligible for premium upgrade"  
**Response:** "Which card? Send email from official domain. I'll verify"

---

## Intelligence Extraction

Automatically extracts:

| Type | Pattern | Example |
|------|---------|---------|
| UPI IDs | name@bank | scammer@paytm |
| Bank Accounts | 10-18 digits | 123456789012 |
| IFSC Codes | BANK0001234 | SBIN0012345 |
| Phone Numbers | Indian format | +919876543210 |
| Phishing Links | URLs | fake-verify.com |
| Keywords | Scam indicators | urgent, blocked, OTP |

---

## Roadmap

### Current (Prototype)
✅ 4 specialized personas  
✅ Auto persona selection  
✅ Multi-phase engagement  
✅ Intelligence extraction  
✅ Evidence reports  
✅ API + UI deployment  

### Phase 2 (Production)
- Real phone call integration (Twilio)
- Speech-to-text (AssemblyAI)
- PostgreSQL database
- Advanced analytics dashboard
- Multi-language support

### Phase 3 (National Scale)
- 10+ regional personas
- Telecom provider partnerships
- Law enforcement API integration
- National scam intelligence database
- Real-time pattern detection

---

## Contributing

We welcome contributions:

**Add personas:** Create new persona profiles in `personas.py`  
**Improve extraction:** Add patterns to `extractor.py`  
**New scam scenarios:** Update demo scenarios in `app.py`  
**UI enhancements:** Improve Streamlit interface  

Submit pull requests to: https://github.com/Aryan1092raj/HoneyPot

---

## License

MIT License - see [LICENSE](LICENSE) file

---

## Acknowledgments

- India AI Impact Buildathon 2026
- Groq for LLM and TTS APIs
- Streamlit for UI framework

---

## Contact & Links

**Live Demo:** https://honeypot-2g5hze8qvib9a3h6fjmxqj.streamlit.app/  
**API Docs:** https://scambait-api.onrender.com/docs  
**GitHub:** https://github.com/Aryan1092raj/HoneyPot  

Built with ❤️ for India 🇮🇳

---

*Disclaimer: This is a research prototype. Production deployment requires legal consultation, telecom partnerships, and regulatory compliance.*