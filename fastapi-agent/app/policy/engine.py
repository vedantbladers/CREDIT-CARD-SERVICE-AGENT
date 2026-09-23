import logging
from typing import Any, Dict, Optional
from app.policy.models import AccountProfile, PolicyDecision, PolicyResult
from app.policy.repository import get_account_profile
from app.policy.rules import (
    evaluate_card_replacement,
    evaluate_credit_limit_increase,
    evaluate_fee_waiver,
    evaluate_dispute_charge,
)

logger = logging.getLogger("orchestrator.policy")


def evaluate_policy(
    intent: str,
    slots: Dict[str, Any],
    account_id: str = "ACC-1001",
    account_profile: Optional[AccountProfile] = None,
) -> PolicyResult:
    """
    Evaluate deterministic safety rules for the given intent and slots.
    Completely LLM-free rule evaluation serving as safety guardrails.
    Returns a typed PolicyResult with APPROVED, REJECTED, or NEEDS_ESCALATION.
    """
    # 1. Resolve Account Profile
    profile = account_profile or get_account_profile(account_id)
    if profile is None:
        logger.warning(f"Policy evaluation failed: Account {account_id} not found.")
        return PolicyResult(
            decision=PolicyDecision.REJECTED,
            rule_name="POL-GEN-001:UnknownAccount",
            reason=f"Account '{account_id}' was not found in the core banking records.",
            details={"account_id": account_id},
        )

    # 2. Dispatch to dedicated intent rule
    if intent == "fee_waiver":
        return evaluate_fee_waiver(profile, slots)

    elif intent == "credit_limit_increase":
        return evaluate_credit_limit_increase(profile, slots)

    elif intent == "card_replacement":
        return evaluate_card_replacement(profile, slots)

    elif intent == "dispute_charge":
        return evaluate_dispute_charge(profile, slots)

    else:
        return PolicyResult(
            decision=PolicyDecision.REJECTED,
            rule_name="POL-GEN-000:UnsupportedIntent",
            reason=f"No automated policy exists for intent '{intent}'.",
            details={"intent": intent},
        )
