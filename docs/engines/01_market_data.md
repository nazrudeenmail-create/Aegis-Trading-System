# Phase 3 — Market Data System Architecture

Status: APPROVED  
Implementation: READY

## 1. Goal Description

The Market Data System serves as the foundational data pipeline for the entire Aegis Trading System (ATS). It is responsible for:
1. Ingesting market data from **Capital.com**.
2. Validating, parsing, and storing raw **1-minute (1M) candles** into the PostgreSQL database.
3. Automatically building higher timeframes (`5M`, `15M`, `1H`, `4H`) in-memory using the 1M data, preventing database bloat and ensuring mathematical consistency.
4. Using robust abstractions (Domain Models, Validators, Caches, Gap Detectors, Repositories, and Quality Reports) to prevent broker API logic from leaking into our core engine and to ensure data integrity.

## 2. Market Data Flow

```text
             Capital.com API
                    |
                    |
                    v
          Capital.com Provider
                    |
                    |
                    v
             Candle Parser
                    |
                    |
                    v
            Candle Validator
                    |
                    |
                    v
          Data Ingestion Service
                    |
                    |
                    v
          Candle Repository
                    |
                    |
                    v
              PostgreSQL
              (1M candles only)


                    |
                    |
                    v

            Timeframe Builder

        +-----------+-----------+
        |           |           |
        v           v           v

       5M          15M          1H          4H


                    |
                    |
                    v

             Candle Cache

                    |
                    |
                    v

            Strategy Engine
```

## 3. Directory Structure

```text
backend/app/
├── market/
│   ├── domain/
│   │   ├── candle.py
│   │   ├── timeframe.py
│   │   └── instrument.py
│   ├── providers/
│   │   └── capital_com_provider.py
│   ├── validators/
│   │   └── candle_validator.py
│   ├── cache/
│   │   └── candle_cache.py
│   ├── calendar/
│   │   └── market_calendar.py
│   ├── provider_base.py
│   ├── provider_factory.py
│   ├── timeframe_builder.py
│   ├── gap_detector.py
│   ├── quality_report.py
│   └── exceptions.py
├── services/
│   └── data_ingestion_service.py
└── database/
    └── repositories/
        └── candle_repository.py
```

## 4. Architecture Standards

### Domain Models
Domain models isolate the ATS from broker API payloads. For example, `Candle` objects will include properties like `source` and `created_at` for strict data lineage.

### Repository Pattern
The `CandleRepository` acts as the explicit barrier between the application logic and the database. The Service Layer uses domain objects, and the Repository handles translating to/from SQLAlchemy models.
```python
class CandleRepository:
    def save_many(self, candles: list[Candle]) -> None:
        pass

    def get_latest(self, instrument: str, limit: int) -> list[Candle]:
        pass
```

### Error Handling Strategy
Defined in `market/exceptions.py`. Trading systems must fail safely.
- `MarketDataError`
- `AuthenticationError`
- `ProviderConnectionError`
- `InvalidCandleError`
- `DuplicateCandleError`
- `MissingDataError`

## 5. Completion Criteria

Before Phase 3 is considered complete, it must satisfy:
- **Data Provider:** Authenticate successfully, download historical candles, and convert payloads to ATS Domain objects.
- **Database:** Only 1M candles stored, no duplicate timestamps, and repository abstraction fully functioning.
- **Data Quality:** No invalid OHLC candles, gap detection working, and Quality Report passes.
- **Timeframes:** 60 x 1M candles must accurately aggregate into 1 x 1H candle.
