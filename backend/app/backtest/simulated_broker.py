from decimal import Decimal
from typing import List, Optional
from datetime import datetime

from app.strategy.models import TradeCandidate, TradeDirection
from app.market.domain.candle import Candle
from app.risk.engine import RiskEngine
from app.risk.models import RiskProfile
from app.backtest.models import BacktestConfig

class SimulatedPosition:
    def __init__(
        self, 
        candidate: TradeCandidate, 
        entry_price: Decimal, 
        position_size: Decimal,
        opened_at: datetime
    ):
        self.candidate = candidate
        self.entry_price = entry_price
        self.position_size = position_size
        self.opened_at = opened_at
        self.stop_loss = candidate.stop_loss
        self.take_profit = candidate.take_profit


class SimulatedTrade:
    def __init__(
        self,
        position: SimulatedPosition,
        exit_price: Decimal,
        closed_at: datetime,
        pnl: Decimal,
        commission: Decimal,
        reason: str
    ):
        self.position = position
        self.exit_price = exit_price
        self.closed_at = closed_at
        self.pnl = pnl
        self.commission = commission
        self.reason = reason


class SimulatedBroker:
    """
    Virtual broker that handles position sizing, slippage, spread, and intraday SL/TP execution.
    """
    def __init__(self, config: BacktestConfig, risk_profile: RiskProfile):
        self.config = config
        self.risk_engine = RiskEngine()
        self.risk_profile = risk_profile
        
        self.balance = config.initial_balance
        self.active_positions: List[SimulatedPosition] = []
        self.closed_trades: List[SimulatedTrade] = []
        
        # Risk tracking context
        self.daily_loss_fiat = Decimal("0.0")
        self.current_day: Optional[int] = None
        
    def submit_candidate(self, candidate: TradeCandidate, current_time: datetime) -> bool:
        """
        Evaluate and potentially execute a candidate based on Risk Rules and Costs.
        Returns True if executed, False if rejected.
        """
        if self.current_day is not None and current_time.day != self.current_day:
            self.daily_loss_fiat = Decimal("0.0")
            
        self.current_day = current_time.day
        
        # Current risk exposure
        current_open_risk = sum(
            [abs(p.entry_price - p.stop_loss) * p.position_size for p in self.active_positions]
        )
        
        context = {
            "current_open_risk_fiat": current_open_risk,
            "daily_loss_fiat": self.daily_loss_fiat
        }
        
        # Keep risk profile in sync with compounded backtest balance
        self.risk_profile.account_balance = self.balance
        
        assessment = self.risk_engine.evaluate(candidate, self.risk_profile, context)
        
        if not assessment.is_approved:
            return False
            
        # Execute trade with slippage and spread penalty
        spread_penalty = self.config.spread / Decimal("2.0")
        slippage_penalty = self.config.slippage
        
        penalty = spread_penalty + slippage_penalty
        
        if candidate.direction == TradeDirection.LONG:
            fill_price = candidate.entry_price + penalty
        else:
            fill_price = candidate.entry_price - penalty
            
        position = SimulatedPosition(
            candidate=candidate,
            entry_price=fill_price,
            position_size=assessment.position_size,
            opened_at=current_time
        )
        
        # Deduct commission on entry
        self.balance -= self.config.commission
        self.active_positions.append(position)
        
        return True

    def process_1m_candle(self, candle: Candle):
        """
        Evaluates open positions against a new 1-minute candle tick-by-tick logic.
        """
        if not self.active_positions:
            return
            
        closed_this_tick = []
        
        for pos in self.active_positions:
            direction = pos.candidate.direction
            
            # Did it hit SL?
            hit_sl = False
            hit_tp = False
            
            if direction == TradeDirection.LONG:
                if candle.low <= pos.stop_loss: hit_sl = True
                if pos.take_profit and candle.high >= pos.take_profit: hit_tp = True
            else:
                if candle.high >= pos.stop_loss: hit_sl = True
                if pos.take_profit and candle.low <= pos.take_profit: hit_tp = True
                
            if hit_sl and hit_tp:
                # Priority mapping logic. If both hit in a single 1M candle, we assume the one closest to Open happened first.
                dist_to_sl = abs(candle.open - float(pos.stop_loss))
                dist_to_tp = abs(candle.open - float(pos.take_profit))
                
                if dist_to_sl <= dist_to_tp:
                    hit_tp = False
                else:
                    hit_sl = False
            
            if hit_sl:
                self._close_position(pos, pos.stop_loss, candle.timestamp, "STOP_LOSS")
                closed_this_tick.append(pos)
            elif hit_tp:
                self._close_position(pos, pos.take_profit, candle.timestamp, "TAKE_PROFIT")
                closed_this_tick.append(pos)
                
        for pos in closed_this_tick:
            self.active_positions.remove(pos)

    def _close_position(self, position: SimulatedPosition, exit_price: Decimal, timestamp: datetime, reason: str):
        # Penalty for exiting (spread/slippage on market exit like SL, TP might be limit but let's be conservative)
        penalty = (self.config.spread / Decimal("2.0")) + self.config.slippage
        if position.candidate.direction == TradeDirection.LONG:
            actual_exit = exit_price - penalty
            pnl_per_unit = actual_exit - position.entry_price
        else:
            actual_exit = exit_price + penalty
            pnl_per_unit = position.entry_price - actual_exit
            
        total_pnl = pnl_per_unit * position.position_size
        
        self.balance += total_pnl
        self.balance -= self.config.commission
        
        if total_pnl < 0:
            self.daily_loss_fiat += abs(total_pnl)
            
        trade = SimulatedTrade(
            position=position,
            exit_price=actual_exit,
            closed_at=timestamp,
            pnl=total_pnl,
            commission=self.config.commission * Decimal("2.0"), # Total commission for round trip
            reason=reason
        )
        self.closed_trades.append(trade)
