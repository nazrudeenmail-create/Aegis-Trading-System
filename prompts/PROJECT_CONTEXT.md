# PROJECT CONTEXT

Version: 1.0
Status: Active Development
Last Updated: 2026-07-09

---

# Project Name

Aegis Trading System (ATS)

---

# Project Goal

Build a professional Quantitative Research Platform capable of objectively evaluating, backtesting, ranking, and executing multiple algorithmic trading strategies in real time.

The focus is not maximum profit.

The focus is making high-quality trading decisions while protecting trading capital.

Project philosophy:

Accuracy > Speed > Profit

---

# Current Tech Stack

Backend

- Python
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL

Frontend

- React
- JavaScript
- Vite
- Tailwind CSS
- Axios
- WebSocket

Infrastructure

- Git
- GitHub
- Docker
- Oracle Cloud (Future)

---

# Quantitative Research Pipeline

The system evaluates the market through a 5-layer pipeline:

1. **Market Intelligence Layer:** Extracts 165+ objective mathematical analyzers (EMA, MACD, ATR, FVG, etc.) from raw candle data.
2. **Strategy Library:** Houses a catalog of objective, testable trading strategies (e.g., EMA Pullback, MACD Cross, London Breakout).
3. **Backtesting Engine:** Simulates the performance of every strategy against years of historical OHLCV data.
4. **Strategy Ranking Engine:** Dynamically scores and selects the most effective strategy for the current market condition.
5. **Execution Engine:** Validates the signal against the Risk Engine and communicates with broker APIs for execution.

# Development Rules

1. Backend owns all business logic.

2. Frontend only displays data.

3. Never calculate indicators in React.

4. Never skip development phases.

5. Documentation is updated before major implementation.

6. Production-ready code only.

7. Simple English.

8. One responsibility per module.

---

# Folder Structure

Aegis-Trading-System/

backend/

frontend/

docs/

prompts/

scripts/

docker/

.github/

---

# Documentation

Completed

- README.md
- 00_Project_Vision.md
- 01_Tech_Stack.md

In Progress

- 02_System_Architecture.md

---

# Current Phase

Phase 0

Project Foundation

Completed

- Git initialized
- GitHub repository created
- Project structure created
- Vision document
- Technology stack document
- README

Next Step

Complete System Architecture document.

No backend code has been written.

No frontend code has been written.

---

# Important Project Principles

Every architecture decision must prioritize:

Maintainability

Scalability

Reliability

Transparency

Capital preservation

The project should be understandable even after several months without development.

---

# Important Decisions

- React uses JavaScript instead of TypeScript.
- PostgreSQL is the production database.
- All higher timeframes are built from 1-minute candles.
- Frontend never calculates indicators.
- Trading logic exists only in the backend.
- Architecture is documented before implementation.
- Market session management will control exchange hours, extended hours, holidays, and execution availability.

---

END OF DOCUMENT