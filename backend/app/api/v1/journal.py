from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.api.schemas import JournalEntryResponse
from app.api.auth import get_current_user, User
from app.database.connection import get_db
from app.database.models.decision_log import DecisionLog

router = APIRouter()

@router.get("/latest", response_model=List[JournalEntryResponse])
def get_latest_decisions(
    current_user: User = Depends(get_current_user), 
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Returns the latest decisions logged from Phase 10 via the database.
    """
    stmt = select(DecisionLog).order_by(desc(DecisionLog.created_at)).limit(limit)
    decisions = db.execute(stmt).scalars().all()
    
    results = []
    for d in decisions:
        # Extract fields from the context JSONB
        ctx = d.decision_context or {}
        strategy_name = ctx.get("strategy_name", "Unknown Strategy")
        
        # In a real app, you might map the risk status from another field or logic.
        # Here we just determine if the outcome was executed or rejected.
        risk_status = "APPROVED" if d.outcome.value in ["EXECUTED", "COMPLETED", "OPENED"] else "REJECTED"
        
        results.append(JournalEntryResponse(
            decision_id=str(d.id),
            timestamp=d.created_at,
            strategy=strategy_name,
            decision=d.decision_type.value,
            reason=d.reason,
            risk_status=risk_status,
            execution_status=d.outcome.value
        ))
        
    return results

@router.get("/history", response_model=List[JournalEntryResponse])
def get_decision_history(
    strategy: Optional[str] = Query(None),
    result: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns filtered decision history.
    """
    stmt = select(DecisionLog).order_by(desc(DecisionLog.created_at)).limit(100)
    
    if result:
        # Simplistic filtering
        stmt = stmt.where(DecisionLog.outcome == result)
        
    decisions = db.execute(stmt).scalars().all()
    
    results = []
    for d in decisions:
        ctx = d.decision_context or {}
        strategy_name = ctx.get("strategy_name", "Unknown Strategy")
        
        if strategy and strategy.lower() not in strategy_name.lower():
            continue
            
        risk_status = "APPROVED" if d.outcome.value in ["EXECUTED", "COMPLETED", "OPENED"] else "REJECTED"
        
        results.append(JournalEntryResponse(
            decision_id=str(d.id),
            timestamp=d.created_at,
            strategy=strategy_name,
            decision=d.decision_type.value,
            reason=d.reason,
            risk_status=risk_status,
            execution_status=d.outcome.value
        ))
        
    return results
