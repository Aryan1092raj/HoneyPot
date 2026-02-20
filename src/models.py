"""
Pydantic request / response models for the Honeypot API.

Provides strict validation with graceful fallbacks:
- MessageField accepts string or object payloads
- Timestamp accepts both epoch integers and ISO strings
- All optional fields have sensible defaults
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Union


# ============================================================
# REQUEST MODELS
# ============================================================

class MessageField(BaseModel):
    """Message payload — either a string or structured object."""

    text: str = Field(..., description="The message content")
    sender: Optional[str] = Field(
        default="scammer", description="Message sender (scammer / user)"
    )
    timestamp: Optional[Union[float, int, str]] = Field(
        default=None,
        description="Epoch ms (int/float) or ISO-8601 timestamp (str)",
    )


class HoneypotRequest(BaseModel):
    """Incoming request to the honeypot endpoint."""

    sessionId: str = Field(
        ...,
        description="Unique session ID. Reuse for follow-up messages.",
    )
    message: Union[str, MessageField] = Field(
        ...,
        description="Scammer's message (plain string or MessageField object).",
    )
    conversationHistory: Optional[List[Dict]] = Field(
        default=[],
        description="Previous turns: [{sender, text}, ...]",
    )
    metadata: Optional[Dict] = Field(
        default={},
        description="Extra context: channel, language, locale",
    )


# ============================================================
# RESPONSE MODELS
# ============================================================

class HoneypotResponse(BaseModel):
    """Outgoing response from the honeypot endpoint."""

    status: str = Field(default="success", description="Always 'success'")
    sessionId: Optional[str] = Field(default=None, description="Session identifier")
    reply: str = Field(..., description="AI persona reply")
    persona: Optional[str] = Field(default=None, description="Active persona name")
    scamDetected: Optional[bool] = Field(default=None, description="Scam detected?")
    totalMessagesExchanged: Optional[int] = Field(default=None, description="Total turn count")
    callbackSent: Optional[str] = Field(default=None, description="Callback status")
    extractedIntelligence: Optional[Dict] = Field(
        default=None, description="Extracted evidence (phones, accounts, UPIs, links, emails)"
    )
    redFlagsIdentified: Optional[List[str]] = Field(
        default=None,
        description="List of identified red-flag categories in this conversation",
    )
    engagementMetrics: Optional[Dict] = Field(
        default=None, description="Engagement duration and message counts"
    )
    agentNotes: Optional[str] = Field(
        default=None, description="AI agent analysis summary"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "success",
                "reply": "Arey beta, account block ho jayega? Aap kaun se bank se bol rahe ho?",
                "persona": "Kamla Devi",
                "scamDetected": True,
                "messagesExchanged": 3,
                "callbackSent": None,
                "extractedIntelligence": {
                    "upiIds": ["claim@paytm"],
                    "phoneNumbers": ["9876543210"],
                    "phishingLinks": [],
                    "bankAccounts": [],
                    "emailAddresses": [],
                    "suspiciousKeywords": ["lottery", "urgent"],
                },
                "redFlagsIdentified": [
                    "Urgency / pressure tactics",
                    "Too-good-to-be-true offer",
                    "Request for money / financial transaction",
                ],
                "engagementMetrics": {
                    "totalMessagesExchanged": 3,
                    "engagementDurationSeconds": 45,
                },
                "agentNotes": "Scammer claiming lottery win. Red flags: urgency, upfront payment request. Extracted UPI ID.",
            }
        }
    }
