"""
Enums — All PostgreSQL ENUM types for the Aegis Trading System

Every Python Enum class defined here maps to a native PostgreSQL ENUM type.
The enum values match Section 5 of 04_Database_Design.md exactly.

Usage in models:
    from app.database.enums import AssetClass, Direction, ...

    asset_class: Mapped[AssetClass] = mapped_column(
        Enum(AssetClass, name="asset_class", create_type=True)
    )

Convention:
    - Python class name: PascalCase (e.g., AssetClass)
    - Enum values: UPPER_SNAKE_CASE (e.g., INDEX, FOREX, CRYPTO)
    - PostgreSQL ENUM name: lowercase (e.g., asset_class)
"""

from enum import Enum


class AccountType(str, Enum):
    """Trading account type — paper, demo, live, or backtest."""
    PAPER = "PAPER"
    DEMO = "DEMO"
    LIVE = "LIVE"
    BACKTEST = "BACKTEST"


class AssetClass(str, Enum):
    """Broad asset classification for instruments."""
    INDEX = "INDEX"
    FOREX = "FOREX"
    COMMODITY = "COMMODITY"
    CRYPTO = "CRYPTO"
    STOCK = "STOCK"


class InstrumentStatus(str, Enum):
    """Trading and analysis status of an instrument."""
    ACTIVE = "ACTIVE"
    WATCHLIST = "WATCHLIST"
    PAUSED = "PAUSED"
    DISABLED = "DISABLED"


class MarketType(str, Enum):
    """Defines the market session schedule for an instrument."""
    US_STOCK = "US_STOCK"
    CRYPTO = "CRYPTO"
    FOREX = "FOREX"
    INDEX_CFD = "INDEX_CFD"
    COMMODITY = "COMMODITY"


class Timeframe(str, Enum):
    """Candle / analysis timeframes.

    Values match PostgreSQL ENUM type 'timeframe'.
    Member names and values are identical so SQLAlchemy
    sends the correct string to PostgreSQL.
    """
    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    H1 = "H1"
    H4 = "H4"
    D1 = "D1"


class IndicatorType(str, Enum):
    """Technical indicator types."""
    ATR = "ATR"
    EMA = "EMA"
    MACD = "MACD"
    RSI = "RSI"
    CISD = "CISD"
    MOMENTUM = "MOMENTUM"


class MarketBias(str, Enum):
    """Directional bias of market analysis."""
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class TrendHealth(str, Enum):
    """Health of the current trend."""
    HEALTHY = "HEALTHY"
    WEAK = "WEAK"
    BROKEN = "BROKEN"


class Direction(str, Enum):
    """Trade direction — long or short."""
    LONG = "LONG"
    SHORT = "SHORT"


class SignalType(str, Enum):
    """Type of trading signal."""
    ENTRY = "ENTRY"
    EXIT = "EXIT"
    PARTIAL_EXIT = "PARTIAL_EXIT"
    RE_ENTRY = "RE_ENTRY"


class SignalStatus(str, Enum):
    """Lifecycle of a trading signal."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class RiskCheckType(str, Enum):
    """Pre-trade risk validation check types."""
    POSITION_SIZE = "POSITION_SIZE"
    STOP_LOSS_DISTANCE = "STOP_LOSS_DISTANCE"
    EXPOSURE_LIMIT = "EXPOSURE_LIMIT"
    MAX_DRAWDOWN = "MAX_DRAWDOWN"
    MAX_POSITIONS = "MAX_POSITIONS"
    DAILY_LOSS_LIMIT = "DAILY_LOSS_LIMIT"


class OrderType(str, Enum):
    """Order types supported by the system."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"


class OrderStatus(str, Enum):
    """Lifecycle of an order."""
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class PositionStatus(str, Enum):
    """Status of a trading position."""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PARTIALLY_CLOSED = "PARTIALLY_CLOSED"


class TradeType(str, Enum):
    """Type of trade execution."""
    ENTRY = "ENTRY"
    EXIT = "EXIT"
    PARTIAL_EXIT = "PARTIAL_EXIT"
    RE_ENTRY = "RE_ENTRY"


class SettingValueType(str, Enum):
    """Data type of a dynamic setting value."""
    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    JSON = "JSON"


class LogLevel(str, Enum):
    """Severity levels for system logging."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DecisionType(str, Enum):
    """Types of trading decisions."""
    ENTRY = "ENTRY"
    EXIT = "EXIT"
    PARTIAL_EXIT = "PARTIAL_EXIT"
    RE_ENTRY = "RE_ENTRY"
    REJECT = "REJECT"
    CANCEL = "CANCEL"


class DecisionOutcome(str, Enum):
    """Outcome of a trading decision."""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    EXPIRED = "EXPIRED"


class UserRole(str, Enum):
    """Role-based access control for API security."""
    READ_ONLY = "READ_ONLY"
    TRADER = "TRADER"
    ADMIN = "ADMIN"