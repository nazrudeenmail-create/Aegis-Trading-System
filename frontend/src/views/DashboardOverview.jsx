import React from 'react';
import { Activity, Server, DollarSign, Briefcase, Bell, Eye, TrendingUp, BarChart2, Cpu, Zap, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import useSWR from 'swr';
import { fetcher } from '../api';
import { InstrumentCard } from '../components/InstrumentCard';

function StatCard({ label, value, sub, icon: Icon, color = 'var(--accent-primary)', delay = 0 }) {
  return (
    <div className={`glass-card stat-card animate-fade-in animate-fade-in-delay-${delay}`}>
      <div className="flex justify-between items-start">
        <div className="stat-label">{label}</div>
        <div className="p-2 rounded-lg" style={{ background: `color-mix(in srgb, ${color} 12%, transparent)` }}>
          <Icon size={16} style={{ color }} />
        </div>
      </div>
      <div className="stat-value" style={{ color: color === 'var(--accent-primary)' ? 'var(--text-primary)' : color }}>{value}</div>
      {sub && <div className="stat-sub">{sub}</div>}
    </div>
  );
}

function EngineCard({ label, value, icon: Icon, color, delay }) {
  return (
    <div className={`glass-card p-4 flex items-center gap-4 animate-fade-in animate-fade-in-delay-${delay}`}>
      <div className="p-2.5 rounded-lg" style={{ background: `color-mix(in srgb, ${color} 12%, transparent)` }}>
        <Icon size={20} style={{ color }} />
      </div>
      <div>
        <div className="text-xs font-medium" style={{ color: 'var(--text-tertiary)' }}>{label}</div>
        <div className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>{value}</div>
      </div>
    </div>
  );
}

export function DashboardOverview() {
  const { data: summary } = useSWR('/dashboard/summary', fetcher, {
    refreshInterval: 10000,
    fallbackData: null,
  });
  const { data: watchData } = useSWR('/dashboard/instruments', fetcher, {
    refreshInterval: 15000,
    fallbackData: { instruments: [] },
  });

  if (!summary) {
    return (
      <div className="space-y-6">
        <div className="skeleton h-8 w-64" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <div key={i} className="skeleton h-32 rounded-xl" />)}
        </div>
        <div className="grid grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => <div key={i} className="skeleton h-20 rounded-xl" />)}
        </div>
      </div>
    );
  }

  const { system_status, trading_mode, broker_status, account, portfolio, market, engine } = summary;
  const dailyPnl = account?.daily_pnl ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>Dashboard</h1>
        <div className="flex items-center gap-2">
          <div className="pulse-dot" style={{ background: system_status?.backend === 'Running' ? 'var(--success)' : 'var(--danger)' }} />
          <span className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>{system_status?.backend || 'Offline'}</span>
        </div>
      </div>

      {/* Top Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="System Status"
          value={system_status?.backend || 'Offline'}
          sub={`CPU: ${system_status?.cpu_percent || 0}% · Mem: ${system_status?.memory_mb || 0} MB`}
          icon={Server}
          delay={1}
        />
        <StatCard
          label="Trading Mode"
          value={trading_mode || 'Unknown'}
          sub={`Broker: ${broker_status || 'Disconnected'}`}
          icon={Activity}
          color="var(--accent-cyan)"
          delay={2}
        />
        <StatCard
          label="Account Balance"
          value={`$${(account?.balance ?? 0).toLocaleString()}`}
          sub={
            <span style={{ color: dailyPnl >= 0 ? 'var(--success)' : 'var(--danger)' }}>
              {dailyPnl >= 0 ? '▲' : '▼'} ${Math.abs(dailyPnl).toFixed(2)} today
            </span>
          }
          icon={DollarSign}
          color={dailyPnl >= 0 ? 'var(--success)' : 'var(--danger)'}
          delay={3}
        />
        <StatCard
          label="Portfolio"
          value={`${portfolio?.active_instruments ?? 0}`}
          sub={`${portfolio?.open_positions ?? 0} positions · ${market?.markets_open ?? 0} markets`}
          icon={Briefcase}
          delay={4}
        />
      </div>

      {/* Engine Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <EngineCard label="Strategies Active" value={engine?.strategies_running ?? 0} icon={TrendingUp} color="var(--accent-primary)" delay={1} />
        <EngineCard label="Signals Today" value={engine?.signals_today ?? 0} icon={BarChart2} color="var(--success)" delay={2} />
        <EngineCard label="Uptime" value={`${system_status?.uptime_hours || 0}h`} icon={Cpu} color="var(--warning)" delay={3} />
      </div>

      {/* Market Watch */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>Market Watch</h2>
          <span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>
            {watchData?.instruments?.length ?? 0} instruments · auto-refresh
          </span>
        </div>

        {(!watchData?.instruments || watchData.instruments.length === 0) ? (
          <div className="glass-card-static p-10 text-center" style={{ color: 'var(--text-tertiary)' }}>
            No instruments tracked. Add instruments in the <strong style={{ color: 'var(--text-secondary)' }}>Instruments</strong> tab.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {watchData.instruments.map(item => (
              <InstrumentCard key={item.id} data={item} />
            ))}
          </div>
        )}
      </div>

      {/* Bottom Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-card-static overflow-hidden flex flex-col">
          <div className="section-header">
            <div className="section-title">
              <Bell size={16} style={{ color: 'var(--accent-primary)' }} /> Recent Activity
            </div>
          </div>
          <div className="p-5 flex-1 flex items-center justify-center min-h-[180px]" style={{ color: 'var(--text-muted)' }}>
            <div className="text-center">
              <Bell size={28} className="mx-auto mb-3" style={{ color: 'var(--text-muted)' }} />
              <div className="text-sm">No recent notifications</div>
            </div>
          </div>
        </div>

        <div className="glass-card-static overflow-hidden flex flex-col">
          <div className="section-header">
            <div className="section-title">
              <Eye size={16} style={{ color: 'var(--accent-primary)' }} /> Decision Inspector
            </div>
          </div>
          <div className="p-5 flex-1 flex items-center justify-center min-h-[180px]" style={{ color: 'var(--text-muted)' }}>
            <div className="text-center">
              <Zap size={28} className="mx-auto mb-3" style={{ color: 'var(--text-muted)' }} />
              <div className="text-sm">Awaiting trade events...</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
