"""
Capital.com HTTP Client
"""
import httpx
import logging
from typing import Dict, Any

from app.execution.broker.capital.rate_limiter import CapitalRateLimiter

logger = logging.getLogger(__name__)


class CapitalClient:
    """
    Wrapper around httpx for Capital.com REST API.
    Handles rate limiting and base URL.
    """
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.rate_limiter = CapitalRateLimiter()

    def _get_headers(self, cst: str, security_token: str) -> Dict[str, str]:
        return {
            "CST": cst,
            "X-SECURITY-TOKEN": security_token,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def get(self, endpoint: str, cst: str, security_token: str) -> Dict[str, Any]:
        await self.rate_limiter.wait()
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(cst, security_token)
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json() if response.content else {}

    async def post(self, endpoint: str, payload: Dict, cst: str, security_token: str) -> Dict[str, Any]:
        await self.rate_limiter.wait()
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(cst, security_token)
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json() if response.content else {}

    async def put(self, endpoint: str, payload: Dict, cst: str, security_token: str) -> Dict[str, Any]:
        await self.rate_limiter.wait()
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(cst, security_token)
        async with httpx.AsyncClient() as client:
            response = await client.put(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json() if response.content else {}

    async def raw_post(self, endpoint: str, payload: Dict, headers: Dict[str, str]) -> httpx.Response:
        await self.rate_limiter.wait()
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response

    async def raw_delete(self, endpoint: str, headers: Dict[str, str]) -> httpx.Response:
        await self.rate_limiter.wait()
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers)
            response.raise_for_status()
            return response
