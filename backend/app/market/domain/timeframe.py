from enum import Enum

class Timeframe(str, Enum):
    """
    Domain representation of supported timeframes.
    Values align with the database ENUM type 'timeframe'.
    """
    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    H1 = "H1"
    H4 = "H4"
    D1 = "D1"
