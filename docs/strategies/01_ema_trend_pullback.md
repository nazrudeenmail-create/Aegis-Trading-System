# Strategy 01 - EMA Trend Pullback

> Version: 2.0
> Status: Design Locked
> Category: Trend Following

---

# 1. Purpose

The EMA Trend Pullback strategy is a trend-following strategy designed to enter trades after a temporary pullback within an established trend.

Instead of chasing price after a strong move, the strategy waits for a healthy pullback and enters only after confirmation that the trend is continuing.

The strategy supports both **Long (Buy)** and **Short (Sell)** trading.

---

# 2. Best Markets

Suitable for:

- Forex
- Stocks
- Crypto
- Indices

---

# 3. Best Timeframes

Recommended:

- 15 Minute
- 1 Hour
- 4 Hour
- Daily

---

# 4. Required Market Analysis

This strategy uses the shared Market Analysis Engine.

Required analyzers:

- EMA Analyzer
- EMA Alignment Analyzer
- ATR Analyzer
- ADX Analyzer
- Volume Analyzer
- Candle Analyzer
- Swing Analyzer
- Trend Analyzer
- Market Regime Analyzer
- Pullback Analyzer

The strategy never calculates indicators directly.

---

# 5. Long Entry Rules (BUY)

All conditions must be true.

## Market Regime

- Market must be Trending.

## Trend Direction

Long Trend Direction:

Higher timeframe:
Price > EMA200

Trend timeframe:
EMA20 > EMA50

Entry timeframe:
EMA9 > EMA21

## Trend Strength

- ADX ≥ 25

## Pullback

Price pulls back toward EMA20.

Condition:

- Distance between Price and EMA20 ≤ 0.2 × ATR

## Market Structure

- Recent Swing Low remains intact.
- Bullish market structure is not broken.

## Candle Confirmation

Confirmation candle must:

- Close above Open
- Close above EMA20

## Volume Confirmation

- Current Volume > Average Volume

## Result

Generate a **BUY Trade Candidate**.

---

# 5A. Multi-Timeframe Trend Alignment

The strategy evaluates EMA structure across multiple timeframes.

Higher timeframe determines market bias.
Lower timeframe determines execution timing.

## Timeframe Responsibilities

| Timeframe | Purpose                    |
| --------- | -------------------------- |
| Daily     | Long-term market direction |
| 4H        | Primary trend quality      |
| 1H        | Setup confirmation         |
| 15M       | Entry trigger              |

---

## Long Example

Higher timeframe:

```
Daily:

Price > EMA200
```

Trend timeframe:

```
4H:

EMA20 > EMA50
EMA50 > EMA200
```

Setup timeframe:

```
1H:

EMA9 > EMA21
Pullback detected
```

Entry timeframe:

```
15M:

Bullish confirmation candle
```

Result:

```
BUY Trade Candidate
```

---

## Short Example

Higher timeframe:

```
Daily:

Price < EMA200
```

Trend timeframe:

```
4H:

EMA20 < EMA50
EMA50 < EMA200
```

Setup timeframe:

```
1H:

EMA9 < EMA21
Pullback detected
```

Entry timeframe:

```
15M:

Bearish confirmation candle
```

Result:

```
SELL Trade Candidate
```

---

# 6. Short Entry Rules (SELL)

All conditions must be true.

## Market Regime

- Market must be Trending.

## Trend Direction

Short Trend Direction:

Higher timeframe:
Price < EMA200

Trend timeframe:
EMA20 < EMA50

Entry timeframe:
EMA9 < EMA21

## Trend Strength

- ADX ≥ 25

## Pullback

Price pulls back toward EMA20 from below.

Condition:

- Distance between Price and EMA20 ≤ 0.2 × ATR

## Market Structure

- Recent Swing High remains intact.
- Bearish market structure is not broken.

## Candle Confirmation

Confirmation candle must:

- Close below Open
- Close below EMA20

## Volume Confirmation

- Current Volume > Average Volume

## Result

Generate a **SELL Trade Candidate**.

---

# 7. Position Sizing

Position sizing is handled by the shared Trade Management module.

The strategy does not calculate:

- Lot size
- Risk amount
- Capital allocation

These are calculated using:

- Account Balance
- Risk Percentage
- Stop Loss Distance

---

# 8. Long Exit Rules

A Long trade closes when either condition occurs.

## Stop Loss

Stop Loss = Recent Swing Low − (0.5 × ATR)

## Exit Conditions

Exit if:

- ATR Trailing Stop is hit

OR

- EMA20 crosses below EMA50

---

# 9. Short Exit Rules

A Short trade closes when either condition occurs.

## Stop Loss

Stop Loss = Recent Swing High + (0.5 × ATR)

## Exit Conditions

Exit if:

- ATR Trailing Stop is hit

OR

- EMA20 crosses above EMA50

---

# 10. Trade Output

When every rule is satisfied, the strategy generates a Trade Candidate.

Example:

Direction:

BUY

Entry Price:

Current Market Price

Stop Loss:

Calculated by Trade Management

Exit Method

Primary Exit:
ATR Trailing Stop (3 × ATR)

Secondary Exit:
EMA20 crosses EMA50

Execution:
Handled by the Trade & Risk Management module.

Market Analysis:

Provides objective market facts only.

Strategy Engine determines trade qualification based on rule satisfaction.

The strategy never executes trades directly.

---

# 11. Trade Rejection Rules

No trade is generated if any of the following conditions are true:

- Market is ranging.
- Trend direction is invalid.
- ADX < 25.
- Pullback is invalid.
- Market structure is broken.
- Confirmation candle is missing.
- Volume confirmation fails.

---

# 12. Advantages

- Trades with the primary trend.
- Objective and rule-based.
- Easy to automate.
- Easy to backtest.
- Works across multiple markets.
- Supports both Long and Short trading.
- Uses shared market analysis for consistency.

---

# 13. Limitations

| Limitation | Aegis Solution |
|------------|----------------|
| Sideways market | Market Regime Analyzer rejects the trade. |
| Weak pullbacks | Pullback Analyzer validates pullback quality. |
| Indicator lag | Confirmation candle, volume, and market structure reduce false entries. |
| Changing volatility | ATR-based stop loss and shared position sizing adapt to market conditions. |

---

# 14. Strategy Flow

Market Data

↓

Market Analysis Engine

↓

Multi-Timeframe EMA Alignment

↓

Market Regime Check

↓

Trend Direction Check

↓

Trend Strength Check

↓

Pullback Quality Check

↓

Market Structure Check

↓

Entry Confirmation Check

↓

Generate Trade Candidate

↓

Trade Management

↓

Order Execution

---

# 15. Summary

The EMA Trend Pullback strategy trades only in the direction of an established trend.

It requires:

- A confirmed trend
- A healthy pullback
- Strong market structure
- Confirmation from price action
- Confirmation from volume

The strategy focuses only on identifying high-quality trading opportunities.

Risk management, position sizing, trade management, and order execution are handled by shared Aegis components, ensuring consistency across all trading strategies.