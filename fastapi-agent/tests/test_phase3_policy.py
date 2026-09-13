import pytest
from app.policy.engine import evaluate_policy
from app.policy.models import AccountProfile, PolicyDecision
from app.policy.repository import reset_account_store
from app.policy.rules import (
    evaluate_card_replacement,
    evaluate_credit_limit_increase,
    evaluate_fee_waiver,
)


@pytest.fixture(autouse=True)
def setup_store():
    reset_account_store()


# --- Fee Waiver Policy Tests ---

def test_fee_waiver_approved_when_zero_waivers():
    account = AccountProfile(
        account_number="ACC-1001",
        name="Alice Johnson",
        balance=1450.50,
        credit_limit=10000.0,
        fees_waived_this_quarter=0,
        tenure_months=18,
        is_active=True,
        status="active",
    )
    result = evaluate_fee_waiver(account, {"fee_type": "annual_fee", "amount": 95.0})

    assert result.decision == PolicyDecision.APPROVED
    assert "POL-FW-001" in result.rule_name
    assert "Fee waiver approved" in result.reason
    assert result.details["fees_waived_this_quarter"] == 0


def test_fee_waiver_rejected_when_limit_reached():
    account = AccountProfile(
        account_number="ACC-1002",
        name="Bob Smith",
        balance=320.0,
        credit_limit=5000.0,
        fees_waived_this_quarter=1,
        tenure_months=3,
        is_active=True,
        status="active",
    )
    result = evaluate_fee_waiver(account, {"fee_type": "late_fee", "amount": 35.0})

    assert result.decision == PolicyDecision.REJECTED
    assert "POL-FW-001" in result.rule_name
    assert "Maximum permissible is 1" in result.reason
    assert result.details["fees_waived_this_quarter"] == 1


def test_fee_waiver_escalates_on_high_amount():
    account = AccountProfile(
        account_number="ACC-1001",
        name="Alice Johnson",
        balance=1450.50,
        credit_limit=10000.0,
        fees_waived_this_quarter=0,
        tenure_months=18,
        is_active=True,
        status="active",
    )
    result = evaluate_fee_waiver(account, {"fee_type": "late_fee", "amount": 250.0})

    assert result.decision == PolicyDecision.NEEDS_ESCALATION
    assert "POL-FW-002" in result.rule_name
    assert "exceeds the $150.00 automated approval threshold" in result.reason
    assert result.details["requested_amount"] == 250.0


def test_fee_waiver_rejected_for_suspended_account():
    account = AccountProfile(
        account_number="ACC-1003",
        name="Charlie Brown",
        balance=5820.75,
        credit_limit=15000.0,
        fees_waived_this_quarter=0,
        tenure_months=24,
        is_active=False,
        status="suspended",
    )
    result = evaluate_fee_waiver(account, {"fee_type": "annual_fee", "amount": 95.0})

    assert result.decision == PolicyDecision.REJECTED
    assert "not in active standing" in result.reason


# --- Credit Limit Increase Policy Tests ---

def test_credit_limit_increase_approved_within_20_percent():
    account = AccountProfile(
        account_number="ACC-1001",
        name="Alice Johnson",
        balance=1450.50,
        credit_limit=10000.0,
        fees_waived_this_quarter=0,
        tenure_months=18,
        is_active=True,
        status="active",
    )
    result = evaluate_credit_limit_increase(account, {"requested_limit": 12000.0})

    assert result.decision == PolicyDecision.APPROVED
    assert "POL-CLI-001" in result.rule_name
    assert result.details["increase_percentage"] == 20.0
    assert "approved" in result.reason.lower()


def test_credit_limit_increase_escalated_between_20_and_50_percent():
    account = AccountProfile(
        account_number="ACC-1001",
        name="Alice Johnson",
        balance=1450.50,
        credit_limit=10000.0,
        fees_waived_this_quarter=0,
        tenure_months=18,
        is_active=True,
        status="active",
    )
    result = evaluate_credit_limit_increase(account, {"requested_limit": 14000.0})

    assert result.decision == PolicyDecision.NEEDS_ESCALATION
    assert "POL-CLI-003" in result.rule_name
    assert result.details["increase_percentage"] == 40.0
    assert "Escalating to Senior Credit Underwriter" in result.reason


def test_credit_limit_increase_rejected_above_50_percent():
    account = AccountProfile(
        account_number="ACC-1001",
        name="Alice Johnson",
        balance=1450.50,
        credit_limit=10000.0,
        fees_waived_this_quarter=0,
        tenure_months=18,
        is_active=True,
        status="active",
    )
    result = evaluate_credit_limit_increase(account, {"requested_limit": 18000.0})

    assert result.decision == PolicyDecision.REJECTED
    assert "POL-CLI-004" in result.rule_name
    assert result.details["increase_percentage"] == 80.0
    assert "exceeds the maximum permissible cap of 50.0%" in result.reason


def test_credit_limit_increase_rejected_tenure_under_6_months():
    account = AccountProfile(
        account_number="ACC-1002",
        name="Bob Smith",
        balance=320.0,
        credit_limit=5000.0,
        fees_waived_this_quarter=0,
        tenure_months=3,
        is_active=True,
        status="active",
    )
    result = evaluate_credit_limit_increase(account, {"requested_limit": 5500.0})

    assert result.decision == PolicyDecision.REJECTED
    assert "POL-CLI-002" in result.rule_name
    assert "requires a minimum of 6 active months" in result.reason
    assert result.details["tenure_months"] == 3


def test_credit_limit_increase_rejected_when_requested_below_current():
    account = AccountProfile(
        account_number="ACC-1001",
        name="Alice Johnson",
        balance=1450.50,
        credit_limit=10000.0,
        fees_waived_this_quarter=0,
        tenure_months=18,
        is_active=True,
        status="active",
    )
    result = evaluate_credit_limit_increase(account, {"requested_limit": 9000.0})

    assert result.decision == PolicyDecision.REJECTED
    assert "must be strictly higher" in result.reason


# --- Card Replacement Policy Tests ---

def test_card_replacement_approved_for_active_account():
    account = AccountProfile(
        account_number="ACC-1001",
        name="Alice Johnson",
        balance=1450.50,
        credit_limit=10000.0,
        fees_waived_this_quarter=0,
        tenure_months=18,
        is_active=True,
        status="active",
    )
    result = evaluate_card_replacement(account, {"reason": "stolen", "delivery_type": "standard"})

    assert result.decision == PolicyDecision.APPROVED
    assert "POL-CR-001" in result.rule_name
    assert "Card replacement authorized" in result.reason


def test_card_replacement_rejected_for_suspended_account():
    account = AccountProfile(
        account_number="ACC-1003",
        name="Charlie Brown",
        balance=5820.75,
        credit_limit=15000.0,
        fees_waived_this_quarter=0,
        tenure_months=24,
        is_active=False,
        status="suspended",
    )
    result = evaluate_card_replacement(account, {"reason": "damaged"})

    assert result.decision == PolicyDecision.REJECTED
    assert "suspended" in result.reason


def test_card_replacement_escalated_for_fraud_alert():
    account = AccountProfile(
        account_number="ACC-1004",
        name="Dana Scully",
        balance=890.0,
        credit_limit=7500.0,
        fees_waived_this_quarter=0,
        tenure_months=14,
        is_active=True,
        status="fraud_alert",
    )
    result = evaluate_card_replacement(account, {"reason": "lost"})

    assert result.decision == PolicyDecision.NEEDS_ESCALATION
    assert "POL-CR-002" in result.rule_name
    assert "Fraud Operations" in result.reason


# --- Policy Engine Integration & Repository Tests ---

def test_evaluate_policy_dispatcher_for_seeded_accounts():
    # 1. Fee waiver on ACC-1001 (0 waivers) -> APPROVED
    res_alice = evaluate_policy(intent="fee_waiver", slots={"fee_type": "late_fee", "amount": 35.0}, account_id="ACC-1001")
    assert res_alice.decision == PolicyDecision.APPROVED

    # 2. Fee waiver on ACC-1002 (1 waiver) -> REJECTED
    res_bob = evaluate_policy(intent="fee_waiver", slots={"fee_type": "late_fee", "amount": 35.0}, account_id="ACC-1002")
    assert res_bob.decision == PolicyDecision.REJECTED

    # 3. Credit limit increase on ACC-1002 (3 months tenure) -> REJECTED
    res_bob_cli = evaluate_policy(intent="credit_limit_increase", slots={"requested_limit": 5500.0}, account_id="ACC-1002")
    assert res_bob_cli.decision == PolicyDecision.REJECTED
    assert "POL-CLI-002" in res_bob_cli.rule_name

    # 4. Unknown account -> REJECTED
    res_unknown = evaluate_policy(intent="fee_waiver", slots={}, account_id="ACC-9999")
    assert res_unknown.decision == PolicyDecision.REJECTED
    assert "UnknownAccount" in res_unknown.rule_name


# --- End-to-End API Integration Tests with TestClient ---

def test_api_chat_policy_approved_flow():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    response = client.post(
        "/chat",
        json={"message": "Can you please waive my $95 annual fee?", "account_id": "ACC-1001"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "fee_waiver"
    assert data["policy_decision"] == "APPROVED"
    assert data["status"] in ["policy_approved", "executed"]
    assert data["policy_decision"] == "APPROVED"


def test_api_chat_policy_rejected_flow():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    response = client.post(
        "/chat",
        json={"message": "Please waive my late fee of $35", "account_id": "ACC-1002"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "fee_waiver"
    assert data["policy_decision"] == "REJECTED"
    assert "POL-FW-001" in data["policy_rule"]
    assert data["status"] == "policy_rejected"


def test_api_accounts_list():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    response = client.get("/accounts")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 3
    account_ids = [a["account_number"] for a in data["accounts"]]
    assert "ACC-1001" in account_ids
    assert "ACC-1002" in account_ids
    assert "ACC-1003" in account_ids


