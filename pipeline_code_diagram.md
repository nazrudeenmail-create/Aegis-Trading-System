# Aegis Trading System (ATS) - Codebase Pipeline Diagram

This diagram represents the exact, actual execution flow of ATS based on the Python codebase, tracing what happens from the moment market data is fetched to the moment an order is executed.

```mermaid
sequenceDiagram
    autonumber
    
    box rgb(20, 20, 30) Background Workers
    participant MDE as MarketDataEngine<br/>(market_data_engine.py)
    participant ORC as SystemOrchestrator<br/>(orchestrator.py)
    end
    
    box rgb(20, 30, 20) Data Layer
    participant CAP as CapitalComProvider<br/>(capital_com.py)
    participant SYNC as DataSynchronizer<br/>(synchronizer.py)
    participant DB as PostgreSQL DB<br/>(candles table)
    end
    
    box rgb(30, 20, 20) Intelligence Layer
    participant MTF as MultiTimeframeService<br/>(mtf_service.py)
    participant TFB as TimeframeBuilder<br/>(timeframe_builder.py)
    participant STR as StrategyEngine<br/>(ranking_engine.py)
    end
    
    box rgb(30, 30, 20) Execution Layer
    participant RE as RiskEngine<br/>(engine.py)
    participant EE as ExecutionEngine<br/>(engine.py)
    participant BM as BrokerManager<br/>(manager.py)
    participant EB as EventBus<br/>(events.py)
    end

    %% Market Data Polling Loop
    loop Every 60 Seconds
        MDE->>DB: query ACTIVE/WATCHLIST instruments
        MDE->>CAP: fetch_historical_candles(M1, limit=10)
        CAP-->>MDE: List[Candle]
        MDE->>SYNC: synchronize_candles(db, symbol, candles)
        SYNC->>DB: INSERT INTO candles ON CONFLICT DO NOTHING
        MDE->>EB: telemetry.record_stage("MarketData")
    end

    %% Orchestrator Evaluation Loop
    loop Every 60 Seconds
        ORC->>DB: query ACTIVE/WATCHLIST instruments
        
        %% Step 1 & 2
        ORC->>ORC: session_manager.is_market_open()
        ORC->>DB: _fetch_recent_candles(limit=1440)
        DB-->>ORC: List[Domain Candle]
        
        %% Step 3: Intelligence
        ORC->>MTF: build_context(base_1m_candles, [M1, M5, M15, H1, H4, D1])
        MTF->>TFB: aggregate(base_candles)
        TFB-->>MTF: Aggregated Timeframes
        MTF->>MTF: Calculate Indicators (EMA, ATR, ADX, Trend, Regime)
        MTF-->>ORC: MarketContext (snapshots)
        ORC->>EB: telemetry.record_stage("Indicators")
        
        %% Step 3.5: Strategy Evaluation
        loop For each Strategy (e.g. EMA Pullback)
            ORC->>STR: strategy.evaluate(strat_context)
            STR-->>ORC: StrategyResult & TradeCandidate
        end
        ORC->>EB: telemetry.record_stage("Strategy")
        
        %% Step 4: Ranking
        ORC->>STR: ranking_engine.rank(strategy_results)
        STR-->>ORC: RankingResult (selected_strategy)
        
        %% Step 5 & 6: Risk & Execution
        alt If strategy selected & trading enabled
            ORC->>BM: get_account_balance()
            BM-->>ORC: Account Balance
            ORC->>EE: execute(candidate, ranking_result, risk_profile)
            
            EE->>RE: evaluate(candidate, context, profile)
            Note over RE: Checks Historical Edge, Market Compatibility,<br/>Setup Quality, and Risk Constraints
            RE-->>EE: RiskAssessment (approved=True/False)
            
            alt If Risk Approved
                EE->>BM: active_broker.execute_order(order_req)
                BM-->>EE: OrderResult
                EE->>DB: Save to Journal (decisions & trades tables)
                EE->>EB: publish(ExecutionEvent)
                ORC->>EB: telemetry.record_stage("Execution", "SUCCESS")
            else If Risk Rejected
                EE->>DB: Save to Journal (decisions table only)
                ORC->>EB: telemetry.record_stage("Risk", "Rejected")
            end
        else If no strategy selected
            ORC->>EB: telemetry.heartbeat("Risk", "Ready")
            ORC->>EB: telemetry.heartbeat("Execution", "Idle")
        end
    end
```

## Codebase Pipeline Breakdown

### 1. Market Data Ingestion (`market_data_engine.py`)
This runs entirely decoupled from analysis in an `asyncio` task loop.
1. `_poll_all_instruments()` selects `ACTIVE` and `WATCHLIST` instruments from the database.
2. Calls `provider.fetch_historical_candles()` (using `CapitalComProvider`) to get the latest 10 1-minute candles.
3. Passes candles to `synchronizer.synchronize_candles()` which attempts to fill gaps and performs a bulk `INSERT INTO candles ... ON CONFLICT DO NOTHING`.
4. Emits a `MarketData` telemetry stage success event to the WebSocket.

### 2. The Orchestrator Loop (`orchestrator.py`)
This is the core trading loop (`_scan_all_instruments()`) that runs sequentially across all instruments.
1. **Fetch Data:** `_fetch_recent_candles()` pulls the last 1440 1-minute candles (24 hours) directly from the `candles` PostgreSQL table.
2. **Intelligence:** Passes the raw 1M candles to `MultiTimeframeService.build_context()`.
   * `TimeframeBuilder` loops over the target timeframes (M5, M15, H1, H4, D1) and aggregates the 1-minute data into higher timeframe candles.
   * Calculates technical indicators (EMA, ADX, ATR, MACD, etc) for *every* timeframe and bundles them into `MarketSnapshot` objects.
3. **Strategy:** Loops through all registered strategies in `StrategyRankingEngine.strategies` and calls `evaluate()`. Returns a `StrategyResult` which may contain a valid `TradeCandidate` (Signal).
4. **Ranking:** If multiple strategies trigger, `ranking_engine.rank()` applies a scoring matrix based on market regime and trends to pick a single winner.
5. **Risk Assessment:** The `winner_candidate` is passed to `ExecutionEngine.execute()`, which immediately calls `RiskEngine.evaluate()`. The Risk Engine performs hard math constraints (e.g. daily loss limits, setup quality score, position sizing).
6. **Execution:** If Risk passes, `ExecutionEngine` routes it to `BrokerManager`, triggering a live API call to Capital.com to open the position. Finally, the trade is saved to the `JournalService` (DB) and an event is broadcasted.
