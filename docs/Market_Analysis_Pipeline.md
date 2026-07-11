# Market Analysis Pipeline

The Market Intelligence Layer strictly separates raw indicator calculation (Tier 1) from business interpretation (Tier 2). Because Tier 2 analyzers consume the output of Tier 1, and some Tier 2 analyzers consume the output of other Tier 2 analyzers, **execution order is strictly enforced**.

## Pipeline Execution Order

### Phase A: Tier 1 (Indicator Engine)
Tier 1 analyzers consume raw `List[Candle]` objects and return raw mathematical facts. They can be executed concurrently.

- `EMAAnalyzer`
- `ATRAnalyzer`
- `ADXAnalyzer`
- `VolumeAnalyzer`
- `SwingAnalyzer`
- `CandleAnalyzer`

*Output: A partially populated `MarketSnapshot` with Tier 1 facts.*

### Phase B: Tier 2 (Intelligence Engine)
Tier 2 analyzers consume the `MarketSnapshot` and return Enums representing subjective intelligence. They MUST be executed in the following strict sequential order:

1. **`TrendAnalyzer`**
   - **Depends on:** `EMAAnalysis`, `ADXAnalysis`
   - **Populates:** `snapshot.trend`
   
2. **`VolatilityAnalyzer`**
   - **Depends on:** `ATRAnalysis`
   - **Populates:** `snapshot.volatility`
   
3. **`MarketRegimeAnalyzer`**
   - **Depends on:** `TrendAnalysis`, `VolatilityAnalysis`
   - **Populates:** `snapshot.regime`
   
4. **`PullbackAnalyzer`**
   - **Depends on:** `TrendAnalysis`, `EMAAnalysis`, `ATRAnalysis`
   - **Populates:** `snapshot.pullback`
   
5. **`MomentumAnalyzer`**
   - **Depends on:** (Future: RSI / MACD)
   - **Populates:** `snapshot.momentum`

## Service Orchestration

The `MarketAnalysisService` (Step 4) is responsible for:
1. Validating incoming `List[Candle]`.
2. Orchestrating Phase A.
3. Orchestrating Phase B sequentially.
4. Returning the final aggregated `MarketSnapshot` to the Strategy Engine.
