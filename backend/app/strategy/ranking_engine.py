from datetime import datetime, timezone
from typing import List, Dict
from sqlalchemy.orm import Session

from app.strategy.base import BaseStrategy
from app.market_analysis.models import MarketSnapshot
from app.strategy.models import StrategyResult

from app.strategy.models.ranking import StrategyScore, RankingResult
from app.strategy.scoring.historical import HistoricalScorer
from app.strategy.scoring.compatibility import CompatibilityScorer
from app.strategy.scoring.setup import SetupScorer

class StrategyRankingEngine:
    """
    Evaluates and ranks multiple strategies based on Historical, Compatibility, and Setup scores.
    Uses the locked 40/30/30 weighting algorithm.
    """
    def __init__(self, strategies: List[BaseStrategy]):
        self.strategies = strategies
        self.historical_scorer = HistoricalScorer()
        self.latest_rankings: Dict[str, RankingResult] = {}
        
    def get_latest_ranking(self, symbol: str) -> RankingResult | None:
        return self.latest_rankings.get(symbol)
        
    def rank(self, db: Session, symbol: str, timeframe: str, snapshot: MarketSnapshot, strategy_results: Dict[str, StrategyResult]) -> RankingResult:
        rankings: List[StrategyScore] = []
        
        for strategy in self.strategies:
            name = strategy.name
            profile = strategy.get_profile()
            
            # 1. Historical Score
            h_score = self.historical_scorer.score(db, name)
            
            # 2. Compatibility Score
            c_score = CompatibilityScorer.score(profile, snapshot)
            
            # 3. Setup Score
            result = strategy_results.get(name)
            if result:
                s_score_obj = SetupScorer.score(name, result)
                s_score = s_score_obj.confidence if s_score_obj.has_setup else 0.0
                rejection = s_score_obj.rejection_reason
            else:
                s_score = 0.0
                rejection = "Not evaluated"
                
            # Final calculation (40/30/30)
            final_score = (h_score * 0.40) + (c_score * 0.30) + (s_score * 0.30)
            
            rankings.append(
                StrategyScore(
                    strategy_name=name,
                    historical_score=h_score,
                    market_score=c_score,
                    setup_score=s_score,
                    final_score=final_score
                )
            )
            
        # Sort by final score descending
        rankings.sort(key=lambda x: x.final_score, reverse=True)
        
        best = rankings[0] if rankings else None
        
        # Explainability
        if best and best.final_score > 0 and best.setup_score > 0:
            selection = best.strategy_name
            reason = (
                f"Highest combined score: {best.final_score:.1f}. "
                f"(Historical: {best.historical_score:.1f}, "
                f"Compatibility: {best.market_score:.1f}, "
                f"Setup: {best.setup_score:.1f})"
            )
        else:
            selection = None
            reason = "No strategies met criteria or produced valid setups."
            
        return RankingResult(
            timestamp=datetime.now(timezone.utc),
            symbol=symbol,
            timeframe=timeframe,
            market_regime=snapshot.regime.regime if snapshot.regime else None,
            rankings=rankings,
            selected_strategy=selection,
            selection_reason=reason
        )
        
        self.latest_rankings[symbol] = result
        return result
