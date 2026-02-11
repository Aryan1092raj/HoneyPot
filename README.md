# ScamBait AI — Autonomous Scam Honeypot

AI-powered honeypot that detects scam intent, engages scammers with realistic personas, extracts intelligence (UPI IDs, phone numbers, bank accounts), and sends evidence to a callback endpoint — all autonomously.

**India AI Impact Buildathon 2026 — Finalist**

---

## Architecture (5 Layers)

| Layer | Component | Approach |
|-------|-----------|----------|
| **1. Scam Detection** | Rule-based + pattern matching | Keywords, UPI/phone/URL regex, lottery instant-detect |
| **2. Agent Controller** | Deterministic state machine | `trust_building → probing → extraction → winding_down → terminated` |
| **3. Persona Engine** | LLM-powered (Groq) | 4 personas auto-selected by scam type |
| **4. Intel Extraction** | Regex (deterministic) | UPI IDs, phone numbers, bank accounts, URLs, keywords |
| **5. Callback Engine** | Background task (non-blocking) | Sends results to GUVI endpoint after 8–20 messages |

**Key design:** The state machine (Layer 2) controls engagement — not the LLM. The LLM only generates in-character responses. Termination, state transitions, and callback triggers are all backend logic.

---

## Personas

| Persona | Age | Targets | Style |
|---------|-----|---------|-------|
| Kamla Devi | 60, retired teacher | Bank/KYC/authority scams | Confused, Hinglish, asks many questions |
| Amit Verma | 22, college student | Lottery/prize scams | Excited but hesitant, worries about parents |
| Rajesh Kumar | 45, kirana store owner | Investment/loan scams | Asks for SEBI registration, documents |
| Priya Sharma | 28, marketing professional | Credit card/tech scams | Smart questions, verifies online |

Persona is auto-selected on first message based on scam intent and locked for the session.

---

## API

**Endpoint:** `POST /api/honeypot`

### Request

```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your bank account is blocked. Verify immediately.",
    "timestamp": 1770005528731
  },
  "conversationHistory": [],
  "metadata": { "channel": "SMS", "language": "English", "locale": "IN" }
}
```

### Response

```json
{
  "status": "success",
  "reply": "Arey beta, kaun se bank se ho? Naam batao na?"
}
```

### Callback (auto-sent after 8–20 messages)

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
  "agentNotes": "AI agent engaged suspected scammer for 15 message exchanges..."
}
```

---

## Setup

```bash
git clone https://github.com/Aryan1092raj/HoneyPot.git
cd HoneyPot
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements-api.txt

# Add your Groq key
echo GROQ_API_KEY=gsk_xxxxx > .env

# Run
python api.py
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

---

## Project Structure

```
├── api.py          # FastAPI server (all 5 layers)
├── personas.py     # 4 AI personas + auto-selection
├── agent.py        # LLM response generation
├── extractor.py    # Intelligence extraction patterns
├── database.py     # Evidence logging
└── .env            # GROQ_API_KEY
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Groq (llama-3.3-70b-versatile) |
| API | FastAPI + Uvicorn |
| Extraction | Compiled regex patterns |
| Deployment | Render |

---

## State Machine Flow

```
Message received
  → Layer 1: Scam detection (rule + pattern hybrid)
  → Layer 4: Extract intelligence (regex, silent)
  → Layer 2: State transition (deterministic)
  → Layer 3: Generate response (LLM, phase-guided)
  → Layer 5: Callback if session should end
```

**Termination rules (backend logic, not LLM):**
- Hard cap: 20 messages
- Minimum 8 messages + 3 intel items extracted
- Callback already sent

---

**GitHub:** https://github.com/Aryan1092raj/HoneyPot  
**API Docs:** https://scambait-api.onrender.com/docs