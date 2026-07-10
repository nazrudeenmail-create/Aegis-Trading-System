class MarketDataError(Exception):
    """Base exception for all market data related errors."""
    pass

class AuthenticationError(MarketDataError):
    """Raised when provider authentication fails."""
    pass

class ProviderConnectionError(MarketDataError):
    """Raised when the provider is unreachable or times out."""
    pass

class InvalidCandleError(MarketDataError):
    """Raised when candle data fails OHLC validation."""
    pass

class DuplicateCandleError(MarketDataError):
    """Raised when attempting to process an already existing candle."""
    pass

class MissingDataError(MarketDataError):
    """Raised when expected market data (e.g., specific minutes) is missing."""
    pass
