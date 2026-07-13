# Aegis Trading System (ATS) — Comprehensive Audit Report

**Date:** 2026-07-13  
**Auditor:** Buffy (Principal Software Architect / Trading Systems Auditor)  
**Repository:** nazrudeenmail-create/Aegis-Trading-System  

---

## Executive Summary

The Aegis Trading System is a sophisticated, well-architected algorithmic trading platform that has undergone **13+ phases of disciplined development** with **244 passing tests**. The architecture follows clean domain-driven design with clear separation of concerns. However, several **critical production-readiness gaps** need attention before demo/live trading can proceed safely.

**Overall Production Readiness: 62%**

The backend core engines, database schema, and execution safety features are strong. The primary gaps are in **state persistence**, **configuration management**, **frontend-backend integration**, and **real-data validation**.

---

## Scores

| Category | Score (0-10) | Notes |
|---|---|---|
| **Architecture** | 8.5 | Clean domain separation; minor duplication issues |
| **Backend Core** | 7.5 | Strong engines; sync/async mismatch hurts |
| **Frontend** | 5.0 | Good UI structure; broken API wiring; stale template |
| **Database** | 8.0 | Well-designed schema; minor enum mismatch |
| **Security** | 4.0 | Hardcoded secrets; no WebSocket auth; production defaults |
| **Testing** | 7.5 | 244 tests; missing integration tests; fragile fixtures |
| **Documentation** | 9.0 | Excellent (too much - some outdated) |
| **DevOps** | 5.0 | CI exists but incomplete; Docker Compose needs secrets |
| **Execution Safety** | 8.0 | Rate limiter, kill switch, readiness gate all good |
| **Production Readiness** | 6.2 | See below |

---

## Critical Issues (MUST FIX Before Demo Trading)

### C1. SYNTHETIC CANDLES IN PRODUCTION CODE
- **File:** `backend/app/workers/orchestrator.py:330-375`
- **Root Cause:** `_generate_synthetic_candles()` generates fake market data when DB is empty
- **Impact:** ATS will generate trading signals and potentially execute orders based on RANDOM data
- **Fix:** Remove synthetic candle generation. Raise a clear error/alert when no real data is available. The orchestrator should poll until real data arrives.

### C2. DUPLICATE MarketDataProvider INTERFACES
- **Files:** `backend/app/market/data_provider.py` (async ABC) vs `backend/app/market/provider_base.py` (sync ABC)
- **Root Cause:** Two abstract classes named `MarketDataProvider` with incompatible signatures
- **Impact:** Import confusion, impossible to type-check provider compatibility
- **Fix:** Delete `data_provider.py` (it's unused dead code). Keep `provider_base.py` as the single source of truth.

### C3. HMAC SECRET HARDCODED
- **Files:** `backend/app/api/auth.py:14` and `backend/scripts/seed_user.py:11`
- **Issue:** `_HMAC_SECRET = b"ats_internal_hmac_key"` is a hardcoded string, not a proper secret
- **Impact:** Any attacker who reads the source code can forge API tokens. All HMAC-based auth is effectively broken.
- **Fix:** Read HMAC secret from `settings.SECRET_KEY` or a dedicated env var.

### C4. `asyncio.run()` CALLED INSIDE RUNNING EVENT LOOP
- **File:** `backend/app/api/v1/dashboard.py:53`
- **Code:** `account_balance = float(asyncio.run(broker_manager.get_account_balance()))`
- **Impact:** Will raise `RuntimeError: asyncio.run() cannot be called from a running event loop` when the app is running under uvicorn
- **Fix:** Make the endpoint async and await the coroutine directly.

### C5. FRONTEND-BACKEND SETTINGS MISMATCH
- **Frontend:** `frontend/src/views/SettingsView.jsx:49` sends `{ global_trading_mode: selectedMode }`
- **Backend:** `backend/app/api/v1/system.py:87` expects `{ account_mode: str }`
- **Impact:** Settings changes silently fail. User thinks they switched modes but nothing happens.
- **Fix:** Align the field name on either side.

### C6. IN-MEMORY DECISION JOURNAL (NO PERSISTENCE)
- **File:** `backend/app/analytics/journal.py:24`
- **Issue:** `self.decisions: Dict[str, DecisionRecord]` is a plain Python dictionary
- **Impact:** All decision history is lost on server restart. The `/journal/latest` and `/journal/history` endpoints query the database `decision_logs` table, but the `DecisionJournal` (which powers the WebSocket broadcast and analytics) only holds data in memory.
- **Fix:** Implement database-backed decision persistence. At minimum, update `DecisionJournal` to write to the `decision_logs` table.

### C7. `lazy="selectin"` ON ALL RELATIONSHIPS (N+1 RISK)
- **Files:** ALL model files in `backend/app/database/models/`
- **Issue:** Every relationship uses `lazy="selectin"`, meaning loading an Instrument loads 7+ related tables
- **Impact:** Querying instruments list triggers 7+ additional SELECT queries. On a table with 100+ instruments, this is hundreds of queries.
- **Fix:** Use `lazy="selectin"` only where needed. Use `lazy="raise"` or explicit joins for production queries.

### C8. NO WEB SOCKET AUTHENTICATION
- **File:** `backend/app/api/v1/websocket.py:44-69`
- **Issue:** The `/ws` WebSocket endpoint accepts any connection without authentication
- **Impact:** Anyone can connect and receive all trading events, order fills, PnL data
- **Fix:** Implement token-based authentication at WebSocket connection time.

---

## High Issues (Fix Before Phase 13.5)

### H1. Frontend Hardcoded API Key
- **File:** `frontend/src/api.js:8`
- **Code:** `config.headers['X-API-Key'] = 'dev-secret-key';`
- **Fix:** Use env variable `VITE_API_KEY` and only apply if set.

### H2. Test API Key Mismatch
- **File:** `backend/tests/test_api/test_endpoints.py:13`
- **Issue:** Tests use `dummy_key` but `seed_user.py` generates `ats_dev_admin-secret-key` format
- **Impact:** API tests that require auth against a real DB will fail
- **Fix:** Generate a consistent test API key or mock auth properly.

### H3. Dashboard Endpoint Called Every 5 Seconds
- **File:** `frontend/src/views/ConnectionsView.jsx:13`
- **Issue:** `refreshInterval: 5000` fetches broker connection data every 5 seconds
- **Impact:** Excessive load on broker API. Rate limiter will throttle.
- **Fix:** Increase to 30-60 seconds for connection data.

### H4. Missing Migration for `backtest_runs` Table
- **File:** `backend/alembic/versions/001_initial_schema.py`
- **Issue:** The initial migration creates 15 tables but not `backtest_runs`. The `BacktestRun` model exists (`backend/app/database/models/backtest_run.py`) but may not have a migration to create it.
- **Fix:** Verify `backtest_runs` table exists in the database. Create migration if missing.

### H5. `app.backtest.persistence` Not Checked
- **File:** `backend/app/backtest/persistence.py` exists but wasn't reviewed for DB integration.
- **Issue:** Backtest results may not persist to database.

### H6. ACCOUNT_MODE enum includes LIVE but LIVE_TRADING_ENABLED defaults to False
- **File:** `backend/app/core/config.py`
- **Issue:** Switching to LIVE mode doesn't automatically require `SYSTEM_LIVE_TRADING_ENABLED=true`. The config validator doesn't check this.
- **Fix:** Add validation: if `ACCOUNT_MODE=live` and `SYSTEM_LIVE_TRADING_ENABLED=False`, fail with clear message.

### H7. CI Pipeline Missing Broker Credentials
- **File:** `.github/workflows/ci.yml`
- **Issue:** No `CAPITAL_COM_API_KEY` etc. in CI env. Integration tests against real broker will fail.
- **Fix:** Use GitHub Secrets for CI credentials or skip broker-dependent tests in CI.

### H8. Frontend ConnectionsView References Dead 'paper' Broker
- **File:** `frontend/src/views/ConnectionsView.jsx:33`
- **Code:** `const paper = connections?.find(c => c.id === 'paper');`
- **Fix:** Remove paper broker references (already deleted from backend).

### H9. `StrategyEngine.evaluate_all()` Duplicates Orchestrator Logic
- **File:** Both `backend/app/strategy/engine.py` and `backend/app/workers/orchestrator.py`
- **Issue:** Both files iterate over strategies and evaluate them. The `StrategyEngine` is effectively dead code since the `SystemOrchestrator` handles strategy evaluation internally.
- **Fix:** Either use `StrategyEngine` in the orchestrator or remove it.

### H10. `PlaceholderView.jsx` is Dead Code
- **File:** `frontend/src/views/PlaceholderView.jsx`
- **Issue:** Exists on disk but never imported in `App.jsx`
- **Fix:** Remove or integrate.

---

## Medium Issues

### M1. Old Vite Template CSS
- **File:** `frontend/src/App.css` — Full of unused `.counter`, `.hero`, `.base`, `.framework`, `.vite` styles from the default Vite template.
- **Fix:** Delete and use only Tailwind.

### M2. Stale Root Files
- **Files:** `=5.9.0` (root) and `ats_trading_state.json` (root)
- **Fix:** Delete stale artifacts.

### M3. Blank CHANGELOG.md
- **File:** `CHANGELOG.md` (empty)
- **Fix:** Populate or remove.

### M4. Wrong HTML Title
- **File:** `frontend/index.html:6` — `<title>frontend</title>`
- **Fix:** Change to `<title>Aegis Trading System</title>`.

### M5. Rate Limiter Bypass in Sync Provider
- **File:** `backend/app/market/providers/capital_com_provider.py:33`
- **Issue:** Uses `min_request_interval=0.5` instead of shared `CapitalRateLimiter`
- **Impact:** When both `CapitalComProvider` and `CapitalComBroker` make requests, they don't share a rate limiter, potentially exceeding API limits.
- **Fix:** Share the rate limiter instance across both classes.

### M6. Missing DB Index on `user.key_hash`
- **File:** `backend/app/database/models/user.py:22`
- **Issue:** `key_prefix` is indexed but `key_hash` is not. Login queries filter by key_prefix then compare key_hash.
- **Fix:** Minor performance concern. Index `key_hash` if sequential scans become an issue.

### M7. `CapitalComProvider` Synchronous with No Auth Retry in Key Places
- **File:** `backend/app/market/providers/capital_com_provider.py:106`
- **Issue:** Only retries auth on 401 for `fetch_historical_candles`. Other methods may fail silently.
- **Fix:** Add retry logic to all provider methods.

### M8. `MarketDataService` is Unused by Main Pipeline
- **File:** `backend/app/services/market_data_service.py`
- **Issue:** Only used in `POST /instruments/{id}/fetch-candles`. The main `MarketDataEngine` creates providers directly.
- **Fix:** Either use the service or remove it.

---

## Low Issues

### L1. Enums Slightly Inconsistent: `InstrumentStatus.ACTIVE` vs Migration `is_active`
- The migration creates `is_active` boolean, but the model now uses `status: InstrumentStatus`. The migration `ec1b29a333af` (instrument_status) was created to handle this, but verify it's been applied.

### L2. `AccountMode` Enum Has No `BACKTEST`
- `config.py::AccountMode` only has `DEMO` and `LIVE` but `database/enums.py::AccountType` has `BACKTEST`, `DEMO`, `LIVE`. The config-level enum should include `BACKTEST` for consistency with the account mode concept.

### L3. Missing `__init__.py` in Test Subdirectories
- Some test subdirectories have `__init__.py` but, e.g., `test_analytics/__init__.py` exists but may be empty.

### L4. Demo Scripts Have Outdated Imports
- `backend/scripts/ats.py:43` imports from `demo_analytics` which may have been refactored.

---

## Dead Code Inventory

| File | Reason |
|---|---|
| `backend/app/market/data_provider.py` | Superseded by `provider_base.py` |
| `backend/app/market/provider_factory.py` | Deprecated wrapper (redirects to BrokerFactory) |
| `backend/app/strategy/engine.py` | Logic duplicated in `SystemOrchestrator` |
| `frontend/src/views/PlaceholderView.jsx` | Never imported |
| `backend/app/App.css` | Old Vite template styles, unused |
| `=5.9.0` (root) | Stale artifact |
| `ats_trading_state.json` (root) | Stale artifact (verify) |
| `backend/manual_test.py` | Manual testing script (verify if still needed) |

---

## Missing Features / APIs

### Frontend Views Missing Backend Wiring
| View | API Called | Status |
|---|---|---|
| DashboardOverview | `/dashboard/summary` | ✅ Working (but async bug in backend) |
| MarketAnalysisView | `/market/current`, `/market/candles`, `/instruments/` | ✅ Working |
| InstrumentsView | `/instruments/`, `/instruments/market-sessions`, `/market/broker/search` | ✅ Working |
| StrategiesView | `/strategy/ranking`, `/strategy/profiles`, `/strategy/{name}/profile` | ✅ Working |
| JournalView | `/journal/latest` | ✅ Working (but data is in-memory only) |
| ConnectionsView | `/broker/connections`, `/system/status` | ⚠️ Paper references dead |
| PortfolioView | `/dashboard/summary`, `/broker/positions/open` | ⚠️ Working but may have data issues |
| OrdersView | `/system/status`, `/broker/orders/recent` | ⚠️ No DB orders integration |
| RiskView | `/risk/profile` | ✅ Working |
| PipelineMonitor | `/pipeline/status`, `/instruments/` | ⚠️ Mostly placeholder data |
| SettingsView | `/system/status`, `PATCH /system/settings` | ❌ Field name mismatch |
| SystemView | `/system/status` | ✅ Working |

### Missing Backend Endpoints
- No endpoint to update `RiskProfile` at runtime (only GET)
- No endpoint to trigger emergency kill switch
- No endpoint to manually close positions

---

## Database Issues

### Schema Drift Check
- **Migration `001_initial_schema`** creates 18 ENUMs and 15 tables with `is_active` on instruments
- **Migration `ec1b29a333af`** adds `instrument_status`, `market_type`, `execution_mode`, `trading_enabled`, `live_trading_enabled`, `allow_new_positions`, `instrument_groups`, and `instrument_group_association`
- **Current model** (`Instrument`) uses `status`, `market_type`, `execution_mode`, etc. — matches the latest migration
- **`BacktestRun` table** — verify migration exists
- **Timeframe enum** — migration `b2c3d4e5f6a7` adds `D1` value — verify applied

### Enum Mismatches Between Python and DB
- Python `enums.py::InstrumentStatus` includes `WATCHLIST`, `PAUSED`, `DISABLED` — verify these are in DB

---

## Security Audit

| Issue | Severity | Status |
|---|---|---|
| HMAC secret hardcoded | **Critical** | Unfixed |
| WebSocket no auth | **Critical** | Unfixed |
| SECRET_KEY weak default | **High** | Needs env override |
| CAPITAL_COM credentials from .env only | **High** | No production secrets management |
| No HTTPS enforcement | **Medium** | All traffic plaintext in Docker |
| No rate limiting on API endpoints | **Medium** | Only broker calls are rate-limited |
| Plaintext API key in localStorage (frontend) | **Medium** | Not implemented yet, but planned pattern |
| Frontend hardcodes API key | **High** | Unfixed |

---

## Top 20 Priority Fixes

| Rank | Issue ID | Severity | Area | Fix |
|---|---|---|---|---|
| 1 | C1 | Critical | Trading | Remove synthetic candles from orchestrator |
| 2 | C3 | Critical | Security | Read HMAC secret from env var |
| 3 | C4 | Critical | Backend | Fix `asyncio.run()` in dashboard endpoint |
| 4 | C6 | Critical | Journaling | Persist DecisionJournal to database |
| 5 | C2 | Critical | Architecture | Remove duplicate MarketDataProvider |
| 6 | C8 | Critical | Security | Add WebSocket authentication |
| 7 | C5 | High | Integration | Fix settings field name mismatch |
| 8 | H1 | High | Security | Remove hardcoded frontend API key |
| 9 | H2 | High | Testing | Fix test API key consistency |
| 10 | H4 | High | Database | Verify backtest_runs migration exists |
| 11 | H6 | High | Safety | Add LIVE validation to config checker |
| 12 | C7 | High | Performance | Fix N+1 relationship loading |
| 13 | H3 | Medium | Performance | Reduce dashboard polling frequency |
| 14 | M5 | Medium | Stability | Share rate limiter across provider/broker |
| 15 | H10 | Low | Code Quality | Remove dead PlaceholderView |
| 16 | M4 | Low | UX | Fix HTML title |
| 17 | M2 | Low | Housekeeping | Remove stale root files |
| 18 | H9 | Medium | Architecture | Remove StrategyEngine dead code |
| 19 | H8 | Medium | Frontend | Remove paper broker references |
| 20 | M3 | Low | Documentation | Fix empty CHANGELOG.md |

---

## Suggested Implementation Order

### Sprint 1 — Safety & Security (Week 1)
1. Remove synthetic candles (C1)
2. Fix HMAC secret (C3)
3. Fix `asyncio.run()` call (C4)
4. Remove hardcoded frontend API key (H1)
5. Add WebSocket auth (C8)

### Sprint 2 — Data Integrity (Week 2)
6. Remove duplicate MarketDataProvider (C2)
7. Add LIVE mode validation (H6)
8. Persist DecisionJournal (C6)
9. Verify backtest_runs migration (H4)

### Sprint 3 — Integration (Week 3)
10. Fix settings field name mismatch (C5)
11. Fix frontend API key consistency (H2)
12. Remove paper broker references (H8)
13. Share rate limiter (M5)

### Sprint 4 — Performance & Polish (Week 4)
14. Fix N+1 relationship loading (C7)
15. Reduce dashboard polling (H3)
16. Remove dead code (H9, H10)
17. Fix HTML title, CHANGELOG.md (M4, M3)
18. Clean up stale files (M2)

---

## Conclusion

The Aegis Trading System is **architecturally sound** with clean separation of concerns, well-designed database schema, thorough test coverage (244 tests), and robust execution safety features (rate limiter, kill switch, readiness gate). The documentation is exemplary.

However, **production readiness is at approximately 62%**. The 8 critical issues (especially synthetic data, hardcoded secrets, in-memory journaling, and the async bug) must be resolved before connecting to any live broker or allowing unsupervised demo trading.

The frontend-backend integration has **several mismatches** that would cause silent failures in production. The frontend UI is well-designed but many views show placeholder data or error states because the backend endpoints return incomplete responses.

With 3-4 weeks of focused fixes (in the order suggested above), this system can reach **~90% production readiness** and proceed safely to Phase 13.5 (Capital.com Demo E2E).
