from collections.abc import Generator

import pytest
from sqlalchemy.orm import Session

from app.db.session import get_engine


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    connection = get_engine().connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()
