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
        
    def build_context(
        self, 
        base_1m_candles: List[Candle], 
        required_timeframes: List[Timeframe],
        primary_timeframe: Timeframe = None
    ) -> MultiTimeframeContext:
        """
        Builds a MultiTimeframeContext from a base list of 1-minute candles.
        For a live system, this might fetch directly from a MarketDataRepository.
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
                snapshot = self.analysis_service.analyze(aggregated_candles)
                context.snapshots[tf] = snapshot
            except Exception as e:
                logger.error(f"Failed to build analysis for timeframe {tf}: {e}")
                
        return context
