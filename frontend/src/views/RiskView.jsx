import React from 'react';
import useSWR from 'swr';
import { fetcher } from '../api';

export function RiskView() {
  const { data: riskProfile, error } = useSWR('/risk/profile', fetcher);
  const isLoading = !riskProfile && !error;

  if (error) return <div className="p-8 text-rose-400">Failed to load risk profile. Ensure the orchestrator is running.</div>;
  if (!riskProfile) return <div className="p-8 text-slate-400">Loading risk parameters...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white tracking-tight">Risk Management</h1>
      
      <div className="bg-slate-950 p-6 rounded-xl border border-slate-800 max-w-2xl">
        <h2 className="text-lg font-semibold text-white mb-4">Global Risk Parameters</h2>
        <div className="space-y-4">
          <div className="flex justify-between items-center p-4 bg-slate-900 rounded border border-slate-700">
            <div>
              <div className="font-medium text-white">Risk Per Trade</div>
              <div className="text-sm text-slate-400">Account percentage to risk per trade</div>
            </div>
            <div className="text-xl font-bold text-slate-300">
              {isLoading ? "..." : `${riskProfile.risk_per_trade_percent.toFixed(1)}%`}
            </div>
          </div>
          <div className="flex justify-between items-center p-4 bg-slate-900 rounded border border-slate-700">
            <div>
              <div className="font-medium text-white">Max Open Risk</div>
              <div className="text-sm text-slate-400">Total concurrent risk allowed across all positions</div>
            </div>
            <div className="text-xl font-bold text-slate-300">
              {isLoading ? "..." : `${riskProfile.max_open_risk_percent.toFixed(1)}%`}
            </div>
          </div>
          <div className="flex justify-between items-center p-4 bg-slate-900 rounded border border-slate-700">
            <div>
              <div className="font-medium text-white">Max Daily Drawdown</div>
              <div className="text-sm text-slate-400">Stop trading if daily loss exceeds this percentage</div>
            </div>
            <div className="text-xl font-bold text-slate-300">
              {isLoading ? "..." : `${riskProfile.max_daily_drawdown_percent.toFixed(1)}%`}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
