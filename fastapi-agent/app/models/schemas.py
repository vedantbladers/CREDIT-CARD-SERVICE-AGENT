from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class IntentType(str, Enum):
    FEE_WAIVER = "fee_waiver"
    CREDIT_LIMIT_INCREASE = "credit_limit_increase"
    CARD_REPLACEMENT = "card_replacement"
    UNCLEAR = "unclear"


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Cardholder query or request")
    account_id: Optional[str] = Field(
        default="ACC-1001",
        description="Authenticated account identifier",
    )


class ChatResponse(BaseModel):
    intent: str = Field(..., description="Detected intent")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="AI confidence score")
    slots: Dict[str, Any] = Field(default_factory=dict, description="Extracted entity slots")
    needs_clarification: bool = Field(default=False, description="Flag if clarification is required")
    clarification_prompt: Optional[str] = Field(
        default=None, description="Prompt to ask user if clarification is needed"
    )
    message: str = Field(..., description="Response message for the cardholder")
    status: str = Field(..., description="Status string: success, needs_clarification, unhandled")
    account_id: Optional[str] = None
    timestamp: str
