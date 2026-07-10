import time
from datetime import datetime, timezone
from decimal import Decimal
from typing import List

import requests

from app.market.domain.candle import Candle
from app.market.domain.timeframe import Timeframe
from app.market.exceptions import AuthenticationError, ProviderConnectionError, InvalidCandleError
from app.market.provider_base import MarketDataProvider


class CapitalComProvider(MarketDataProvider):
    """
    Concrete implementation for Capital.com API.
    Handles REST authentication, rate limits, and parsing JSON payloads
    into internal ATS Domain objects.
    """

    def __init__(self, api_url: str, api_key: str, username: str, password: str):
        self.api_url = api_url
        self.api_key = api_key
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.cst: str | None = None
        self.x_security_token: str | None = None
        self.last_request_time = 0.0
        self.min_request_interval = 0.5  # 500ms between requests

    def close(self) -> None:
        self.session.close()

    def _wait_for_rate_limit(self) -> None:
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def authenticate(self) -> None:
        """
        Creates a session with Capital.com using credentials.
        Extracts CST and X-SECURITY-TOKEN from response headers.
        """
        url = f"{self.api_url}/session"
        payload = {
            "identifier": self.username,
            "password": self.password
        }
        headers = {
            "X-CAP-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            self._wait_for_rate_limit()
            response = self.session.post(url, json=payload, headers=headers)
        except requests.RequestException as e:
            raise ProviderConnectionError(f"Failed to connect to Capital.com: {str(e)}")

        if response.status_code != 200:
            raise AuthenticationError(f"Authentication failed: {response.text}")

        # Capital.com returns session tokens in the headers
        self.cst = response.headers.get("CST")
        self.x_security_token = response.headers.get("X-SECURITY-TOKEN")

        if not self.cst or not self.x_security_token:
            raise AuthenticationError("Authentication failed: Missing security tokens in headers")

        # Update session headers for subsequent requests
        self.session.headers.update({
            "CST": self.cst,
            "X-SECURITY-TOKEN": self.x_security_token,
        })

    def fetch_historical_candles(
        self, instrument: str, timeframe: Timeframe, limit: int
    ) -> List[Candle]:
        """
        Fetches historical prices and parses them into ATS Candle domain objects.
        """
        if not self.cst or not self.x_security_token:
            self.authenticate()

        # Map ATS timeframe to Capital.com resolution
        # Capital.com resolutions: MINUTE, MINUTE_5, MINUTE_15, HOUR, HOUR_4, DAY
        resolution_map = {
            Timeframe.M1: "MINUTE",
            Timeframe.M5: "MINUTE_5",
            Timeframe.M15: "MINUTE_15",
            Timeframe.H1: "HOUR",
            Timeframe.H4: "HOUR_4",
            Timeframe.D1: "DAY"
        }
        resolution = resolution_map.get(timeframe, "MINUTE")

        url = f"{self.api_url}/prices/{instrument}"
        params = {
            "resolution": resolution,
            "max": limit
        }

        try:
            self._wait_for_rate_limit()
            response = self.session.get(url, params=params)
        except requests.RequestException as e:
            raise ProviderConnectionError(f"Failed to fetch prices: {str(e)}")

        if response.status_code == 401:
            # Token might have expired, re-authenticate and retry once
            self.authenticate()
            self._wait_for_rate_limit()
            response = self.session.get(url, params=params)

        if response.status_code != 200:
            raise ProviderConnectionError(f"Error fetching prices: {response.text}")

        data = response.json()
        prices = data.get("prices", [])

        candles = []
        for p in prices:
            # Parse timestamp (e.g. "2026-07-10T10:01:00")
            # Capital.com sometimes returns snapshotTime or snapshotTimeUTC
            raw_time = p.get("snapshotTimeUTC", p.get("snapshotTime"))
            if not raw_time:
                continue
                
            # Convert to aware UTC datetime
            try:
                dt = datetime.fromisoformat(raw_time.replace("Z", "+00:00")).astimezone(timezone.utc)
            except ValueError:
                continue

            # We use 'bid' prices as standard for our candles
            open_bid = p.get("openPrice", {}).get("bid")
            high_bid = p.get("highPrice", {}).get("bid")
            low_bid = p.get("lowPrice", {}).get("bid")
            close_bid = p.get("closePrice", {}).get("bid")

            if open_bid is None or high_bid is None or low_bid is None or close_bid is None:
                raise InvalidCandleError("Missing bid price in Capital.com response")

            open_price = Decimal(str(open_bid))
            high_price = Decimal(str(high_bid))
            low_price = Decimal(str(low_bid))
            close_price = Decimal(str(close_bid))
            volume = Decimal(str(p.get("lastTradedVolume", p.get("volume", 0))))

            candles.append(
                Candle(
                    instrument=instrument,
                    timeframe=timeframe,
                    timestamp=dt,
                    open=open_price,
                    high=high_price,
                    low=low_price,
                    close=close_price,
                    volume=volume,
                    source="capital_com"
                )
            )

        return candles
