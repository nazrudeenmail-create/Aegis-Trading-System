class MarketAnalysisError(Exception):
    """Base exception for market analysis errors."""
    pass

class IndicatorCalculationError(MarketAnalysisError):
    """Raised when pandas-ta or a math wrapper fails to calculate an indicator."""
    pass

class InsufficientMarketDataError(MarketAnalysisError):
    """Raised when there are not enough candles to perform an analysis."""
    pass
