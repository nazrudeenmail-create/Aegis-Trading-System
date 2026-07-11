# 09 - Market Analysis Catalog

Version: 1.0

---

# Purpose
This document serves as the master roadmap for the Market Intelligence Layer (Phase 4). It lists all objective market analysis capabilities required by Aegis V1 Research Strategies, as well as subjective/advanced capabilities planned for future versions.

## Status Key
* `✅` - Fully Implemented
* `⏳` - In Progress / Required for V1 Strategies (Phase 4 scope)
* `❌` - Planned (Deferred to V2+)

---

## 1. Trend Analysis
| Analyzer | Description | Status |
| :--- | :--- | :--- |
| **EMA** | Exponential Moving Average | ⏳ |
| SMA | Simple Moving Average | ❌ |
| WMA | Weighted Moving Average | ❌ |
| Trend Direction | Basic mathematical trend direction | ❌ |

## 2. Momentum
| Analyzer | Description | Status |
| :--- | :--- | :--- |
| **MACD** | Moving Average Convergence Divergence | ⏳ |
| **RSI** | Relative Strength Index | ⏳ |
| Stochastic Oscillator | Momentum indicator comparing closing price to a range | ❌ |

## 3. Volatility
| Analyzer | Description | Status |
| :--- | :--- | :--- |
| **ATR** | Average True Range | ⏳ |
| Standard Deviation | Statistical volatility measure | ❌ |
| Bollinger Bands | Price envelope based on standard deviation | ❌ |

## 4. Volume
| Analyzer | Description | Status |
| :--- | :--- | :--- |
| **VWAP** | Volume Weighted Average Price | ⏳ |
| OBV | On Balance Volume | ❌ |
| Relative Volume | Current volume compared to historical average | ❌ |

## 5. Candle Analysis
| Analyzer | Description | Status |
| :--- | :--- | :--- |
| **Engulfing** | Bullish and Bearish Engulfing detection | ⏳ |
| **Inside Bar** | Inside bar detection | ⏳ |
| Pin Bar | Pin bar / Hammer detection | ❌ |
| Doji | Doji detection | ❌ |

## 6. Market Structure
| Analyzer | Description | Status |
| :--- | :--- | :--- |
| **Swing High/Low** | Mathematical detection of fractal swing points | ⏳ |
| BOS | Break of Structure | ❌ |
| CHoCH | Change of Character | ❌ |
| **Donchian Channel** | Highest High / Lowest Low over X periods | ⏳ |

## 7. Smart Money / ICT
| Analyzer | Description | Status |
| :--- | :--- | :--- |
| **FVG** | Fair Value Gap | ⏳ |
| **CISD** | Change in State of Delivery | ⏳ |
| **Previous Day Sweep** | Sweeps of PDH/PDL | ⏳ |
| Order Blocks | Subjective institutional zones | ❌ |
| Breaker Blocks | Failed order blocks | ❌ |

## 8. Support & Resistance (Deferred)
| Analyzer | Description | Status |
| :--- | :--- | :--- |
| Pivot Points | Mathematical pivot levels | ❌ |
| Dynamic Support | Support based on moving averages | ❌ |

## 9. Historical Context
| Analyzer | Description | Status |
| :--- | :--- | :--- |
| **Previous Day High/Low** | Yesterday's extreme prices | ⏳ |
| Rolling High/Low | Highest/lowest price over N periods | ❌ |

## 10. Session Analysis
| Analyzer | Description | Status |
| :--- | :--- | :--- |
| **Asian Session Range** | High/low of the Asian session | ⏳ |
| Kill Zones | High probability time windows | ❌ |

## Categories 11-17 (Deferred to Future Versions)
The following categories are fully deferred to V2 and beyond, as they are not required by any V1 Research Strategy:
* 11. Time Analysis (Time until close, etc.)
* 12. Gap Analysis (Common gap, breakaway gap)
* 13. Fibonacci (Retracements, Extensions)
* 14. Statistics (Z-Score, Correlation)
* 15. Risk Metrics (Position sizing logic)
* 16. Multi-Timeframe Analysis (HTF confluence)
* 17. Event Analysis (News, Earnings, CPI)
