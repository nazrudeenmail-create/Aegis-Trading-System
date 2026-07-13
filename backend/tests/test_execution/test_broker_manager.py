"""Tests for BrokerManager and emergency-stop/readiness integration."""
import pytest
from decimal import Decimal

from app.execution.broker.manager import BrokerManager
from app.execution.broker.models import ConnectionState
from app.execution.models.order import OrderRequest, OrderDirection, OrderType, OrderResult, OrderStatus


class FakeBroker:
    def __init__(self):
        self.connected = False
        self.orders = []
        self.positions = []

    async def connect(self):
        self.connected = True

    async def disconnect(self):
        self.connected = False

    async def is_connected(self):
        return self.connected

    async def place_market_order(self, order: OrderRequest) -> OrderResult:
        self.orders.append(("market", order))
        return OrderResult(
            order_id="FAKE1",
            status=OrderStatus.FILLED,
            filled_price=Decimal("100"),
            filled_quantity=order.quantity,
        )

    async def place_limit_order(self, order: OrderRequest) -> OrderResult:
        self.orders.append(("limit", order))
        return OrderResult(order_id="FAKE2", status=OrderStatus.PENDING)

    async def place_stop_order(self, order: OrderRequest) -> OrderResult:
        self.orders.append(("stop", order))
        return OrderResult(order_id="FAKE3", status=OrderStatus.PENDING)

    async def cancel_order(self, order_id: str) -> bool:
        return True

    async def get_order_status(self, order_id: str):
        return None

    async def sync_positions(self):
        return self.positions

    async def get_account_balance(self):
        return 1000.0


@pytest.fixture
def manager():
    return BrokerManager()


@pytest.fixture
def broker():
    return FakeBroker()


@pytest.mark.asyncio
async def test_manager_routes_market_order(manager, broker):
    manager.set_active_broker(broker, environment="Demo")
    manager.state = ConnectionState.CONNECTED

    order = OrderRequest(
        symbol="EURUSD",
        direction=OrderDirection.LONG,
        order_type=OrderType.MARKET,
        quantity=Decimal("1.0"),
    )
    result = await manager.place_order(order)

    assert result.status == OrderStatus.FILLED
    assert broker.orders[0][0] == "market"


@pytest.mark.asyncio
async def test_manager_routes_limit_order(manager, broker):
    manager.set_active_broker(broker, environment="Demo")
    manager.state = ConnectionState.CONNECTED

    order = OrderRequest(
        symbol="EURUSD",
        direction=OrderDirection.SHORT,
        order_type=OrderType.LIMIT,
        quantity=Decimal("1.0"),
        price=Decimal("1.0900"),
    )
    result = await manager.place_order(order)

    assert result.status == OrderStatus.PENDING
    assert broker.orders[0][0] == "limit"


@pytest.mark.asyncio
async def test_manager_rejects_order_when_not_connected(manager, broker):
    manager.set_active_broker(broker, environment="Demo")
    manager.state = ConnectionState.DISCONNECTED

    order = OrderRequest(
        symbol="EURUSD",
        direction=OrderDirection.LONG,
        order_type=OrderType.MARKET,
        quantity=Decimal("1.0"),
    )
    with pytest.raises(RuntimeError, match="Broker disconnected"):
        await manager.place_order(order)


@pytest.mark.asyncio
async def test_manager_sync_positions_caches_result(manager, broker):
    broker.positions = [{"symbol": "EURUSD", "quantity": Decimal("1.0")}]
    manager.set_active_broker(broker, environment="Demo")

    positions = await manager.sync_positions()

    assert positions == broker.positions
    assert manager.get_cached_positions() == broker.positions


@pytest.mark.asyncio
async def test_manager_connect_sets_state(manager, broker):
    manager.set_active_broker(broker, environment="Demo")
    await manager.connect()

    assert broker.connected is True
    assert manager.state == ConnectionState.CONNECTED


@pytest.mark.asyncio
async def test_manager_disconnect_sets_state(manager, broker):
    manager.set_active_broker(broker, environment="Demo")
    manager.state = ConnectionState.CONNECTED
    await manager.disconnect()

    assert broker.connected is False
    assert manager.state == ConnectionState.DISCONNECTED
