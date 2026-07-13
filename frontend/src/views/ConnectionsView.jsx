import React from 'react';
import { Link2, Clock, Activity, Settings2, ShieldAlert } from 'lucide-react';
import useSWR from 'swr';
import { api } from '../api';

export function ConnectionsView() {
  const { data, error, isLoading } = useSWR('/broker/connections', async (url) => {
    const res = await api.get(url);
    return res.data;
  }, { refreshInterval: 30000 });

  if (isLoading) return <div className="text-slate-400">Loading connections...</div>;
  if (error) return <div className="text-red-400">Failed to load connection data</div>;

  const { connections, active_account } = data || {};
  const capital = connections?.find(c => c.id === 'capital');

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Broker Connections</h1>
          <p className="text-slate-400 mt-1 text-sm">Manage execution venues and active sessions.</p>
        </div>
      </div>
      
      {active_account && capital?.status === 'CONNECTED' && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-sm font-medium text-slate-400 mb-4 uppercase tracking-wider">Active Session Details</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-slate-500 text-xs">Account ID</p>
              <p className="text-white font-medium">{active_account.account_id}</p>
            </div>
            <div>
              <p className="text-slate-500 text-xs">Equity ({active_account.currency})</p>
              <p className="text-white font-medium">${active_account.equity.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-slate-500 text-xs">Available Margin</p>
              <p className="text-white font-medium">${active_account.available_margin.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-slate-500 text-xs">Used Margin</p>
              <p className="text-white font-medium">${active_account.used_margin.toLocaleString()}</p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-1 gap-6">
        {/* Capital.com Broker */}
        <div className={`bg-slate-950 p-6 rounded-xl border border-slate-800 flex flex-col ${capital?.status !== 'CONNECTED' ? 'opacity-80' : ''}`}>
          <div className="flex justify-between items-start mb-4">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Link2 size={18} className={capital?.status === 'CONNECTED' ? "text-blue-400" : "text-slate-500"}/> {capital?.name}
            </h2>
            <span className={`px-3 py-1 rounded-full text-xs font-medium border ${
              capital?.status === 'CONNECTED' 
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                : 'bg-slate-800 text-slate-400 border-slate-700'
            }`}>
              {capital?.status || 'DISCONNECTED'}
            </span>
          </div>
          
          <div className="grid grid-cols-2 gap-4 mb-6 flex-grow">
            <div className="flex flex-col">
              <span className="text-xs text-slate-500 mb-1 flex items-center gap-1"><Activity size={12}/> API Health</span>
              <span className="text-sm text-slate-200">{capital?.api_health || 'Unknown'}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs text-slate-500 mb-1 flex items-center gap-1"><Clock size={12}/> Latency</span>
              <span className="text-sm text-slate-200">{capital?.latency_ms || 0} ms</span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs text-slate-500 mb-1">Reconnects Today</span>
              <span className="text-sm text-slate-200">{capital?.reconnects_today || 0}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs text-slate-500 mb-1">Last Heartbeat</span>
              <span className="text-sm text-slate-200">
                {capital?.last_heartbeat ? new Date(capital.last_heartbeat).toLocaleTimeString() : 'N/A'}
              </span>
            </div>
          </div>

          <div className="flex justify-between items-center border-t border-slate-800 pt-4">
            <span className="text-xs text-indigo-400 flex items-center gap-1"><Settings2 size={14}/> {capital?.environment} Environment</span>
            <button className="text-indigo-400 text-sm hover:underline">Manage Session</button>
          </div>
        </div>
      </div>
    </div>
  );
}
