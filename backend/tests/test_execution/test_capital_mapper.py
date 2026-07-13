"""Tests for Capital.com order mapper and response parsing."""
from decimal import Decimal

from app.execution.models.order import OrderRequest, OrderDirection, OrderType, OrderStatus
from app.execution.broker.capital.mapper import CapitalMapper


def test_map_market_order_request():
    order = OrderRequest(
        symbol="EURUSD",
        direction=OrderDirection.LONG,
        order_type=OrderType.MARKET,
        quantity=Decimal("1.5"),
    )
    payload = CapitalMapper.map_order_request(order)

    assert payload["epic"] == "EURUSD"
    assert payload["direction"] == "BUY"
    assert payload["size"] == "1.5"
    assert "type" not in payload
    assert "level" not in payload


def test_map_limit_order_request():
    order = OrderRequest(
        symbol="EURUSD",
        direction=OrderDirection.SHORT,
        order_type=OrderType.LIMIT,
        quantity=Decimal("2.0"),
        price=Decimal("1.0950"),
    )
    payload = CapitalMapper.map_order_request(order)

    assert payload["direction"] == "SELL"
    assert payload["type"] == "LIMIT"
    assert payload["level"] == "1.0950"


def test_map_stop_order_request():
    order = OrderRequest(
        symbol="EURUSD",
        direction=OrderDirection.LONG,
        order_type=OrderType.STOP,
        quantity=Decimal("1.0"),
        stop_price=Decimal("1.1000"),
    )
    payload = CapitalMapper.map_order_request(order)

    assert payload["type"] == "STOP"
    assert payload["level"] == "1.1000"


def test_parse_position_response_captures_fill():
    order = OrderRequest(
        symbol="EURUSD",
        direction=OrderDirection.LONG,
        order_type=OrderType.MARKET,
        quantity=Decimal("1.0"),
    )
    response = {
        "position": {
            "dealId": "DEAL123",
            "level": "1.1010",
            "size": "1.5",
        }
    }
    result = CapitalMapper.parse_position_response(response, order)

    assert result.status == OrderStatus.FILLED
    assert result.order_id == "DEAL123"
    assert result.filled_price == Decimal("1.1010")
    assert result.filled_quantity == Decimal("1.5")


def test_parse_working_order_response():
    response = {"dealReference": "REF456", "dealId": "DEAL789"}
    result = CapitalMapper.parse_working_order_response(response)

    assert result.status == OrderStatus.PENDING
    assert result.order_id == "DEAL789"
    assert result.filled_price is None


def test_map_order_status_normalization():
    assert CapitalMapper.map_order_status("OPEN") == OrderStatus.FILLED
    assert CapitalMapper.map_order_status("PENDING") == OrderStatus.PENDING
    assert CapitalMapper.map_order_status("PARTIALLY_FILLED") == OrderStatus.PARTIALLY_FILLED
    assert CapitalMapper.map_order_status("CANCELLED") == OrderStatus.CANCELLED
    assert CapitalMapper.map_order_status("REJECTED") == OrderStatus.REJECTED
    assert CapitalMapper.map_order_status("") == OrderStatus.PENDING
