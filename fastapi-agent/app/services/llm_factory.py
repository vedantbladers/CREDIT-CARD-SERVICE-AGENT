import json
import logging
import re
from typing import Any, Dict, Optional, Tuple
from app.core.config import settings

logger = logging.getLogger("orchestrator.llm")


# --- Fireworks AI Client (Commented out) ---
# class FireworksResponse:
#     """Lightweight response wrapper mimicking LangChain AIMessage."""
#     def __init__(self, content: str):
#         self.content = content
#
#
# class FireworksChatClient:
#     """
#     Native, zero-dependency Fireworks AI client for DeepSeek.
#     Communicates directly via standard HTTPS without requiring langchain-openai.
#     """
#     def __init__(self, api_key: str, model: str, base_url: str):
#         self.api_key = api_key
#         self.model = model
#         self.endpoint = f"{base_url.rstrip('/')}/chat/completions"
#
#     def invoke(self, messages: list) -> FireworksResponse:
#         import urllib.request
#
#         formatted = []
#         for m in messages:
#             msg_type = getattr(m, "type", "")
#             cls_name = m.__class__.__name__
#             if msg_type == "system" or cls_name == "SystemMessage":
#                 role = "system"
#             elif msg_type == "human" or cls_name == "HumanMessage":
#                 role = "user"
#             else:
#                 role = "user"
#             content = getattr(m, "content", str(m))
#             formatted.append({"role": role, "content": content})
#
#         payload = {
#             "model": self.model,
#             "messages": formatted,
#             "max_tokens": 1024,
#             "temperature": 0.0,
#         }
#         headers = {
#             "Accept": "application/json",
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {self.api_key}",
#         }
#         req = urllib.request.Request(
#             self.endpoint,
#             data=json.dumps(payload).encode("utf-8"),
#             headers=headers,
#             method="POST",
#         )
#         with urllib.request.urlopen(req, timeout=15) as resp:
#             data = json.loads(resp.read().decode("utf-8"))
#             content = data["choices"][0]["message"]["content"]
#             return FireworksResponse(content=content)


class OpenRouterResponse:
    """Lightweight response wrapper holding content and reasoning details."""
    def __init__(self, content: str, reasoning_details: Any = None):
        self.content = content
        self.reasoning_details = reasoning_details


class OpenRouterChatClient:
    """
    OpenRouter client using the official OpenAI SDK with reasoning support.
    Reads model and base URL strictly from environment settings.
    """
    def __init__(self, api_key: str, model: str, base_url: str):
        from openai import OpenAI
        if not model or not base_url:
            raise ValueError("OPENROUTER_MODEL and OPENROUTER_BASE_URL must be configured in .env")
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        self.model = model

    def invoke(self, messages: list) -> OpenRouterResponse:
        formatted = []
        for m in messages:
            msg_type = getattr(m, "type", "")
            cls_name = m.__class__.__name__
            if msg_type == "system" or cls_name == "SystemMessage":
                role = "system"
            elif msg_type == "human" or cls_name == "HumanMessage":
                role = "user"
            elif msg_type == "ai" or cls_name == "AIMessage":
                role = "assistant"
            else:
                role = "user"

            content = getattr(m, "content", str(m))
            entry: Dict[str, Any] = {"role": role, "content": content}
            if hasattr(m, "reasoning_details") and m.reasoning_details:
                entry["reasoning_details"] = m.reasoning_details
            formatted.append(entry)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=formatted,
            extra_body={"reasoning": {"enabled": True}},
        )
        msg = response.choices[0].message
        content = msg.content or ""
        reasoning_details = getattr(msg, "reasoning_details", None)
        return OpenRouterResponse(content=content, reasoning_details=reasoning_details)


def get_configured_llm():
    """
    Returns an instantiated OpenRouterChatClient configured from environment settings.
    """
    # --- Fireworks AI (Commented out) ---
    # if settings.FIREWORKS_API_KEY:
    #     try:
    #         return FireworksChatClient(
    #             api_key=settings.FIREWORKS_API_KEY,
    #             model=settings.FIREWORKS_MODEL,
    #             base_url=settings.FIREWORKS_BASE_URL,
    #         )
    #     except Exception as e:
    #         logger.warning(f"Failed to initialize Fireworks AI client: {e}")

    if settings.OPENROUTER_API_KEY:
        try:
            return OpenRouterChatClient(
                api_key=settings.OPENROUTER_API_KEY,
                model=settings.OPENROUTER_MODEL,
                base_url=settings.OPENROUTER_BASE_URL,
            )
        except Exception as e:
            logger.warning(f"Failed to initialize OpenRouter client: {e}")

    logger.info("Using native deterministic NLP inference engine.")
    return None


def run_deterministic_classification(message: str) -> Tuple[str, float]:
    """
    Simulates high-precision LLM intent classification when API keys are not supplied.
    Returns (intent, confidence_score).
    """
    text = message.lower().strip()

    # Ambiguity check: Out of scope keywords
    out_of_scope = ["loan", "mortgage", "car", "weather", "crypto", "bitcoin", "joke", "transfer", "deposit"]
    for word in out_of_scope:
        if word in text and not any(k in text for k in ["fee", "limit", "card", "replace"]):
            return "unclear", 0.35

    # 1. Fee Waiver checks
    fee_signals = ["fee", "charge", "penalty", "annual fee", "late fee", "interest charge"]
    waiver_signals = ["waive", "waiver", "refund", "remove", "reversal", "reimburse", "drop"]
    has_fee = any(s in text for s in fee_signals)
    has_waiver = any(s in text for s in waiver_signals)

    if has_fee and has_waiver:
        return "fee_waiver", 0.95
    if has_fee and not has_waiver and not any(k in text for k in ["limit", "card", "replace"]):
        # Vague about fees -> lower confidence
        return "fee_waiver", 0.60

    # 2. Credit Limit Increase checks
    limit_signals = ["limit", "credit limit", "spending limit", "credit line"]
    increase_signals = ["increase", "raise", "higher", "boost", "upgrade", "more credit", "expand"]
    has_limit = any(s in text for s in limit_signals)
    has_increase = any(s in text for s in increase_signals)

    if has_limit and has_increase:
        return "credit_limit_increase", 0.96
    if has_limit and not has_increase and not any(k in text for k in ["fee", "replace", "card"]):
        return "credit_limit_increase", 0.65

    # 3. Card Replacement checks
    card_signals = ["card", "credit card", "plastic"]
    replacement_signals = ["replace", "replacement", "new card", "reissue", "stolen", "lost", "damaged", "broken", "expired"]
    has_card = any(s in text for s in card_signals)
    has_replace = any(s in text for s in replacement_signals)

    if has_card and has_replace:
        return "card_replacement", 0.94
    if has_replace and not has_card:
        return "card_replacement", 0.85

    # Fallback to unclear if no strong intent detected
    return "unclear", 0.25


def run_deterministic_slot_extraction(intent: str, message: str) -> Dict[str, Any]:
    """
    Simulates high-precision LLM slot extraction when API keys are not supplied.
    """
    text = message.lower().strip()
    slots: Dict[str, Any] = {}

    if intent == "fee_waiver":
        # Extract fee type
        if "annual" in text:
            slots["fee_type"] = "annual_fee"
        elif "late" in text:
            slots["fee_type"] = "late_fee"
        elif "foreign" in text or "international" in text:
            slots["fee_type"] = "foreign_transaction_fee"
        elif "overlimit" in text or "over limit" in text:
            slots["fee_type"] = "overlimit_fee"
        else:
            slots["fee_type"] = "unspecified_fee"

        # Extract amount if present
        amount_match = re.search(r"\$?\s*(\d+(?:\.\d{2})?)", message)
        if amount_match:
            try:
                slots["amount"] = float(amount_match.group(1))
            except ValueError:
                slots["amount"] = None
        else:
            slots["amount"] = None

        slots["reason"] = "cardholder request"

    elif intent == "credit_limit_increase":
        # Extract requested limit amount
        amount_match = re.search(r"(?:to|by|for)?\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\d+)(?:\s*(?:k|thousand))?", text)
        extracted_limit: Optional[float] = None

        # Look specifically for numbers
        numbers = re.findall(r"\$?\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?)", message)
        if numbers:
            # Pick the largest number as likely requested limit
            clean_nums = [float(n.replace(",", "").replace("$", "").strip()) for n in numbers]
            if clean_nums:
                extracted_limit = clean_nums[0]
                # Check for "k" notation e.g., 10k -> 10000
                if re.search(r"\b\d+\s*k\b", text):
                    extracted_limit = extracted_limit * 1000

        slots["requested_limit"] = extracted_limit
        slots["reason"] = "cardholder request"

    elif intent == "card_replacement":
        # Extract reason: damaged, lost, stolen, expired
        if "stolen" in text:
            slots["reason"] = "stolen"
        elif "lost" in text:
            slots["reason"] = "lost"
        elif "damaged" in text or "broken" in text or "chipped" in text:
            slots["reason"] = "damaged"
        elif "expired" in text or "expiring" in text:
            slots["reason"] = "expired"
        else:
            slots["reason"] = None  # Missing slot! Triggers clarification

        # Extract delivery type
        if "rush" in text or "express" in text or "expedited" in text or "overnight" in text:
            slots["delivery_type"] = "expedited"
        else:
            slots["delivery_type"] = "standard"

    return slots
