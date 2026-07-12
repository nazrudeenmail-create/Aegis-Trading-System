import React from 'react';
import useSWR from 'swr';

export function RiskView() {
  const { data: riskProfile, error } = useSWR('/risk/profile');
  const isLoading = !riskProfile && !error;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white tracking-tight">Risk Management</h1>
      
      <div className="bg-slate-950 p-6 rounded-xl border border-slate-800 max-w-2xl">
        <h2 className="text-lg font-semibold text-white mb-4">Global Risk Parameters</h2>
        <div className="space-y-4">
          <div className="flex justify-between items-center p-4 bg-slate-900 rounded border border-slate-700">
            <div>
              <div className="font-medium text-white">Max Daily Loss</div>
              <div className="text-sm text-slate-400">Stop trading if daily loss exceeds this amount</div>
            </div>
            <div className="text-xl font-bold text-slate-300">
              {isLoading ? "..." : `$${riskProfile.max_daily_loss.toLocaleString()}`}
            </div>
          </div>
          <div className="flex justify-between items-center p-4 bg-slate-900 rounded border border-slate-700">
            <div>
              <div className="font-medium text-white">Max Open Positions</div>
              <div className="text-sm text-slate-400">Maximum concurrent trades allowed</div>
            </div>
            <div className="text-xl font-bold text-slate-300">
              {isLoading ? "..." : riskProfile.max_open_positions}
            </div>
          </div>
          <div className="flex justify-between items-center p-4 bg-slate-900 rounded border border-slate-700">
            <div>
              <div className="font-medium text-white">Max Risk Per Trade</div>
              <div className="text-sm text-slate-400">Account percentage to risk per trade</div>
            </div>
            <div className="text-xl font-bold text-slate-300">
              {isLoading ? "..." : `${(riskProfile.max_risk_per_trade * 100).toFixed(1)}%`}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
