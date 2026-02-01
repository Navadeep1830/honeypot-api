"""
Pydantic models for the Agentic Honey-Pot System.
Defines request/response structures for the API.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ConversationMessage(BaseModel):
    """Individual message in conversation history."""
    role: str = Field(..., description="Role: 'scammer' or 'agent'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HoneypotRequest(BaseModel):
    """Incoming request from Mock Scammer API."""
    conversation_id: str = Field(..., description="Unique conversation identifier")
    message: str = Field(..., description="Scammer's message content")
    sender_id: Optional[str] = Field(None, description="Optional sender identifier")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ExtractedIntelligence(BaseModel):
    """Extracted scam intelligence from conversation."""
    bank_accounts: List[str] = Field(default_factory=list, description="Detected bank account numbers")
    ifsc_codes: List[str] = Field(default_factory=list, description="Detected IFSC codes")
    upi_ids: List[str] = Field(default_factory=list, description="Detected UPI IDs")
    phishing_urls: List[str] = Field(default_factory=list, description="Detected phishing URLs")
    phone_numbers: List[str] = Field(default_factory=list, description="Detected phone numbers")
    other_data: Dict[str, Any] = Field(default_factory=dict, description="Other extracted data")


class EngagementMetrics(BaseModel):
    """Metrics tracking engagement with scammer."""
    turn_count: int = Field(0, description="Number of conversation turns")
    engagement_duration_seconds: float = Field(0.0, description="Total engagement time")
    messages_exchanged: int = Field(0, description="Total messages in conversation")


class HoneypotResponse(BaseModel):
    """Response structure for the Honeypot API."""
    conversation_id: str = Field(..., description="Conversation identifier")
    response_message: str = Field(..., description="Agent's response to scammer")
    scam_detected: bool = Field(False, description="Whether scam intent was detected")
    confidence_score: float = Field(0.0, description="Confidence score for scam detection (0-1)")
    extracted_intelligence: ExtractedIntelligence = Field(
        default_factory=ExtractedIntelligence,
        description="Intelligence extracted from conversation"
    )
    engagement_metrics: EngagementMetrics = Field(
        default_factory=EngagementMetrics,
        description="Engagement metrics for the conversation"
    )
    agent_active: bool = Field(False, description="Whether AI agent has taken over")
    status: str = Field("success", description="Response status")


class ErrorResponse(BaseModel):
    """Error response structure."""
    status: str = Field("error")
    message: str = Field(..., description="Error description")
    error_code: Optional[str] = Field(None, description="Error code for debugging")
