"""
Database Models — All 15 SQLAlchemy models for the Aegis Trading System

Imports:
    Imported here so that Alembic's `Base.metadata` can auto-discover
    all registered models during migration generation.

    Alembic env.py imports:
        from app.database.base import Base
        from app.database.models import *  # noqa: F401, F403

    This ensures Base.metadata contains all 15 tables.

Dependency Order:
    Models are imported in dependency order to avoid circular imports.
    Order: no-FK models → FK-dependent models.
"""

from app.database.models.instrument import Instrument
from app.database.models.candle import Candle
from app.database.models.market_session import MarketSession
from app.database.models.market_holiday import MarketHoliday
from app.database.models.indicator_value import IndicatorValue
from app.database.models.market_analysis import MarketAnalysis
from app.database.models.signal import Signal
from app.database.models.risk_check import RiskCheck
from app.database.models.account import Account
from app.database.models.order import Order
from app.database.models.position import Position
from app.database.models.trade import Trade
from app.database.models.setting import Setting
from app.database.models.system_log import SystemLog
from app.database.models.decision_log import DecisionLog
from app.database.models.backtest_run import BacktestRun

__all__ = [
    "Instrument",
    "Candle",
    "MarketSession",
    "MarketHoliday",
    "IndicatorValue",
    "MarketAnalysis",
    "Signal",
    "RiskCheck",
    "Account",
    "Order",
    "Position",
    "Trade",
    "Setting",
    "SystemLog",
    "DecisionLog",
    "BacktestRun",
]
