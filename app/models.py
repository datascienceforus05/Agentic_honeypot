"""
Pydantic models for request/response validation.
Strictly adheres to the EXACT format from Problem Statement 2.
"""

from typing import List, Optional, Union
from pydantic import BaseModel, Field


# ============================================================================
# INPUT MODELS - Exactly matches Problem Statement Section 6
# ============================================================================

class Message(BaseModel):
    """Incoming message structure - matches 6.3 specification."""
    sender: str = Field(..., description="'scammer' or 'user'")
    text: str = Field(..., description="Message content")
    timestamp: Union[str, int, float] = Field(..., description="ISO-8601 format timestamp or millisecond integer")


class ConversationMessage(BaseModel):
    """
    Single message in conversation history.
    Matches Problem Statement 6.2 format exactly.
    """
    sender: str = Field(..., description="'scammer' or 'user'")
    text: str = Field(..., description="Message content")
    timestamp: Optional[Union[str, int, float]] = Field(None, description="ISO-8601 format timestamp or millisecond integer")


class Metadata(BaseModel):
    """Request metadata - matches 6.3 specification."""
    channel: str = Field(default="SMS", description="SMS / WhatsApp / Email / Chat")
    language: str = Field(default="English", description="Language used")
    locale: str = Field(default="IN", description="Country or region")


class HoneypotRequest(BaseModel):
    """
    Main request model - EXACTLY matches Problem Statement Section 6.
    Includes sessionId, message, conversationHistory, and metadata.
    """
    sessionId: Optional[str] = Field(None, description="Unique session ID for the conversation")
    message: Message = Field(..., description="The latest incoming message in the conversation")
    conversationHistory: List[ConversationMessage] = Field(
        default_factory=list, 
        description="All previous messages in the same conversation. Empty array for first message."
    )
    metadata: Optional[Metadata] = Field(
        default_factory=Metadata,
        description="Channel and language metadata (optional but recommended)"
    )


# ============================================================================
# OUTPUT MODELS - Exactly matches Problem Statement Section 8
# ============================================================================

class EngagementMetrics(BaseModel):
    """Metrics tracking engagement with the scammer."""
    engagementDurationSeconds: int = Field(
        default=0, 
        description="Total engagement duration in seconds"
    )
    totalMessagesExchanged: int = Field(
        default=0, 
        description="Total number of messages exchanged"
    )


class ExtractedIntelligence(BaseModel):
    """Intelligence extracted from the scam conversation."""
    bankAccounts: List[str] = Field(
        default_factory=list, 
        description="Extracted bank account numbers (e.g., XXXX-XXXX-XXXX)"
    )
    upiIds: List[str] = Field(
        default_factory=list, 
        description="Extracted UPI IDs (e.g., scammer@upi)"
    )
    phishingLinks: List[str] = Field(
        default_factory=list, 
        description="Extracted phishing/malicious URLs"
    )


class HoneypotResponse(BaseModel):
    """
    Main response model - EXACTLY matches Problem Statement Section 8.
    
    Example from problem:
    {
      "status": "success",
      "scamDetected": true,
      "engagementMetrics": {...},
      "extractedIntelligence": {...},
      "agentNotes": "..."
    }
    """
    status: str = Field(default="success", description="Response status")
    scamDetected: bool = Field(..., description="Whether scam intent was detected")
    engagementMetrics: EngagementMetrics = Field(
        default_factory=EngagementMetrics,
        description="Engagement tracking metrics"
    )
    extractedIntelligence: ExtractedIntelligence = Field(
        default_factory=ExtractedIntelligence,
        description="Extracted scam intelligence"
    )
    agentNotes: str = Field(
        default="", 
        description="Agent notes about tactics observed (e.g., 'Scammer used urgency tactics')"
    )


# ============================================================================
# INTERNAL MODELS (Not exposed in API)
# ============================================================================

class ScamAnalysis(BaseModel):
    """Internal model for scam analysis results."""
    is_scam: bool
    confidence: float
    scam_type: Optional[str] = None
    reasoning: str
    risk_level: str = "low"  # low, medium, high, critical


class AgentContext(BaseModel):
    """Context for the autonomous agent persona."""
    persona_name: str = "Ramesh Kumar"
    persona_age: int = 58
    persona_occupation: str = "Retired government employee"
    persona_traits: List[str] = Field(default_factory=lambda: [
        "trusting", "slightly confused with technology", 
        "polite", "eager to help", "gullible"
    ])
    engagement_goal: str = "Extract maximum intelligence while appearing naive"
