from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class PolicyDecision(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NEEDS_ESCALATION = "NEEDS_ESCALATION"


class AccountProfile(BaseModel):
    account_number: str = Field(..., description="Unique cardholder account identifier")
    name: str = Field(..., description="Cardholder legal name")
    balance: float = Field(default=0.0, description="Current account ledger balance")
    credit_limit: float = Field(default=5000.0, description="Current revolving credit limit")
    fees_waived_this_quarter: int = Field(default=0, description="Number of fees waived in current calendar quarter")
    tenure_months: int = Field(default=12, description="Number of consecutive active months on the account")
    is_active: bool = Field(default=True, description="Account active status flag")
    status: str = Field(default="active", description="Account standing: active, suspended, fraud_alert, closed")


class PolicyResult(BaseModel):
    decision: PolicyDecision = Field(..., description="Deterministic policy evaluation verdict")
    rule_name: str = Field(..., description="Identifier of the specific policy rule applied")
    reason: str = Field(..., description="Human-readable justification for the decision")
    details: Dict[str, Any] = Field(default_factory=dict, description="Numerical & context metrics used in decision")
    evaluated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="UTC timestamp of the policy determination",
    )
