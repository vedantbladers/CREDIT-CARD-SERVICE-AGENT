import json
import logging
import re
from typing import Any, Dict, Optional, TypedDict
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

from app.models.schemas import ChatResponse
from app.services.llm_factory import (
    get_configured_llm,
    run_deterministic_classification,
    run_deterministic_slot_extraction,
)

logger = logging.getLogger("orchestrator.graph")


# 1. State Definition
class AgentState(TypedDict):
    message: str
    account_id: str
    intent: str
    confidence_score: float
    slots: Dict[str, Any]
    needs_clarification: bool
    clarification_prompt: Optional[str]
    response_message: str
    status: str


# 2. Node 1: Classify Intent
def classify_intent_node(state: AgentState) -> Dict[str, Any]:
    message = state["message"]
    llm = get_configured_llm()

    if llm is not None:
        try:
            system_prompt = (
                "You are an AI intent classifier for a credit card servicing platform. "
                "Classify the user message into exactly ONE of the following intents:\n"
                "- fee_waiver: Requesting waiver, refund, or reversal of credit card fees.\n"
                "- credit_limit_increase: Requesting a higher credit line or limit.\n"
                "- card_replacement: Requesting a replacement for a lost, damaged, stolen, or expired card.\n"
                "- unclear: Anything outside the three supported services or ambiguous.\n\n"
                "Respond ONLY with a JSON object in this exact format:\n"
                '{"intent": "<one of the 4 above>", "confidence_score": <float between 0.0 and 1.0>}'
            )
            response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=message)])
            clean_content = response.content.strip().replace("```json", "").replace("```", "").strip()
            parsed = json.loads(clean_content)
            return {
                "intent": parsed.get("intent", "unclear"),
                "confidence_score": float(parsed.get("confidence_score", 0.5)),
            }
        except Exception as e:
            logger.warning(f"LLM intent classification failed: {e}. Falling back to deterministic classifier.")

    intent, confidence = run_deterministic_classification(message)
    return {"intent": intent, "confidence_score": confidence}


# 3. Node 2: Extract Slots
def extract_slots_node(state: AgentState) -> Dict[str, Any]:
    intent = state.get("intent", "unclear")
    message = state["message"]

    if intent == "unclear":
        return {"slots": {}}

    llm = get_configured_llm()
    if llm is not None:
        try:
            system_prompt = (
                f"You are a parameter slot extractor for the credit card intent '{intent}'. "
                "Extract parameters from the user's message into JSON.\n"
                "Rules per intent:\n"
                "- fee_waiver: extract 'fee_type' (str: annual_fee, late_fee, foreign_transaction_fee, or unspecified_fee), "
                "'amount' (float or null), 'reason' (str or null).\n"
                "- credit_limit_increase: extract 'requested_limit' (float or null), 'reason' (str or null).\n"
                "- card_replacement: extract 'reason' (damaged, lost, stolen, expired, or null), "
                "'delivery_type' (standard or expedited).\n\n"
                "Respond ONLY with a JSON object of the extracted slots."
            )
            response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=message)])
            clean_content = response.content.strip().replace("```json", "").replace("```", "").strip()
            slots = json.loads(clean_content)
            # Post-process amount with regex if dollar sign appears in text
            if "amount" in slots or intent == "fee_waiver":
                dollar_m = re.search(r"\$\s*([\d,]+(?:\.\d{2})?)", message)
                if dollar_m:
                    slots["amount"] = float(dollar_m.group(1).replace(",", ""))
            if intent == "credit_limit_increase":
                dollar_m = re.search(r"\$\s*([\d,]+(?:\.\d{2})?)", message)
                if dollar_m:
                    slots["requested_limit"] = float(dollar_m.group(1).replace(",", ""))
            return {"slots": slots}
        except Exception as e:
            logger.warning(f"LLM slot extraction failed: {e}. Falling back to deterministic extractor.")

    slots = run_deterministic_slot_extraction(intent, message)
    return {"slots": slots}


# 4. Node 3: Route Decision
def route_decision_node(state: AgentState) -> Dict[str, Any]:
    intent = state.get("intent", "unclear")
    confidence = state.get("confidence_score", 0.0)
    slots = state.get("slots", {})

    # Check for unclear or low confidence
    if intent == "unclear" or confidence < 0.70:
        return {
            "needs_clarification": True,
            "clarification_prompt": (
                "I specialize in credit card servicing. I can help you with: "
                "1) Fee waivers, 2) Credit limit increases, or 3) Card replacements. "
                "Which of these can I assist you with today?"
            ),
            "response_message": (
                "I could not clearly determine your credit card request. "
                "I can assist with fee waivers, credit limit increases, or card replacements. "
                "Could you please clarify your request?"
            ),
            "status": "needs_clarification",
        }

    # Check for required slots per intent
    if intent == "credit_limit_increase":
        if slots.get("requested_limit") is None:
            return {
                "needs_clarification": True,
                "clarification_prompt": "Could you please specify the new credit limit amount you are requesting (e.g., $5,000)?",
                "response_message": (
                    "I understand you are requesting a credit limit increase. "
                    "How much would you like your credit limit increased to?"
                ),
                "status": "needs_clarification",
            }
        return {
            "needs_clarification": False,
            "clarification_prompt": None,
            "response_message": (
                f"Credit limit increase request identified: New limit of ${slots['requested_limit']:,.2f}. "
                "Intent and parameters extracted successfully. Ready for Policy Engine verification in Phase 3."
            ),
            "status": "success",
        }

    if intent == "card_replacement":
        if slots.get("reason") is None:
            return {
                "needs_clarification": True,
                "clarification_prompt": "Could you please specify why you need a replacement (e.g., damaged, lost, or stolen)?",
                "response_message": (
                    "I can help issue a replacement card. "
                    "Could you specify why you need a replacement (e.g., damaged, lost, or stolen) so we can secure your account appropriately?"
                ),
                "status": "needs_clarification",
            }
        return {
            "needs_clarification": False,
            "clarification_prompt": None,
            "response_message": (
                f"Card replacement request identified for reason: '{slots['reason']}' (Delivery: {slots.get('delivery_type', 'standard')}). "
                "Parameters extracted successfully. Ready for Policy Engine verification in Phase 3."
            ),
            "status": "success",
        }

    if intent == "fee_waiver":
        fee_type_str = slots.get("fee_type", "unspecified fee").replace("_", " ")
        amount_str = f" of ${slots['amount']:,.2f}" if slots.get("amount") else ""
        return {
            "needs_clarification": False,
            "clarification_prompt": None,
            "response_message": (
                f"Fee waiver request identified for {fee_type_str}{amount_str}. "
                "Parameters extracted successfully. Ready for Policy Engine verification in Phase 3."
            ),
            "status": "success",
        }

    if intent == "dispute_charge":
        amount_str = f" of ${slots['amount']:,.2f}" if slots.get("amount") else ""
        merchant_str = f" from {slots['merchant']}" if slots.get("merchant") else ""
        return {
            "needs_clarification": False,
            "clarification_prompt": None,
            "response_message": (
                f"Transaction dispute initiated for charge{amount_str}{merchant_str}. "
                "Request routed to statutory cardholder dispute engine under zero-liability rules."
            ),
            "status": "success",
        }

    # Fallback
    return {
        "needs_clarification": True,
        "clarification_prompt": "Could you please clarify your credit card request?",
        "response_message": "Could you please clarify your request?",
        "status": "needs_clarification",
    }


# 5. Build and Compile LangGraph State Graph
def build_orchestrator_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("extract_slots", extract_slots_node)
    workflow.add_node("route_decision", route_decision_node)

    workflow.set_entry_point("classify_intent")
    workflow.add_edge("classify_intent", "extract_slots")
    workflow.add_edge("extract_slots", "route_decision")
    workflow.add_edge("route_decision", END)

    return workflow.compile()


orchestrator_app = build_orchestrator_graph()


def execute_agent_graph(message: str, account_id: str = "ACC-1001") -> Dict[str, Any]:
    """
    Executes the compiled LangGraph state graph.
    Returns structured dict containing intent, confidence, slots, and message.
    """
    initial_state: AgentState = {
        "message": message,
        "account_id": account_id,
        "intent": "",
        "confidence_score": 0.0,
        "slots": {},
        "needs_clarification": False,
        "clarification_prompt": None,
        "response_message": "",
        "status": "pending",
    }

    final_state = orchestrator_app.invoke(initial_state)
    return final_state
