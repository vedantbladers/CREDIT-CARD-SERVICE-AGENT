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
    # Phase 3 Deterministic Policy Engine Fields
    policy_decision: Optional[str] = Field(
        default=None,
        description="Policy Engine verdict: APPROVED, REJECTED, NEEDS_ESCALATION, or None if clarification is needed",
    )
    policy_rule: Optional[str] = Field(
        default=None,
        description="Specific policy rule identifier applied by the deterministic engine",
    )
    policy_reason: Optional[str] = Field(
        default=None,
        description="Human and audit readable justification for policy determination",
    )
    policy_details: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Evaluation metrics, thresholds, and account risk indicators",
    )
    # Phase 4 MCP Execution Result Field
    execution_result: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Result of transactional execution against PostgreSQL via MCP server",
    )
    message: str = Field(..., description="Response message for the cardholder")
    status: str = Field(..., description="Status string: success, needs_clarification, policy_approved, policy_rejected, policy_escalated, executed")
    account_id: Optional[str] = None
    timestamp: str


class AccountInfo(BaseModel):
    account_number: str
    name: str
    balance: float
    credit_limit: float
    fees_waived_this_quarter: int
    tenure_months: int
    is_active: bool
    status: str


class AccountListResponse(BaseModel):
    accounts: list[AccountInfo]
    count: int

