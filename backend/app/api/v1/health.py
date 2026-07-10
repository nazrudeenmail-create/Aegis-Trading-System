"""
Aegis Trading System — Health Check Endpoint

Responsibility:
    - Respond to health check requests from frontend and monitoring tools.
    - Expose system status, version, and environment.

Endpoint:
    GET /api/v1/health

Used by:
    - Frontend: verify backend is reachable on startup
    - External monitoring tools
    - CI/CD pipelines

Note:
    The root /health endpoint (for Docker/Kubernetes) is defined in main.py.
    This versioned endpoint is for API clients.
"""

import logging

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()

settings = get_settings()


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str
    service: str
    version: str
    environment: str


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="API health check",
    description="Returns system status. Used by frontend and monitoring tools.",
)
async def health_check() -> HealthResponse:
    """
    API health check endpoint.

    Returns:
        HealthResponse: Current system status.
    """
    logger.debug("Health check requested.")

    return HealthResponse(
        status="ok",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
    )
