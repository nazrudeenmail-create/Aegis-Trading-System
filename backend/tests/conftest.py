"""
Aegis Trading System — Pytest Configuration and Shared Fixtures

Fixtures defined here are automatically available in all test files
without needing to import them.

Current fixtures:
    client — FastAPI TestClient for testing API endpoints

Adding new fixtures (Phase 2+):
    - db_session: Test database session with automatic rollback
    - test_candles: Sample market data for indicator tests
    - mock_broker: Paper broker for execution tests
"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.main import app
from app.core.config import get_settings


@pytest.fixture(scope="module")
def client() -> TestClient:
    """
    FastAPI TestClient.

    Provides an HTTP client for testing API endpoints without
    starting a real server. Scope is 'module' — one client
    instance is shared across all tests in a test file.

    Usage:
        def test_something(client):
            response = client.get("/health")
            assert response.status_code == 200

    Yields:
        TestClient: Configured test client for the ATS application.
    """
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Provide a database session that rolls back after each test.
    This means every test starts with a clean slate and leaves none
    of its data behind. No tear-down scripts, no database resets.
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
