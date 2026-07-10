from typing import List, Dict, Any

from app.market.domain.candle import Candle
from app.market.gap_detector import GapDetector


class QualityReport:
    """
    Generates a report on the quality of a given market data dataset.
    """

    @staticmethod
    def generate(candles: List[Candle]) -> Dict[str, Any]:
        """
        Generates metadata and quality metrics for a sequence of candles.
        """
        if not candles:
            return {"status": "empty"}

        gaps = GapDetector.detect_gaps(candles)
        
        # Check for zero volume (which could indicate stale pricing)
        zero_volume_count = sum(1 for c in candles if c.volume == 0)

        report = {
            "instrument": candles[0].instrument,
            "timeframe": candles[0].timeframe.value,
            "total_candles": len(candles),
            "start_time": candles[0].timestamp.isoformat(),
            "end_time": candles[-1].timestamp.isoformat(),
            "gaps_detected": len(gaps),
            "missing_candles": sum(g.missing_count for g in gaps),
            "zero_volume_candles": zero_volume_count,
            "quality_score": 100.0
        }

        # Simple penalty heuristic: 
        # -10% for every gap
        # -1% for every zero volume candle
        penalty = (len(gaps) * 10) + (zero_volume_count * 1)
        report["quality_score"] = max(0.0, 100.0 - penalty)

        return report
