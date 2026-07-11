import pytest
from app.strategy.engine import StrategyEngine
from tests.test_strategy.conftest import create_mock_snapshot

def test_engine_evaluate_all_valid():
    # Valid snapshot for Strategy 01 (EMA Trend Pullback) LONG
    snapshot = create_mock_snapshot()
    
    engine = StrategyEngine()
    candidates = engine.evaluate_all(snapshot)
    
    assert len(candidates) == 1
    assert candidates[0].strategy_name == "EMA Trend Pullback"
    assert candidates[0].direction == "LONG"

from app.market_analysis.enums import MarketRegime

def test_engine_evaluate_all_invalid():
    # Invalid snapshot for Strategy 01 (Ranging market)
    snapshot = create_mock_snapshot(regime=MarketRegime.RANGING)
    
    engine = StrategyEngine()
    candidates = engine.evaluate_all(snapshot)
    
    # Should return empty list because no strategies passed
    assert len(candidates) == 0
