import React, { useState, useEffect } from 'react';
import { Activity, Server, DollarSign, Briefcase, TrendingUp, BarChart2, Cpu, Zap, ArrowDownRight, Check, X, CheckCircle2, XCircle, AlertCircle, Clock } from 'lucide-react';
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

function EngineStatusStrip({ engines }) {
  if (!engines || engines.length === 0) return null;
  return (
    <div className="flex flex-wrap gap-3 mt-4 mb-2 animate-fade-in">
      {engines.map((eng) => (
        <div key={eng.name} className="flex items-center gap-2 px-3 py-1.5 rounded-md border" style={{ borderColor: 'var(--border-primary)', background: 'var(--bg-secondary)' }}>
          <div className="pulse-dot" style={{ background: eng.color }} />
          <span className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>{eng.name}</span>
          <span className="text-xs ml-1" style={{ color: eng.color }}>{eng.status}</span>
        </div>
      ))}
    </div>
  );
}

function MarketCycleStatus({ cycle }) {
  if (!cycle) return null;
  
  return (
    <div className="flex flex-wrap gap-6 text-xs font-mono mb-4 animate-fade-in" style={{ animationDelay: '0.2s' }}>
      <div className="flex gap-2 items-center">
        <Clock size={14} style={{ color: 'var(--text-tertiary)' }} />
        <span style={{ color: 'var(--text-tertiary)' }}>Next Candle</span>
        <span style={{ color: 'var(--accent-primary)' }}>00:00:{cycle.next_candle?.toString().padStart(2, '0') || '00'}</span>
      </div>
      <div className="flex gap-2 items-center">
        <Activity size={14} style={{ color: 'var(--text-tertiary)' }} />
        <span style={{ color: 'var(--text-tertiary)' }}>Last Candle</span>
        <span style={{ color: 'var(--text-secondary)' }}>{cycle.last_candle}</span>
      </div>
      <div className="flex gap-2 items-center">
        <Cpu size={14} style={{ color: 'var(--text-tertiary)' }} />
        <span style={{ color: 'var(--text-tertiary)' }}>Pipeline</span>
        <span style={{ color: cycle.status === 'Completed' ? 'var(--success)' : 'var(--warning)' }}>
          {cycle.status === 'Completed' ? '✓ ' : ''}{cycle.status}
        </span>
      </div>
      <div className="flex gap-2 items-center">
        <Zap size={14} style={{ color: 'var(--text-tertiary)' }} />
        <span style={{ color: 'var(--text-tertiary)' }}>Duration</span>
        <span style={{ color: 'var(--text-secondary)' }}>{cycle.duration}</span>
      </div>
    </div>
  );
}

function RecentActivityTimeline({ events }) {
  const getIcon = (type) => {
    switch (type) {
      case 'success': return <CheckCircle2 size={16} style={{ color: 'var(--success)' }} />;
      case 'warning': return <AlertCircle size={16} style={{ color: 'var(--warning)' }} />;
      case 'error': return <XCircle size={16} style={{ color: 'var(--danger)' }} />;
      case 'info':
      default: return <Clock size={16} style={{ color: 'var(--info)' }} />;
    }
  };

  if (!events || events.length === 0) {
    return (
      <div className="p-5 flex-1 flex flex-col items-center justify-center text-center">
        <Activity size={32} className="mb-3" style={{ color: 'var(--border-secondary)' }} />
        <div className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>System running normally</div>
        <div className="text-xs mt-1" style={{ color: 'var(--text-tertiary)' }}>Waiting for next market update...</div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-5 relative">
      <div className="absolute left-[39px] top-8 bottom-8 w-[2px]" style={{ background: 'var(--border-primary)' }}></div>
      <div className="space-y-6 relative z-10">
        {events.map((evt, i) => (
          <div key={i} className="flex gap-4 text-sm animate-fade-in" style={{ animationDelay: `${i * 0.05}s` }}>
            <div className="text-xs mt-0.5 font-mono text-right" style={{ color: 'var(--text-tertiary)', minWidth: '55px' }}>{evt.time}</div>
            <div className="mt-0.5 relative">
              <div className="bg-[#0d1020] rounded-full p-0.5">{getIcon(evt.type)}</div>
            </div>
            <div>
              <div style={{ color: 'var(--text-primary)' }}>{evt.title || evt.text}</div>
              {(evt.sub || evt.message) && <div className="text-xs mt-1" style={{ color: evt.type === 'error' ? 'var(--danger)' : (evt.type === 'success' ? 'var(--success)' : 'var(--text-secondary)') }}>{evt.sub || evt.message}</div>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function DecisionInspector({ currentDecision }) {
  const [tab, setTab] = useState('current');

  return (
    <div className="flex-1 flex flex-col h-full">
      <div className="flex border-b" style={{ borderColor: 'var(--border-primary)' }}>
        {['current', 'history', 'journal'].map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-5 py-3 text-xs font-bold uppercase tracking-wider transition-colors`}
            style={{ 
              color: tab === t ? 'var(--accent-primary)' : 'var(--text-tertiary)',
              borderBottom: tab === t ? '2px solid var(--accent-primary)' : '2px solid transparent',
              background: tab === t ? 'var(--bg-elevated)' : 'transparent'
            }}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="flex-1 p-5 overflow-y-auto">
        {tab === 'current' && (
          !currentDecision ? (
            <div className="h-full flex flex-col items-center justify-center text-center animate-pulse">
              <Activity size={32} className="mb-3" style={{ color: 'var(--border-secondary)' }} />
              <div className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Loading latest strategy evaluation...</div>
            </div>
          ) : currentDecision.state === 'SCANNING' ? (
            <div className="space-y-6 animate-fade-in">
              <div className="flex justify-between items-start">
                <div>
                  <div className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>{currentDecision.instrument}</div>
                  <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>Strategy: {currentDecision.strategy}</div>
                </div>
                <div className="text-right">
                  <div className="text-xs uppercase tracking-wider mb-1" style={{ color: 'var(--text-tertiary)' }}>Current Stage</div>
                  <div className="badge-info flex items-center gap-1.5 justify-center">
                    <Activity size={10} className="animate-pulse" /> {currentDecision.decision}
                  </div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span style={{ color: 'var(--text-secondary)' }}>Evaluation Progress</span>
                </div>
                <div className="progress-track mb-3 relative overflow-hidden" style={{ background: 'var(--bg-elevated)' }}>
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[var(--accent-primary)] to-transparent opacity-30 skeleton"></div>
                </div>
                <div className="text-xs px-3 py-2 rounded border flex items-center gap-2" style={{ color: 'var(--info)', borderColor: 'var(--border-primary)', background: 'var(--bg-secondary)' }}>
                  <Activity size={12} className="animate-pulse" />
                  Reason: <strong style={{ color: 'var(--text-primary)' }}>{currentDecision.reason}</strong>
                </div>
              </div>

              {currentDecision.checks && currentDecision.checks.length > 0 && (
                <div className="space-y-3 p-4 rounded-xl border" style={{ borderColor: 'var(--border-primary)', background: 'var(--bg-secondary)' }}>
                  <div className="text-xs uppercase font-bold tracking-wider mb-2" style={{ color: 'var(--text-tertiary)' }}>Engine Status</div>
                  
                  {currentDecision.checks.map((check, idx) => (
                    <React.Fragment key={check.name}>
                      <div className="flex justify-between items-center text-sm">
                        <span style={{ color: 'var(--text-primary)' }}>{check.name}</span>
                        {check.status === 'PASS' ? <Check size={16} style={{ color: 'var(--success)' }} /> : 
                         check.status === 'WAIT' ? <div className="flex items-center gap-1 text-xs" style={{ color: 'var(--info)' }}><Activity size={12} className="animate-pulse" /> WAIT</div> :
                         <span className="badge-warning">{check.status}</span>}
                      </div>
                      {idx < currentDecision.checks.length - 1 && (
                        <div className="flex justify-center -my-1"><ArrowDownRight size={14} style={{ color: 'var(--border-secondary)' }}/></div>
                      )}
                    </React.Fragment>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-6 animate-fade-in">
              <div className="flex justify-between items-start">
                <div>
                  <div className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>{currentDecision.instrument}</div>
                  <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>Strategy: {currentDecision.strategy}</div>
                </div>
                <div className="text-right">
                  <div className="text-xs uppercase tracking-wider mb-1" style={{ color: 'var(--text-tertiary)' }}>Decision</div>
                  <div className={`badge-${currentDecision.decision === 'WAIT' ? 'warning' : 'success'}`}>{currentDecision.decision}</div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span style={{ color: 'var(--text-secondary)' }}>Trade Readiness</span>
                  <span className="font-mono font-bold" style={{ color: 'var(--accent-primary)' }}>{currentDecision.readiness}%</span>
                </div>
                <div className="progress-track mb-3">
                  <div className="progress-fill" style={{ width: `${currentDecision.readiness}%`, background: 'var(--accent-primary)' }}></div>
                </div>
                <div className="text-xs px-3 py-2 rounded border" style={{ color: 'var(--warning)', borderColor: 'var(--border-primary)', background: 'var(--bg-secondary)' }}>
                  Reason: <strong style={{ color: 'var(--text-primary)' }}>{currentDecision.reason}</strong>
                </div>
              </div>

              {currentDecision.checks && currentDecision.checks.length > 0 && (
                <div className="space-y-3 p-4 rounded-xl border" style={{ borderColor: 'var(--border-primary)', background: 'var(--bg-secondary)' }}>
                  <div className="text-xs uppercase font-bold tracking-wider mb-2" style={{ color: 'var(--text-tertiary)' }}>Evaluation Tree</div>
                  
                  {currentDecision.checks.map((check, idx) => (
                    <React.Fragment key={check.name}>
                      <div className="flex justify-between items-center text-sm">
                        <span style={{ color: 'var(--text-primary)' }}>{check.name}</span>
                        {check.status === 'PASS' ? <Check size={16} style={{ color: 'var(--success)' }} /> : 
                         check.status === 'FAIL' ? <X size={16} style={{ color: 'var(--danger)' }} /> :
                         <span className="badge-warning">{check.status}</span>}
                      </div>
                      {idx < currentDecision.checks.length - 1 && (
                        <div className="flex justify-center -my-1"><ArrowDownRight size={14} style={{ color: 'var(--border-secondary)' }}/></div>
                      )}
                    </React.Fragment>
                  ))}
                </div>
              )}
            </div>
          )
        )}

        {(tab === 'history' || tab === 'journal') && (
           <div className="h-full flex flex-col items-center justify-center text-center">
             <div className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>No {tab} data available</div>
             <div className="text-xs mt-1" style={{ color: 'var(--text-tertiary)' }}>Backend implementation pending</div>
           </div>
        )}
      </div>
    </div>
  );
}

export function DashboardOverview() {
  const { data: summary } = useSWR('/dashboard/summary', fetcher, {
    refreshInterval: 1000,
    fallbackData: null,
  });
  const { data: watchData } = useSWR('/dashboard/instruments', fetcher, {
    refreshInterval: 15000,
    fallbackData: { instruments: [] },
  });

  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString('en-US', { hour12: false }));

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString('en-US', { hour12: false }));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

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

  const { system_status, trading_mode, broker_status, account, portfolio, market, engine, engine_status, market_cycle, events, current_decision } = summary;
  const dailyPnl = account?.daily_pnl ?? 0;

  return (
    <div className="space-y-6 pb-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>Dashboard</h1>
          <div className="text-xs mt-1 font-mono" style={{ color: 'var(--text-tertiary)' }}>Last update: {currentTime}</div>
        </div>
        <div className="flex items-center gap-3 bg-opacity-20 px-4 py-2 rounded-lg border" style={{ borderColor: 'var(--border-primary)', background: 'var(--bg-secondary)' }}>
          <div className="pulse-dot" style={{ background: system_status?.backend === 'Running' ? 'var(--success)' : 'var(--danger)' }} />
          <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>System: {system_status?.backend || 'Offline'}</span>
        </div>
      </div>

      <EngineStatusStrip engines={engine_status} />

      {/* Top Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="Trading Mode"
          value={trading_mode || 'Unknown'}
          sub={`Broker: ${broker_status || 'Disconnected'}`}
          icon={Activity}
          color="var(--accent-cyan)"
          delay={1}
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
          delay={2}
        />
        <StatCard
          label="Portfolio"
          value={`${portfolio?.active_instruments ?? 0}`}
          sub={`${portfolio?.open_positions ?? 0} positions · ${market?.markets_open ?? 0} markets`}
          icon={Briefcase}
          delay={3}
        />
        <StatCard
          label="Signals Today"
          value={engine?.signals_today ?? 0}
          sub={`${engine?.strategies_running ?? 0} active strategies`}
          icon={BarChart2}
          color="var(--success)"
          delay={4}
        />
      </div>

      <MarketCycleStatus cycle={market_cycle} />

      {/* Market Watch */}
      <div className="glass-card-static p-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-sm font-bold uppercase tracking-wider" style={{ color: 'var(--text-primary)' }}>Market Watch</h2>
          <span className="text-xs flex items-center gap-2" style={{ color: 'var(--text-tertiary)' }}>
            <div className="w-2 h-2 rounded-full" style={{ background: 'var(--info)' }}></div>
            {watchData?.instruments?.length ?? 0} instruments actively scanning
          </span>
        </div>

        {(!watchData?.instruments || watchData.instruments.length === 0) ? (
          <div className="p-8 text-center border border-dashed rounded-lg" style={{ color: 'var(--text-tertiary)', borderColor: 'var(--border-secondary)' }}>
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

      {/* Bottom Panels - The Decision Center */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[450px]">
        {/* Recent Activity Timeline */}
        <div className="glass-card-static overflow-hidden flex flex-col h-full shadow-lg border" style={{ borderColor: 'var(--border-secondary)' }}>
          <div className="section-header bg-black/20">
            <div className="section-title">
              <Activity size={16} style={{ color: 'var(--info)' }} /> System Event Timeline
            </div>
            <div className="flex items-center gap-2">
              <div className="pulse-dot" style={{ background: 'var(--success)' }}></div>
              <span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>Recording</span>
            </div>
          </div>
          <RecentActivityTimeline events={events} />
        </div>

        {/* Decision Inspector */}
        <div className="glass-card-static overflow-hidden flex flex-col h-full shadow-lg border" style={{ borderColor: 'var(--border-secondary)' }}>
          <div className="section-header bg-black/20">
            <div className="section-title">
              <Zap size={16} style={{ color: 'var(--warning)' }} /> Decision Inspector
            </div>
            <span className="badge-neutral text-[10px]">EVALUATING</span>
          </div>
          <DecisionInspector currentDecision={current_decision} />
        </div>
      </div>
    </div>
  );
}
