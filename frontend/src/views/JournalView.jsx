import React from 'react';
import useSWR from 'swr';
import { fetcher } from '../api';
import { ScrollText, CheckCircle2, XCircle, Clock, AlertTriangle } from 'lucide-react';

export function JournalView() {
  const { data: decisions, error, isLoading } = useSWR('/journal/latest?limit=50', fetcher, { refreshInterval: 10000 });

  return (
    <div className="space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>Decision Journal</h1>

      <div className="glass-card-static overflow-hidden animate-fade-in-delay-1">
        <div className="section-header">
          <h2 className="section-title">
            <ScrollText size={18} style={{ color: 'var(--accent-primary)' }} /> All Trading Decisions
          </h2>
        </div>
        {isLoading ? (
          <div className="p-8 text-center"><div className="skeleton h-4 w-1/2 mx-auto" /></div>
        ) : !decisions || decisions.length === 0 ? (
          <div className="p-8 text-center" style={{ color: 'var(--text-tertiary)' }}>
            <ScrollText size={24} className="mx-auto mb-2" style={{ color: 'var(--text-muted)' }} />
            No decisions recorded yet. Decisions are logged when the Strategy or Risk Engine evaluates a candidate.
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Strategy</th>
                <th>Decision</th>
                <th>Risk</th>
                <th>Execution</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              {decisions.map((d, i) => (
                <tr key={d.decision_id || i}>
                  <td className="text-xs font-mono" style={{ color: 'var(--text-secondary)' }}>
                    {d.timestamp ? new Date(d.timestamp).toLocaleTimeString() : '--'}
                  </td>
                  <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{d.strategy || 'Unknown'}</td>
                  <td>
                    <span className={d.decision === 'REJECT' ? 'badge-danger' : 'badge-success'}>
                      {d.decision || 'PENDING'}
                    </span>
                  </td>
                  <td>
                    <span className="flex items-center gap-1 text-xs" style={{ color: d.risk_status === 'APPROVED' ? 'var(--success)' : 'var(--danger)' }}>
                      {d.risk_status === 'APPROVED' ? <CheckCircle2 size={12} /> : <XCircle size={12} />}
                      {d.risk_status || 'UNKNOWN'}
                    </span>
                  </td>
                  <td>
                    <span className={
                      d.execution_status === 'EXECUTED' || d.execution_status === 'WIN' ? 'badge-success' :
                      d.execution_status === 'REJECTED' || d.execution_status === 'LOSS' ? 'badge-danger' :
                      'badge-neutral'
                    }>
                      {d.execution_status || 'PENDING'}
                    </span>
                  </td>
                  <td className="text-xs max-w-[200px] truncate" style={{ color: 'var(--text-secondary)' }} title={d.reason}>
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