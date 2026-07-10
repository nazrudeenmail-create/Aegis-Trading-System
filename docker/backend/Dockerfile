# Aegis Trading System — Backend Dockerfile
#
# Base: python:3.12-slim (minimal footprint)
# Mode: Development (--reload for hot-reload)
#
# Production notes (Phase 12):
#   - Remove --reload flag
#   - Add --workers flag for multi-process
#   - Use gunicorn as process manager

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies required by psycopg3
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Run with hot-reload for development
# --host 0.0.0.0 makes the server accessible from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
