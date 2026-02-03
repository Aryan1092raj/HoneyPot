# 🕵️ ScamBait AI - Autonomous Scam Honeypot System

**Fighting India's ₹60 Crore Daily Fraud Crisis with Agentic AI**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://honeypot-2g5hze8qvib9a3h6fjmxqj.streamlit.app/)

ScamBait AI is an **autonomous AI-powered honeypot** that engages scammers in realistic conversations, wastes their time, and collects evidence for law enforcement. Built for the India AI Impact Buildathon.

---


## 🎯 The Problem

India faces a massive fraud crisis:
- **5,00,000+ scam calls** flood India daily
- **₹60+ crore lost** to fraudulent calls every day
- **3+ spam calls** per citizen per day
- Current solutions only **detect and block** — they don't fight back

---
## 🚀 Live Demo

**Try it now:** [https://honeypot-2g5hze8qvib9a3h6fjmxqj.streamlit.app/](https://honeypot-2g5hze8qvib9a3h6fjmxqj.streamlit.app/)

---

## 🔌 API Endpoint (Hackathon Submission)

**Production API:** Available for hackathon evaluation

**Authentication:** API key required via `X-API-Key` header

**Endpoint:** `POST /api/honeypot`

**Features:**
- ✅ API key authentication
- ✅ Multi-turn conversation support with history
- ✅ Autonomous scam detection and engagement
- ✅ Real-time intelligence extraction
- ✅ Automatic callback to hackathon system
- ✅ Structured JSON response

**Documentation:** See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API reference

**Quick Test:**
```bash
curl -X POST http://localhost:8000/api/honeypot \
  -H "X-API-Key: your-key-here" \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "test-1", "message": "Your bank account is blocked!"}'
```

---

## 💡 Our Solution

**ScamBait AI** doesn't just detect scams — it **traps them.**

### How It Works:
1. User receives scam call and detects it's fraudulent
2. Hands off conversation to AI agent
3. AI pretends to be a vulnerable person (elderly teacher, student, etc.)
4. AI **autonomously decides strategies** to keep scammer engaged
5. While talking, AI **secretly extracts evidence**: UPI IDs, bank accounts, phishing links
6. System logs everything and generates **law enforcement-ready reports**

---

## 🌟 Key Features

### 🤖 Agentic AI System
- **Autonomous Decision Making**: AI chooses strategies (STALL, TRUST, EXTRACT, CONFIRM) without human input
- **4-Phase Engagement**: Trust Building → Feigned Confusion → Extraction → Evidence Collection
- **Adaptive Responses**: Changes behavior based on scammer's tactics

### 🎭 Realistic Personas
- **Elderly Teacher** (62, retired, tech-unsure, speaks Hinglish)
- **Young Professional** (28, software engineer, busy, impatient)
- **College Student** (20, naive, easily pressured)

### 🔊 Voice Mode
- Real-time text-to-speech using Groq Orpheus
- Different voices for each persona
- Sequential audio playback (scammer → agent)

### 📞 Demo Call Mode
- Simulated incoming scam calls with realistic UI
- Auto-progression through conversation
- Live intelligence panel showing extraction in real-time
- Call timer, session tracking, risk indicators

### 🔍 Evidence Extraction
Automatically detects and extracts:
- 💳 **UPI IDs** (name@paytm, name@ybl, etc.)
- 🏦 **Bank Account Numbers** (9-18 digits)
- 🏦 **IFSC Codes** (e.g., SBIN0001234)
- 📞 **Phone Numbers** (Indian format)
- 🔗 **Phishing Links** (suspicious URLs)

### 📊 Intelligence Dashboard
- Real-time risk level tracking (🟢 LOW → 🟡 MEDIUM → 🔴 HIGH)
- Live strategy display (what AI is thinking)
- Current engagement phase indicator
- Evidence counter with detailed breakdown

### 📄 Evidence Reports
- Downloadable TXT reports
- Includes full conversation log
- Extracted evidence summary
- Timestamped exchanges with AI strategy notes
- Ready for law enforcement submission

---

### Demo Call Mode Instructions:
1. Click **"📞 Demo Call Mode"** tab
2. Select a scam scenario (Banking, Lottery, or Police Threat)
3. Click **"Accept Call"**
4. Click **"Continue Call"** to progress through conversation
5. Watch AI engage scammer and extract evidence in real-time

---

## 🛠️ Tech Stack

| Component | Technology | Why |
|-----------|------------|-----|
| **LLM** | Groq (llama-3.3-70b-versatile) | Fast, free, high-quality responses |
| **TTS** | Groq Orpheus (canopylabs/orpheus-v1-english) | Natural-sounding voices with emotion control |
| **Frontend** | Streamlit | Rapid prototyping, clean UI |
| **Extraction** | Regex + Pattern Matching | Reliable, no external dependencies |
| **Database** | SQLite | Lightweight, file-based, perfect for prototype |
| **Deployment** | Streamlit Cloud | Free hosting, easy updates |

---

## 📦 Installation (Local Development)

### Prerequisites
- Python 3.10+
- Groq API key ([Get one free](https://console.groq.com))

### Setup

```bash
# Clone repository
git clone https://github.com/Aryan1092raj/HoneyPot.git
cd scamhoneypot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements-ui.txt    # For Streamlit UI
pip install -r requirements-api.txt   # For API server

# Configure environment
cp .env.example .env
# Edit .env and add:
#   GROQ_API_KEY=your_groq_key_here
#   HONEYPOT_API_KEY=your_secure_api_key_here

# Run Streamlit UI
streamlit run app.py

# OR run API server
python api.py
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

---

## 📁 Project Structure

```
scamhoneypot/
├── app.py                 # Main Streamlit UI (Chat + Demo Call modes)
├── api.py                 # FastAPI backend for hackathon submission
├── agent.py               # Agentic AI logic (strategy decisions)
├── personas.py            # Persona definitions with Hinglish
├── extractor.py           # Evidence extraction patterns
├── database.py            # SQLite conversation logging
├── tts_handler.py         # Groq TTS integration
├── stt_handler.py         # Groq STT integration
├── requirements-ui.txt    # UI dependencies
├── requirements-api.txt   # API dependencies
├── .env.example           # Environment template
├── API_DOCUMENTATION.md   # Complete API reference
└── README.md              # This file
```
├── requirements.txt       # Python dependencies
├── .env                   # API keys (not in repo)
├── .gitignore             # Git exclusions
└── README.md              # This file
```

---

## 🎯 How the Agentic System Works

### Strategy Decision Process:
```
Scammer Message
    ↓
AI Analyzes:
  - Current phase (trust_building/confusion/extraction/evidence_collection)
  - Data extracted so far
  - Scammer's pressure level
    ↓
AI Decides Strategy:
  - STALL: Ask for repetition, pretend confusion
  - TRUST: Build rapport, seem vulnerable
  - EXTRACT: Push for financial details
  - CONFIRM: Repeat back to get clearer evidence
  - ESCALATE: Move to next phase
    ↓
AI Generates Response
    ↓
Extracts Evidence Automatically
    ↓
Logs Everything to Database
```

### Example Exchange:
```
Scammer: "Your account is blocked. Share your UPI ID immediately."
    ↓
AI Strategy Decision: STALL (waste time)
    ↓
AI Response: "Beta, mujhe samajh nahi aaya. My hearing is not good. 
              Can you repeat slowly? Which account you are saying?"
    ↓
Extraction: [No evidence yet]
    ↓
Phase: Still in "trust_building"
```

---

## 📊 Demo Scenarios

### 1. Banking Scam (KYC Update)
Scammer claims incomplete KYC, threatens account block, asks for verification fee.

### 2. Lottery Scam
Claims user won ₹50 lakhs, needs processing fee and bank details to "verify identity."

### 3. Police/Legal Threat
Impersonates cyber crime officer, threatens arrest, demands bank details for "investigation."

---

## 🔧 Configuration

### Environment Variables
```bash
# .env file
GROQ_API_KEY=gsk_your_api_key_here
```

### Customization
- **Add personas**: Edit `personas.py`
- **Add scenarios**: Edit `DEMO_SCENARIOS` in `app.py`
- **Modify extraction**: Edit patterns in `extractor.py`
- **Change voices**: Edit `persona_voices` in `tts_handler.py`

---

## 🚦 Usage

### Chat Mode (Manual Testing)
1. Toggle "Demo Mode" ON
2. Select scenario
3. Click "Send Next Demo Message" to progress
4. Watch AI respond with strategy + phase indicators

### Demo Call Mode (Simulated Calls)
1. Switch to "Demo Call Mode" tab
2. See incoming call from random scenario
3. Accept call
4. Click "Continue Call" to auto-progress
5. View live extraction on right panel
6. Download evidence report when complete

---

## 📈 Impact & Scalability

### Current (Prototype):
- ✅ Proves agentic AI can engage scammers convincingly
- ✅ Demonstrates evidence extraction works
- ✅ Shows phase-based engagement strategy
- ✅ Validates persona-based responses

### Phase 2 (Production):
- 🔄 Integrate with Twilio for real phone calls
- 🔄 Add AssemblyAI for real-time speech-to-text
- 🔄 Connect to telecom providers for call routing
- 🔄 Law enforcement API integration
- 🔄 Scale to handle 1000+ concurrent calls

### Vision:
- 🎯 Waste scammer time = fewer victims
- 🎯 Build national scammer database
- 🎯 Provide evidence for police prosecutions
- 🎯 Make scamming India too expensive/risky

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- More persona variations
- Better extraction patterns
- Additional scam scenarios
- UI/UX enhancements
- Performance optimizations

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🏆 Acknowledgments

- **India AI Impact Buildathon** for the challenge
- **Groq** for fast, free LLM + TTS APIs
- **Streamlit** for the amazing framework

---

## 📞 Contact

**Demo:** https://honeypot-2g5hze8qvib9a3h6fjmxqj.streamlit.app/

**Built with ❤️ for India** 🇮🇳

---

**⚠️ Disclaimer:** This is a prototype for educational and research purposes. Real-world deployment requires legal consultation, telecom partnerships, and regulatory compliance.
