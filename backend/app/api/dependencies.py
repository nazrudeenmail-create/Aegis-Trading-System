"""
FastAPI Dependencies
"""
from app.execution.broker.manager import BrokerManager
from app.execution.kill_switch import init_kill_switch

# Singletons for the application lifecycle
_broker_manager = BrokerManager()
_kill_switch = init_kill_switch(_broker_manager)

def get_broker_manager() -> BrokerManager:
    return _broker_manager

def get_kill_switch():
    return _kill_switch
