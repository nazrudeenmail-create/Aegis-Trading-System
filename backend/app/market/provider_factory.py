from app.core.config import get_settings
from app.market.provider_base import MarketDataProvider
from app.market.providers.capital_com_provider import CapitalComProvider


class ProviderFactory:
    """
    Factory to instantiate the appropriate market data provider based on configuration.
    """

    @staticmethod
    def get_provider() -> MarketDataProvider:
        settings = get_settings()
        
        if settings.MARKET_DATA_PROVIDER == "capital_com":
            return CapitalComProvider(
                api_url=settings.CAPITAL_COM_API_URL,
                api_key=settings.CAPITAL_COM_API_KEY,
                username=settings.CAPITAL_COM_USERNAME,
                password=settings.CAPITAL_COM_PASSWORD
            )
            
        raise ValueError(f"Unknown market data provider: {settings.MARKET_DATA_PROVIDER}")
