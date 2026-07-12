Understood. Strategy 02 should follow **Strategy 01 documentation style**: shorter, architecture-focused, no excessive explanation.

Here is the revised version.

```markdown
# Strategy 02 - Multi-Timeframe Trend Alignment

> Version: 1.0
> Status: Design Locked
> Category: Trend Following

---

# 1. Purpose

The Multi-Timeframe Trend Alignment strategy is a trend-following strategy designed to enter trades when multiple timeframes confirm the same market direction.

Instead of relying on a single timeframe, the strategy combines higher timeframe trend direction with lower timeframe entry confirmation.

The strategy supports both **Long (Buy)** and **Short (Sell)** trading.

---

# 2. Best Markets

Suitable for:

- Stocks
- Forex
- Crypto
- Indices
- Commodities

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
- ADX Analyzer
- Volume Analyzer
- Trend Analyzer
- Market Structure Analyzer
- Market Regime Analyzer
- ATR Analyzer

The strategy never calculates indicators directly.

---

# 5. Long Entry Rules (BUY)

All conditions must be true.

## Market Regime

- Market must be Trending.

## Higher Timeframe Trend

Daily:

- Price > EMA200

## Trend Timeframe Confirmation

4H:

- EMA20 > EMA50
- EMA50 > EMA200

## Entry Timeframe Confirmation

15M / 1H:

- EMA9 > EMA21

## Trend Strength

- ADX ≥ 25

## Market Structure

- Higher Highs and Higher Lows must be present.
- Previous swing low must remain intact.

## Volume Confirmation

- Current Volume > Average Volume

## Result

Generate a **BUY Trade Candidate**.

---

# 5A. Multi-Timeframe Responsibilities

| Timeframe | Purpose |
|-----------|---------|
| Daily | Long-term market direction |
| 4H | Primary trend confirmation |
| 1H | Setup validation |
| 15M | Entry timing |

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

Entry timeframe:

```

15M:

EMA9 > EMA21
Bullish confirmation

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

Entry timeframe:

```

15M:

EMA9 < EMA21
Bearish confirmation

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

## Higher Timeframe Trend

Daily:

- Price < EMA200

## Trend Timeframe Confirmation

4H:

- EMA20 < EMA50
- EMA50 < EMA200

## Entry Timeframe Confirmation

15M / 1H:

- EMA9 < EMA21

## Trend Strength

- ADX ≥ 25

## Market Structure

- Lower Highs and Lower Lows must be present.
- Previous swing high must remain intact.

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

## Stop Loss

Stop Loss:

```

Recent Swing Low - (0.5 × ATR)

```

## Exit Conditions

Exit if:

- ATR Trailing Stop is hit

OR

- EMA20 crosses below EMA50

---

# 9. Short Exit Rules

## Stop Loss

Stop Loss:

```

Recent Swing High + (0.5 × ATR)

```

## Exit Conditions

Exit if:

- ATR Trailing Stop is hit

OR

- EMA20 crosses above EMA50

---

# 10. Trade Output

When all rules are satisfied, the strategy generates a Trade Candidate.

Example:

```

Direction:

BUY

Entry Price:

Current Market Price

Stop Loss:

Calculated by Trade Management

Execution:

Handled by Trade & Risk Management module

```

The strategy does not execute trades directly.

---

# 11. Trade Rejection Rules

No trade is generated if:

- Market is ranging.
- Higher and lower timeframes disagree.
- ADX < 25.
- Trend structure is broken.
- Volume confirmation fails.
- EMA alignment is invalid.

---

# 12. Advantages

- Filters weak trends using multiple timeframes.
- Reduces false signals.
- Objective and rule-based.
- Easy to automate.
- Easy to backtest.
- Works across multiple markets.
- Supports Long and Short trading.

---

# 13. Limitations

| Limitation | Aegis Solution |
|------------|----------------|
| Late entries after trend confirmation | Lower timeframe entry trigger improves timing. |
| Misses early trend reversals | Combine with EMA Trend Pullback strategy. |
| Sideways market creates false alignment | Market Regime Analyzer rejects ranging conditions. |
| Strong trends can reverse quickly | ATR stop loss and Risk Management protect capital. |
| Fewer trading opportunities | Strategy Ranking Engine selects best setups. |

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

Market Structure Check

↓

Volume Confirmation

↓

Generate Trade Candidate

↓

Trade Management

↓

Order Execution

---

# 15. Summary

The Multi-Timeframe Trend Alignment strategy identifies trades when multiple timeframes confirm the same trend direction.

It requires:

- Long-term trend confirmation
- Medium-term EMA alignment
- Lower timeframe entry confirmation
- Strong trend strength
- Valid market structure

The strategy focuses only on finding high-quality trend opportunities.

Risk management, position sizing, trade management, and execution are handled by shared Aegis components.
```

This now matches **Strategy 01 structure, length, and ATS architecture style**. It can directly go into:

```
docs/
 └── strategies/
      └── strategy_02_mtf_trend_alignment.md
```
