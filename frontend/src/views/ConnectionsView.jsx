import React from 'react';
import { Link2, Clock, Activity, Settings2, ShieldAlert } from 'lucide-react';
import useSWR from 'swr';
import { api } from '../api';

export function ConnectionsView() {
  const { data, error, isLoading } = useSWR('/broker/connections', async (url) => {
    const res = await api.get(url);
    return res.data;
  }, { refreshInterval: 30000 });

  if (isLoading) return <div style={{ color: 'var(--text-tertiary)' }}>Loading connections...</div>;
  if (error) return <div style={{ color: 'var(--danger)' }}>Failed to load connection data</div>;

  const { connections, active_account } = data || {};
  const capital = connections?.find(c => c.id === 'capital');

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>Broker Connections</h1>
          <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>Manage execution venues and active sessions.</p>
        </div>
      </div>
      
      {active_account && capital?.status === 'CONNECTED' && (
        <div className="glass-card p-6 animate-fade-in-delay-1">
          <h3 className="text-sm font-medium mb-4 uppercase tracking-wider" style={{ color: 'var(--text-tertiary)' }}>Active Session Details</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>Account ID</p>
              <p className="font-medium" style={{ color: 'var(--text-primary)' }}>{active_account.account_id}</p>
            </div>
            <div>
              <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>Equity ({active_account.currency})</p>
              <p className="font-medium" style={{ color: 'var(--text-primary)' }}>${active_account.equity.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>Available Margin</p>
              <p className="font-medium" style={{ color: 'var(--text-primary)' }}>${active_account.available_margin.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>Used Margin</p>
              <p className="font-medium" style={{ color: 'var(--text-primary)' }}>${active_account.used_margin.toLocaleString()}</p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 animate-fade-in-delay-2">
        {/* Capital.com Broker */}
        <div className={`glass-card p-6 flex flex-col ${capital?.status !== 'CONNECTED' ? 'opacity-80' : ''}`}>
          <div className="flex justify-between items-start mb-4">
            <h2 className="text-lg font-semibold flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
              <Link2 size={18} style={{ color: capital?.status === 'CONNECTED' ? 'var(--accent-primary)' : 'var(--text-tertiary)' }}/> {capital?.name}
            </h2>
            <span className={capital?.status === 'CONNECTED' ? 'badge-success' : 'badge-neutral'}>
              {capital?.status || 'DISCONNECTED'}
            </span>
          </div>
          
          <div className="grid grid-cols-2 gap-4 mb-6 flex-grow">
            <div className="flex flex-col">
              <span className="text-xs mb-1 flex items-center gap-1" style={{ color: 'var(--text-secondary)' }}><Activity size={12}/> API Health</span>
              <span className="text-sm" style={{ color: 'var(--text-primary)' }}>{capital?.api_health || 'Unknown'}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs mb-1 flex items-center gap-1" style={{ color: 'var(--text-secondary)' }}><Clock size={12}/> Latency</span>
              <span className="text-sm" style={{ color: 'var(--text-primary)' }}>{capital?.latency_ms || 0} ms</span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>Reconnects Today</span>
              <span className="text-sm" style={{ color: 'var(--text-primary)' }}>{capital?.reconnects_today || 0}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>Last Heartbeat</span>
              <span className="text-sm" style={{ color: 'var(--text-primary)' }}>
                {capital?.last_heartbeat ? new Date(capital.last_heartbeat).toLocaleTimeString() : 'N/A'}
              </span>
            </div>
          </div>

          <div className="flex justify-between items-center pt-4" style={{ borderTop: '1px solid var(--border-primary)' }}>
            <span className="text-xs flex items-center gap-1" style={{ color: 'var(--accent-primary)' }}>
              <Settings2 size={14}/> {capital?.environment} Environment
            </span>
            <button className="text-sm hover:underline" style={{ color: 'var(--accent-primary)' }}>Manage Session</button>
          </div>
        </div>
      </div>
    </div>
  );
}
