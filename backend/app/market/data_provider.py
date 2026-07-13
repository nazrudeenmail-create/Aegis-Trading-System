\"\"\"
DEPRECATED: This file has been replaced by provider_base.py.

Please use:
    from app.market.provider_base import MarketDataProvider

This file is kept as a stub for backward compatibility and will be removed
in a future release.
\"\"\"
import warnings
from app.market.provider_base import MarketDataProvider  # noqa: F401

warnings.warn(
    "app.market.data_provider is deprecated. Use app.market.provider_base instead.",
    DeprecationWarning,
    stacklevel=2,
)
