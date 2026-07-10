from enum import Enum

class Timeframe(str, Enum):
    """
    Domain representation of supported timeframes.
    Values align with the system's standard definitions.
    """
    M1 = "1M"
    M5 = "5M"
    M15 = "15M"
    H1 = "1H"
    H4 = "4H"
    D1 = "1D"
