"""
Capital.com Broker Implementation
"""
import logging
from decimal import Decimal
from typing import Optional, List, Dict, Any

from app.execution.broker.interface import BrokerInterface
from app.execution.models.order import OrderRequest, OrderResult, OrderStatus
from app.execution.broker.models import ConnectionState
from app.execution.broker.capital.auth import CapitalAuthManager
from app.execution.broker.capital.client import CapitalClient
from app.execution.broker.capital.mapper import CapitalMapper

logger = logging.getLogger(__name__)


class CapitalComBroker(BrokerInterface):
    """
    Capital.com implementation.
    Supports Demo and Live environments natively via base_url.

    Order routing:
      - MARKET orders -> POST /positions (immediate execution)
      - LIMIT/STOP orders -> POST /workingorders (pending orders)

    Internal endpoints (/positions, /workingorders) are accessed only inside
    this class. The rest of ATS interacts through BrokerInterface methods.
    """
    def __init__(self, api_key: str, identifier: str, password: str, base_url: str):
        self.client = CapitalClient(base_url)
        self.auth = CapitalAuthManager(api_key, identifier, password, self.client)
        self._balance: float = 0.0
        self._positions: List[Dict[str, Any]] = []
        self._working_orders: List[Dict[str, Any]] = []

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
            await self._sync_account()
            await self.sync_positions()
            await self._sync_working_orders()
        except Exception as e:
            logger.error(f"Capital.com synchronization failed: {e}")

        logger.info("Synchronization complete.")

    async def _sync_account(self) -> None:
        accounts_res = await self.client.get("/accounts", self.auth.cst, self.auth.x_security_token)
        accounts = accounts_res.get("accounts", [])
        if accounts:
            self._balance = accounts[0].get("balance", {}).get("balance", 0.0)

    async def disconnect(self) -> None:
        await self.auth.disconnect()

    async def is_connected(self) -> bool:
        return self.auth.state == ConnectionState.CONNECTED

    async def place_market_order(self, order: OrderRequest) -> OrderResult:
        """Route a market order to Capital.com immediate execution endpoint."""
        logger.info(f"Capital.com routing MARKET order: {order}")
        payload = CapitalMapper.map_order_request(order)

        try:
            response = await self.client.post("/positions", payload, self.auth.cst, self.auth.x_security_token)
            return CapitalMapper.parse_position_response(response, order)
        except Exception as e:
            logger.error(f"Failed to place market order: {e}")
            return self._rejected_result(order, str(e))

    async def place_limit_order(self, order: OrderRequest) -> OrderResult:
        """Route a limit order to Capital.com working orders endpoint."""
        return await self._place_pending_order(order)

    async def place_stop_order(self, order: OrderRequest) -> OrderResult:
        """Route a stop order to Capital.com working orders endpoint."""
        return await self._place_pending_order(order)

    async def _place_pending_order(self, order: OrderRequest) -> OrderResult:
        logger.info(f"Capital.com routing pending order: {order}")
        payload = CapitalMapper.map_order_request(order)

        try:
            response = await self.client.post("/workingorders", payload, self.auth.cst, self.auth.x_security_token)
            return CapitalMapper.parse_working_order_response(response)
        except Exception as e:
            logger.error(f"Failed to place pending order: {e}")
            return self._rejected_result(order, str(e))

    async def cancel_order(self, order_id: str) -> bool:
        logger.info(f"Capital.com cancelling order {order_id}")
        try:
            headers = self.client._get_headers(self.auth.cst, self.auth.x_security_token)
            await self.client.raw_delete(f"/workingorders/{order_id}", headers)
            return True
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return False

    async def get_order_status(self, order_id: str) -> Optional[OrderResult]:
        """Fetch the latest status of a working order or position deal."""
        try:
            # Try working orders first
            orders_res = await self.client.get("/workingorders", self.auth.cst, self.auth.x_security_token)
            for order in orders_res.get("workingOrders", []):
                if order.get("dealId") == order_id:
                    mapped = CapitalMapper.map_working_order_to_domain(order)
                    return OrderResult(
                        order_id=order_id,
                        status=CapitalMapper.map_order_status(mapped.get("status", "PENDING")),
                        filled_price=mapped.get("price"),
                        filled_quantity=mapped.get("quantity"),
                    )

            # Then try positions
            positions_res = await self.client.get("/positions", self.auth.cst, self.auth.x_security_token)
            for position in positions_res.get("positions", []):
                deal_id = position.get("position", {}).get("dealId")
                if deal_id == order_id:
                    mapped = CapitalMapper.map_position_to_domain(position)
                    return OrderResult(
                        order_id=order_id,
                        status=OrderStatus.FILLED,
                        filled_price=mapped.get("entry_price"),
                        filled_quantity=mapped.get("quantity"),
                    )
        except Exception as e:
            logger.error(f"Failed to get order status {order_id}: {e}")

        return None

    async def sync_positions(self) -> List[Dict[str, Any]]:
        """Fetch open positions from Capital.com and cache them locally."""
        if not self.auth.cst or not self.auth.x_security_token:
            return []

        try:
            positions_res = await self.client.get("/positions", self.auth.cst, self.auth.x_security_token)
            open_positions = positions_res.get("positions", [])
            self._positions = [CapitalMapper.map_position_to_domain(p) for p in open_positions]
            logger.info(f"Synchronized {len(self._positions)} open positions from Capital.com")
            return self._positions
        except Exception as e:
            logger.error(f"Capital.com position sync failed: {e}")
            return []

    async def _sync_working_orders(self) -> None:
        if not self.auth.cst or not self.auth.x_security_token:
            return

        try:
            orders_res = await self.client.get("/workingorders", self.auth.cst, self.auth.x_security_token)
            working_orders = orders_res.get("workingOrders", [])
            self._working_orders = [CapitalMapper.map_working_order_to_domain(o) for o in working_orders]
            logger.info(f"Synchronized {len(self._working_orders)} working orders from Capital.com")
        except Exception as e:
            logger.error(f"Capital.com working order sync failed: {e}")

    async def get_account_balance(self) -> float:
        try:
            if self.auth.cst and self.auth.x_security_token:
                await self._sync_account()
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
                        mapped_type = "US_STOCK"

                    results.append({
                        "symbol": m.get("epic"),
                        "name": m.get("instrumentName"),
                        "market_type": mapped_type
                    })
                return results
        except Exception as e:
            logger.error(f"Capital.com search failed for query '{query}': {e}")
        return []

    def _rejected_result(self, order: OrderRequest, message: str) -> OrderResult:
        return OrderResult(
            order_id="",
            status=OrderStatus.REJECTED,
            filled_price=None,
            filled_quantity=None,
            message=message,
        )
