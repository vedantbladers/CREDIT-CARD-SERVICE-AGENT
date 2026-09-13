from datetime import datetime, timezone
from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse
from app.policy.engine import evaluate_policy
from app.policy.models import PolicyDecision
from app.services.graph_orchestrator import execute_agent_graph

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
def handle_chat(request: ChatRequest) -> ChatResponse:
    """
    Handle cardholder chat queries:
    1. LangGraph State Graph: classify_intent -> extract_slots -> route_decision
    2. Deterministic Policy Engine: evaluates business rules (LLM-free safety layer)
       Returns APPROVED, REJECTED, or NEEDS_ESCALATION.
    """
    account_id = request.account_id or "ACC-1001"

    # Step 1: LangGraph Intent & Slot Extraction
    result = execute_agent_graph(
        message=request.message,
        account_id=account_id,
    )

    needs_clarification = result.get("needs_clarification", False)
    policy_decision = None
    policy_rule = None
    policy_reason = None
    policy_details = {}
    response_message = result.get("response_message", "")
    status = result.get("status", "success")

    # Step 2: Policy Engine Evaluation (only if request has sufficient parameters)
    if not needs_clarification and result.get("intent") != "unclear":
        policy_res = evaluate_policy(
            intent=result["intent"],
            slots=result.get("slots", {}),
            account_id=account_id,
        )
        policy_decision = policy_res.decision.value
        policy_rule = policy_res.rule_name
        policy_reason = policy_res.reason
        policy_details = policy_res.details

        if policy_res.decision == PolicyDecision.APPROVED:
            status = "policy_approved"
            response_message = (
                f"{response_message}\n\n"
                f"✅ [Policy Approved - {policy_res.rule_name}]: {policy_res.reason}"
            )
        elif policy_res.decision == PolicyDecision.REJECTED:
            status = "policy_rejected"
            response_message = (
                f"❌ [Policy Rejection - {policy_res.rule_name}]: {policy_res.reason}"
            )
        elif policy_res.decision == PolicyDecision.NEEDS_ESCALATION:
            status = "policy_escalated"
            response_message = (
                f"⚠️ [Escalation Required - {policy_res.rule_name}]: {policy_res.reason}"
            )

    return ChatResponse(
        intent=result["intent"],
        confidence_score=result["confidence_score"],
        slots=result.get("slots", {}),
        needs_clarification=needs_clarification,
        clarification_prompt=result.get("clarification_prompt"),
        policy_decision=policy_decision,
        policy_rule=policy_rule,
        policy_reason=policy_reason,
        policy_details=policy_details,
        message=response_message,
        status=status,
        account_id=account_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

