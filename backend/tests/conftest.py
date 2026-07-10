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

import pytest
from fastapi.testclient import TestClient

from app.main import app


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
