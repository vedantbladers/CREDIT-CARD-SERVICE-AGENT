from typing import Any, Dict
from app.policy.models import AccountProfile, PolicyDecision, PolicyResult


def evaluate_fee_waiver(account: AccountProfile, slots: Dict[str, Any]) -> PolicyResult:
    """
    Deterministic rule evaluation for fee waiver requests.
    Rules:
    - Account must be active.
    - Max 1 waiver per calendar quarter.
    - Requests > $150.00 require manager escalation.
    - Otherwise APPROVED.
    """
    rule_name = "POL-FW-001:QuarterlyFeeWaiverLimit"

    if not account.is_active or account.status != "active":
        return PolicyResult(
            decision=PolicyDecision.REJECTED,
            rule_name=rule_name,
            reason=f"Account {account.account_number} is not in active standing (status: {account.status}). Fee waiver cannot be granted.",
            details={"is_active": account.is_active, "status": account.status},
        )

    if account.fees_waived_this_quarter >= 1:
        return PolicyResult(
            decision=PolicyDecision.REJECTED,
            rule_name=rule_name,
            reason=(
                f"Account {account.account_number} has already received {account.fees_waived_this_quarter} fee waiver(s) "
                "this quarter. Maximum permissible is 1 per calendar quarter."
            ),
            details={
                "fees_waived_this_quarter": account.fees_waived_this_quarter,
                "max_allowed_per_quarter": 1,
            },
        )

    requested_amount = slots.get("amount")
    if requested_amount is not None:
        try:
            amount_val = float(requested_amount)
            if amount_val > 150.0:
                return PolicyResult(
                    decision=PolicyDecision.NEEDS_ESCALATION,
                    rule_name="POL-FW-002:HighValueFeeEscalation",
                    reason=(
                        f"Requested fee waiver amount (${amount_val:,.2f}) exceeds the $150.00 automated approval threshold. "
                        "Escalating to Customer Relations Supervisor for review."
                    ),
                    details={"requested_amount": amount_val, "escalation_threshold": 150.0},
                )
        except (ValueError, TypeError):
            pass

    fee_type = slots.get("fee_type", "unspecified fee")
    return PolicyResult(
        decision=PolicyDecision.APPROVED,
        rule_name=rule_name,
        reason=(
            f"Fee waiver approved for {fee_type.replace('_', ' ')}. "
            f"Account has 0 waivers this quarter and is in active standing."
        ),
        details={
            "fees_waived_this_quarter": account.fees_waived_this_quarter,
            "requested_amount": requested_amount,
            "fee_type": fee_type,
        },
    )


def evaluate_credit_limit_increase(account: AccountProfile, slots: Dict[str, Any]) -> PolicyResult:
    """
    Deterministic rule evaluation for credit limit increase requests.
    Rules:
    - Account must be active.
    - Account tenure must be >= 6 months.
    - Max automated increase is 20% of current credit limit.
    - Increases between 20% and 50% require manual underwriter escalation.
    - Increases > 50% or below current limit are REJECTED.
    """
    rule_name = "POL-CLI-001:CreditLimitRatioAndTenure"

    if not account.is_active or account.status != "active":
        return PolicyResult(
            decision=PolicyDecision.REJECTED,
            rule_name=rule_name,
            reason=f"Account {account.account_number} is not in active standing (status: {account.status}). Credit limit increase denied.",
            details={"is_active": account.is_active, "status": account.status},
        )

    if account.tenure_months < 6:
        return PolicyResult(
            decision=PolicyDecision.REJECTED,
            rule_name="POL-CLI-002:MinimumAccountTenure",
            reason=(
                f"Account tenure is {account.tenure_months} month(s). Credit policy requires a minimum of 6 active months "
                "before credit limit increases may be considered."
            ),
            details={"tenure_months": account.tenure_months, "required_tenure_months": 6},
        )

    requested_limit_raw = slots.get("requested_limit")
    if requested_limit_raw is None:
        return PolicyResult(
            decision=PolicyDecision.REJECTED,
            rule_name=rule_name,
            reason="Requested credit limit amount was not provided or is invalid.",
            details={"requested_limit": None},
        )

    try:
        requested_limit = float(requested_limit_raw)
    except (ValueError, TypeError):
        return PolicyResult(
            decision=PolicyDecision.REJECTED,
            rule_name=rule_name,
            reason=f"Invalid credit limit value provided: {requested_limit_raw}",
            details={"requested_limit": requested_limit_raw},
        )

    current_limit = account.credit_limit
    if requested_limit <= current_limit:
        return PolicyResult(
            decision=PolicyDecision.REJECTED,
            rule_name=rule_name,
            reason=(
                f"Requested limit (${requested_limit:,.2f}) must be strictly higher than current limit "
                f"(${current_limit:,.2f})."
            ),
            details={"current_limit": current_limit, "requested_limit": requested_limit},
        )

    increase_amount = requested_limit - current_limit
    increase_pct = (increase_amount / current_limit) * 100.0

    if increase_pct <= 20.0:
        return PolicyResult(
            decision=PolicyDecision.APPROVED,
            rule_name=rule_name,
            reason=(
                f"Credit limit increase of {increase_pct:.1f}% (+${increase_amount:,.2f}) approved. "
                f"Within the 20% automated limit and meets 6-month account tenure criteria."
            ),
            details={
                "current_limit": current_limit,
                "requested_limit": requested_limit,
                "increase_amount": increase_amount,
                "increase_percentage": round(increase_pct, 2),
                "tenure_months": account.tenure_months,
            },
        )
    elif 20.0 < increase_pct <= 50.0:
        return PolicyResult(
            decision=PolicyDecision.NEEDS_ESCALATION,
            rule_name="POL-CLI-003:ManualUnderwritingEscalation",
            reason=(
                f"Requested increase of {increase_pct:.1f}% (+${increase_amount:,.2f}) exceeds the 20% automated limit "
                "but is within the 50% manual underwriting band. Escalating to Senior Credit Underwriter."
            ),
            details={
                "current_limit": current_limit,
                "requested_limit": requested_limit,
                "increase_amount": increase_amount,
                "increase_percentage": round(increase_pct, 2),
            },
        )
    else:
        return PolicyResult(
            decision=PolicyDecision.REJECTED,
            rule_name="POL-CLI-004:ExcessiveCreditIncreaseCap",
            reason=(
                f"Requested increase of {increase_pct:.1f}% (+${increase_amount:,.2f}) exceeds the maximum permissible "
                "cap of 50.0% in a single request. Denied under automated risk policy."
            ),
            details={
                "current_limit": current_limit,
                "requested_limit": requested_limit,
                "increase_amount": increase_amount,
                "increase_percentage": round(increase_pct, 2),
                "max_allowed_percentage": 50.0,
            },
        )


def evaluate_card_replacement(account: AccountProfile, slots: Dict[str, Any]) -> PolicyResult:
    """
    Deterministic rule evaluation for card replacement requests.
    Rules:
    - Account must be active.
    - If status has fraud_alert, escalate immediately to Fraud Operations.
    - Otherwise always APPROVED for active accounts.
    """
    rule_name = "POL-CR-001:ActiveCardReplacement"

    if not account.is_active or account.status == "suspended":
        return PolicyResult(
            decision=PolicyDecision.REJECTED,
            rule_name=rule_name,
            reason=f"Account {account.account_number} is {account.status}. Card replacement cannot be initiated.",
            details={"is_active": account.is_active, "status": account.status},
        )

    if account.status == "fraud_alert":
        return PolicyResult(
            decision=PolicyDecision.NEEDS_ESCALATION,
            rule_name="POL-CR-002:FraudAlertHold",
            reason=(
                f"Account {account.account_number} is flagged with an active fraud alert. "
                "Card replacement request routed to Fraud Operations Team for identity verification."
            ),
            details={"status": account.status},
        )

    reason = slots.get("reason", "standard replacement")
    delivery_type = slots.get("delivery_type", "standard")

    return PolicyResult(
        decision=PolicyDecision.APPROVED,
        rule_name=rule_name,
        reason=(
            f"Card replacement authorized for reason '{reason}'. "
            f"Dispatch method set to '{delivery_type}' delivery."
        ),
        details={
            "account_status": account.status,
            "reason": reason,
            "delivery_type": delivery_type,
        },
    )


def evaluate_dispute_charge(account: AccountProfile, slots: Dict[str, Any]) -> PolicyResult:
    """
    Deterministic rule for transaction disputes (Statutory Card Guardrail):
    - If account is suspended or delinquent -> REJECTED (POL-DSP-003)
    - If amount <= 500.00 -> APPROVED (POL-DSP-001: Automated provisional credit under $500 cap)
    - If amount > 500.00 -> NEEDS_ESCALATION (POL-DSP-002: High-value dispute escalated to fraud desk)
    """
    if not account.is_active or account.status == "suspended":
        return PolicyResult(
            decision=PolicyDecision.REJECTED,
            rule_name="POL-DSP-003:AccountStandingViolation",
            reason=f"Account {account.account_number} is currently {account.status}. Disputes must be submitted via verified phone agent.",
            details={"is_active": account.is_active, "status": account.status},
        )

    amt = slots.get("amount") or 0.0
    merchant = slots.get("merchant", "Unspecified Merchant")

    if amt <= 500.00 and amt > 0:
        return PolicyResult(
            decision=PolicyDecision.APPROVED,
            rule_name="POL-DSP-001:AutomatedProvisionalCredit",
            reason=(
                f"Dispute of ${amt:,.2f} from '{merchant}' qualifies for instant automated provisional credit "
                f"under statutory $500.00 threshold."
            ),
            details={
                "merchant": merchant,
                "dispute_amount": amt,
                "provisional_credit": amt,
                "instant_threshold": 500.00,
            },
        )
    else:
        return PolicyResult(
            decision=PolicyDecision.NEEDS_ESCALATION,
            rule_name="POL-DSP-002:HighValueDisputeInvestigation",
            reason=(
                f"Dispute of ${amt:,.2f} from '{merchant}' exceeds the $500.00 instant credit threshold. "
                "Temporary hold placed on merchant descriptor and escalated to Senior Fraud Analyst via Visa Resolve Online."
            ),
            details={
                "merchant": merchant,
                "dispute_amount": amt,
                "escalation_queue": "Senior Fraud Desk",
                "threshold": 500.00,
            },
        )

