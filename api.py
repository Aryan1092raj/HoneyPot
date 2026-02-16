"""
ScamBait AI - Honeypot API Entry Point.

This file is the **deployment entry point** consumed by Render / Uvicorn:
    uvicorn api:app --host 0.0.0.0 --port 8000

All application logic lives in the ``src/`` package:
    src/main.py           - FastAPI app & endpoints
    src/honeypot_agent.py - Persona engine, state machine, LLM
    src/scam_detection.py - Multi-layer scam detection + red-flag identification
    src/intelligence.py   - Regex-based intelligence extraction
    src/models.py         - Pydantic request / response models
    src/config.py         - Configuration constants & logging
    src/personas.py       - 4 AI persona definitions
"""

# Re-export the FastAPI application so that
#   uvicorn api:app
# continues to work without changing the Render start command.
from src.main import app  # noqa: F401

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
