# 10 - Strategy Catalog

Version: 1.0

---

# Purpose
This document serves as the research roadmap for the Strategy Library (Phase 5). It defines the 14 objective, mathematical strategies that will be backtested and ranked in V1 of the Aegis Trading System.

Each strategy is a **Research Candidate**. Their inclusion here does not guarantee profitability; it guarantees that they are testable.

## Status Key
* `✅` - Backtested & Validated
* `⏳` - In Progress
* `❌` - Planned (Pending Analyzers)

---

## 1. EMA Trend Pullback
* **Purpose:** Trend Following
* **Markets:** Forex, Stocks, Crypto, Indices
* **Timeframes:** 15M, 1H, 4H
* **Required Analyzers:** EMA, ATR
* **Entry Rules:** Enter when price pulls back to the fast EMA while fast EMA > slow EMA.
* **Exit Rules:** Target 2R or Trail with ATR.
* **Backtest Status:** ❌ Planned

---

## 2. EMA Cross
* **Purpose:** Trend Reversal / Momentum
* **Markets:** Forex, Crypto, Indices
* **Timeframes:** 1H, 4H, Daily
* **Required Analyzers:** EMA, ATR
* **Entry Rules:** Enter when the fast EMA crosses the slow EMA.
* **Exit Rules:** Exit on reverse cross or 2R.
* **Backtest Status:** ❌ Planned

---

## 3. MACD Momentum Cross
* **Purpose:** Momentum Continuation
* **Markets:** Forex, Stocks, Crypto
* **Timeframes:** 1H, 4H
* **Required Analyzers:** MACD, EMA
* **Entry Rules:** MACD line crosses signal line in the direction of the EMA trend.
* **Exit Rules:** MACD crosses back or fixed R:R.
* **Backtest Status:** ❌ Planned

---

## 4. MACD Zero Line Break
* **Purpose:** Trend Ignition
* **Markets:** Stocks, Indices, Forex
* **Timeframes:** 1H, 4H
* **Required Analyzers:** MACD, EMA
* **Entry Rules:** MACD crosses above/below the zero line while EMA trend aligns.
* **Exit Rules:** Trend exhaustion or trailing stop.
* **Backtest Status:** ❌ Planned

---

## 5. RSI Pullback
* **Purpose:** Mean Reversion within a Trend
* **Markets:** Forex, Indices, Crypto
* **Timeframes:** 15M, 1H
* **Required Analyzers:** RSI, EMA, Engulfing
* **Entry Rules:** RSI < 30 in a Bullish EMA Trend, confirmed by a Bullish Engulfing candle.
* **Exit Rules:** RSI > 70 or Fixed R:R.
* **Backtest Status:** ❌ Planned

---

## 6. ATR Volatility Breakout
* **Purpose:** Momentum Breakout
* **Markets:** Crypto, Indices
* **Timeframes:** 1M, 5M, 15M
* **Required Analyzers:** ATR
* **Entry Rules:** Candle closes > (N * ATR) indicating extreme momentum ignition.
* **Exit Rules:** Trailing ATR stop.
* **Backtest Status:** ❌ Planned

---

## 7. VWAP Mean Reversion
* **Purpose:** Mean Reversion
* **Markets:** Stocks, Indices (Exchange volume required)
* **Timeframes:** 1M, 5M
* **Required Analyzers:** VWAP
* **Entry Rules:** Price extends > 2 standard deviations away from the VWAP. Fade the move.
* **Exit Rules:** Price touches VWAP.
* **Backtest Status:** ❌ Planned

---

## 8. Engulfing Swing Bounce
* **Purpose:** Price Action Reversal
* **Markets:** Forex, Crypto
* **Timeframes:** 1H, 4H
* **Required Analyzers:** Swing High/Low, Engulfing, ATR
* **Entry Rules:** Bullish engulfing candle prints immediately following a confirmed Swing Low.
* **Exit Rules:** Target next Swing High.
* **Backtest Status:** ❌ Planned

---

## 9. Previous Day Sweep (ICT)
* **Purpose:** Liquidity Sweep
* **Markets:** Forex, Indices
* **Timeframes:** 15M, 1H
* **Required Analyzers:** Previous Day High/Low
* **Entry Rules:** Price sweeps below Previous Day Low and immediately closes back above it.
* **Exit Rules:** Target Previous Day High or 2R.
* **Backtest Status:** ❌ Planned

---

## 10. FVG Retest (ICT)
* **Purpose:** Smart Money Continuation
* **Markets:** Forex, Indices
* **Timeframes:** 5M, 15M, 1H
* **Required Analyzers:** FVG, EMA
* **Entry Rules:** Price taps into a previously unmitigated FVG in the direction of the EMA trend.
* **Exit Rules:** Target nearest liquidity pool (Swing High/Low).
* **Backtest Status:** ❌ Planned

---

## 11. CISD Continuation (ICT)
* **Purpose:** Market Structure Shift
* **Markets:** Forex, Crypto, Indices
* **Timeframes:** 15M, 1H, 4H
* **Required Analyzers:** CISD, Swing High/Low
* **Entry Rules:** Change in State of Delivery confirms higher timeframe trend direction.
* **Exit Rules:** Next opposing Swing point.
* **Backtest Status:** ❌ Planned

---

## 12. London Open Breakout
* **Purpose:** Session Breakout
* **Markets:** Forex (GBP, EUR pairs)
* **Timeframes:** 5M, 15M
* **Required Analyzers:** Asian Session Range
* **Entry Rules:** Price breaks and closes outside the Asian Session range during the first hour of London open.
* **Exit Rules:** Fixed time exit (End of London Session) or 2R.
* **Backtest Status:** ❌ Planned

---

## 13. Inside Bar Trend Breakout
* **Purpose:** Trend Continuation Breakout
* **Markets:** Forex, Crypto
* **Timeframes:** 1H, 4H, Daily
* **Required Analyzers:** Inside Bar, EMA
* **Entry Rules:** Break of an inside bar in a strongly trending market (EMA sloping).
* **Exit Rules:** 1.5R to 2R target.
* **Backtest Status:** ❌ Planned

---

## 14. Donchian Channel Breakout
* **Purpose:** Macro Trend Following
* **Markets:** Commodities, Crypto, Stocks
* **Timeframes:** Daily, Weekly
* **Required Analyzers:** Donchian Channel
* **Entry Rules:** Price closes above the 20-period highest high (Donchian upper band).
* **Exit Rules:** Price closes below the 10-period lowest low.
* **Backtest Status:** ❌ Planned
