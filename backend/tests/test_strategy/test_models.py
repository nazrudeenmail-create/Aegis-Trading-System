from decimal import Decimal
from app.strategy.models import TradeCandidate, TradeDirection, StrategyResult

def test_trade_candidate_creation():
    candidate = TradeCandidate(
        strategy_name="Test Strategy",
        strategy_version="1.0",
        symbol="BTC/USD",
        direction=TradeDirection.LONG,
        entry_price=Decimal("100.0"),
        stop_loss=Decimal("95.0"),
        market_conditions={"trend": "BULLISH"}
    )
    
    assert candidate.strategy_name == "Test Strategy"
    assert candidate.strategy_version == "1.0"
    assert candidate.symbol == "BTC/USD"
    assert candidate.direction == TradeDirection.LONG
    assert candidate.entry_price == Decimal("100.0")
    assert candidate.stop_loss == Decimal("95.0")
    assert candidate.market_conditions["trend"] == "BULLISH"

def test_strategy_result_valid():
    candidate = TradeCandidate(
        strategy_name="Test Strategy",
        strategy_version="1.0",
        symbol="BTC/USD",
        direction=TradeDirection.SHORT,
        entry_price=Decimal("100.0"),
        stop_loss=Decimal("105.0"),
        market_conditions={"trend": "BEARISH"}
    )
    
    result = StrategyResult(
        is_valid=True,
        candidate=candidate
    )
    
    assert result.is_valid is True
    assert result.candidate is not None
    assert result.rejection_reason is None

def test_strategy_result_invalid():
    result = StrategyResult(
        is_valid=False,
        rejection_reason="ADX < 25"
    )
    
    assert result.is_valid is False
    assert result.candidate is None
    assert result.rejection_reason == "ADX < 25"
