```markdown
# Strategy 03 - Donchian Channel Breakout

> Version: 1.0
> Status: Design Locked
> Category: Breakout Trading

---

# 1. Purpose

The Donchian Channel Breakout strategy is a breakout-based strategy designed to enter trades when price breaks above or below recent market boundaries.

Instead of predicting reversals, the strategy waits for confirmed breakouts supported by trend strength and volume.

The strategy supports both **Long (Buy)** and **Short (Sell)** trading.

---

# 2. Best Markets

Suitable for:

- Stocks
- Forex
- Crypto
- Indices
- Commodities

Best conditions:

- Strong trending markets
- High volatility environments
- Expansion after consolidation

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

- Donchian Channel Analyzer
- EMA Analyzer
- ATR Analyzer
- ADX Analyzer
- Volume Analyzer
- Candle Analyzer
- Trend Analyzer
- Market Regime Analyzer
- Swing Analyzer

The strategy never calculates indicators directly.

---

# 5. Long Entry Rules (BUY)

All conditions must be true.

## Market Regime

- Market must support trending or breakout conditions.

## Donchian Breakout

Condition:

- Price breaks above the upper Donchian Channel.

Example:

```

Price > Highest High of previous N candles

```

---

## Trend Direction

Required:

- Price > EMA200

AND

- EMA20 > EMA50

---

## Trend Strength

Required:

- ADX ≥ 25

---

## Breakout Confirmation Candle

Confirmation candle must:

- Close above Donchian Upper Band
- Close above Open
- Show strong candle body

---

## Volume Confirmation

Required:

- Current Volume > Average Volume

---

## Result

Generate a **BUY Trade Candidate**.

---

# 5A. Multi-Timeframe Responsibilities

| Timeframe | Purpose |
|-----------|---------|
| Daily | Long-term market direction |
| 4H | Breakout quality confirmation |
| 1H | Setup validation |
| 15M | Entry trigger |

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

ADX ≥ 25

```

Entry timeframe:

```

15M:

Price breaks Donchian Upper Channel

Volume increases

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

ADX ≥ 25

```

Entry timeframe:

```

15M:

Price breaks Donchian Lower Channel

Volume increases

```

Result:

```

SELL Trade Candidate

```

---

# 6. Short Entry Rules (SELL)

All conditions must be true.

## Market Regime

- Market must support trending or breakout conditions.

## Donchian Breakout

Condition:

- Price breaks below the lower Donchian Channel.

Example:

```

Price < Lowest Low of previous N candles

```

---

## Trend Direction

Required:

- Price < EMA200

AND

- EMA20 < EMA50

---

## Trend Strength

Required:

- ADX ≥ 25

---

## Breakout Confirmation Candle

Confirmation candle must:

- Close below Donchian Lower Band
- Close below Open
- Show strong candle body

---

## Volume Confirmation

Required:

- Current Volume > Average Volume

---

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

Breakout Candle Low - (0.5 × ATR)

```

---

## Exit Conditions

Exit if:

- ATR Trailing Stop is hit

OR

- Price closes back inside Donchian Channel

OR

- EMA20 crosses below EMA50

---

# 9. Short Exit Rules

## Stop Loss

Stop Loss:

```

Breakout Candle High + (0.5 × ATR)

```

---

## Exit Conditions

Exit if:

- ATR Trailing Stop is hit

OR

- Price closes back inside Donchian Channel

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

Breakout Price

Stop Loss:

Calculated by Trade Management

Exit Method:

ATR Trailing Stop

Execution:

Handled by Trade & Risk Management module

```

The strategy does not execute trades directly.

---

# 11. Trade Rejection Rules

No trade is generated if:

- Market is ranging.
- Breakout occurs without volume confirmation.
- ADX < 25.
- Breakout candle is weak.
- Price immediately returns inside the channel.
- Trend direction is opposite.
- Volatility is too low.

---

# 12. Advantages

- Captures strong market moves.
- Does not require predicting reversals.
- Objective and rule-based.
- Easy to automate.
- Easy to backtest.
- Works across multiple markets.
- Supports Long and Short trading.

---

# 13. Limitations

| Limitation | Aegis Solution |
|------------|----------------|
| False breakouts | Volume confirmation and candle validation reduce weak breakouts. |
| Late entries after breakout | ATR-based trailing stop allows capturing continuation moves. |
| Poor performance in sideways markets | Market Regime Analyzer rejects ranging conditions. |
| Breakouts can fail quickly | Risk Management controls loss using ATR stop loss. |
| Frequent signals during volatility spikes | ADX and volatility filters improve quality. |

---

# 14. Strategy Flow

Market Data

↓

Market Analysis Engine

↓

Donchian Channel Calculation

↓

Market Regime Check

↓

Trend Direction Check

↓

Breakout Detection

↓

ADX Strength Check

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

The Donchian Channel Breakout strategy identifies opportunities when price breaks significant market boundaries with confirmation.

It requires:

- Valid breakout
- Trend alignment
- Strong momentum
- Volume confirmation
- Risk-controlled exits

The strategy focuses on capturing strong directional moves.

Risk management, position sizing, trade management, and execution are handled by shared Aegis components.
```

This matches **Strategy 01 + Strategy 02 documentation style** and is ready for:

```text
docs/
 └── strategies/
      └── strategy_03_donchian_breakout.md
```
