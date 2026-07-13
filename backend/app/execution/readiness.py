"""
Aegis Trading System - Trading Readiness Check

Responsibility:
    Determine whether ATS is safe to send orders to the broker.
    Checks all critical subsystems before allowing execution.

If any check fails, execution is blocked and the reason is logged.
"""
from dataclasses import dataclass
from typing import List, Optional
import logging

from app.core.state import global_state, SystemStateEnum
from app.execution.broker.manager import BrokerManager

logger = logging.getLogger(__name__)


@dataclass
class ReadinessResult:
    ready: bool
    checks: List[dict]

    @property
    def blocking_reasons(self) -> List[str]:
        return [c["name"] for c in self.checks if not c["passed"]]


class TradingReadiness:
    """
    Evaluates whether all required subsystems are healthy enough to trade.
    """
    def __init__(self, broker_manager: Optional[BrokerManager] = None):
        self.broker_manager = broker_manager or global_state.broker_manager

    def check(self) -> ReadinessResult:
        checks = [
            self._check_system_state(),
            self._check_market_service(),
            self._check_strategy_engine(),
            self._check_ranking_engine(),
            self._check_risk_engine(),
            self._check_broker_connection(),
            self._check_position_sync(),
        ]

        ready = all(c["passed"] for c in checks)
        if not ready:
            logger.warning(f"Trading readiness failed: {self._blocking_reasons(checks)}")
        return ReadinessResult(ready=ready, checks=checks)

    def _check_system_state(self) -> dict:
        state = global_state.system_state
        passed = state is not None and state.state == SystemStateEnum.ACTIVE
        return {"name": "system_state", "passed": passed, "detail": state.state.value if state else "missing"}

    def _check_market_service(self) -> dict:
        passed = global_state.market_service is not None
        return {"name": "market_service", "passed": passed, "detail": "healthy" if passed else "missing"}

    def _check_strategy_engine(self) -> dict:
        passed = global_state.ranking_engine is not None
        return {"name": "strategy_engine", "passed": passed, "detail": "healthy" if passed else "missing"}

    def _check_ranking_engine(self) -> dict:
        passed = global_state.ranking_engine is not None
        return {"name": "ranking_engine", "passed": passed, "detail": "healthy" if passed else "missing"}

    def _check_risk_engine(self) -> dict:
        passed = global_state.risk_engine is not None
        return {"name": "risk_engine", "passed": passed, "detail": "healthy" if passed else "missing"}

    def _check_broker_connection(self) -> dict:
        if not self.broker_manager:
            return {"name": "broker_connection", "passed": False, "detail": "no broker manager"}
        passed = self.broker_manager.state.value == "CONNECTED"
        return {"name": "broker_connection", "passed": passed, "detail": self.broker_manager.state.value}

    def _check_position_sync(self) -> dict:
        if not self.broker_manager:
            return {"name": "position_sync", "passed": False, "detail": "no broker manager"}
        positions = self.broker_manager.get_cached_positions()
        # We consider sync healthy if we have attempted a sync (positions may legitimately be empty).
        # The broker manager caches positions after connect; empty list is acceptable.
        passed = positions is not None
        return {"name": "position_sync", "passed": passed, "detail": f"{len(positions)} positions cached"}

    @staticmethod
    def _blocking_reasons(checks: List[dict]) -> List[str]:
        return [c["name"] for c in checks if not c["passed"]]
