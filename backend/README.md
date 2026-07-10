# ATS Backend

FastAPI backend for the Aegis Trading System.

---

## Quick Start (Local Development)

### 1. Create Python virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment

```powershell
Copy-Item .env.example .env
# Edit .env with your local values
```

### 4. Initialize Alembic (first time only)

```powershell
alembic upgrade head
```

### 5. Run the development server

```powershell
uvicorn app.main:app --reload
```

Backend will be available at:

- API: http://localhost:8000
- Health check: http://localhost:8000/health
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Run Tests

```powershell
pytest -v
```

---

## Project Structure

```
backend/
├── app/
│   ├── api/            REST endpoints and WebSocket
│   ├── core/           Configuration and logging
│   ├── database/       SQLAlchemy engine, session, base model
│   ├── execution/      Order management, broker interface
│   ├── indicators/     Technical indicator calculations
│   ├── market/         Market data, timeframe builder, sessions
│   ├── risk/           Position sizing, stop loss, risk limits
│   ├── services/       Application service layer
│   ├── strategy/       Trading decisions, confidence engine
│   ├── workers/        Background tasks
│   └── main.py         FastAPI entry point
├── alembic/            Database migrations
├── tests/              Test suite
├── .env                Local environment (gitignored)
├── .env.example        Environment template
└── requirements.txt    Python dependencies
```

---

## Architecture Rules

- Business logic lives in the backend only.
- Frontend never calculates indicators, bias, risk, or trading decisions.
- All higher timeframes are built from 1-minute candles.
- Every trading decision must be explainable and stored in decision_logs.
- Database access goes through repositories only.
