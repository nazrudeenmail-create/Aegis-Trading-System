import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from app.market.domain.candle import Candle
from app.market.domain.timeframe import Timeframe
from app.market.gap_detector import GapDetector, Gap
from app.market.quality_report import QualityReport

def create_candle(ts: datetime, volume: str = "100") -> Candle:
    return Candle(
        instrument="EURUSD",
        timeframe=Timeframe.M1,
        timestamp=ts,
        open=Decimal("1"), high=Decimal("1"), low=Decimal("1"), close=Decimal("1"),
        volume=Decimal(volume),
        source="test"
    )

def test_gap_detector_returns_dataclass():
    base = datetime(2026, 7, 10, 10, 0, 0, tzinfo=timezone.utc)
    
    # 10:00, 10:01, [missing 10:02, 10:03], 10:04
    candles = [
        create_candle(base),
        create_candle(base + timedelta(minutes=1)),
        create_candle(base + timedelta(minutes=4))
    ]
    
    gaps = GapDetector.detect_gaps(candles)
    assert len(gaps) == 1
    
    gap = gaps[0]
    assert isinstance(gap, Gap)
    assert gap.start == (base + timedelta(minutes=1)).isoformat()
    assert gap.end == (base + timedelta(minutes=4)).isoformat()
    assert gap.missing_count == 2

@pytest.mark.future
def test_gap_detector_respects_market_calendar():
    """
    To be implemented when Forex calendar is fully built out.
    Should verify that Friday close to Sunday open is NOT flagged as a gap.
    """
    pass

def test_quality_report_penalties():
    base = datetime(2026, 7, 10, 10, 0, 0, tzinfo=timezone.utc)
    
    # 10:00 (vol=0), 10:01, [missing], 10:03
    candles = [
        create_candle(base, volume="0"), # Zero volume penalty: -1
        create_candle(base + timedelta(minutes=1)),
        create_candle(base + timedelta(minutes=3)) # Gap penalty: -10
    ]
    
    report = QualityReport.generate(candles)
    
    assert report["total_candles"] == 3
    assert report["gaps_detected"] == 1
    assert report["missing_candles"] == 1
    assert report["zero_volume_candles"] == 1
    
    # Base 100 - 10 (gap) - 1 (zero vol) = 89
    assert report["quality_score"] == 89.0
