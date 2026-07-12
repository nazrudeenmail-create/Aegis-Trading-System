from app.market_analysis.models import MarketSnapshot
from app.strategy.models.ranking import StrategyProfile

class CompatibilityScorer:
    """
    Computes the Live Compatibility Score (0-100) for a strategy based on current market conditions.
    """
    @staticmethod
    def score(profile: StrategyProfile, snapshot: MarketSnapshot) -> float:
        base_score = 100.0
        
        # 1. Regime Multiplier
        regime_val = snapshot.regime.regime if snapshot.regime else None
        if regime_val in profile.preferred_regimes:
            regime_mult = 1.0
        elif regime_val in profile.acceptable_regimes:
            regime_mult = 0.75
        elif regime_val in profile.avoided_regimes:
            regime_mult = 0.40
        else:
            regime_mult = 0.50 # Neutral unknown
            
        # 2. ADX Multiplier
        adx_mult = 1.0
        if profile.minimum_adx is not None and snapshot.adx is not None and snapshot.adx.adx is not None:
            if snapshot.adx.adx >= profile.minimum_adx:
                adx_mult = 1.0
            else:
                adx_mult = max(0.5, float(snapshot.adx.adx) / profile.minimum_adx)

        # 3. Trend / Direction Multiplier
        trend_mult = 1.0
        if profile.preferred_direction is not None and snapshot.trend is not None and snapshot.trend.direction is not None:
            if str(snapshot.trend.direction.value).upper() == profile.preferred_direction.upper():
                trend_mult = 1.0
            else:
                trend_mult = 0.8
                
        # 4. Volatility Preference Multiplier
        vol_mult = 1.0
        if profile.volatility_preference and snapshot.volatility and snapshot.volatility.state:
            pref = profile.volatility_preference.lower()
            actual = str(snapshot.volatility.state.value).lower()
            
            if pref in actual or actual in pref:
                vol_mult = 1.0
            else:
                vol_mult = 0.9
                
        # 5. Volume Multiplier (Assume average volume checking if available, else neutral)
        volume_mult = 1.0
        # If snapshot had volume insight, we'd adjust here. For now, we'll keep it 1.0 unless explicitly told.
        # e.g., if snapshot.volume_insight == "LOW": volume_mult = 0.8
        
        # 6. ATR Expansion Multiplier
        atr_mult = 1.0
        # If ATR expansion is higher than max_atr_expansion, penalize
        
        final_score = base_score * regime_mult * adx_mult * trend_mult * vol_mult * volume_mult * atr_mult
        return float(max(0.0, min(100.0, final_score)))
