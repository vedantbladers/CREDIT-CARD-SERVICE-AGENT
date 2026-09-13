from fastapi import APIRouter
from app.models.schemas import AccountInfo, AccountListResponse
from app.policy.repository import list_all_accounts

router = APIRouter()


@router.get("/accounts", response_model=AccountListResponse, tags=["Accounts"])
def get_accounts() -> AccountListResponse:
    """
    List all seeded mock core banking accounts and their policy profile attributes.
    """
    accounts = list_all_accounts()
    items = [
        AccountInfo(
            account_number=acc.account_number,
            name=acc.name,
            balance=acc.balance,
            credit_limit=acc.credit_limit,
            fees_waived_this_quarter=acc.fees_waived_this_quarter,
            tenure_months=acc.tenure_months,
            is_active=acc.is_active,
            status=acc.status,
        )
        for acc in accounts
    ]
    return AccountListResponse(accounts=items, count=len(items))
