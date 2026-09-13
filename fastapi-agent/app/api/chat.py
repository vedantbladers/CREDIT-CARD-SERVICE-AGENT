from datetime import datetime, timezone
from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse
from app.policy.engine import evaluate_policy
from app.policy.models import PolicyDecision
from app.services.graph_orchestrator import execute_agent_graph
from app.services.mcp_client import call_mcp_tool

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
def handle_chat(request: ChatRequest) -> ChatResponse:
    """
    Handle cardholder chat queries:
    1. LangGraph State Graph: classify_intent -> extract_slots -> route_decision
    2. Deterministic Policy Engine: evaluates business rules (LLM-free safety layer)
    3. MCP Server Tool Execution: ONLY called if policy decision is APPROVED.
       Executes real ACID transactions against PostgreSQL.
    """
    account_id = request.account_id or "ACC-1001"

    # Step 1: LangGraph Intent & Slot Extraction
    result = execute_agent_graph(
        message=request.message,
        account_id=account_id,
    )

    needs_clarification = result.get("needs_clarification", False)
    intent = result.get("intent", "unclear")
    slots = result.get("slots", {})
    policy_decision = None
    policy_rule = None
    policy_reason = None
    policy_details = {}
    execution_result = None
    response_message = result.get("response_message", "")
    status = result.get("status", "success")

    # Step 2: Policy Engine Evaluation (only if request has sufficient parameters)
    if not needs_clarification and intent != "unclear":
        policy_res = evaluate_policy(
            intent=intent,
            slots=slots,
            account_id=account_id,
        )
        policy_decision = policy_res.decision.value
        policy_rule = policy_res.rule_name
        policy_reason = policy_res.reason
        policy_details = policy_res.details

        # Step 3: MCP Tool Execution (Defense-in-depth: ONLY on APPROVED)
        if policy_res.decision == PolicyDecision.APPROVED:
            status = "executed"
            response_message = (
                f"{response_message}\n\n"
                f"✅ [Policy Approved - {policy_res.rule_name}]: {policy_res.reason}"
            )

            if intent == "fee_waiver":
                execution_result = call_mcp_tool(
                    "waive_fee",
                    {
                        "account_id": account_id,
                        "amount": slots.get("amount", 95.0),
                        "fee_type": slots.get("fee_type", "annual_fee"),
                    },
                )
                if execution_result.get("status") == "SUCCESS":
                    db_state = execution_result.get("database_state", {})
                    bal_after = db_state.get("balance", {}).get("after", 0.0)
                    waivers_after = db_state.get("fees_waived_this_quarter", {}).get("after", 1)
                    tx_id = execution_result.get("transaction_id", "N/A")
                    response_message += (
                        f"\n\n⚡ [MCP Execution - ACID Committed]: Fee waiver successfully applied to core database. "
                        f"New Balance: ${bal_after:,.2f}, Quarterly Waivers: {waivers_after} (Tx ID: #{tx_id})."
                    )

            elif intent == "credit_limit_increase":
                execution_result = call_mcp_tool(
                    "adjust_credit_limit",
                    {
                        "account_id": account_id,
                        "new_limit": slots.get("requested_limit"),
                    },
                )
                if execution_result.get("status") == "SUCCESS":
                    new_lim = execution_result.get("database_state", {}).get("credit_limit", {}).get("after", 0.0)
                    tx_id = execution_result.get("transaction_id", "N/A")
                    response_message += (
                        f"\n\n⚡ [MCP Execution - ACID Committed]: Credit limit adjusted to ${new_lim:,.2f} "
                        f"in core banking ledger (Tx ID: #{tx_id})."
                    )

            elif intent == "card_replacement":
                execution_result = call_mcp_tool(
                    "replace_card",
                    {
                        "account_id": account_id,
                        "reason": slots.get("reason", "stolen"),
                        "delivery_type": slots.get("delivery_type", "standard"),
                    },
                )
                if execution_result.get("status") == "SUCCESS":
                    rep_id = execution_result.get("replacement_id", "N/A")
                    deliv = execution_result.get("delivery_type", "standard")
                    est_days = execution_result.get("estimated_delivery_days", 5)
                    response_message += (
                        f"\n\n⚡ [MCP Execution - ACID Committed]: Replacement card dispatched via {deliv} shipping "
                        f"(Dispatch Order #{rep_id}, Estimated: {est_days} business days)."
                    )

        elif policy_res.decision == PolicyDecision.REJECTED:
            status = "policy_rejected"
            response_message = (
                f"❌ [Policy Rejection - {policy_res.rule_name}]: {policy_res.reason}"
            )
            execution_result = {
                "status": "BLOCKED_BY_POLICY",
                "reason": policy_res.reason,
                "tool_called": None,
            }

        elif policy_res.decision == PolicyDecision.NEEDS_ESCALATION:
            status = "policy_escalated"
            response_message = (
                f"⚠️ [Escalation Required - {policy_res.rule_name}]: {policy_res.reason}"
            )
            execution_result = {
                "status": "ESCALATED_MANUAL_REVIEW",
                "reason": policy_res.reason,
                "tool_called": None,
            }

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
        execution_result=execution_result,
        message=response_message,
        status=status,
        account_id=account_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

