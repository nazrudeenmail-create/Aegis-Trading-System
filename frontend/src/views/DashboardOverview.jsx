import React, { useEffect, useState } from 'react';
import { Activity, Server, DollarSign, Briefcase, Bell, Eye } from 'lucide-react';
import { fetcher } from '../api';

export function DashboardOverview() {
  const [summary, setSummary] = useState(null);
  
  useEffect(() => {
    fetcher('/dashboard/summary').then(setSummary).catch(console.error);
  }, []);

  if (!summary) return <div className="p-8 text-slate-400">Loading Dashboard...</div>;

  const { system_status, trading_mode, broker_status, account_balance, active_instruments_count, open_positions } = summary;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white tracking-tight">Dashboard Overview</h1>
      
      {/* Top Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        
        {/* System Status */}
        <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 flex flex-col gap-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-sm font-medium">System Status</span>
            <Server size={16} />
          </div>
          <div className="text-2xl font-semibold text-white">{system_status.backend}</div>
          <div className="text-xs text-slate-500 mt-1">CPU: {system_status.cpu_percent}% | Mem: {system_status.memory_mb}MB</div>
        </div>

        {/* Trading Mode */}
        <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 flex flex-col gap-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-sm font-medium">Trading Mode</span>
            <Activity size={16} />
          </div>
          <div className="text-2xl font-semibold text-indigo-400">{trading_mode}</div>
          <div className="text-xs text-slate-500 mt-1">Broker: {broker_status}</div>
        </div>

        {/* Account Balance */}
        <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 flex flex-col gap-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-sm font-medium">Account Balance</span>
            <DollarSign size={16} />
          </div>
          <div className="text-2xl font-semibold text-emerald-400">${(account_balance || 0).toLocaleString()}</div>
          <div className="text-xs text-slate-500 mt-1">Daily PnL: $0.00</div>
        </div>

        {/* Active Markets */}
        <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 flex flex-col gap-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-sm font-medium">Active Markets</span>
            <Briefcase size={16} />
          </div>
          <div className="text-2xl font-semibold text-white">{active_instruments_count} <span className="text-sm font-normal text-slate-500">watching</span></div>
          <div className="text-xs text-slate-500 mt-1">{open_positions} Open Positions</div>
        </div>

      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Notifications */}
        <div className="bg-slate-950 rounded-xl border border-slate-800 overflow-hidden flex flex-col">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <h2 className="font-semibold flex items-center gap-2"><Bell size={18} className="text-slate-400"/> Recent Activity</h2>
          </div>
          <div className="p-4 flex-1 flex items-center justify-center text-sm text-slate-500 min-h-[300px]">
            No recent notifications
          </div>
        </div>

        {/* Decision Inspector */}
        <div className="bg-slate-950 rounded-xl border border-slate-800 overflow-hidden flex flex-col">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <h2 className="font-semibold flex items-center gap-2"><Eye size={18} className="text-slate-400"/> Decision Inspector</h2>
          </div>
          <div className="p-4 flex-1 overflow-y-auto min-h-[300px]">
            <div className="text-sm text-slate-500 flex justify-center items-center h-full">
              Awaiting trade events...
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
