"""
DEPRECATED: This module has been replaced by broker_factory.py.

Please use:
    from app.market.broker_factory import BrokerFactory

This file is kept only for backward compatibility and will be removed
in a future release.
"""
import warnings
from app.market.broker_factory import BrokerFactory

# Re-export for backward compatibility
ProviderFactory = BrokerFactory

warnings.warn(
    "provider_factory is deprecated. Use app.market.broker_factory.BrokerFactory instead.",
    DeprecationWarning,
    stacklevel=2
)