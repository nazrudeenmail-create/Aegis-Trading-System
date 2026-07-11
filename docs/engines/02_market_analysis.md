# 05 - Market Analysis Engine

> Version: 1.0
> Status: Design Locked

---

# Purpose

The Market Analysis Engine is the shared intelligence layer of Aegis.

Its job is to analyze the current market and provide standardized market information to every trading strategy.

The Market Analysis Engine **does not** generate BUY or SELL signals.

It only answers questions about the market.

Every strategy uses the same analysis and makes its own trading decisions.

---

# Architecture

Market Data

        │

        ▼

Market Analysis Engine

        │

        ├── Strategy 1
        ├── Strategy 2
        ├── Strategy 3
        ├── ...
        └── Strategy 15

The market is analyzed once.

All strategies reuse the same results.

This avoids duplicate calculations and keeps every strategy consistent.

---

# Responsibilities

The Market Analysis Engine is responsible for:

- Calculate technical indicators
- Identify market trend
- Measure trend strength
- Measure momentum
- Detect pullbacks
- Measure volatility
- Analyze market structure

The engine does **not** decide whether to enter a trade.

That responsibility belongs to each trading strategy.

---

# Market Analyzers

The engine extracts objective data from the market using modular analyzers. 

For the complete, up-to-date master list of all supported and planned analyzers (EMA, ATR, FVG, etc.), please refer to the **Market Analysis Catalog** (`09_Market_Analysis_Catalog.md`).

---

# Market Intelligence

The Market Analysis Engine combines all analyzers to understand the current market.

---

## Trend Analyzer

Determines:

- Bullish
- Bearish
- Neutral

---

## Market Regime Analyzer

Determines:

- Trending
- Ranging

Strategies can avoid unsuitable market conditions.

---

## Momentum Analyzer

Determines:

- Bullish Momentum
- Bearish Momentum
- Weak Momentum

---

## Pullback Analyzer

Determines whether the current pullback is healthy.

Checks:

- Trend remains valid
- Pullback depth
- Market structure
- Confirmation

---

## Volatility Analyzer

Determines:

- Low Volatility
- Normal Volatility
- High Volatility

Used by the Risk Engine.

---



The Market Analysis Engine produces standardized market information.

Example:

Trend:
Bullish

Market Regime:
Trending

Momentum:
Bullish

Trend Strength:
Strong

Pullback:
Valid

Volatility:
Normal

Volume:
Confirmed

Every strategy receives the same information.

Each strategy applies its own entry and exit rules.

---

# Strategy Integration

Example:

Strategy 1 (EMA Trend Pullback)

Uses:

- Trend
- Momentum
- Pullback
- Volume

Strategy 2 (Breakout)

Uses:

- Trend
- Volume
- Volatility

Strategy 3 (Range Trading)

Uses:

- Market Regime
- Volatility

The Market Analysis Engine remains unchanged.

Only strategy logic changes.

---

# Design Principles

- Analyze the market once.
- Reuse analysis across all strategies.
- Keep indicator calculations centralized.
- Keep strategies simple.
- Separate market analysis from trading decisions.
- Ensure consistent results for every strategy.

---

# Summary

The Market Analysis Engine is the foundation of Aegis.

It converts raw market data into meaningful market intelligence.

Strategies do not calculate indicators themselves.

Instead, they use the shared market analysis to decide whether a trading opportunity matches their own rules.