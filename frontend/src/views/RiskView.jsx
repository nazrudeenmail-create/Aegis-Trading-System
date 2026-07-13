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

  if (error) return <div className="p-8 text-rose-400">Failed to load risk profile. Ensure the orchestrator is running.</div>;
  if (!riskProfile) return <div className="p-8 text-slate-400">Loading risk parameters...</div>;

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
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white tracking-tight">Risk Management</h1>

      {/* ── Global Risk Parameters ── */}
      <div className="bg-slate-950 p-6 rounded-xl border border-slate-800 max-w-2xl">
        <h2 className="text-lg font-semibold text-white mb-4">Global Risk Parameters</h2>
        <div className="space-y-4">
          <div className="flex justify-between items-center p-4 bg-slate-900 rounded border border-slate-700">
            <div>
              <div className="font-medium text-white">Risk Per Trade</div>
              <div className="text-sm text-slate-400">Account percentage to risk per trade</div>
            </div>
            <div className="text-xl font-bold text-slate-300">
              {riskProfile.risk_per_trade_percent.toFixed(1)}%
            </div>
          </div>
          <div className="flex justify-between items-center p-4 bg-slate-900 rounded border border-slate-700">
            <div>
              <div className="font-medium text-white">Max Open Risk</div>
              <div className="text-sm text-slate-400">Total concurrent risk across all positions</div>
            </div>
            <div className="text-xl font-bold text-slate-300">
              {riskProfile.max_open_risk_percent.toFixed(1)}%
            </div>
          </div>
          <div className="flex justify-between items-center p-4 bg-slate-900 rounded border border-slate-700">
            <div>
              <div className="font-medium text-white">Max Daily Drawdown</div>
              <div className="text-sm text-slate-400">Stop trading if daily loss exceeds this</div>
            </div>
            <div className="text-xl font-bold text-slate-300">
              {riskProfile.max_daily_drawdown_percent.toFixed(1)}%
            </div>
          </div>
        </div>
      </div>

      {/* ── Portfolio Heat ── */}
      <div className="bg-slate-950 p-6 rounded-xl border border-slate-800">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-white">Portfolio Heat</h2>
          <div className="text-xs text-slate-500">
            Total Exposure:{' '}
            <span className={`font-bold ${totalExposurePercent > maxRisk * 0.8 ? 'text-rose-400' : 'text-emerald-400'}`}>
              {totalExposurePercent.toFixed(2)}%
            </span>
            {' '}/ {maxRisk}% max
          </div>
        </div>

        {/* Total risk bar */}
        <div className="mb-6">
          <div className="flex justify-between text-xs text-slate-400 mb-1">
            <span>Total Portfolio Risk</span>
            <span>{totalExposurePercent.toFixed(2)}% of {maxRisk}%</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all ${
                totalExposurePercent / maxRisk > 0.8 ? 'bg-rose-500' :
                totalExposurePercent / maxRisk > 0.5 ? 'bg-amber-500' : 'bg-indigo-500'
              }`}
              style={{ width: `${Math.min((totalExposurePercent / maxRisk) * 100, 100)}%` }}
            />
          </div>
        </div>

        {instrumentExposures.length === 0 ? (
          <div className="space-y-3">
            <div className="text-xs text-slate-500 mb-3">No open positions — showing watched instruments at 0% exposure.</div>
            {instruments.slice(0, 8).map(inst => (
              <div key={inst.id} className="flex items-center gap-3">
                <div className="w-24 text-xs font-bold text-slate-400 truncate">{inst.symbol}</div>
                <div className="flex-1 bg-slate-800 rounded-full h-2">
                  <div className="h-2 rounded-full bg-slate-700" style={{ width: '0%' }} />
                </div>
                <div className="w-16 text-right text-xs text-slate-600">0.00%</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {instrumentExposures.map(({ symbol, exposurePercent }) => {
              const pct = Math.min((exposurePercent / maxRisk) * 100, 100);
              return (
                <div key={symbol} className="flex items-center gap-3">
                  <div className="w-24 text-xs font-bold text-white truncate">{symbol}</div>
                  <div className="flex-1 bg-slate-800 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        pct > 80 ? 'bg-rose-500' : pct > 50 ? 'bg-amber-500' : 'bg-indigo-500'
                      }`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <div className="w-16 text-right text-xs text-slate-300">
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
