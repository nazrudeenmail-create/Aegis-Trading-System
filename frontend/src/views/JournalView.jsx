import React from 'react';
import useSWR from 'swr';
import { fetcher } from '../api';
import { ScrollText, CheckCircle2, XCircle, Clock, AlertTriangle } from 'lucide-react';

export function JournalView() {
  const { data: decisions, error, isLoading } = useSWR('/journal/latest?limit=50', fetcher, { refreshInterval: 10000 });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white tracking-tight">Decision Journal</h1>

      <div className="bg-slate-950 rounded-xl border border-slate-800 overflow-hidden">
        <div className="p-4 border-b border-slate-800">
          <h2 className="font-semibold text-white flex items-center gap-2">
            <ScrollText size={18} className="text-indigo-400" /> All Trading Decisions
          </h2>
        </div>
        {isLoading ? (
          <div className="p-8 text-center text-slate-500">Loading decisions...</div>
        ) : !decisions || decisions.length === 0 ? (
          <div className="p-8 text-center text-slate-500">
            <ScrollText size={24} className="mx-auto mb-2 text-slate-600" />
            No decisions recorded yet. Decisions are logged when the Strategy or Risk Engine evaluates a candidate.
          </div>
        ) : (
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-900/50 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="p-4 font-medium">Time</th>
                <th className="p-4 font-medium">Strategy</th>
                <th className="p-4 font-medium">Decision</th>
                <th className="p-4 font-medium">Risk</th>
                <th className="p-4 font-medium">Execution</th>
                <th className="p-4 font-medium">Reason</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {decisions.map((d, i) => (
                <tr key={d.decision_id || i} className="hover:bg-slate-900/50 transition">
                  <td className="p-4 text-slate-400 text-xs font-mono">
                    {d.timestamp ? new Date(d.timestamp).toLocaleTimeString() : '--'}
                  </td>
                  <td className="p-4 font-medium text-white">{d.strategy || 'Unknown'}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${d.decision === 'REJECT' ? 'bg-rose-500/10 text-rose-400' : 'bg-emerald-500/10 text-emerald-400'}`}>
                      {d.decision || 'PENDING'}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className={`flex items-center gap-1 text-xs ${d.risk_status === 'APPROVED' ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {d.risk_status === 'APPROVED' ? <CheckCircle2 size={12} /> : <XCircle size={12} />}
                      {d.risk_status || 'UNKNOWN'}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      d.execution_status === 'EXECUTED' || d.execution_status === 'WIN' ? 'bg-emerald-500/10 text-emerald-400' :
                      d.execution_status === 'REJECTED' || d.execution_status === 'LOSS' ? 'bg-rose-500/10 text-rose-400' :
                      'bg-slate-800 text-slate-400'
                    }`}>
                      {d.execution_status || 'PENDING'}
                    </span>
                  </td>
                  <td className="p-4 text-slate-400 text-xs max-w-[200px] truncate" title={d.reason}>
                    {d.reason || '--'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}