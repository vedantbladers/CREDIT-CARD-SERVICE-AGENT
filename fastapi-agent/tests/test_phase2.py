import pytest
from app.services.graph_orchestrator import execute_agent_graph


def test_fee_waiver_full_slots():
    query = "Can you please waive my $95 annual membership fee?"
    result = execute_agent_graph(query)

    assert result["intent"] == "fee_waiver"
    assert result["confidence_score"] >= 0.70
    assert result["needs_clarification"] is False
    assert result["slots"]["fee_type"] == "annual_fee"
    assert result["slots"]["amount"] == 95.0


def test_credit_limit_increase_with_amount():
    query = "I would like to raise my credit limit to $15,000 please"
    result = execute_agent_graph(query)

    assert result["intent"] == "credit_limit_increase"
    assert result["confidence_score"] >= 0.70
    assert result["needs_clarification"] is False
    assert result["slots"]["requested_limit"] == 15000.0


def test_credit_limit_increase_missing_amount_triggers_clarify():
    query = "I would like to request an increase on my card credit limit"
    result = execute_agent_graph(query)

    assert result["intent"] == "credit_limit_increase"
    assert result["needs_clarification"] is True
    assert "specify the new credit limit amount" in result["clarification_prompt"]


def test_card_replacement_with_reason():
    query = "My credit card was stolen in the subway, I need a replacement right away"
    result = execute_agent_graph(query)

    assert result["intent"] == "card_replacement"
    assert result["confidence_score"] >= 0.70
    assert result["needs_clarification"] is False
    assert result["slots"]["reason"] == "stolen"


def test_card_replacement_missing_reason_triggers_clarify():
    query = "Can you please send me a replacement card to my address?"
    result = execute_agent_graph(query)

    assert result["intent"] == "card_replacement"
    assert result["needs_clarification"] is True
    assert "specify why you need a replacement" in result["clarification_prompt"]


def test_ambiguous_out_of_scope_triggers_clarify():
    query = "Can you help me apply for a used car loan?"
    result = execute_agent_graph(query)

    assert result["intent"] == "unclear"
    assert result["needs_clarification"] is True
    assert "specialize in credit card servicing" in result["clarification_prompt"]
