"""
Aegis Trading System — Health Endpoint Tests

Tests:
    - Root health check (/health) — used by Docker health checks
    - API health check (/api/v1/health) — used by frontend and monitoring

These are the first automated tests in the project.
They verify the application starts correctly and responds to health checks.
"""


class TestRootHealth:
    """Tests for the root /health endpoint."""

    def test_health_returns_200(self, client):
        """Root health check must return HTTP 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_ok_status(self, client):
        """Root health check must return status: ok."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_returns_service_name(self, client):
        """Root health check must include the service name."""
        response = client.get("/health")
        data = response.json()
        assert "service" in data
        assert len(data["service"]) > 0

    def test_health_returns_version(self, client):
        """Root health check must include the application version."""
        response = client.get("/health")
        data = response.json()
        assert "version" in data

    def test_health_returns_environment(self, client):
        """Root health check must include the environment."""
        response = client.get("/health")
        data = response.json()
        assert "environment" in data


class TestApiHealth:
    """Tests for the versioned /api/v1/health endpoint."""

    def test_api_health_returns_200(self, client):
        """API health check must return HTTP 200."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_api_health_returns_ok_status(self, client):
        """API health check must return status: ok."""
        response = client.get("/api/v1/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_api_health_returns_service_name(self, client):
        """API health check must include the service name."""
        response = client.get("/api/v1/health")
        data = response.json()
        assert "service" in data

    def test_api_health_returns_version(self, client):
        """API health check must include the version."""
        response = client.get("/api/v1/health")
        data = response.json()
        assert "version" in data

    def test_api_health_returns_environment(self, client):
        """API health check must include the environment."""
        response = client.get("/api/v1/health")
        data = response.json()
        assert "environment" in data

    def test_api_health_json_content_type(self, client):
        """API health check must return JSON content type."""
        response = client.get("/api/v1/health")
        assert "application/json" in response.headers["content-type"]

    def test_both_health_endpoints_agree(self, client):
        """Both health endpoints must return the same status."""
        root_response = client.get("/health")
        api_response = client.get("/api/v1/health")
        assert root_response.json()["status"] == api_response.json()["status"]
