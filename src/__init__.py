"""
ScamBait AI - Autonomous Scam Honeypot
=======================================

An AI-powered scam honeypot that detects scam intent, engages scammers
with realistic personas, extracts intelligence (UPI IDs, phone numbers,
bank accounts, phishing links, emails), and sends evidence to a callback
endpoint — all autonomously.

Modules:
    config          - Configuration constants, logging setup
    models          - Pydantic request/response models
    scam_detection  - Multi-layer scam detection + red-flag identification
    intelligence    - Regex-based intelligence extraction
    honeypot_agent  - Persona engine, state machine, LLM integration
    main            - FastAPI application and endpoints
"""

__version__ = "1.0.0"
__author__ = "ScamBait AI Team"
