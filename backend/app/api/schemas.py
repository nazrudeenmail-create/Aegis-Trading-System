from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SystemStatusResponse(BaseModel):
    system: str
    status: str
    mode: str
    broker: str
    account_mode: str
    balance: float
    open_positions: int
    engines: Dict[str, str] = {}
    last_update: datetime

    model_config = ConfigDict(frozen=True)

class TrendInfo(BaseModel):
    direction: str
    strength: str

class MarketSnapshotResponse(BaseModel):
    symbol: str
    timeframe: str
    price: float
    trend: TrendInfo
    regime: str
    indicators: Dict[str, Any]

class StrategyScoreInfo(BaseModel):
    strategy: str
    total: float
    historical: Optional[float] = None
    compatibility: Optional[float] = None
    setup: Optional[float] = None
    rejection_reason: Optional[str] = None
    setup_progress: float = 0.0
    failed_rule: Optional[Dict[str, Any]] = None

class RankingResponse(BaseModel):
    winner: str
    score: float
    ranking: List[StrategyScoreInfo]

class JournalEntryResponse(BaseModel):
    decision_id: str
    timestamp: datetime
    strategy: str
    decision: str
    reason: str
    risk_status: str
    execution_status: str
