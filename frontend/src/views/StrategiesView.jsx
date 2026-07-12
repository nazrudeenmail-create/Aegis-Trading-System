import React from 'react';
import useSWR from 'swr';

export function StrategiesView() {
  const { data: rankingData, error } = useSWR('/strategy/ranking?symbol=BTCUSD');
  const isLoading = !rankingData && !error;
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white tracking-tight">Trading Strategies</h1>
      
      <div className="bg-slate-950 rounded-xl border border-slate-800 overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-900/50 text-slate-400 border-b border-slate-800">
            <tr>
              <th className="p-4 font-medium">Strategy Name</th>
              <th className="p-4 font-medium">Status</th>
              <th className="p-4 font-medium">Last Signal</th>
              <th className="p-4 font-medium">Confidence</th>
              <th className="p-4 font-medium">Candidates</th>
              <th className="p-4 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50 text-slate-300">
            {isLoading ? (
              <tr>
                <td colSpan="6" className="p-8 text-center text-slate-500">Loading strategy rankings...</td>
              </tr>
            ) : rankingData?.ranking ? (
              rankingData.ranking.map((s, i) => (
                <tr key={i} className="hover:bg-slate-900/50 transition">
                  <td className="p-4 font-medium text-white">
                    {s.strategy} 
                    {rankingData.winner === s.strategy && <span className="ml-2 text-xs bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded">Winner</span>}
                  </td>
                  <td className="p-4"><span className="text-emerald-400">Enabled</span></td>
                  <td className="p-4 text-slate-400">Historical: {s.historical?.toFixed(1) || 0}</td>
                  <td className="p-4">Compat: {s.compatibility?.toFixed(1) || 0}</td>
                  <td className="p-4">Setup: {s.setup?.toFixed(1) || 0}</td>
                  <td className="p-4 text-right font-bold text-indigo-400">{s.total?.toFixed(1) || 0}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="p-8 text-center text-slate-500">No strategy data available. Ensure market data is flowing.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
