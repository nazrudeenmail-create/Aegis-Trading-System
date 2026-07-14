from typing import List, Dict
from datetime import datetime
import logging

from app.market.domain.candle import Candle
from app.market.domain.timeframe import Timeframe
from app.market.timeframe_builder import TimeframeBuilder
from app.market_analysis.models import MultiTimeframeContext, MarketSnapshot
from app.market_analysis.service import MarketAnalysisService

logger = logging.getLogger(__name__)

class MultiTimeframeService:
    """
    Orchestrates market analysis across multiple timeframes.
    Delegates to TimeframeBuilder for candle aggregation and 
    MarketAnalysisService for indicator calculations.
    Returns a MultiTimeframeContext.
    """
    def __init__(self, analysis_service: MarketAnalysisService = None):
        self.analysis_service = analysis_service or MarketAnalysisService()
        self.latest_contexts: Dict[str, MultiTimeframeContext] = {}
        self.latest_snapshots: Dict[str, MarketSnapshot] = {}

    def get_latest_snapshot(self, symbol: str, timeframe: str = "15M") -> MarketSnapshot | None:
        """
        Returns the most recent MarketSnapshot for a given symbol and timeframe.
        The API endpoint uses this to serve /market/current data.
        """
        tf = Timeframe[timeframe] if timeframe in Timeframe.__members__ else Timeframe.M15
        context = self.latest_contexts.get(symbol)
        if context and tf in context.snapshots:
            return context.snapshots[tf]
        return self.latest_snapshots.get(symbol)
        
    def build_context(
        self, 
        base_1m_candles: List[Candle], 
        required_timeframes: List[Timeframe],
        primary_timeframe: Timeframe = None,
        db=None
    ) -> MultiTimeframeContext:
        """
        Builds a MultiTimeframeContext from a base list of 1-minute candles.
        Passes db session to MarketAnalysisService to fetch cached IndicatorState.
        """
        if not base_1m_candles:
            return MultiTimeframeContext()
            
        instrument = base_1m_candles[0].instrument
        timestamp = base_1m_candles[-1].timestamp
        
        context = MultiTimeframeContext(
            instrument=instrument,
            timestamp=timestamp,
            primary_timeframe=primary_timeframe,
            snapshots={}
        )
        
        for tf in required_timeframes:
            try:
                aggregated_candles = TimeframeBuilder.aggregate(base_1m_candles, tf)
                
                from app.market_analysis.quality import DataQualityValidator
                is_valid, reason = DataQualityValidator.validate(aggregated_candles, expected_count=50)
                
                if not is_valid:
                    logger.warning(f"Data quality validation failed for {tf} on {instrument}: {reason}")
                    snapshot = MarketSnapshot(candles=aggregated_candles, is_valid=False)
                    snapshot.analysis_errors.append(f"Data Quality: {reason}")
                else:
                    snapshot = self.analysis_service.analyze(candles=aggregated_candles, tf=tf, db=db)
                    
                context.snapshots[tf] = snapshot
            except Exception as e:
                logger.error(f"Failed to build analysis for timeframe {tf}: {e}")
                
        return context