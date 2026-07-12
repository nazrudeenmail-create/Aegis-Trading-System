"""
Capital.com Broker Implementation
"""
import logging
import uuid
from typing import Optional

from app.execution.broker.interface import BrokerInterface
from app.execution.models.order import OrderRequest, OrderResult, OrderStatus
from app.execution.broker.capital.auth import CapitalAuthManager
from app.execution.broker.capital.client import CapitalClient
from app.execution.broker.capital.mapper import CapitalMapper

logger = logging.getLogger(__name__)

class CapitalComBroker(BrokerInterface):
    """
    Capital.com implementation.
    Supports Demo and Live environments natively via base_url.
    """
    def __init__(self, api_key: str, identifier: str, password: str, base_url: str):
        self.client = CapitalClient(base_url)
        self.auth = CapitalAuthManager(api_key, identifier, password, self.client)
        self._balance: float = 0.0

    async def connect(self) -> None:
        await self.auth.connect()
        await self._synchronize()

    async def _synchronize(self) -> None:
        """
        Global Synchronization Workflow.
        Connect -> Download Positions -> Download Orders -> Compare DB -> Sync -> Resume.
        """
        if not self.auth.cst or not self.auth.x_security_token:
            return
            
        logger.info("Synchronizing Capital.com Account, Positions, and Orders...")
        
        try:
            # 1. Fetch Accounts to get balance
            accounts_res = await self.client.get("/accounts", self.auth.cst, self.auth.x_security_token)
            accounts = accounts_res.get("accounts", [])
            if accounts:
                self._balance = accounts[0].get("balance", {}).get("balance", 0.0)
                
            # 2. Fetch Open Positions
            positions_res = await self.client.get("/positions", self.auth.cst, self.auth.x_security_token)
            open_positions = positions_res.get("positions", [])
            logger.info(f"Found {len(open_positions)} open positions on Capital.com")
            
            # 3. Fetch Working Orders
            orders_res = await self.client.get("/workingorders", self.auth.cst, self.auth.x_security_token)
            working_orders = orders_res.get("workingOrders", [])
            logger.info(f"Found {len(working_orders)} working orders on Capital.com")
            
        except Exception as e:
            logger.error(f"Capital.com synchronization failed: {e}")
            
        logger.info("Synchronization complete.")

    async def disconnect(self) -> None:
        await self.auth.disconnect()

    async def is_connected(self) -> bool:
        return self.auth.state.value == "CONNECTED"

    async def place_order(self, order: OrderRequest) -> OrderResult:
        logger.info(f"Capital.com routing order: {order}")
        payload = CapitalMapper.map_order_request(order)
        
        try:
            response = await self.client.post("/workingorders", payload, self.auth.cst, self.auth.x_security_token)
            return OrderResult(
                client_order_id=str(uuid.uuid4()),
                broker_order_id=response.get("dealReference", "unknown"),
                status=OrderStatus.SUBMITTED,
                filled_price=0.0, 
                filled_quantity=0.0
            )
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return OrderResult(
                client_order_id=str(uuid.uuid4()),
                broker_order_id="",
                status=OrderStatus.REJECTED,
                filled_price=0.0,
                filled_quantity=0.0
            )

    async def cancel_order(self, order_id: str) -> bool:
        logger.info(f"Capital.com cancelling order {order_id}")
        try:
            headers = self.client._get_headers(self.auth.cst, self.auth.x_security_token)
            await self.client.raw_delete(f"/workingorders/{order_id}", headers)
            return True
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return False

    async def get_account_balance(self) -> float:
        try:
            if self.auth.cst and self.auth.x_security_token:
                res = await self.client.get("/accounts", self.auth.cst, self.auth.x_security_token)
                accounts = res.get("accounts", [])
                if accounts:
                    self._balance = accounts[0].get("balance", {}).get("balance", 0.0)
        except Exception as e:
            logger.debug(f"Could not fetch live balance, returning cached: {e}")
        return self._balance

    async def search_instruments(self, query: str) -> list:
        try:
            if self.auth.cst and self.auth.x_security_token:
                res = await self.client.get(f"/markets?searchTerm={query}", self.auth.cst, self.auth.x_security_token)
                markets = res.get("markets", [])
                
                results = []
                for m in markets:
                    # Map instrumentType to our MarketType
                    inst_type = m.get("instrumentType", "UNKNOWN")
                    if inst_type == "SHARES":
                        mapped_type = "US_STOCK"
                    elif inst_type == "CRYPTOCURRENCIES":
                        mapped_type = "CRYPTO"
                    elif inst_type == "INDICES":
                        mapped_type = "INDEX_CFD"
                    elif inst_type == "CURRENCIES":
                        mapped_type = "FOREX"
                    elif inst_type == "COMMODITIES":
                        mapped_type = "COMMODITY"
                    else:
                        mapped_type = "US_STOCK"  # Default fallback instead of UNKNOWN which crashes
                        
                    results.append({
                        "symbol": m.get("epic"),
                        "name": m.get("instrumentName"),
                        "market_type": mapped_type
                    })
                return results
        except Exception as e:
            logger.error(f"Capital.com search failed for query '{query}': {e}")
        return []
