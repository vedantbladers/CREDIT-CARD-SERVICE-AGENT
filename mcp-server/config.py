import os
from pydantic import BaseModel


class Settings(BaseModel):
    HOST: str = os.getenv("MCP_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("MCP_PORT", "8001"))
    # In docker network: postgres:5432; on host: localhost:5433
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgrespassword@localhost:5433/banking_db",
    )
    SERVER_NAME: str = "credit-card-mcp-server"
    SERVER_VERSION: str = "1.0.0"


settings = Settings()
