import React from 'react';
import useSWR from 'swr';
import { fetcher } from '../api';

export function PortfolioView() {
  const { data: summary, error: summaryError } = useSWR('/dashboard/summary', fetcher);
  const { data: positionsData, error: positionsError } = useSWR('/broker/positions/open', fetcher);

  const isLoading = !summary && !summaryError;
  const isPositionsLoading = !positionsData && !positionsError;

  // Defaults if no data
  const mode = summary?.trading_mode || "Unknown";
  const balance = summary?.account_balance || 0;
  const margin = summary?.available_margin || 0;
  const pnl = summary?.unrealized_pnl || 0;

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
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-900/50 text-slate-400 border-b border-slate-800">
            <tr>
              <th className="p-4 font-medium">Symbol</th>
              <th className="p-4 font-medium">Direction</th>
              <th className="p-4 font-medium">Size</th>
              <th className="p-4 font-medium">Entry Price</th>
              <th className="p-4 font-medium">Current Price</th>
              <th className="p-4 font-medium text-right">Unrealized PnL</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {isPositionsLoading ? (
              <tr>
                <td colSpan="6" className="p-8 text-center text-slate-500">Loading positions...</td>
              </tr>
            ) : (!positionsData || positionsData.length === 0) ? (
              <tr>
                <td colSpan="6" className="p-8 text-center text-slate-500">No open positions.</td>
              </tr>
            ) : (
              positionsData.map((pos, idx) => (
                <tr key={idx} className="hover:bg-slate-900/50 transition">
                  <td className="p-4 font-bold text-white">{pos.symbol}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${pos.direction === 'LONG' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                      {pos.direction}
                    </span>
                  </td>
                  <td className="p-4 text-slate-300">{pos.size}</td>
                  <td className="p-4 text-slate-300">${pos.entry_price?.toFixed(2) || '--'}</td>
                  <td className="p-4 text-slate-300">${pos.current_price?.toFixed(2) || '--'}</td>
                  <td className={`p-4 text-right font-bold ${pos.unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    ${pos.unrealized_pnl?.toFixed(2) || '0.00'}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
