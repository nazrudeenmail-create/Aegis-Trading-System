from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import datetime, timezone
from app.api.schemas import JournalEntryResponse
from app.api.auth import get_current_user, User
from app.core.state import global_state

router = APIRouter()

@router.get("/latest", response_model=List[JournalEntryResponse])
def get_latest_decisions(current_user: User = Depends(get_current_user), limit: int = 10):
    """
    Returns the latest decisions logged from Phase 10.
    """
    if global_state.journal:
        decisions = global_state.journal.get_all_decisions()
        sorted_decisions = sorted(decisions, key=lambda d: d.timestamp, reverse=True)
        results = []
        for d in sorted_decisions[:limit]:
            results.append(JournalEntryResponse(
                decision_id=d.decision_id,
                timestamp=d.timestamp,
                strategy=d.selected_strategy,
                decision="EXECUTE" if d.risk_approved else "REJECT",
                reason=d.risk_reason if not d.risk_approved else "Ranked Top / Risk Approved",
                risk_status="APPROVED" if d.risk_approved else "REJECTED",
                execution_status=d.outcome_status
            ))
        return results
        
    # Mock data
    return [
        JournalEntryResponse(
            decision_id="mock-uuid-1",
            timestamp=datetime.now(timezone.utc),
            strategy="EMA Pullback",
            decision="BUY",
            reason="EMA aligned, ADX strong, Pullback valid",
            risk_status="APPROVED",
            execution_status="EXECUTED"
        ),
        JournalEntryResponse(
            decision_id="mock-uuid-2",
            timestamp=datetime.now(timezone.utc),
            strategy="Donchian",
            decision="REJECTED",
            reason="ADX = 18, Required >= 25",
            risk_status="REJECTED",
            execution_status="REJECTED"
        )
    ]

@router.get("/history", response_model=List[JournalEntryResponse])
def get_decision_history(
    strategy: Optional[str] = Query(None),
    result: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """
    Returns filtered decision history.
    """
    # For MVP, return mock empty or single mock based on filter
    return []
