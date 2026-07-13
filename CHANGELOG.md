# Changelog

## v0.1.0 — Initial Development

- Project foundation and architecture
- Backend: FastAPI with PostgreSQL, SQLAlchemy, Alembic
- Frontend: React + Vite + Tailwind CSS scaffold
- Database: 15 tables, 18 enums with full migration support
- Market data ingestion from Capital.com provider
- Market intelligence pipeline (EMA, ATR, ADX, volume, swing, candle, donchian analyzers)
- Strategy library: EMA Trend Pullback, MTF Trend Alignment, Donchian Channel Breakout
- Strategy Ranking Engine with 40/30/30 weighting (historical/compatibility/setup)
- Risk Management Engine with position calculator, exposure validator, daily loss validator
- Execution Engine with Capital.com broker integration
- Emergency kill switch and trading readiness gate
- Decision Journal and analytics engine
- REST API and WebSocket real-time updates
- 244 passing tests
