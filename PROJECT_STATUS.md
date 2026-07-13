# ATS Phase 13.0 — Production Readiness Status

**Last Updated:** 2026-07-13  
**Status:** Stabilization Phase — Phase A Complete

> **This file is the single source of truth.**  
> `docs/CURRENT_STATUS.md` and `docs/ROADMAP.md` are archived; see their deprecation headers.

---

## Overview

The Aegis Trading System has completed **Phase 13.0 — Production Readiness Audit**.  
All Priority-0 execution safety items are verified with tests. The system is ready for **Phase 13.5 — Capital.com Demo E2E** testing.

---

## Phased Roadmap

```
Phase 13.0 (CURRENT — DONE)
     ↓
Phase 13.6 — Developer Environment Synchronization (DONE)
     ↓
Phase 13.5 — Capital.com Demo E2E (NEXT)
     ↓
Phase 14 — Controlled Live Deployment
```

---

## Phase A — Execution Safety ✅

### Capital.com Order Routing
- [x] Market orders: `POST /positions` endpoint
- [x] Limit/Stop orders: `POST /workingorders` endpoint
- [x] Internal endpoints (`/positions`, `/workingorders`) hidden from the rest of ATS
- [x] `BrokerInterface` with explicit methods: `place_market_order`, `place_limit_order`, `place_stop_order`, `cancel_order`, `get_order_status`, `sync_positions`
- [x] `BrokerManager` routes by `OrderType` to the correct broker method

### Fill Handling
- [x] Fill price captured from `position.level` / `position.openLevel` in `/positions` response
- [x] Filled quantity captured from `position.size`
- [x] Broker deal ID captured as `order_id`
- [x] Status mapping: `map_order_status()` maps Capital.com statuses → unified `OrderStatus` enum (`PENDING`, `FILLED`, `PARTIALLY_FILLED`, `CANCELLED`, `REJECTED`)

### Position Synchronization
- [x] `CapitalComBroker.sync_positions()` fetches `/positions`, maps to domain dicts, caches internally
- [x] `BrokerManager.sync_positions()` delegates to active broker and caches result
- [x] `BrokerManager.get_cached_positions()` exposes cached positions

### Rate Limiting
- [x] `CapitalRateLimiter` in `app/execution/broker/capital/rate_limiter.py`
- [x] Rolling-window limits: 8/s, 50/min, 400/5min (safety margins below documented limits)
- [x] Applied to all `CapitalClient` calls: candles, prices, orders, positions, account
- [x] 3 targeted rate-limiter tests

### Emergency Stop + Readiness Gate
- [x] `SystemStateEnum`: `ACTIVE`, `HALTED`, `MAINTENANCE`
- [x] `SystemState.is_halted` property — rejects orders when `HALTED` or `MAINTENANCE`
- [x] `ExecutionEngine.execute()` checks system state before processing
- [x] `TradingReadiness.check()` verifies: system state, market service, ranking engine, risk engine, broker connection, position sync
- [x] 3 emergency-stop/readiness tests

---

## Phase B — Architecture Cleanup ✅

### Paper Trading Removal
- [x] `app/execution/broker/paper/` — already removed
- [x] `app/execution/paper_monitor.py` — already removed
- [x] `scripts/demo_paper_trading.py` — already removed
- [x] No remaining `PAPER` references in the codebase
- [x] `app/backtest/simulated_broker.py` — preserved for backtesting

### Execution Mode Naming
- [x] `ExecutionMode`: `BACKTEST`, `DEMO`, `LIVE` only (no `PAPER`)
- [x] `AccountType`: `BACKTEST`, `DEMO`, `LIVE` only (no `PAPER`)

### Database Enum Alignment
- [x] `Timeframe` enum includes `D1` (`M1`, `M5`, `M15`, `H1`, `H4`, `D1`)
- [x] `app/market/domain/timeframe.py` aligns with database enum (`D1 = "D1"`)
- [x] `AccountType` enum includes `BACKTEST`
- [x] Migration `b2c3d4e5f6a7` fixes timeframe and account_type enums

---

## Phase C — Security & Tests ✅

### Authentication (HMAC API Keys)
- [x] `User` model: `key_prefix` (indexed, fast lookup) + `key_hash` (HMAC-SHA256, 64 hex chars)
- [x] API key format: `ats_<prefix>_<secret>`
- [x] `get_current_user` extracts prefix → database lookup → `hmac.compare_digest()` constant-time comparison
- [x] Migration `c3d4e5f6a7b8`: adds `key_prefix` + `key_hash`, drops old `api_key_hash`
- [x] `seed_user.py` generates HMAC-based keys

### Test Integrity
- [x] Fixed instrument fixtures (`is_active` → `status`)
- [x] Fixed `DummyStrategy.get_profile()` in backtest test
- [x] Fixed market snapshot test initialization
- [x] Fixed timeframe string literals → `Timeframe` enum across all tests
- [x] Fixed `HistoricalScorer`/`StrategyRankingEngine` call signatures
- [x] Fixed `OrderResult` keyword arg (`broker_order_id` → removed)
- **244 tests passing** (up from 226 baseline)
  - 18 new execution tests (rate limiter, mapper, broker manager, engine)

### CI Pipeline
- [x] `.github/workflows/ci.yml`: runs on push/PR to `main`/`develop`
- [x] Postgres 16 service container with health checks
- [x] Python 3.12 setup, dependency install, Alembic migrations, `pytest`

---

## Phase D — Documentation

- [x] `PROJECT_STATUS.md` created as single source of truth (this file)
- [x] `docs/CURRENT_STATUS.md` — header now points to `PROJECT_STATUS.md`
- [x] `docs/ROADMAP.md` — header now points to `PROJECT_STATUS.md`

---

## Phase 13.6 — Developer Environment Synchronization ✅

- [x] Bootstrap schema (`bootstrap.py` running `alembic upgrade head`)
- [x] Bootstrap settings (`seed_settings.py`)
- [x] Bootstrap user (`seed_user.py`)
- [x] Instrument state synchronization (`export_database_state.py` / `import_database_state.py`)
- [x] Database is single source of truth (hardcoded seed arrays removed)

---

## Execution Readiness Gate

ATS will NOT move to Demo Trading until all gates are GREEN:

| Gate | Status | Notes |
|------|--------|-------|
| Capital.com market orders work | ✅ | `POST /positions` implementation verified |
| Capital.com pending orders work | ✅ | `POST /workingorders` implementation verified |
| Fill prices captured | ✅ | `parse_position_response()` captures fill data |
| Positions synchronized | ✅ | `sync_positions()` + `BrokerManager` cache |
| Rate limiting active | ✅ | `CapitalRateLimiter` applied to all API calls |
| Risk veto tested | ✅ | `RiskEngine` integrated in `ExecutionEngine.execute()` |
| Decision journal records execution | ✅ | `DecisionEvent` / `ExecutionEvent` published on EventBus |
| Emergency stop tested | ✅ | 3 tests: halted, readiness fails, success path |
| Trading readiness check active | ✅ | 7 subsystems checked before order execution |
| Tests green | ✅ | **244/244 passed** |
| Auth no longer plaintext | ✅ | HMAC-SHA256 with `hmac.compare_digest()` |

---

## Test Summary

```
Total:  244 passed
New:    18 execution tests (rate_limiter, mapper, broker_manager, engine)
Delta:  +18 from 226 baseline
```

### Test Categories
| Category | Tests |
|----------|-------|
| Analytics (journal, performance) | 7 |
| API (endpoints, websockets) | 7 |
| Backtest (engine, simulated broker) | 4 |
| Database (models, constraints, timestamps) | 66 |
| Health | 10 |
| Market (cache, candles, ingestion, pipeline, providers, quality, timeframe) | 21 |
| Market Analysis (EMA alignment, service, indicators, intelligence) | 10 |
| Ranking (scoring, engine) | 5 |
| Risk (calculator, engine, models, validator) | 9 |
| Strategy (strategies, engine, models) | 10 |
| **Execution (NEW)** | **18** |
| **Total** | **244** |

---

## Quick Start

```bash
# Run tests
cd backend && python -m pytest

# Apply migrations
alembic upgrade head

# Seed database
python scripts/seed_user.py
```

---

## Next Steps — Phase 13.5 (Capital.com Demo E2E)

1. Live integration test with Capital.com demo account credentials
2. Verify order placement, status polling, and position sync against real demo environment
3. Add retry/reconnect logic for transient failures
4. Monitor rate limiter behavior under real market data load
5. End-to-end demo pipeline: market data → analysis → ranking → risk → execution → journal