import React, { useState, useEffect } from 'react';
import useSWR from 'swr';
import { fetcher, wsClient } from '../api';
import { Radio, CheckCircle2, XCircle, Clock, AlertTriangle, Wifi } from 'lucide-react';

function PipelineRow({ instrument, events }) {
  const { data: status } = useSWR(`/pipeline/status?symbol=${instrument.symbol}`, fetcher, { refreshInterval: 5000 });

  return (
    <tr className="hover:bg-slate-900/50 transition">
      <td className="p-4 font-bold text-white">{instrument.symbol}</td>
      <td className="p-4">
        <span className={`px-2 py-1 rounded text-xs font-medium ${
          status?.session === 'REGULAR' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-800 text-slate-400'
        }`}>
          {status?.session || 'UNKNOWN'}
        </span>
      </td>
      <td className="p-4 text-xs font-mono text-slate-300">
        {status?.data_status || '-'}
      </td>
      <td className="p-4 text-xs font-mono text-indigo-300">
        {status?.intelligence_status || '-'}
      </td>
      <td className="p-4">
        <div className="flex flex-col">
          <span className="text-xs text-slate-300 font-medium">{status?.strategy_status || '-'}</span>
          {status?.ranking_score > 0 && (
            <span className="text-xs text-slate-500">Score: {status.ranking_score.toFixed(1)} pts</span>
          )}
        </div>
      </td>
      <td className="p-4 text-xs font-mono text-slate-300">
        {status?.risk_status || '-'}
      </td>
      <td className="p-4 text-xs font-mono">
        <span className={status?.position_status === 'OPEN' ? 'text-emerald-400 font-bold' : 'text-slate-500'}>
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
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white tracking-tight">Pipeline Monitor</h1>

      {/* Active Instruments Pipeline Status */}
      <div className="bg-slate-950 rounded-xl border border-slate-800 overflow-hidden">
        <div className="p-4 border-b border-slate-800">
          <h2 className="font-semibold text-white flex items-center gap-2">
            <Radio size={18} className="text-indigo-400"/> Pipeline Status Monitor
          </h2>
        </div>
        {activeInstruments.length === 0 ? (
          <div className="p-8 text-center text-slate-500">
            No active or watchlist instruments. Go to Instruments to add one.
          </div>
        ) : (
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-900/50 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="p-4 font-medium">Symbol</th>
                <th className="p-4 font-medium">Session</th>
                <th className="p-4 font-medium">Market Data</th>
                <th className="p-4 font-medium">Intelligence</th>
                <th className="p-4 font-medium">Strategy</th>
                <th className="p-4 font-medium">Risk</th>
                <th className="p-4 font-medium">Position</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {activeInstruments.map(inst => (
                <PipelineRow key={inst.id} instrument={inst} events={events} />
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Live Event Feed */}
      <div className="bg-slate-950 rounded-xl border border-slate-800 overflow-hidden">
        <div className="p-4 border-b border-slate-800">
          <h2 className="font-semibold text-white flex items-center gap-2">
            <Radio size={18} className="text-indigo-400"/> Live Pipeline Events
          </h2>
        </div>
        <div className="p-4 max-h-[400px] overflow-y-auto">
          {events.length === 0 ? (
            <div className="text-sm text-slate-500 text-center py-8">
              Waiting for orchestrator events...
            </div>
          ) : (
            <div className="space-y-2">
              {events.map((evt, i) => (
                <div key={i} className="flex items-start gap-3 p-2 bg-slate-900/50 rounded border border-slate-800 text-xs">
                  <span className="text-slate-500 font-mono whitespace-nowrap">
                    {evt.event || 'system.log'}
                  </span>
                  <span className="text-slate-400 font-mono">
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