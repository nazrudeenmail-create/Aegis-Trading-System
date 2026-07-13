"""
Capital.com Mapper

Converts ATS internal order models to Capital.com JSON payloads
and broker responses back to normalized ATS domain objects.

Capital.com endpoints:
  - Market orders (immediate execution) -> POST /positions
  - Working orders (limit/stop)         -> POST /workingorders
"""
from decimal import Decimal
from typing import Dict, Any

from app.execution.models.order import OrderRequest, OrderDirection, OrderType, OrderStatus, OrderResult


class CapitalMapper:
    """
    Converts ATS internal models to Capital.com JSON payloads and back.
    """

    @staticmethod
    def map_order_request(order: OrderRequest) -> Dict[str, Any]:
        """
        Map a generic OrderRequest to a Capital.com order payload.

        This payload is suitable for both /positions (market) and
        /workingorders (limit/stop). The caller decides the endpoint.
        """
        payload = {
            "epic": order.symbol,
            "direction": "BUY" if order.direction == OrderDirection.LONG else "SELL",
            "size": str(order.quantity),
            "guaranteedStop": False,
            "forceOpen": True,
        }

        if order.order_type == OrderType.LIMIT and order.price is not None:
            payload["type"] = "LIMIT"
            payload["level"] = str(order.price)
        elif order.order_type == OrderType.STOP and order.stop_price is not None:
            payload["type"] = "STOP"
            payload["level"] = str(order.stop_price)
        else:
            # Market order via /positions does not send a type field.
            pass

        return payload

    @staticmethod
    def map_position_to_domain(position: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map a Capital.com /positions item to a normalized ATS position dict.
        """
        deal = position.get("position", {})
        market = position.get("market", {})
        direction = deal.get("direction", "")

        return {
            "broker_position_id": deal.get("dealId"),
            "symbol": market.get("epic"),
            "direction": "LONG" if direction == "BUY" else "SHORT" if direction == "SELL" else "UNKNOWN",
            "quantity": Decimal(str(deal.get("size", 0))),
            "entry_price": Decimal(str(deal.get("openLevel", 0))),
            "current_price": Decimal(str(deal.get("level", 0))),
            "unrealized_pnl": Decimal(str(position.get("unrealisedPnl", 0))),
            "opened_at": deal.get("created"),
            "raw": position,
        }

    @staticmethod
    def map_working_order_to_domain(order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map a Capital.com /workingorders item to a normalized ATS order dict.
        """
        return {
            "broker_order_id": order.get("dealId"),
            "symbol": order.get("epic"),
            "direction": "LONG" if order.get("direction") == "BUY" else "SHORT" if order.get("direction") == "SELL" else "UNKNOWN",
            "order_type": order.get("orderType", "UNKNOWN"),
            "quantity": Decimal(str(order.get("size", 0))),
            "price": Decimal(str(order.get("level", 0))) if order.get("level") is not None else None,
            "status": "PENDING",
            "raw": order,
        }

    @staticmethod
    def map_order_status(status: str) -> OrderStatus:
        """
        Map Capital.com order/position status strings to unified OrderStatus.
        """
        status = (status or "").upper()
        if status in ("OPEN", "FILLED"):
            return OrderStatus.FILLED
        if status == "PARTIALLY_FILLED":
            return OrderStatus.PARTIALLY_FILLED
        if status in ("PENDING", "WORKING", "ACCEPTED"):
            return OrderStatus.PENDING
        if status in ("CANCELLED", "DELETED"):
            return OrderStatus.CANCELLED
        if status in ("REJECTED", "FAILED"):
            return OrderStatus.REJECTED
        return OrderStatus.PENDING

    @staticmethod
    def parse_position_response(response: Dict[str, Any], order: OrderRequest) -> OrderResult:
        """
        Parse a Capital.com POST /positions response into a filled OrderResult.
        """
        position = response.get("position", {})
        deal_id = position.get("dealId") or response.get("dealReference") or ""
        fill_price_raw = position.get("level") or position.get("openLevel")
        fill_qty_raw = position.get("size") or order.quantity

        fill_price = Decimal(str(fill_price_raw)) if fill_price_raw is not None else None
        fill_qty = Decimal(str(fill_qty_raw)) if fill_qty_raw is not None else order.quantity

        return OrderResult(
            order_id=deal_id or "",
            status=OrderStatus.FILLED,
            filled_price=fill_price,
            filled_quantity=fill_qty,
            message="Market order filled",
        )

    @staticmethod
    def parse_working_order_response(response: Dict[str, Any]) -> OrderResult:
        """
        Parse a Capital.com POST /workingorders response into a pending OrderResult.
        """
        deal_reference = response.get("dealReference", "")
        deal_id = response.get("dealId", "") or deal_reference

        return OrderResult(
            order_id=deal_id or deal_reference or "",
            status=OrderStatus.PENDING,
            filled_price=None,
            filled_quantity=None,
            message="Pending order accepted",
        )
