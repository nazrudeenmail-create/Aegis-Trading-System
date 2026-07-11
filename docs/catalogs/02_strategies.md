# 10 - Strategy Catalog

Version: 1.1

---

# Purpose
This document serves as the research roadmap for the Strategy Library (Phase 5). It defines the 15 objective, mathematical strategies that will be backtested and ranked in V1 of the Aegis Trading System.

The strategies are organized by "Family" to facilitate comparison. Each strategy is a **Research Candidate**. Their inclusion here does not guarantee profitability; it guarantees that they are testable.

## Status Key
* `✅` - Backtested & Validated
* `⏳` - In Progress
* `❌` - Planned (Pending Analyzers)

---

# 1. Trend Following Family

## 1.1 EMA Trend Pullback
* **Markets:** Forex, Stocks, Crypto, Indices
* **Timeframes:** 15M, 1H, 4H
* **Required Analyzers:** EMA, ATR
* **Entry Rules:** Enter when price pulls back to the fast EMA while fast EMA > slow EMA.
* **Exit Rules:** Target 2R or Trail with ATR.
* **Backtest Status:** ❌ Planned

## 1.2 EMA Cross
* **Markets:** Forex, Crypto, Indices
* **Timeframes:** 1H, 4H, Daily
* **Required Analyzers:** EMA, ATR
* **Entry Rules:** Enter when the fast EMA crosses the slow EMA.
* **Exit Rules:** Exit on reverse cross or 2R.
* **Backtest Status:** ❌ Planned

## 1.3 Multi-Timeframe Trend Alignment
* **Markets:** Forex, Crypto, Stocks, Indices
* **Timeframes:** 4H, 1H, 15M, 5M
* **Required Analyzers:** EMA, Swing High/Low, Trend Direction, Multi-Timeframe Analyzer
* **Entry Rules:** 4H/1H/15M trends align bullish, enter on 5M bullish engulfing.
* **Exit Rules:** Next Swing High or ATR Trailing Stop.
* **Backtest Status:** ❌ Planned

## 1.4 Donchian Channel Breakout
* **Markets:** Commodities, Crypto, Stocks
* **Timeframes:** Daily, Weekly
* **Required Analyzers:** Donchian Channel
* **Entry Rules:** Price closes above the 20-period highest high.
* **Exit Rules:** Price closes below the 10-period lowest low.
* **Backtest Status:** ❌ Planned

---

# 2. Momentum Family

## 2.1 MACD Momentum Cross
* **Markets:** Forex, Stocks, Crypto
* **Timeframes:** 1H, 4H
* **Required Analyzers:** MACD, EMA
* **Entry Rules:** MACD line crosses signal line in the direction of the EMA trend.
* **Exit Rules:** MACD crosses back or fixed R:R.
* **Backtest Status:** ❌ Planned

## 2.2 MACD Zero Line Break
* **Markets:** Stocks, Indices, Forex
* **Timeframes:** 1H, 4H
* **Required Analyzers:** MACD, EMA
* **Entry Rules:** MACD crosses above/below the zero line while EMA trend aligns.
* **Exit Rules:** Trend exhaustion or trailing stop.
* **Backtest Status:** ❌ Planned

## 2.3 ATR Volatility Breakout
* **Markets:** Crypto, Indices
* **Timeframes:** 1M, 5M, 15M
* **Required Analyzers:** ATR
* **Entry Rules:** Candle closes > (N * ATR) indicating extreme momentum ignition.
* **Exit Rules:** Trailing ATR stop.
* **Backtest Status:** ❌ Planned

---

# 3. Mean Reversion Family

## 3.1 RSI Pullback
* **Markets:** Forex, Indices, Crypto
* **Timeframes:** 15M, 1H
* **Required Analyzers:** RSI, EMA, Engulfing
* **Entry Rules:** RSI < 30 in a Bullish EMA Trend, confirmed by a Bullish Engulfing candle.
* **Exit Rules:** RSI > 70 or Fixed R:R.
* **Backtest Status:** ❌ Planned

## 3.2 VWAP Mean Reversion
* **Markets:** Stocks, Indices
* **Timeframes:** 1M, 5M
* **Required Analyzers:** VWAP
* **Entry Rules:** Price extends > 2 standard deviations away from the VWAP. Fade the move.
* **Exit Rules:** Price touches VWAP.
* **Backtest Status:** ❌ Planned

---

# 4. Price Action Family

## 4.1 Engulfing Swing Bounce
* **Markets:** Forex, Crypto
* **Timeframes:** 1H, 4H
* **Required Analyzers:** Swing High/Low, Engulfing, ATR
* **Entry Rules:** Bullish engulfing candle prints immediately following a confirmed Swing Low.
* **Exit Rules:** Target next Swing High.
* **Backtest Status:** ❌ Planned

## 4.2 Inside Bar Trend Breakout
* **Markets:** Forex, Crypto
* **Timeframes:** 1H, 4H, Daily
* **Required Analyzers:** Inside Bar, EMA
* **Entry Rules:** Break of an inside bar in a strongly trending market.
* **Exit Rules:** 1.5R to 2R target.
* **Backtest Status:** ❌ Planned

---

# 5. ICT / Smart Money Family

## 5.1 Previous Day Sweep
* **Markets:** Forex, Indices
* **Timeframes:** 15M, 1H
* **Required Analyzers:** Previous Day High/Low
* **Entry Rules:** Price sweeps below Previous Day Low and immediately closes back above it.
* **Exit Rules:** Target Previous Day High or 2R.
* **Backtest Status:** ❌ Planned

## 5.2 FVG Retest
* **Markets:** Forex, Indices
* **Timeframes:** 5M, 15M, 1H
* **Required Analyzers:** FVG, EMA
* **Entry Rules:** Price taps into a previously unmitigated FVG in the direction of the EMA trend.
* **Exit Rules:** Target nearest liquidity pool.
* **Backtest Status:** ❌ Planned

## 5.3 CISD Continuation
* **Markets:** Forex, Crypto, Indices
* **Timeframes:** 15M, 1H, 4H
* **Required Analyzers:** CISD, Swing High/Low
* **Entry Rules:** Change in State of Delivery confirms higher timeframe trend direction.
* **Exit Rules:** Next opposing Swing point.
* **Backtest Status:** ❌ Planned

---

# 6. Session Family

## 6.1 London Open Breakout
* **Markets:** Forex (GBP, EUR pairs)
* **Timeframes:** 5M, 15M
* **Required Analyzers:** Asian Session Range
* **Entry Rules:** Price breaks and closes outside the Asian Session range during the first hour of London open.
* **Exit Rules:** Fixed time exit or 2R.
* **Backtest Status:** ❌ Planned
