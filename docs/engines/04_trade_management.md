# 07 - Trade Management

> Version: 1.0
> Status: Design Locked

---

# Purpose

The Trade Management module is responsible for managing every trade after a strategy generates a Trade Signal.

It applies the same risk management rules to every strategy, ensuring consistent and disciplined trading.

The Trade Management module does not analyze the market or generate trading signals.

---

# Responsibilities

Trade Management is responsible for:

- Validate Trade Signals
- Calculate Stop Loss
- Calculate Position Size
- Manage Open Trades
- Update Trailing Stops
- Close Trades
- Record Trade History

---

# Architecture

Market Analysis

↓

Strategy Engine

↓

Trade Signal

↓

Trade Management

↓

Order Execution

↓

Broker

---

# Trade Workflow

Every trade follows the same lifecycle.

Trade Signal

↓

Risk Validation

↓

Position Size Calculation

↓

Place Order

↓

Monitor Trade

↓

Exit Trade

↓

Record Result

---

# Risk Validation

Before placing a trade, Trade Management verifies:

- Trade signal is valid
- Stop loss can be calculated
- Position size is greater than zero
- Risk does not exceed account limits

If any validation fails:

Reject the trade.

---

# Stop Loss Calculation

Long Trade

Stop Loss:

Recent Swing Low − (0.5 × ATR)

Short Trade

Stop Loss:

Recent Swing High + (0.5 × ATR)

The same method is used by every strategy unless a strategy explicitly defines a different stop-loss model.

---

# Position Size

Position size is calculated using:

- Account Balance
- Risk Percentage
- Stop Loss Distance

Formula:

Position Size = Risk Amount ÷ Stop Loss Distance

Example:

Account Balance:

$10,000

Risk:

1%

Maximum Risk:

$100

If Stop Loss Distance = $2

Position Size = 50 shares

---

# Risk Lock Principle

Risk is calculated only once when the trade is opened.

Once a trade is active:

- Position size never increases automatically.
- Market confidence cannot increase risk.
- The original risk remains fixed.

This prevents uncontrolled exposure.

---

# Open Trade Management

While a trade is open, Trade Management continuously monitors:

- Current Price
- Stop Loss
- ATR Trailing Stop
- Strategy Exit Rules

No new entry decisions are made during an active trade.

---

# Exit Rules

A trade closes when one of the following occurs:

- Stop Loss is hit
- ATR Trailing Stop is hit
- Strategy exit condition is triggered

The first condition reached closes the trade.

---

# Trade Record

Every completed trade is stored with:

- Strategy Name
- Symbol
- Direction
- Entry Price
- Exit Price
- Stop Loss
- Position Size
- Profit/Loss
- Entry Time
- Exit Time
- Exit Reason

This information is used for reporting and backtesting.

---

# Design Principles

- Shared by every strategy.
- Risk is calculated once.
- Position size is objective.
- No emotional decisions.
- Every trade follows the same lifecycle.
- Strategies focus only on finding opportunities.

---

# Summary

The Trade Management module is the universal risk and trade control layer of Aegis.

Strategies generate Trade Signals.

Trade Management determines whether the trade can be taken, calculates the appropriate position size, manages the trade until completion, and records the result.

This separation keeps strategies simple, reusable, and consistent.