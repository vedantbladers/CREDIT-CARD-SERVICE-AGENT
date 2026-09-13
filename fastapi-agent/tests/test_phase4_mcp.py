import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure mcp-server is in Python path for test execution
MCP_SERVER_DIR = Path(__file__).resolve().parent.parent.parent / "mcp-server"
if str(MCP_SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(MCP_SERVER_DIR))

from server import app as mcp_app
from tools import (
    TOOLS_MANIFEST,
    execute_adjust_credit_limit,
    execute_get_account,
    execute_replace_card,
    execute_waive_fee,
)
from app.models.schemas import ChatRequest
from app.api.chat import handle_chat


mcp_test_client = TestClient(mcp_app)


# =====================================================================
# 1. MCP Manifest & Protocol Tests
# =====================================================================

def test_mcp_tools_manifest_structure():
    """Verify approved MCP tools conform to Model Context Protocol schema specifications."""
    tool_names = [t["name"] for t in TOOLS_MANIFEST]
    assert "waive_fee" in tool_names
    assert "adjust_credit_limit" in tool_names
    assert "replace_card" in tool_names
    assert "get_account" in tool_names
    assert len(TOOLS_MANIFEST) == 4

    for tool in TOOLS_MANIFEST:
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool
        assert tool["inputSchema"]["type"] == "object"
        assert "properties" in tool["inputSchema"]
        assert "required" in tool["inputSchema"]


def test_mcp_jsonrpc_tools_list():
    """Verify JSON-RPC 2.0 tools/list method returns registered tools."""
    response = mcp_test_client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 42,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 42
    assert "result" in data
    assert len(data["result"]["tools"]) == 4


def test_mcp_jsonrpc_unknown_method():
    """Verify JSON-RPC 2.0 error response for unrecognized methods."""
    response = mcp_test_client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "method": "database/raw_query",
            "params": {"sql": "DROP TABLE accounts;"},
            "id": 99,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == -32601
    assert "not found" in data["error"]["message"].lower()


# =====================================================================
# 2. ACID Transactional Core Tool Execution Tests
# =====================================================================

def test_mcp_execute_get_account():
    """Verify reading account state directly from PostgreSQL."""
    acc = execute_get_account("ACC-1001")
    assert acc["status"] == "SUCCESS"
    data = acc["data"]
    assert data["account_number"] == "ACC-1001"
    assert data["name"] == "Alice Johnson"
    assert data["status"] == "active"


def test_mcp_execute_waive_fee_acid_delta():
    """Verify waive_fee performs ACID update with before/after state and audit logging."""
    # Read initial state
    before_acc = execute_get_account("ACC-1001")["data"]
    init_balance = float(before_acc["balance"])
    init_waivers = int(before_acc["fees_waived_this_quarter"])

    # Execute $50 waiver
    res = execute_waive_fee(account_id="ACC-1001", amount=50.0, fee_type="late_fee")
    assert res["status"] == "SUCCESS"
    assert res["acid_guarantee"] == "COMMITTED"
    assert "transaction_id" in res

    db_state = res["database_state"]
    assert db_state["balance"]["before"] == init_balance
    assert abs(db_state["balance"]["after"] - (init_balance - 50.0)) < 0.01
    assert db_state["fees_waived_this_quarter"]["after"] == init_waivers + 1

    # Verify audit transaction record
    audit = res["audit_record"]
    assert audit["account_id"] == "ACC-1001"
    assert audit["action"] == "WAIVE_FEE"
    assert audit["status"] == "COMMITTED"


def test_mcp_execute_adjust_credit_limit():
    """Verify adjust_credit_limit updates credit line and writes audit record."""
    acc_id = "ACC-1002"
    res = execute_adjust_credit_limit(account_id=acc_id, new_limit=7500.0)
    assert res["status"] == "SUCCESS"
    assert res["acid_guarantee"] == "COMMITTED"
    assert res["database_state"]["credit_limit"]["after"] == 7500.0

    # Read back from DB to confirm persistence
    current = execute_get_account(acc_id)["data"]
    assert float(current["credit_limit"]) == 7500.0


def test_mcp_execute_replace_card():
    """Verify replace_card records replacement order and estimates delivery accurately."""
    res = execute_replace_card(
        account_id="ACC-1001",
        reason="damaged",
        delivery_type="expedited",
    )
    assert res["status"] == "SUCCESS"
    assert res["acid_guarantee"] == "COMMITTED"
    assert res["delivery_type"] == "expedited"
    assert res["estimated_delivery_days"] == 2
    assert "replacement_id" in res


def test_mcp_nonexistent_account_fails_gracefully():
    """Verify attempting to waive fee on non-existent account rolls back safely."""
    with pytest.raises(ValueError) as excinfo:
        execute_waive_fee(account_id="ACC-NONEXISTENT-9999", amount=50.0)
    assert "Account 'ACC-NONEXISTENT-9999' not found" in str(excinfo.value)


# =====================================================================
# 3. JSON-RPC tools/call Endpoint Integration
# =====================================================================

def test_mcp_jsonrpc_tools_call_success():
    """Test calling waive_fee through the standard JSON-RPC HTTP endpoint."""
    response = mcp_test_client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "waive_fee",
                "arguments": {
                    "account_id": "ACC-1003",
                    "amount": 25.0,
                    "fee_type": "overdraft_fee",
                },
            },
            "id": 101,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 101
    assert "result" in data
    assert data["result"]["isError"] is False
    assert data["result"]["data"]["status"] == "SUCCESS"


# =====================================================================
# 4. Defense-in-Depth Orchestration Tests (Policy -> MCP Gate)
# =====================================================================

def test_chat_blocks_mcp_when_policy_rejected():
    """
    CRITICAL DEFENSE-IN-DEPTH:
    When policy engine returns REJECTED, MCP tool MUST NOT be executed.
    """
    # ACC-1002 has 1 fee waived this quarter (limit is 1 for non-VIP)
    # Ensure ACC-1002 has 1 fee waiver recorded
    execute_adjust_credit_limit("ACC-1002", 5000.0)  # clean check
    
    req = ChatRequest(
        message="Please waive my late fee of $35",
        account_id="ACC-1002",
    )
    resp = handle_chat(req)

    # ACC-1002 has tenure 3 months & already has 1 waiver -> REJECTED
    assert resp.policy_decision == "REJECTED"
    assert resp.status == "policy_rejected"
    assert resp.execution_result is not None
    assert resp.execution_result["status"] == "BLOCKED_BY_POLICY"
    assert resp.execution_result["tool_called"] is None


def test_chat_blocks_mcp_when_policy_escalated():
    """
    CRITICAL DEFENSE-IN-DEPTH:
    When policy engine returns NEEDS_ESCALATION, MCP tool MUST NOT be executed.
    """
    # Alice requests a credit limit of $50,000 (exceeds automatic approval ceiling of $25,000)
    req = ChatRequest(
        message="I would like to increase my credit limit to $50,000 please",
        account_id="ACC-1001",
    )
    resp = handle_chat(req)

    assert resp.policy_decision == "NEEDS_ESCALATION"
    assert resp.status == "policy_escalated"
    assert resp.execution_result is not None
    assert resp.execution_result["status"] == "ESCALATED_MANUAL_REVIEW"
    assert resp.execution_result["tool_called"] is None
