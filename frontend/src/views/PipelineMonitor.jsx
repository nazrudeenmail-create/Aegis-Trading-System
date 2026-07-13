import React, { useState, useEffect } from 'react';
import useSWR from 'swr';
import { fetcher, wsClient } from '../api';
import { Radio, CheckCircle2, XCircle, Clock, AlertTriangle, Wifi } from 'lucide-react';

function PipelineRow({ instrument, events }) {
  const { data: status } = useSWR(`/pipeline/status?symbol=${instrument.symbol}`, fetcher, { refreshInterval: 5000 });

  return (
    <tr>
      <td style={{ color: 'var(--text-primary)', fontWeight: 'bold' }}>{instrument.symbol}</td>
      <td>
        <span className={status?.session === 'REGULAR' ? 'badge-success' : 'badge-neutral'}>
          {status?.session || 'UNKNOWN'}
        </span>
      </td>
      <td className="text-xs font-mono" style={{ color: 'var(--text-secondary)' }}>
        {status?.data_status || '-'}
      </td>
      <td className="text-xs font-mono" style={{ color: 'var(--accent-primary)' }}>
        {status?.intelligence_status || '-'}
      </td>
      <td>
        <div className="flex flex-col">
          <span className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>{status?.strategy_status || '-'}</span>
          {status?.ranking_score > 0 && (
            <span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>Score: {status.ranking_score.toFixed(1)} pts</span>
          )}
        </div>
      </td>
      <td className="text-xs font-mono" style={{ color: 'var(--text-secondary)' }}>
        {status?.risk_status || '-'}
      </td>
      <td className="text-xs font-mono">
        <span style={{ color: status?.position_status === 'OPEN' ? 'var(--success)' : 'var(--text-tertiary)', fontWeight: status?.position_status === 'OPEN' ? 'bold' : 'normal' }}>
          {status?.position_status || '-'}
        </span>
      </td>
    </tr>
  );
}

export function PipelineMonitor() {
  const [events, setEvents] = useState([]);
  const { data: instruments } = useSWR('/instruments/', fetcher, { refreshInterval: 30000 });

  useEffect(() => {
    const unsub = wsClient.subscribe((msg) => {
      if (msg.event) {
        setEvents((prev) => [msg, ...prev].slice(0, 100));
      }
    });
    return unsub;
  }, []);

  const activeInstruments = instruments?.filter(i => i.status === 'ACTIVE' || i.status === 'WATCHLIST') || [];

  return (
    <div className="space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>Pipeline Monitor</h1>

      {/* Active Instruments Pipeline Status */}
      <div className="glass-card-static overflow-hidden animate-fade-in-delay-1">
        <div className="section-header">
          <h2 className="section-title">
            <Radio size={18} style={{ color: 'var(--accent-primary)' }}/> Pipeline Status Monitor
          </h2>
        </div>
        {activeInstruments.length === 0 ? (
          <div className="p-8 text-center" style={{ color: 'var(--text-tertiary)' }}>
            No active or watchlist instruments. Go to Instruments to add one.
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Session</th>
                <th>Market Data</th>
                <th>Intelligence</th>
                <th>Strategy</th>
                <th>Risk</th>
                <th>Position</th>
              </tr>
            </thead>
            <tbody>
              {activeInstruments.map(inst => (
                <PipelineRow key={inst.id} instrument={inst} events={events} />
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Live Event Feed */}
      <div className="glass-card-static overflow-hidden animate-fade-in-delay-2">
        <div className="section-header">
          <h2 className="section-title">
            <Radio size={18} style={{ color: 'var(--accent-primary)' }}/> Live Pipeline Events
          </h2>
        </div>
        <div className="p-4 max-h-[400px] overflow-y-auto" style={{ background: 'var(--bg-secondary)' }}>
          {events.length === 0 ? (
            <div className="text-sm text-center py-8" style={{ color: 'var(--text-tertiary)' }}>
              Waiting for orchestrator events...
            </div>
          ) : (
            <div className="space-y-2">
              {events.map((evt, i) => (
                <div key={i} className="flex items-start gap-3 p-2 rounded text-xs" style={{ background: 'var(--bg-primary)', border: '1px solid var(--border-primary)' }}>
                  <span className="font-mono whitespace-nowrap" style={{ color: 'var(--text-tertiary)' }}>
                    {evt.event || 'system.log'}
                  </span>
                  <span className="font-mono" style={{ color: 'var(--text-secondary)' }}>
                    {JSON.stringify(evt.data || evt).slice(0, 120)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}