"""
Aegis Trading System - Analytics & Journaling Models
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


class StrategyScoreRecord(BaseModel):
    """
    Records the ranking score for a specific strategy considered during a decision.
    """
    strategy_name: str
    score: float
    rank: int


class DecisionRecord(BaseModel):
    """
    Immutable log of a trading decision. 
    Captures the context and outcome of the strategy evaluation pipeline.
    """
    decision_id: str
    timestamp: datetime
    symbol: str
    timeframe: str
    market_regime: str
    
    # Strategy Competition
    strategies_considered: List[StrategyScoreRecord]
    selected_strategy: Optional[str] = None
    
    # Selected Strategy Ranking Details
    historical_score: Optional[float] = None
    compatibility_score: Optional[float] = None
    setup_score: Optional[float] = None
    final_score: Optional[float] = None
    confidence_score: Optional[float] = None
    
    # Risk Assessment
    risk_approved: bool = False
    risk_reason: Optional[str] = None
    
    # Execution Linking
    order_id: Optional[str] = None
    trade_id: Optional[str] = None
    
    # Trade Outcome
    outcome_status: str = "PENDING"
    profit_loss: Optional[Decimal] = None
    r_multiple: Optional[float] = None
    
    # Pydantic v2 frozen
    model_config = {"frozen": True}


class StrategyPerformance(BaseModel):
    """
    Aggregated performance for a specific strategy.
    """
    strategy_name: str
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    expectancy: float = 0.0
    max_drawdown_percent: float = 0.0
    net_profit: Decimal = Decimal("0")


class RegimePerformance(BaseModel):
    """
    Aggregated performance grouped by Market Regime.
    """
    regime_name: str
    total_trades: int = 0
    win_rate: float = 0.0
    net_profit: Decimal = Decimal("0")
    strategy_breakdown: dict[str, StrategyPerformance] = Field(default_factory=dict)


class ConfidenceCalibration(BaseModel):
    """
    Evaluates if high confidence predictions actually win more often.
    """
    confidence_bucket: str  # e.g., "90-100%"
    total_trades: int = 0
    win_rate: float = 0.0


class RankingAccuracy(BaseModel):
    """
    Tracks if the top-ranked strategy actually performed well.
    """
    total_decisions: int = 0
    profitable_decisions: int = 0
    accuracy_percent: float = 0.0


class StrategyIntelligenceReport(BaseModel):
    """
    Comprehensive output of the Analytics Engine.
    """
    generated_at: datetime
    total_decisions_logged: int
    total_trades_executed: int
    overall_net_profit: Decimal
    
    strategy_performance: dict[str, StrategyPerformance]
    regime_performance: dict[str, RegimePerformance]
    ranking_accuracy: RankingAccuracy
    confidence_calibration: List[ConfidenceCalibration]
