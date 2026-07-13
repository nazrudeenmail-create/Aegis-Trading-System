"""
Broker Factory — Infrastructure Layer

Creates and caches broker-related components (provider, broker).
This is the ONLY place that constructs Capital.com provider/broker instances.

Architecture:
    Configuration → BrokerFactory → Services → API

The factory uses settings.capital_api_url to select the correct
demo or live endpoint. No other file should know about demo vs live URLs.
"""
import logging
from typing import Optional

from app.core.config import get_settings, BrokerType
from app.market.provider_base import MarketDataProvider
from app.market.providers.capital_com_provider import CapitalComProvider

logger = logging.getLogger(__name__)


class BrokerFactory:
    """
    Factory for creating broker infrastructure components.
    
    Creates singleton instances of provider and broker at first access.
    All subsequent calls return the same cached instances.
    """
    
    _provider: Optional[MarketDataProvider] = None
    _broker: Optional[object] = None  # CapitalComBroker typed loosely to avoid circular import
    
    @classmethod
    def create_provider(cls) -> MarketDataProvider:
        """Create or return cached market data provider.
        
        Uses settings.capital_api_url to select demo/live endpoint.
        """
        if cls._provider is not None:
            return cls._provider
        
        settings = get_settings()
        
        if settings.BROKER == BrokerType.CAPITAL.value:
            cls._provider = CapitalComProvider(
                api_url=settings.capital_api_url,
                api_key=settings.CAPITAL_COM_API_KEY,
                username=settings.CAPITAL_COM_USERNAME,
                password=settings.CAPITAL_COM_PASSWORD
            )
            logger.info(
                f"BrokerFactory: Created CapitalComProvider "
                f"(mode={settings.account_mode_display}, url={settings.capital_api_url})"
            )
            return cls._provider
        
        raise ValueError(f"Unknown broker type: {settings.BROKER}")
    
    @classmethod
    def create_broker(cls):
        """Create or return cached broker instance for order execution.
        
        Uses settings.capital_api_url to select demo/live endpoint.
        """
        if cls._broker is not None:
            return cls._broker
        
        settings = get_settings()
        
        if settings.BROKER == BrokerType.CAPITAL.value:
            # Import here to avoid circular imports at module level
            from app.execution.broker.capital.broker import CapitalComBroker
            cls._broker = CapitalComBroker(
                api_key=settings.CAPITAL_COM_API_KEY,
                identifier=settings.CAPITAL_COM_USERNAME,
                password=settings.CAPITAL_COM_PASSWORD,
                base_url=settings.capital_api_url
            )
            logger.info(
                f"BrokerFactory: Created CapitalComBroker "
                f"(mode={settings.account_mode_display}, url={settings.capital_api_url})"
            )
            return cls._broker
        
        raise ValueError(f"Unknown broker type: {settings.BROKER}")
    
    @classmethod
    def reset(cls):
        """Reset cached instances. Useful for testing."""
        cls._provider = None
        cls._broker = None