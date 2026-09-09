import os
from typing import Optional
from pydantic import BaseModel


class Settings(BaseModel):
    APP_TITLE: str = "Credit Card AI Agent Orchestrator"
    APP_DESCRIPTION: str = "Agentic AI platform orchestrator for credit card servicing (LangGraph State Graph)"
    APP_VERSION: str = "0.2.0"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgrespassword@postgres:5432/banking_db",
    )

    # LLM Settings - Exclusively Fireworks AI (DeepSeek)
    FIREWORKS_API_KEY: Optional[str] = os.getenv("FIREWORKS_API_KEY", "fw_BcMQKedtvL563MWiPqdvka")
    FIREWORKS_MODEL: str = os.getenv(
        "FIREWORKS_MODEL", "accounts/fireworks/models/deepseek-v4-flash-0731"
    )
    FIREWORKS_BASE_URL: str = os.getenv(
        "FIREWORKS_BASE_URL", "https://api.fireworks.ai/inference/v1"
    )


settings = Settings()
