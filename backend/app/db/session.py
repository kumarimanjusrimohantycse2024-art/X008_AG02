from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.core.config import get_settings


def create_database_engine() -> Engine:
    settings = get_settings()
    return create_engine(settings.database_url, pool_pre_ping=True)


def get_engine() -> Engine:
    return create_database_engine()


def check_database_connection() -> bool:
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_db() -> Generator:
    engine = get_engine()
    with engine.connect() as connection:
        yield connection
