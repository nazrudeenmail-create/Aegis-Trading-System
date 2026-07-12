"""
Capital.com Mapper
"""
from typing import Dict, Any
from app.execution.models.order import OrderRequest, OrderDirection

class CapitalMapper:
    """
    Converts ATS internal models to Capital.com JSON payloads.
    """
    
    @staticmethod
    def map_order_request(order: OrderRequest) -> Dict[str, Any]:
        return {
            "epic": order.symbol,
            "direction": "BUY" if order.direction == OrderDirection.LONG else "SELL",
            "size": str(order.quantity),
            "type": order.order_type.value,
            "guaranteedStop": False,
            "forceOpen": True # Typical for new positions
        }
