import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()


class Settings(BaseModel):
    APP_TITLE: str = "Credit Card AI Agent Orchestrator"
    APP_DESCRIPTION: str = "Agentic AI platform orchestrator for credit card servicing (LangGraph State Graph)"
    APP_VERSION: str = "0.2.0"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "",
    )

    # --- Fireworks AI (Commented out) ---
    # FIREWORKS_API_KEY: Optional[str] = os.getenv("FIREWORKS_API_KEY")
    # FIREWORKS_MODEL: Optional[str] = os.getenv("FIREWORKS_MODEL")
    # FIREWORKS_BASE_URL: Optional[str] = os.getenv("FIREWORKS_BASE_URL")

    # OpenRouter AI Configuration
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL: Optional[str] = os.getenv("OPENROUTER_MODEL")
    OPENROUTER_BASE_URL: Optional[str] = os.getenv("OPENROUTER_BASE_URL")


settings = Settings()
