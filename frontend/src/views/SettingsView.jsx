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
  }, [data]);    const handleApply = async () => {
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

  if (isLoading) return <div className="text-slate-400">Loading settings...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white tracking-tight">Trading Settings</h1>

      <div className="bg-slate-950 p-6 rounded-xl border border-slate-800 max-w-2xl">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2 mb-2">
          <Power size={18} className="text-indigo-400" /> Global Trading Mode
        </h2>
        <p className="text-sm text-slate-500 mb-6 flex items-center gap-2">
          <ShieldAlert size={14} /> Note: Changing this at runtime will not re-authenticate the broker until a restart.
        </p>

        <div className="space-y-4">
          <label className={`flex items-start gap-4 p-4 rounded-lg border transition cursor-pointer ${selectedMode === 'BROKER_DEMO' ? 'bg-indigo-500/10 border-indigo-500/50' : 'bg-slate-900 border-slate-700'}`}>
            <input 
              type="radio" 
              name="tradingMode" 
              value="BROKER_DEMO" 
              checked={selectedMode === 'BROKER_DEMO'}
              onChange={(e) => setSelectedMode(e.target.value)}
              className="mt-1 accent-indigo-500"
            />
            <div>
              <div className="font-semibold text-white">Broker Demo</div>
              <div className="text-sm text-slate-400 mt-1">Orders are sent to a live broker's demo/paper environment (e.g., Capital.com Demo). Simulates real latency.</div>
            </div>
          </label>

          <label className={`flex items-start gap-4 p-4 rounded-lg border transition cursor-pointer ${selectedMode === 'BROKER_LIVE' ? 'bg-red-500/10 border-red-500/50' : 'bg-slate-900 border-slate-700'}`}>
            <input 
              type="radio" 
              name="tradingMode" 
              value="BROKER_LIVE" 
              checked={selectedMode === 'BROKER_LIVE'}
              onChange={(e) => setSelectedMode(e.target.value)}
              className="mt-1 accent-red-500"
            />
            <div>
              <div className="font-semibold text-white flex items-center gap-2">Broker Live <ShieldAlert size={14} className="text-red-400"/></div>
              <div className="text-sm text-slate-400 mt-1">Orders are executed on a live brokerage account with real capital. Strict risk checks apply.</div>
            </div>
          </label>
        </div>

        <div className="mt-8 flex justify-end">
          <button 
            onClick={handleApply}
            disabled={isApplying || selectedMode === data?.global_trading_mode} 
            className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded shadow transition disabled:opacity-50 disabled:cursor-not-allowed">
            {isApplying ? "Applying..." : "Apply Changes"}
          </button>
        </div>
      </div>
    </div>
  );
}
