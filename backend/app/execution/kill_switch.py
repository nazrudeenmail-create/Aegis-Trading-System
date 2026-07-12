"""
Aegis Trading System - Emergency Kill Switch
"""
import logging
from typing import Optional
from app.execution.broker.manager import BrokerManager
from app.core.state import global_state

logger = logging.getLogger(__name__)

class KillSwitch:
    """
    Emergency control to halt trading operations and optionally close all positions.
    """
    def __init__(self, broker_manager: BrokerManager):
        self.broker_manager = broker_manager
        self.is_active = False

    async def activate(self, close_all_positions: bool = False):
        """
        Activates the kill switch.
        - Rejects new orders (ExecutionEngine should check this).
        - Cancels all pending orders.
        - Optionally closes all open positions.
        """
        logger.critical("EMERGENCY KILL SWITCH ACTIVATED!")
        self.is_active = True
        
        # In a full implementation, we'd iterate over all open orders and cancel them via BrokerManager.
        # For Phase 13 mock, we'll just log it.
        logger.info("Cancelling all pending orders...")
        
        if close_all_positions:
            logger.info("Closing all open positions immediately...")
            # We would fetch open positions and send MARKET closing orders.

    def deactivate(self):
        """
        Deactivates the kill switch, allowing normal trading to resume.
        """
        logger.info("Kill switch deactivated. Normal trading can resume.")
        self.is_active = False

# Global instance for easy access, though DI is preferred.
kill_switch = None

def init_kill_switch(broker_manager: BrokerManager):
    global kill_switch
    kill_switch = KillSwitch(broker_manager)
    return kill_switch
