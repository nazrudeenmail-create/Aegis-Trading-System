"""
Aegis Trading System — Application Entry Point

Responsibility:
    - Create and configure the FastAPI application instance.
    - Register all API routers.
    - Configure middleware (CORS).
    - Handle application startup and shutdown lifecycle.
    - Expose the health check endpoint at root level (for Docker health checks).

This file must not contain:
    - Trading logic
    - Database queries
    - Indicator calculations
    - Strategy decisions
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.api.router import api_router

# Initialize logging before anything else.
setup_logging()

logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI):
    """
    Application lifespan handler (modern FastAPI pattern).

    Replaces deprecated @app.on_event("startup") / @app.on_event("shutdown").

    Code before `yield` runs on startup.
    Code after `yield` runs on shutdown.

    Future phases will add:
        Startup:
            - Database connection pool verification (Phase 2)
            - Market data worker startup (Phase 3)
            - WebSocket manager initialization (Phase 9)
        Shutdown:
            - Graceful worker shutdown (Phase 3+)
            - Open position safety checks before shutdown (Phase 8)
    """
    # ── Startup ──────────────────────────────────────────────────────────
    logger.info(
        "ATS backend starting | env=%s | version=%s",
        settings.APP_ENV,
        settings.APP_VERSION,
    )

    yield  # Application runs here

    # ── Shutdown ─────────────────────────────────────────────────────────
    logger.info("ATS backend shutting down.")


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured application instance.
    """
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Professional rule-based algorithmic trading platform.",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS — allow frontend to communicate with backend.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register all API routes under /api/v1
    application.include_router(api_router)

    return application


app = create_application()


@app.get("/health", tags=["Health"])
async def health_root():
    """
    Root health check endpoint.

    Used by:
        - Docker HEALTHCHECK instruction
        - Kubernetes liveness probes
        - Load balancers

    Returns:
        dict: System status.
    """
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }
