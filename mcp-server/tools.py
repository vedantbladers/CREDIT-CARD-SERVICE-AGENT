from datetime import datetime, timezone
from typing import Any, Dict, Optional
from db import get_db_connection

# Approved MCP Tool Definitions following the Model Context Protocol specification
TOOLS_MANIFEST = [
    {
        "name": "waive_fee",
        "description": "Waives a cardholder fee, decrements account balance, increments quarterly fee waiver count, and records an ACID audit transaction.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "Unique cardholder account identifier (e.g. ACC-1001)",
                },
                "amount": {
                    "type": "number",
                    "description": "Fee amount to waive/credit (defaults to $95.00 if omitted)",
                },
                "fee_type": {
                    "type": "string",
                    "description": "Category of fee (e.g. annual_fee, late_fee, foreign_transaction_fee)",
                },
            },
            "required": ["account_id"],
        },
    },
    {
        "name": "adjust_credit_limit",
        "description": "Adjusts revolving credit limit for a cardholder in an ACID transaction and records an audit log.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "Unique cardholder account identifier (e.g. ACC-1001)",
                },
                "new_limit": {
                    "type": "number",
                    "description": "The approved new revolving credit limit amount",
                },
            },
            "required": ["account_id", "new_limit"],
        },
    },
    {
        "name": "replace_card",
        "description": "Authorizes and orders a physical credit card replacement, registers dispatch order, and logs audit record.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "Unique cardholder account identifier (e.g. ACC-1001)",
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for replacement: stolen, lost, damaged, expired",
                },
                "delivery_type": {
                    "type": "string",
                    "description": "Delivery method: standard or expedited",
                },
            },
            "required": ["account_id"],
        },
    },
    {
        "name": "get_account",
        "description": "Retrieves the current real-time core banking account record from PostgreSQL.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "Unique cardholder account identifier",
                },
            },
            "required": ["account_id"],
        },
    },
]


def execute_waive_fee(
    account_id: str,
    amount: Optional[float] = 95.0,
    fee_type: str = "annual_fee",
) -> Dict[str, Any]:
    """
    Executes a fee waiver as an ACID transaction against PostgreSQL.
    1. Lock row with SELECT ... FOR UPDATE
    2. Adjust balance = balance - amount (or credit)
    3. Increment fees_waived_this_quarter = fees_waived_this_quarter + 1
    4. Write immutable record to audit_transactions
    5. Commit transaction
    """
    waiver_amount = float(amount) if amount is not None else 95.0

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # 1. Lock and fetch current row state
            cur.execute(
                "SELECT id, account_number, name, balance, fees_waived_this_quarter, status "
                "FROM accounts WHERE account_number = %s FOR UPDATE;",
                (account_id,),
            )
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Account '{account_id}' not found in core banking database")

            if row["status"] != "active":
                raise ValueError(f"Account '{account_id}' is not active (status: {row['status']})")

            before_balance = float(row["balance"])
            before_waivers = int(row["fees_waived_this_quarter"])

            # 2. Compute updated balances
            new_balance = round(max(0.0, before_balance - waiver_amount), 2)
            new_waivers = before_waivers + 1

            # 3. Update account record
            cur.execute(
                "UPDATE accounts SET balance = %s, fees_waived_this_quarter = %s "
                "WHERE account_number = %s;",
                (new_balance, new_waivers, account_id),
            )

            # 4. Insert transaction audit record
            description = (
                f"Fee waiver of ${waiver_amount:.2f} granted for {fee_type.replace('_', ' ')}. "
                f"Previous balance: ${before_balance:.2f}, New balance: ${new_balance:.2f}."
            )
            cur.execute(
                "INSERT INTO audit_transactions (account_number, transaction_type, amount, description) "
                "VALUES (%s, %s, %s, %s) RETURNING id, created_at;",
                (account_id, "FEE_WAIVER", waiver_amount, description),
            )
            audit_row = cur.fetchone()
            tx_id = audit_row["id"]
            tx_time = audit_row["created_at"].isoformat()

    return {
        "status": "SUCCESS",
        "tool": "waive_fee",
        "account_id": account_id,
        "transaction_id": tx_id,
        "fee_type": fee_type,
        "amount_waived": waiver_amount,
        "database_state": {
            "balance": {
                "before": before_balance,
                "after": new_balance,
                "delta": -waiver_amount,
            },
            "fees_waived_this_quarter": {
                "before": before_waivers,
                "after": new_waivers,
            },
        },
        "executed_at": tx_time,
        "acid_guarantee": "COMMITTED",
    }


def execute_adjust_credit_limit(account_id: str, new_limit: float) -> Dict[str, Any]:
    """
    Adjusts credit limit in an ACID transaction.
    """
    limit_val = float(new_limit)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, account_number, credit_limit, status FROM accounts "
                "WHERE account_number = %s FOR UPDATE;",
                (account_id,),
            )
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Account '{account_id}' not found in core banking database")

            if row["status"] != "active":
                raise ValueError(f"Account '{account_id}' is not active (status: {row['status']})")

            before_limit = float(row["credit_limit"])

            cur.execute(
                "UPDATE accounts SET credit_limit = %s WHERE account_number = %s;",
                (limit_val, account_id),
            )

            description = f"Credit limit adjusted from ${before_limit:,.2f} to ${limit_val:,.2f}."
            cur.execute(
                "INSERT INTO audit_transactions (account_number, transaction_type, amount, description) "
                "VALUES (%s, %s, %s, %s) RETURNING id, created_at;",
                (account_id, "CREDIT_LIMIT_ADJUSTMENT", limit_val - before_limit, description),
            )
            audit_row = cur.fetchone()
            tx_id = audit_row["id"]
            tx_time = audit_row["created_at"].isoformat()

    return {
        "status": "SUCCESS",
        "tool": "adjust_credit_limit",
        "account_id": account_id,
        "transaction_id": tx_id,
        "database_state": {
            "credit_limit": {
                "before": before_limit,
                "after": limit_val,
                "delta": limit_val - before_limit,
            },
        },
        "executed_at": tx_time,
        "acid_guarantee": "COMMITTED",
    }


def execute_replace_card(
    account_id: str,
    reason: str = "stolen",
    delivery_type: str = "standard",
) -> Dict[str, Any]:
    """
    Registers card replacement order and audit log in an ACID transaction.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, account_number, status FROM accounts WHERE account_number = %s FOR UPDATE;",
                (account_id,),
            )
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Account '{account_id}' not found in core banking database")

            if row["status"] == "suspended":
                raise ValueError(f"Account '{account_id}' is suspended. Replacement card blocked.")

            cur.execute(
                "INSERT INTO card_replacements (account_number, reason, delivery_type, status) "
                "VALUES (%s, %s, %s, 'dispatched') RETURNING id, created_at;",
                (account_id, reason, delivery_type),
            )
            rep_row = cur.fetchone()
            rep_id = rep_row["id"]
            rep_time = rep_row["created_at"].isoformat()

            description = f"Replacement card ordered. Reason: {reason}, Delivery: {delivery_type}."
            cur.execute(
                "INSERT INTO audit_transactions (account_number, transaction_type, amount, description) "
                "VALUES (%s, %s, %s, %s) RETURNING id;",
                (account_id, "CARD_REPLACEMENT", 0.00, description),
            )
            tx_row = cur.fetchone()

    estimated_days = 2 if delivery_type == "expedited" else 5

    return {
        "status": "SUCCESS",
        "tool": "replace_card",
        "account_id": account_id,
        "replacement_id": rep_id,
        "transaction_id": tx_row["id"],
        "reason": reason,
        "delivery_type": delivery_type,
        "dispatch_status": "dispatched",
        "estimated_delivery_days": estimated_days,
        "ordered_at": rep_time,
        "acid_guarantee": "COMMITTED",
    }


def execute_get_account(account_id: str) -> Dict[str, Any]:
    """
    Reads live account record from PostgreSQL.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT account_number, name, balance, credit_limit, fees_waived_this_quarter, tenure_months, status "
                "FROM accounts WHERE account_number = %s;",
                (account_id,),
            )
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Account '{account_id}' not found in core banking database")

            return {
                "account_number": row["account_number"],
                "name": row["name"],
                "balance": float(row["balance"]),
                "credit_limit": float(row["credit_limit"]),
                "fees_waived_this_quarter": int(row["fees_waived_this_quarter"]),
                "tenure_months": int(row["tenure_months"]),
                "status": row["status"],
            }
