import React from 'react';
import { Activity, Server, DollarSign, Briefcase, Bell, Eye, TrendingUp, BarChart2, Cpu } from 'lucide-react';
import useSWR from 'swr';
import { fetcher } from '../api';
import { InstrumentCard } from '../components/InstrumentCard';

export function DashboardOverview() {
  const { data: summary } = useSWR('/dashboard/summary', fetcher, {
    refreshInterval: 10000,
    fallbackData: null,
  });
  const { data: watchData } = useSWR('/dashboard/instruments', fetcher, {
    refreshInterval: 15000,
    fallbackData: { instruments: [] },
  });

  if (!summary) return <div className="p-8 text-slate-400">Loading Dashboard...</div>;

  const { system_status, trading_mode, broker_status, account, portfolio, market, engine } = summary;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white tracking-tight">Dashboard Overview</h1>

      {/* ── Top Stats Row ── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">

        <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 flex flex-col gap-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-sm font-medium">System</span>
            <Server size={16} />
          </div>
          <div className="text-2xl font-semibold text-white">{system_status.backend}</div>
          <div className="text-xs text-slate-500">
            CPU: {system_status.cpu_percent}% · Mem: {system_status.memory_mb} MB
          </div>
        </div>

        <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 flex flex-col gap-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-sm font-medium">Trading Mode</span>
            <Activity size={16} />
          </div>
          <div className="text-2xl font-semibold text-indigo-400">{trading_mode}</div>
          <div className="text-xs text-slate-500">Broker: {broker_status}</div>
        </div>

        <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 flex flex-col gap-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-sm font-medium">Account Balance</span>
            <DollarSign size={16} />
          </div>
          <div className="text-2xl font-semibold text-emerald-400">
            ${(account?.balance ?? 0).toLocaleString()}
          </div>
          <div className={`text-xs ${(account?.daily_pnl ?? 0) >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
            Daily PnL: ${(account?.daily_pnl ?? 0).toFixed(2)}
          </div>
        </div>

        <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 flex flex-col gap-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-sm font-medium">Portfolio</span>
            <Briefcase size={16} />
          </div>
          <div className="text-2xl font-semibold text-white">
            {portfolio?.active_instruments ?? 0}{' '}
            <span className="text-sm font-normal text-slate-500">instruments</span>
          </div>
          <div className="text-xs text-slate-500">
            {portfolio?.open_positions ?? 0} open · {market?.markets_open ?? 0} markets open
          </div>
        </div>

      </div>

      {/* ── Engine Stats Row ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex items-center gap-4">
          <div className="p-2 bg-indigo-500/10 rounded-lg">
            <TrendingUp size={20} className="text-indigo-400" />
          </div>
          <div>
            <div className="text-xs text-slate-500">Strategies Active</div>
            <div className="text-xl font-bold text-white">{engine?.strategies_running ?? 0}</div>
          </div>
        </div>
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex items-center gap-4">
          <div className="p-2 bg-emerald-500/10 rounded-lg">
            <BarChart2 size={20} className="text-emerald-400" />
          </div>
          <div>
            <div className="text-xs text-slate-500">Signals Today</div>
            <div className="text-xl font-bold text-white">{engine?.signals_today ?? 0}</div>
          </div>
        </div>
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex items-center gap-4">
          <div className="p-2 bg-amber-500/10 rounded-lg">
            <Cpu size={20} className="text-amber-400" />
          </div>
          <div>
            <div className="text-xs text-slate-500">Uptime</div>
            <div className="text-xl font-bold text-white">{system_status.uptime_hours}h</div>
          </div>
        </div>
      </div>

      {/* ── Market Watch — dynamic instrument grid ── */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-white">Market Watch</h2>
          <span className="text-xs text-slate-500">
            {watchData?.instruments?.length ?? 0} instruments · refreshes every 15s
          </span>
        </div>

        {(!watchData?.instruments || watchData.instruments.length === 0) ? (
          <div className="bg-slate-950 rounded-xl border border-slate-800 p-10 text-center text-slate-500">
            No instruments tracked. Add instruments in the{' '}
            <strong className="text-slate-300">Instruments</strong> tab and set status to{' '}
            <strong className="text-slate-300">ACTIVE</strong>.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {watchData.instruments.map(item => (
              <InstrumentCard key={item.id} data={item} />
            ))}
          </div>
        )}
      </div>

      {/* ── Bottom Row ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <div className="bg-slate-950 rounded-xl border border-slate-800 overflow-hidden flex flex-col">
          <div className="p-4 border-b border-slate-800 flex items-center gap-2">
            <Bell size={18} className="text-slate-400" />
            <h2 className="font-semibold">Recent Activity</h2>
          </div>
          <div className="p-4 flex-1 flex items-center justify-center text-sm text-slate-500 min-h-[200px]">
            No recent notifications
          </div>
        </div>

        <div className="bg-slate-950 rounded-xl border border-slate-800 overflow-hidden flex flex-col">
          <div className="p-4 border-b border-slate-800 flex items-center gap-2">
            <Eye size={18} className="text-slate-400" />
            <h2 className="font-semibold">Decision Inspector</h2>
          </div>
          <div className="p-4 flex-1 flex items-center justify-center text-sm text-slate-500 min-h-[200px]">
            Awaiting trade events...
          </div>
        </div>

      </div>
    </div>
  );
}
