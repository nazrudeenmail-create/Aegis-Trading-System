import React from 'react';
import useSWR from 'swr';

export function PortfolioView() {
  const { data: summary, error } = useSWR('/dashboard/summary');

  const isLoading = !summary && !error;

  // Defaults if no data
  const mode = summary?.trading_mode || "Unknown";
  const balance = summary?.account_balance || 0;
  const margin = summary?.available_margin || 0;
  const pnl = summary?.unrealized_pnl || 0;
  const positions = summary?.open_positions || 0;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white tracking-tight">Portfolio</h1>
        <div className="text-sm font-medium text-slate-400 bg-slate-900 px-3 py-1 rounded border border-slate-700">
          Current Account: <span className="text-indigo-400">{mode}</span>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-950 p-6 rounded-xl border border-slate-800">
          <h2 className="text-sm font-medium text-slate-400 mb-2">Total Equity</h2>
          <div className="text-3xl font-bold text-white">
            {isLoading ? "..." : `$${balance.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`}
          </div>
        </div>
        <div className="bg-slate-950 p-6 rounded-xl border border-slate-800">
          <h2 className="text-sm font-medium text-slate-400 mb-2">Available Margin</h2>
          <div className="text-3xl font-bold text-white">
            {isLoading ? "..." : `$${margin.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`}
          </div>
        </div>
        <div className="bg-slate-950 p-6 rounded-xl border border-slate-800">
          <h2 className="text-sm font-medium text-slate-400 mb-2">Unrealized PnL</h2>
          <div className={`text-3xl font-bold ${pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {isLoading ? "..." : `$${pnl.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`}
          </div>
        </div>
      </div>

      <div className="bg-slate-950 rounded-xl border border-slate-800 overflow-hidden mt-6">
        <div className="p-4 border-b border-slate-800">
          <h2 className="font-semibold text-white">Open Positions</h2>
        </div>
        <div className="p-8 text-center text-slate-500 text-sm">
          {isLoading ? "Loading positions..." : 
           positions > 0 ? `${positions} open position(s).` : 
           `No open positions in ${mode} mode.`}
        </div>
      </div>
    </div>
  );
}
