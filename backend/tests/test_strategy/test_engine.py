import pytest
from app.strategy.engine import StrategyEngine
from app.market_analysis.mtf_service import MultiTimeframeService
from tests.test_strategy.conftest import create_mock_mtf_context
from app.market.domain.candle import Candle
from app.market.domain.timeframe import Timeframe
from datetime import datetime, timezone
from decimal import Decimal

class MockMTFService(MultiTimeframeService):
    def __init__(self, context_to_return):
        self.context_to_return = context_to_return
        
    def build_context(self, base_1m_candles, required_timeframes, primary_timeframe=None):
        return self.context_to_return

def get_dummy_candles():
    return [Candle(
        timestamp=datetime.now(timezone.utc), instrument="BTC/USD", timeframe=Timeframe.M1, source="test",
        open=Decimal("100"), high=Decimal("110"), low=Decimal("95"), close=Decimal("105"), volume=Decimal("150")
    )]

def test_engine_evaluate_all_valid():
    context = create_mock_mtf_context()
    mock_service = MockMTFService(context)
    
    engine = StrategyEngine(mtf_service=mock_service)
    candidates = engine.evaluate_all(get_dummy_candles())
    
    # We should get a candidate from EMATrendPullback and MultiTimeframeTrendAlignment Strategy
    # Wait, Donchian will fail because DonchianAnalysis is None in the mock context
    assert len(candidates) > 0
    assert any(c.strategy_name == "EMA Trend Pullback" for c in candidates)

from app.market_analysis.enums import MarketRegime, EMAAlignment

def test_engine_evaluate_all_invalid():
    # Invalid snapshot for Strategy 01 and 02 (Ranging market, mixed alignment)
    context = create_mock_mtf_context(regime=MarketRegime.RANGING, alignment=EMAAlignment.MIXED)
    mock_service = MockMTFService(context)
    
    engine = StrategyEngine(mtf_service=mock_service)
    candidates = engine.evaluate_all(get_dummy_candles())
    
    # Should return empty list because no strategies passed
    assert len(candidates) == 0
