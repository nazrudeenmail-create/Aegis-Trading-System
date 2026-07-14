import time
from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime, timezone
from app.analytics.events import EventBus, PipelineMetricsEvent

@dataclass
class StageMetrics:
    status: str = "Idle"
    last_update: float = 0.0
    throughput: int = 0
    
    # Latency tracking
    last_duration_ms: float = 0.0
    max_duration_ms: float = 0.0
    total_duration_ms: float = 0.0
    count: int = 0
    
    @property
    def avg_duration_ms(self) -> float:
        return self.total_duration_ms / self.count if self.count > 0 else 0.0

class TelemetryService:
    """
    Centralized monitoring service for ATS infrastructure observability.
    Engines do not emit metrics directly to EventBus; they use this service
    to record execution details, enforcing a consistent schema and
    maintaining live aggregate counters (throughput, latency, freshness).
    """
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.stages: Dict[str, StageMetrics] = {
            "Broker": StageMetrics(),
            "MarketData": StageMetrics(),
            "Indicators": StageMetrics(),
            "Strategy": StageMetrics(),
            "Risk": StageMetrics(),
            "Execution": StageMetrics()
        }
        
    def record_stage(self, stage: str, instrument: str, event_name: str, duration_ms: float, status: str = "SUCCESS"):
        now = time.time()
        
        if stage not in self.stages:
            self.stages[stage] = StageMetrics()
            
        metrics = self.stages[stage]
        metrics.status = status
        metrics.last_update = now
        metrics.throughput += 1
        metrics.last_duration_ms = duration_ms
        metrics.total_duration_ms += duration_ms
        metrics.count += 1
        if duration_ms > metrics.max_duration_ms:
            metrics.max_duration_ms = duration_ms
            
        # Emit the structured event to EventBus for the frontend live stream
        if self.event_bus:
            self.event_bus.publish(PipelineMetricsEvent(
                engine=stage,
                instrument=instrument,
                event_name=event_name,
                timestamp=datetime.now(timezone.utc).isoformat(),
                duration_ms=duration_ms,
                status=status
            ))

    def heartbeat(self, stage: str, status: str = "Healthy"):
        """Record an explicit heartbeat without an execution event."""
        if stage not in self.stages:
            self.stages[stage] = StageMetrics()
        self.stages[stage].status = status
        self.stages[stage].last_update = time.time()

    def get_health_snapshot(self) -> Dict[str, Any]:
        """Returns the in-memory health registry for the Pipeline Monitor UI."""
        now = time.time()
        snapshot = {
            "stages": {},
            "throughput": {},
            "latency": {}
        }
        
        for name, metrics in self.stages.items():
            freshness_sec = now - metrics.last_update if metrics.last_update > 0 else -1
            is_stale = freshness_sec > 120 and freshness_sec != -1 # Stale if > 2 minutes
            
            color = "var(--text-tertiary)"
            if is_stale:
                color = "var(--danger)"
            elif metrics.status.upper() in ["SUCCESS", "HEALTHY", "CONNECTED", "UPDATED", "SCANNING"]:
                color = "var(--success)"
            elif metrics.status.upper() in ["ERROR", "FAILED", "DISCONNECTED"]:
                color = "var(--danger)"
            elif metrics.last_update > 0:
                color = "var(--info)"
                
            display_freshness = f"{int(freshness_sec)}s ago" if freshness_sec >= 0 else "Never"
            
            snapshot["stages"][name] = {
                "status": "Stale" if is_stale else metrics.status,
                "color": color,
                "freshness": display_freshness
            }
            
            snapshot["throughput"][name] = metrics.throughput
            
            if metrics.count > 0:
                snapshot["latency"][name] = {
                    "last": f"{metrics.last_duration_ms:.1f} ms",
                    "avg": f"{metrics.avg_duration_ms:.1f} ms",
                    "max": f"{metrics.max_duration_ms:.1f} ms"
                }
                
        return snapshot
