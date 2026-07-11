import logging
from typing import List, Any
from app.market.domain.candle import Candle
from app.market_analysis.models import MarketSnapshot

# Tier 1
from app.market_analysis.analyzers.ema_analyzer import EMAAnalyzer
from app.market_analysis.analyzers.atr_analyzer import ATRAnalyzer
from app.market_analysis.analyzers.adx_analyzer import ADXAnalyzer
from app.market_analysis.analyzers.volume_analyzer import VolumeAnalyzer
from app.market_analysis.analyzers.candle_analyzer import CandleAnalyzer
from app.market_analysis.analyzers.swing_analyzer import SwingAnalyzer

# Tier 2
from app.market_analysis.analyzers.trend_analyzer import TrendAnalyzer
from app.market_analysis.analyzers.volatility_analyzer import VolatilityAnalyzer
from app.market_analysis.analyzers.market_regime_analyzer import MarketRegimeAnalyzer
from app.market_analysis.analyzers.pullback_analyzer import PullbackAnalyzer
from app.market_analysis.analyzers.momentum_analyzer import MomentumAnalyzer

# Exception
from app.market_analysis.exceptions import IndicatorCalculationError

logger = logging.getLogger(__name__)

class MarketAnalysisService:
    """
    Orchestrates the Market Intelligence Pipeline.
    Executes Tier 1 (Math Facts) followed by Tier 2 (Intelligence).
    Returns a unified MarketSnapshot.
    """
    
    def __init__(self):
        # Initialize Tier 1 Analyzers
        self.ema = EMAAnalyzer()
        self.atr = ATRAnalyzer()
        self.adx = ADXAnalyzer()
        self.volume = VolumeAnalyzer()
        self.candle = CandleAnalyzer()
        self.swing = SwingAnalyzer()
        
        # Initialize Tier 2 Analyzers
        self.trend = TrendAnalyzer()
        self.volatility = VolatilityAnalyzer()
        self.regime = MarketRegimeAnalyzer()
        self.pullback = PullbackAnalyzer()
        self.momentum = MomentumAnalyzer()
        
    def _run_analyzer(self, analyzer: Any, snapshot: MarketSnapshot, field: str) -> None:
        """
        Safely executes a single analyzer and sets the result on the snapshot.
        Prevents a single analyzer failure from crashing the pipeline.
        """
        try:
            result = analyzer.analyze(snapshot)
            setattr(snapshot, field, result)
        except IndicatorCalculationError as e:
            logger.error(f"{field.upper()} calculation failed", exc_info=e)
            snapshot.analysis_errors.append(f"{field}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in {field.upper()} analyzer", exc_info=e)
            snapshot.analysis_errors.append(f"{field}: {str(e)}")
            
    def analyze(self, candles: List[Candle]) -> MarketSnapshot:
        """
        Executes the 2-Tier analysis pipeline safely.
        """
        snapshot = MarketSnapshot(candles=candles)
        
        if not snapshot.is_valid:
            return snapshot
            
        # ----------------------------------------------------
        # Phase A: Tier 1 (Indicator Engine)
        # ----------------------------------------------------
        self._run_analyzer(self.ema, snapshot, "ema")
        self._run_analyzer(self.atr, snapshot, "atr")
        self._run_analyzer(self.adx, snapshot, "adx")
        self._run_analyzer(self.volume, snapshot, "volume")
        self._run_analyzer(self.candle, snapshot, "candle")
        self._run_analyzer(self.swing, snapshot, "swing")
        
        # ----------------------------------------------------
        # Phase B: Tier 2 (Intelligence Engine)
        # ----------------------------------------------------
        # Execution order is strictly enforced based on dependencies
        
        # 1. Trend (Depends on EMA, ADX)
        self._run_analyzer(self.trend, snapshot, "trend")
        
        # 2. Volatility (Depends on ATR)
        self._run_analyzer(self.volatility, snapshot, "volatility")
        
        # 3. Regime (Depends on Trend, Volatility)
        self._run_analyzer(self.regime, snapshot, "regime")
        
        # 4. Pullback (Depends on Trend, EMA, ATR)
        self._run_analyzer(self.pullback, snapshot, "pullback")
        
        # 5. Momentum (Independent for now)
        self._run_analyzer(self.momentum, snapshot, "momentum")
        
        return snapshot
