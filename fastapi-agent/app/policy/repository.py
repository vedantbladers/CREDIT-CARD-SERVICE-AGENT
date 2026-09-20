from typing import Dict, List, Optional
from app.policy.models import AccountProfile


# In-memory account store seeded identically to PostgreSQL core banking table with additional risk parameters
_ACCOUNT_STORE: Dict[str, AccountProfile] = {
    "ACC-1001": AccountProfile(
        account_number="ACC-1001",
        name="Alice Johnson",
        balance=1450.50,
        credit_limit=10000.00,
        fees_waived_this_quarter=0,
        tenure_months=18,
        is_active=True,
        status="active",
    ),
    "ACC-1002": AccountProfile(
        account_number="ACC-1002",
        name="Bob Smith",
        balance=320.00,
        credit_limit=5000.00,
        fees_waived_this_quarter=1,
        tenure_months=3,  # < 6 months tenure
        is_active=True,
        status="active",
    ),
    "ACC-1003": AccountProfile(
        account_number="ACC-1003",
        name="Charlie Brown",
        balance=5820.75,
        credit_limit=15000.00,
        fees_waived_this_quarter=2,
        tenure_months=24,
        is_active=False,  # Suspended account
        status="suspended",
    ),
    "ACC-1004": AccountProfile(
        account_number="ACC-1004",
        name="Dana Scully",
        balance=890.00,
        credit_limit=7500.00,
        fees_waived_this_quarter=0,
        tenure_months=14,
        is_active=True,
        status="fraud_alert",  # Fraud alert flag
    ),
}


def get_account_profile(account_id: str) -> Optional[AccountProfile]:
    """
    Retrieve an account profile by account identifier.
    In Phase 4, queries the live core banking state via MCP get_account tool
    so deterministic policy evaluations reflect real-time database state.
    Falls back to in-memory store if MCP is unavailable.
    """
    try:
        from app.services.mcp_client import call_mcp_tool
        data = call_mcp_tool("get_account", {"account_id": account_id.upper()})
        if data and "account_number" in data:
            return AccountProfile(
                account_number=data["account_number"],
                name=data.get("name", "Cardholder"),
                balance=float(data.get("balance", 0.0)),
                credit_limit=float(data.get("credit_limit", 5000.0)),
                fees_waived_this_quarter=int(data.get("fees_waived_this_quarter", 0)),
                tenure_months=int(data.get("tenure_months", 12)),
                is_active=(data.get("status") == "active"),
                status=data.get("status", "active"),
            )
    except Exception:
        pass

    return _ACCOUNT_STORE.get(account_id.upper())


def save_account_profile(profile: AccountProfile) -> None:
    """Save or update an account profile in the store."""
    _ACCOUNT_STORE[profile.account_number.upper()] = profile


def list_all_accounts() -> List[AccountProfile]:
    """List all configured account profiles."""
    return list(_ACCOUNT_STORE.values())


def reset_account_store() -> None:
    """Reset account store to initial default values (useful for unit test isolation)."""
    global _ACCOUNT_STORE
    _ACCOUNT_STORE = {
        "ACC-1001": AccountProfile(
            account_number="ACC-1001",
            name="Alice Johnson",
            balance=1450.50,
            credit_limit=10000.00,
            fees_waived_this_quarter=0,
            tenure_months=18,
            is_active=True,
            status="active",
        ),
        "ACC-1002": AccountProfile(
            account_number="ACC-1002",
            name="Bob Smith",
            balance=320.00,
            credit_limit=5000.00,
            fees_waived_this_quarter=1,
            tenure_months=3,
            is_active=True,
            status="active",
        ),
        "ACC-1003": AccountProfile(
            account_number="ACC-1003",
            name="Charlie Brown",
            balance=5820.75,
            credit_limit=15000.00,
            fees_waived_this_quarter=2,
            tenure_months=24,
            is_active=False,
            status="suspended",
        ),
        "ACC-1004": AccountProfile(
            account_number="ACC-1004",
            name="Dana Scully",
            balance=890.00,
            credit_limit=7500.00,
            fees_waived_this_quarter=0,
            tenure_months=14,
            is_active=True,
            status="fraud_alert",
        ),
    }

    # Reset PostgreSQL database state if available to ensure complete test hermeticity
    try:
        import os
        import psycopg2
        db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgrespassword@localhost:5433/banking_db")
        if "postgres:5432" in db_url:
            db_url = "postgresql://postgres:postgrespassword@localhost:5433/banking_db"
        conn = psycopg2.connect(db_url, connect_timeout=1)
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE accounts SET balance = 1450.50, credit_limit = 10000.00, fees_waived_this_quarter = 0, status = 'active' WHERE account_number = 'ACC-1001';
                UPDATE accounts SET balance = 320.00, credit_limit = 5000.00, fees_waived_this_quarter = 1, status = 'active' WHERE account_number = 'ACC-1002';
                UPDATE accounts SET balance = 5820.75, credit_limit = 15000.00, fees_waived_this_quarter = 2, status = 'suspended' WHERE account_number = 'ACC-1003';
                UPDATE accounts SET balance = 890.00, credit_limit = 7500.00, fees_waived_this_quarter = 0, status = 'fraud_alert' WHERE account_number = 'ACC-1004';
            """)
            conn.commit()
        conn.close()
    except Exception:
        pass
