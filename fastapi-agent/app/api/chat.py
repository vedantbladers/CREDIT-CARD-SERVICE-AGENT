from datetime import datetime, timezone
from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse
from app.services.graph_orchestrator import execute_agent_graph

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
def handle_chat(request: ChatRequest) -> ChatResponse:
    """
    Handle cardholder chat queries using LangGraph State Graph.
    Nodes: classify_intent -> extract_slots -> route_decision.
    """
    result = execute_agent_graph(
        message=request.message,
        account_id=request.account_id or "ACC-1001",
    )

    return ChatResponse(
        intent=result["intent"],
        confidence_score=result["confidence_score"],
        slots=result.get("slots", {}),
        needs_clarification=result.get("needs_clarification", False),
        clarification_prompt=result.get("clarification_prompt"),
        message=result.get("response_message", ""),
        status=result.get("status", "success"),
        account_id=request.account_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
