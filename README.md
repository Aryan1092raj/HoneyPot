# 🎣 ScamBait AI - Autonomous Scam Honeypot

**Fighting India's ₹60 Crore Daily Fraud Crisis with AI**

ScamBait AI is an autonomous AI-powered honeypot that engages scammers in realistic conversations, wastes their time, and collects evidence for law enforcement.

## 🌟 Features

- **AI Personas** - Multiple victim personas (Elderly Teacher, Young Professional, Small Business Owner)
- **Voice Mode** - Real-time speech-to-text and text-to-speech using Groq
- **Evidence Collection** - Automatic extraction of UPI IDs, bank accounts, phone numbers, and phishing links
- **Demo Call Mode** - Interactive roleplay where you act as scammer, AI plays victim
- **Conversation Logging** - SQLite database for evidence storage

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Groq API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/scamhoneypot.git
cd scamhoneypot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### Running the App

```bash
streamlit run app.py
```

## 📁 Project Structure

```
scamhoneypot/
├── app.py              # Main Streamlit UI
├── agent.py            # HoneypotAgent - AI victim responses
├── tts_handler.py      # Text-to-Speech (Groq Orpheus)
├── stt_handler.py      # Speech-to-Text (Groq Whisper)
├── database.py         # SQLite conversation logging
├── extractor.py        # Regex extraction for evidence
├── personas.py         # AI persona definitions
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## 🎯 How It Works

1. **Chat Mode** - Paste scammer messages, AI responds as confused victim
2. **Demo Call Mode** - You roleplay as scammer, AI plays victim with voice

### AI Strategies
- **TRUST** - Build rapport with scammer
- **STALL** - Waste time with confusion
- **EXTRACT** - Manipulate scammer into revealing details
- **CONFUSE** - Ask repetitive questions

## 🔧 Configuration

Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
```

## 📊 Evidence Collection

The system automatically extracts:
- 📱 UPI IDs (name@upi, name@paytm)
- 🏦 Bank Account Numbers
- 📞 Phone Numbers
- 🔗 Phishing Links

## 🛡️ Tech Stack

- **Frontend**: Streamlit
- **LLM**: Groq (llama-3.3-70b-versatile)
- **TTS**: Groq Orpheus (canopylabs/orpheus-v1-english)
- **STT**: Groq Whisper (whisper-large-v3)
- **Database**: SQLite

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

---

**Built for India AI Impact Buildathon** 🇮🇳
