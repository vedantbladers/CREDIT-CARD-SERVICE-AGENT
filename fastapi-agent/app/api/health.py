from datetime import datetime, timezone
from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "fastapi-agent",
        "architecture": "modular",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
