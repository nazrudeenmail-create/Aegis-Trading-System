import React, { useState, useEffect } from 'react';
import { Settings, ShieldAlert, Power } from 'lucide-react';
import useSWR from 'swr';
import { api, fetcher } from '../api';

export function SettingsView() {
  const { data, isLoading, mutate } = useSWR('/system/status', fetcher);
  const [selectedMode, setSelectedMode] = useState('BROKER_DEMO');
  const [isApplying, setIsApplying] = useState(false);

  useEffect(() => {
    if (data?.account_mode) {
      // Map backend's "Demo" / "Live" to our radio button values
      setSelectedMode(data.account_mode.toLowerCase() === 'live' ? 'BROKER_LIVE' : 'BROKER_DEMO');
    }
  }, [data]);

  const handleApply = async () => {
    setIsApplying(true);
    try {
      // The backend expects 'account_mode' (e.g. "demo" or "live")
      const modeValue = selectedMode === 'BROKER_LIVE' ? 'live' : 'demo';
      await api.patch('/system/settings', { account_mode: modeValue });
      await mutate();
    } catch (e) {
      console.error(e);
    } finally {
      setIsApplying(false);
    }
  };

  if (isLoading) return <div style={{ color: 'var(--text-tertiary)' }}>Loading settings...</div>;

  return (
    <div className="space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>Trading Settings</h1>

      <div className="glass-card p-6 max-w-2xl animate-fade-in-delay-1">
        <h2 className="text-lg font-semibold flex items-center gap-2 mb-2" style={{ color: 'var(--text-primary)' }}>
          <Power size={18} style={{ color: 'var(--accent-primary)' }} /> Global Trading Mode
        </h2>
        <p className="text-sm mb-6 flex items-center gap-2" style={{ color: 'var(--text-secondary)' }}>
          <ShieldAlert size={14} /> Note: Changing this at runtime will not re-authenticate the broker until a restart.
        </p>

        <div className="space-y-4">
          <label className="flex items-start gap-4 p-4 rounded-lg border transition cursor-pointer" 
                 style={{ 
                   background: selectedMode === 'BROKER_DEMO' ? 'var(--accent-primary-dim)' : 'var(--bg-secondary)', 
                   borderColor: selectedMode === 'BROKER_DEMO' ? 'var(--accent-primary)' : 'var(--border-primary)' 
                 }}>
            <input 
              type="radio" 
              name="tradingMode" 
              value="BROKER_DEMO" 
              checked={selectedMode === 'BROKER_DEMO'}
              onChange={(e) => setSelectedMode(e.target.value)}
              className="mt-1 w-4 h-4 accent-indigo-500"
            />
            <div>
              <div className="font-semibold" style={{ color: 'var(--text-primary)' }}>Broker Demo</div>
              <div className="text-sm mt-1" style={{ color: 'var(--text-tertiary)' }}>Orders are sent to a live broker's demo/paper environment (e.g., Capital.com Demo). Simulates real latency.</div>
            </div>
          </label>

          <label className="flex items-start gap-4 p-4 rounded-lg border transition cursor-pointer" 
                 style={{ 
                   background: selectedMode === 'BROKER_LIVE' ? 'var(--danger-dim)' : 'var(--bg-secondary)', 
                   borderColor: selectedMode === 'BROKER_LIVE' ? 'var(--danger)' : 'var(--border-primary)' 
                 }}>
            <input 
              type="radio" 
              name="tradingMode" 
              value="BROKER_LIVE" 
              checked={selectedMode === 'BROKER_LIVE'}
              onChange={(e) => setSelectedMode(e.target.value)}
              className="mt-1 w-4 h-4 accent-red-500"
            />
            <div>
              <div className="font-semibold flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>Broker Live <ShieldAlert size={14} style={{ color: 'var(--danger)' }}/></div>
              <div className="text-sm mt-1" style={{ color: 'var(--text-tertiary)' }}>Orders are executed on a live brokerage account with real capital. Strict risk checks apply.</div>
            </div>
          </label>
        </div>

        <div className="mt-8 flex justify-end">
          <button 
            onClick={handleApply}
            disabled={isApplying || selectedMode === data?.global_trading_mode} 
            className="btn-primary"
            style={{ opacity: (isApplying || selectedMode === data?.global_trading_mode) ? 0.5 : 1 }}
          >
            {isApplying ? "Applying..." : "Apply Changes"}
          </button>
        </div>
      </div>
    </div>
  );
}
