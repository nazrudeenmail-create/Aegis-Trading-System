"""
Database Test Fixtures — Transaction-per-test rollback pattern

Every test gets a fresh database session wrapped in a transaction.
The transaction is rolled back after each test, so no data is ever
committed to the database. This keeps tests isolated and repeatable.

Requires:
    - PostgreSQL running with the ATS schema applied
    - DATABASE_URL set in backend/.env (same as the application uses)

Usage:
    def test_something(db_session):
        instrument = Instrument(symbol="TEST", name="Test", ...)
        db_session.add(instrument)
        db_session.flush()
        # ... assert ...
        # Transaction rolls back automatically — no cleanup needed
"""
from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Provide a database session that rolls back after each test.

    Pattern:
        1. Create engine from the application DATABASE_URL
        2. Open a connection
        3. Begin a transaction
        4. Create a session bound to that connection
        5. Yield the session to the test
        6. Roll back the transaction (discard all test data)
        7. Close the connection

    This means every test starts with a clean slate and leaves none
    of its data behind. No tear-down scripts, no database resets.

    Yields:
        Session: Active SQLAlchemy session for test use.
    """
    settings = get_settings()

    engine = create_engine(settings.DATABASE_URL)
    connection = engine.connect()
    transaction = connection.begin()

    TestSession = sessionmaker(bind=connection)
    session = TestSession()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        engine.dispose()
