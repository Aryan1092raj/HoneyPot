# ScamBait AI — Architecture

## System Overview

ScamBait AI is a **5-layer autonomous scam honeypot** that detects incoming
scam messages, engages the scammer with a realistic AI persona, silently
extracts intelligence (UPI IDs, phone numbers, bank accounts, URLs, emails),
and reports evidence to a callback endpoint.

```
┌──────────────────────────────────────────────────────────────────┐
│                     Incoming Scammer Message                      │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
                 ┌───────────────▼───────────────┐
                 │   Layer 1: Scam Detection      │
                 │   (rule-based + red-flag ID)   │
                 └───────────────┬───────────────┘
                                 │
                 ┌───────────────▼───────────────┐
                 │   Layer 2: Agent Controller    │
                 │   (deterministic state machine)│
                 └───────────────┬───────────────┘
                                 │
                 ┌───────────────▼───────────────┐
                 │   Layer 3: Persona Engine      │
                 │   (Groq LLM, 4 personas)       │
                 └───────────────┬───────────────┘
                                 │
                 ┌───────────────▼───────────────┐
                 │   Layer 4: Intel Extraction     │
                 │   (regex, dedup, accumulate)    │
                 └───────────────┬───────────────┘
                                 │
                 ┌───────────────▼───────────────┐
                 │   Layer 5: Callback Engine      │
                 │   (POST to GUVI endpoint)       │
                 └────────────────────────────────┘
```

---

## Layer Details

### Layer 1 — Scam Detection (`src/scam_detection.py`)

Multi-signal detection evaluated top-to-bottom (first match wins):

| Priority | Condition | Example |
|----------|-----------|---------|
| 1 | Lottery keyword + monetary amount | "Won Rs.25 lakh lottery" |
| 2 | Urgency keyword + financial keyword | "Account blocked, share OTP immediately" |
| 3 | 3+ SCAM_KEYWORDS in one message | "urgent blocked bank verify" |
| 4 | 2+ signal types (keywords + UPI/phone/URL/email) | "Call 9876543210 to verify KYC" |

**Red-flag identification** runs independently on every message and tags
categories like:

- Urgency / pressure tactics
- Impersonation of authority / institution
- Request for sensitive personal information
- Too-good-to-be-true offer
- Threatening / fear-based language
- Request for money / financial transaction
- Contains suspicious links or redirects
- Upfront payment required before benefit
- Request for secrecy

Red flags accumulate across all turns and are reported in `redFlagsIdentified`
and `agentNotes`.

### Layer 2 — Agent Controller (`src/honeypot_agent.py`)

A **deterministic state machine** that controls engagement phases.
The LLM generates text; the state machine decides phase transitions.

```
trust_building (turns 1-2)
    │
    ▼
probing (turns 3-5)
    │
    ▼
extraction (turns 6-8)
    │
    ▼
winding_down (turns 9-10)
```

Each phase injects a specific instruction into the LLM system prompt:

- **trust_building** — Confused, demand caller identity, ask for phone number
- **probing** — Show interest, ask for UPI ID / website / email / link
- **extraction** — Almost comply, but keep asking for one more detail
- **winding_down** — Express doubt, mention family checking, ask for proof

The LLM also receives a "STILL MISSING" directive listing intelligence
types not yet collected, focusing its probing questions on the gaps.

### Layer 3 — Persona Engine (`src/personas.py`)

Four culturally-authentic Indian personas auto-selected by scam type:

| Persona | Age | Target scams | Language style |
|---------|-----|--------------|----------------|
| **Kamla Devi** | 60, retired teacher | Bank/KYC/authority | Confused Hinglish, mentions grandson/pension |
| **Amit Verma** | 22, student | Lottery/prize | Excited casual, "bro"/"yaar" |
| **Rajesh Kumar** | 45, store owner | Investment/loan | Business Hinglish, asks for SEBI docs |
| **Priya Sharma** | 28, marketing pro | Credit card/tech | Modern English-heavy, verifies online |

Persona is selected **once** on first message and locked for the session.
Selection uses semantic intent routing (keyword groups), not the LLM.

### Layer 4 — Intelligence Extraction (`src/intelligence.py`)

Compiled regex patterns extract and deduplicate:

| Type | Pattern | Example |
|------|---------|---------|
| UPI ID | `user@provider` | `scam@paytm` |
| Phone | `+91XXXXXXXXXX` or 10-digit | `+91-9876543210` |
| URL | `http://` or `www.` | `http://fake-bank.com` |
| Bank account | 10–18 digit number | `1234567890123` |
| Email | Full TLD validation | `scam@fake.com` |

Extraction runs on **every turn** (both current message and full
conversation history) and is idempotent.

### Layer 5 — Callback Engine (`src/main.py`)

After `MIN_MESSAGES` (5) turns, a callback is sent to the GUVI endpoint
on **every subsequent turn**, updating with the latest intelligence.

Payload includes: `sessionId`, `scamDetected`, `totalMessagesExchanged`,
`extractedIntelligence`, `redFlagsIdentified`, `engagementMetrics`,
`agentNotes`.

---

## Request / Response Flow

```
POST /api/honeypot
  ├── Parse & validate (Pydantic, always returns 200)
  ├── Get/create session
  ├── Scan conversationHistory for intel + red flags
  ├── detect_scam(message)
  ├── extract_intelligence(message)
  ├── identify_red_flags(message)
  ├── get_llm_response() or get_suspicion_reply() or fallback
  ├── transition_state() — deterministic
  ├── send_callback() if turn ≥ MIN_MESSAGES
  └── Return HoneypotResponse
```

---

## Error Handling

- **Validation errors** (bad JSON, missing fields) → HTTP 200 with safe default reply
- **HTTP errors** (405, 404, etc.) → HTTP 200 with safe default reply
- **Unhandled exceptions** → HTTP 200 with safe default reply
- **LLM failures** → Fallback to scripted NAIVE_RESPONSES that still probe for intel
- **Callback failures** → Logged, never crashes the response path

---

## File Structure

```
scamhoneypot/
├── api.py                    # Entry point (thin wrapper → src/main.py)
├── render.yaml               # Render deployment configuration
├── src/
│   ├── __init__.py           # Package metadata
│   ├── main.py               # FastAPI app, endpoints, error handlers
│   ├── honeypot_agent.py     # Persona engine, state machine, LLM integration
│   ├── scam_detection.py     # Multi-layer scam detection + red-flag ID
│   ├── intelligence.py       # Regex-based intelligence extraction
│   ├── models.py             # Pydantic request/response models
│   ├── config.py             # Constants, logging, compiled patterns
│   └── personas.py           # 4 AI persona definitions + auto-selection
├── test.py                   # Automated 10-turn integration test
├── requirements.txt          # Streamlit UI dependencies
├── requirements-api.txt      # API server dependencies (production)
├── .env.example              # Environment variable template
├── .gitignore                # Standard Python gitignore
├── README.md                 # Setup & usage documentation
└── docs/
    └── architecture.md       # This file
```

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Web framework | FastAPI 0.110 |
| ASGI server | Uvicorn 0.27 |
| LLM provider | Groq (llama-3.3-70b-versatile) |
| HTTP client | httpx 0.27 |
| Validation | Pydantic v2 |
| Deployment | Render (auto-deploy from GitHub) |
| Python | 3.12+ |
