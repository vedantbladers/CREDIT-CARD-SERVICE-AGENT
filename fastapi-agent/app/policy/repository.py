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
    Returns None if the account is not found.
    """
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
