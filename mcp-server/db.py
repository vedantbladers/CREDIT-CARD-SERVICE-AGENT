import logging
from contextlib import contextmanager
from typing import Generator
import psycopg2
from psycopg2.extras import RealDictCursor
from config import settings

logger = logging.getLogger("mcp.db")


@contextmanager
def get_db_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """
    Yields a PostgreSQL connection with transactional management.
    Ensures ACID compliance: commits on normal return, rolls back on exception.
    """
    conn = None
    try:
        conn = psycopg2.connect(settings.DATABASE_URL, cursor_factory=RealDictCursor)
        conn.autocommit = False  # Explicit ACID transaction control
        yield conn
        conn.commit()
    except Exception as e:
        if conn is not None:
            conn.rollback()
            logger.error(f"Transaction rolled back due to error: {e}")
        raise
    finally:
        if conn is not None:
            conn.close()
