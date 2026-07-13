import React from 'react';
import useSWR from 'swr';
import { fetcher } from '../api';

export function RiskView() {
  const { data: riskProfile, error } = useSWR('/risk/profile', fetcher);
  const { data: positionsData } = useSWR('/broker/positions/open', fetcher, { fallbackData: [] });
  const { data: watchData } = useSWR('/dashboard/instruments', fetcher, {
    refreshInterval: 15000,
    fallbackData: { instruments: [] },
  });
  const { data: summary } = useSWR('/dashboard/summary', fetcher, { fallbackData: null });

  if (error) return <div className="p-8" style={{ color: 'var(--danger)' }}>Failed to load risk profile. Ensure the orchestrator is running.</div>;
  if (!riskProfile) return <div className="p-8" style={{ color: 'var(--text-tertiary)' }}>Loading risk parameters...</div>;

  const balance = summary?.account?.balance ?? summary?.account_balance ?? 0;
  const instruments = watchData?.instruments ?? [];
  const positions = positionsData ?? [];

  // Build per-instrument risk from open positions
  const positionsBySymbol = {};
  for (const pos of positions) {
    positionsBySymbol[pos.symbol] = pos;
  }

  const maxRisk = riskProfile.max_open_risk_percent ?? 5;
  const riskPerTrade = riskProfile.risk_per_trade_percent ?? 1;

  // Compute total exposure (sum of all open position sizes as % of balance)
  let totalExposurePercent = 0;
  const instrumentExposures = instruments
    .filter(i => positionsBySymbol[i.symbol])
    .map(i => {
      const pos = positionsBySymbol[i.symbol];
      const exposurePercent = balance > 0
        ? Math.abs((pos.unrealized_pnl ?? 0) / balance) * 100
        : 0;
      totalExposurePercent += exposurePercent;
      return { symbol: i.symbol, asset_class: i.asset_class, exposurePercent };
    });

  return (
    <div className="space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>Risk Management</h1>

      {/* ── Global Risk Parameters ── */}
      <div className="glass-card p-6 max-w-2xl">
        <h2 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Global Risk Parameters</h2>
        <div className="space-y-3">
          <div className="metric-row">
            <div>
              <div className="font-medium" style={{ color: 'var(--text-primary)' }}>Risk Per Trade</div>
              <div className="text-sm" style={{ color: 'var(--text-tertiary)' }}>Account percentage to risk per trade</div>
            </div>
            <div className="text-xl font-bold" style={{ color: 'var(--text-secondary)' }}>
              {riskProfile.risk_per_trade_percent.toFixed(1)}%
            </div>
          </div>
          <div className="metric-row">
            <div>
              <div className="font-medium" style={{ color: 'var(--text-primary)' }}>Max Open Risk</div>
              <div className="text-sm" style={{ color: 'var(--text-tertiary)' }}>Total concurrent risk across all positions</div>
            </div>
            <div className="text-xl font-bold" style={{ color: 'var(--text-secondary)' }}>
              {riskProfile.max_open_risk_percent.toFixed(1)}%
            </div>
          </div>
          <div className="metric-row">
            <div>
              <div className="font-medium" style={{ color: 'var(--text-primary)' }}>Max Daily Drawdown</div>
              <div className="text-sm" style={{ color: 'var(--text-tertiary)' }}>Stop trading if daily loss exceeds this</div>
            </div>
            <div className="text-xl font-bold" style={{ color: 'var(--text-secondary)' }}>
              {riskProfile.max_daily_drawdown_percent.toFixed(1)}%
            </div>
          </div>
        </div>
      </div>

      {/* ── Portfolio Heat ── */}
      <div className="glass-card p-6 animate-fade-in-delay-1">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>Portfolio Heat</h2>
          <div className="text-xs" style={{ color: 'var(--text-tertiary)' }}>
            Total Exposure:{' '}
            <span className="font-bold" style={{ color: totalExposurePercent > maxRisk * 0.8 ? 'var(--danger)' : 'var(--success)' }}>
              {totalExposurePercent.toFixed(2)}%
            </span>
            {' '}/ {maxRisk}% max
          </div>
        </div>

        {/* Total risk bar */}
        <div className="mb-6">
          <div className="flex justify-between text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>
            <span>Total Portfolio Risk</span>
            <span>{totalExposurePercent.toFixed(2)}% of {maxRisk}%</span>
          </div>
          <div className="progress-track">
            <div
              className="progress-fill"
              style={{ 
                width: `${Math.min((totalExposurePercent / maxRisk) * 100, 100)}%`,
                background: totalExposurePercent / maxRisk > 0.8 ? 'var(--danger)' :
                            totalExposurePercent / maxRisk > 0.5 ? 'var(--warning)' : 'var(--accent-primary)'
              }}
            />
          </div>
        </div>

        {instrumentExposures.length === 0 ? (
          <div className="space-y-3">
            <div className="text-xs mb-3" style={{ color: 'var(--text-tertiary)' }}>No open positions — showing watched instruments at 0% exposure.</div>
            {instruments.slice(0, 8).map(inst => (
              <div key={inst.id} className="flex items-center gap-3">
                <div className="w-24 text-xs font-bold truncate" style={{ color: 'var(--text-secondary)' }}>{inst.symbol}</div>
                <div className="flex-1 progress-track">
                  <div className="progress-fill" style={{ width: '0%' }} />
                </div>
                <div className="w-16 text-right text-xs" style={{ color: 'var(--text-tertiary)' }}>0.00%</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {instrumentExposures.map(({ symbol, exposurePercent }) => {
              const pct = Math.min((exposurePercent / maxRisk) * 100, 100);
              return (
                <div key={symbol} className="flex items-center gap-3">
                  <div className="w-24 text-xs font-bold truncate" style={{ color: 'var(--text-primary)' }}>{symbol}</div>
                  <div className="flex-1 progress-track">
                    <div
                      className="progress-fill"
                      style={{ 
                        width: `${pct}%`,
                        background: pct > 80 ? 'var(--danger)' : pct > 50 ? 'var(--warning)' : 'var(--accent-primary)'
                      }}
                    />
                  </div>
                  <div className="w-16 text-right text-xs" style={{ color: 'var(--text-secondary)' }}>
                    {exposurePercent.toFixed(2)}%
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
