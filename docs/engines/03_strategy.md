# 06 - Strategy Engine

> Version: 1.0
> Status: Design Locked

---

# Purpose

The Strategy Engine is responsible for finding trading opportunities.

It receives market information from the Market Analysis Engine and evaluates every trading strategy.

Each strategy has its own rules.

If all rules are satisfied, the strategy generates a Trade Candidate.

The Strategy Engine does not execute trades.

---

# Architecture

Market Data

      │

      ▼

Market Analysis Engine

      │

      ▼

Strategy Engine

      │

      ├── Strategy 01 - EMA Trend Pullback
      ├── Strategy 02
      ├── Strategy 03
      ├── ...
      └── Strategy 15

      │

      ▼

Trade Candidate

      │

      ▼

Risk Engine

---

# Responsibilities

The Strategy Engine is responsible for:

- Evaluate every strategy
- Check entry conditions
- Generate trade candidates
- Reject invalid setups
- Send valid trade candidates to the Risk Engine

The Strategy Engine does NOT:

- Calculate indicators
- Calculate position size
- Calculate stop loss
- Execute orders

---

# Strategy Workflow

Every strategy follows the same workflow.

1. Receive market analysis.
2. Check strategy rules.
3. Validate entry conditions.
4. Create Trade Candidate.
5. Send Trade Candidate to Risk Engine.

---

# Strategy Structure

Every strategy should contain:

- Strategy Name
- Strategy Purpose
- Required Market Conditions
- Entry Rules
- Exit Rules
- Required Analyzers

This keeps all strategies consistent.

---

# Trade Candidate

If a strategy finds a valid setup, it creates a Trade Candidate.

Example:

Strategy:

EMA Trend Pullback

Direction:

BUY

Entry Price:

100

Strategy Confidence:

High

The Trade Candidate is not an executed trade.

It is only a proposed trading opportunity.

---

# Multiple Strategies

Sometimes several strategies may identify opportunities at the same time.

Example:

Strategy 01

BUY

Strategy 04

BUY

Strategy 08

No Trade

Each strategy works independently.

The Risk Engine decides whether a trade should proceed.

---

# No Trade

If a strategy's conditions are not satisfied, it returns:

No Trade

No further action is taken.

---

# Strategy Independence

Each strategy is independent.

Adding or removing one strategy must not affect the others.

Example:

Adding Strategy 16 should not require changes to Strategy 01.

---

# Strategy Reusability

Every strategy uses the same shared components.

Shared Components:

- Market Analysis Engine
- Risk Engine
- Execution Engine

Strategies only define their own trading logic.

---

# Strategy Development Rules

Every strategy must:

- Have objective rules
- Avoid subjective decisions
- Be fully backtestable
- Be reusable
- Produce consistent results

---

# Example Flow

Market Analysis:

Trend:
Bullish

Momentum:
Bullish

Pullback:
Valid

Volume:
Confirmed

↓

Strategy 01

Checks:

Trend?

Yes

Pullback?

Yes

Confirmation?

Yes

↓

Generate BUY Trade Candidate

↓

Send to Risk Engine

---

# Summary

The Strategy Engine is responsible for identifying trading opportunities.

It receives market intelligence from the Market Analysis Engine.

Each strategy evaluates the same market using its own rules.

Valid opportunities become Trade Candidates.

The Risk Engine then decides how much capital to risk before the trade can be executed.