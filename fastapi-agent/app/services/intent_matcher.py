from datetime import datetime, timezone
from app.models.schemas import ChatRequest, ChatResponse


class KeywordIntentService:
    """
    Phase 1 Heuristic Intent Classifier.
    Detects fee waiver intent via keywords until replaced with LangGraph in Phase 2.
    """

    @staticmethod
    def process_message(request: ChatRequest) -> ChatResponse:
        text = request.message.lower().strip()
        current_time = datetime.now(timezone.utc).isoformat()

        # Check for fee waiver keywords
        is_fee_waiver = "fee" in text and ("waive" in text or "waiver" in text or "refund" in text)

        if is_fee_waiver:
            return ChatResponse(
                intent="fee_waiver",
                message=(
                    "I detected a fee waiver request for your account. "
                    "[Phase 1 Mock Response]: Your request has been acknowledged by the orchestrator. "
                    "Real LLM reasoning and policy verification will be added in Phases 2 and 3."
                ),
                status="success",
                account_id=request.account_id,
                timestamp=current_time,
            )

        return ChatResponse(
            intent="unknown",
            message=(
                "I could not identify your request. In Phase 1, only 'fee waiver' requests "
                "(e.g., 'Please waive my late fee') are supported by keyword matching."
            ),
            status="unhandled",
            account_id=request.account_id,
            timestamp=current_time,
        )
