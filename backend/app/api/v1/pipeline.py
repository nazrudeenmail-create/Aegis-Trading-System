from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Dict, Any
from app.api.auth import get_current_user, User
from app.core.state import global_state
from pydantic import BaseModel
from datetime import datetime, timezone

router = APIRouter()

class PipelineHealthResponse(BaseModel):
    stages: Dict[str, Any]
    throughput: Dict[str, int]
    latency: Dict[str, Any]

@router.get("/health", response_model=PipelineHealthResponse)
def get_pipeline_health(current_user: User = Depends(get_current_user)):
    """
    Returns real-time pipeline health, throughput, and latency
    served directly from the TelemetryService (In-Memory Health Registry).
    """
    if not global_state.telemetry:
        return PipelineHealthResponse(
            stages={"System": {"status": "Starting", "color": "var(--warning)", "freshness": "Just now"}},
            throughput={},
            latency={}
        )
        
    snapshot = global_state.telemetry.get_health_snapshot()
    
    return PipelineHealthResponse(
        stages=snapshot.get("stages", {}),
        throughput=snapshot.get("throughput", {}),
        latency=snapshot.get("latency", {})
    )
