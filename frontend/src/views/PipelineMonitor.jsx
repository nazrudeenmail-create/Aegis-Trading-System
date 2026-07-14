import React, { useState, useEffect } from 'react';
import useSWR from 'swr';
import { fetcher, wsClient } from '../api';
import { Activity, Server, Clock, ShieldAlert, Cpu, Network, FileText, BarChart2, AlertTriangle, ArrowRight, Database, Workflow, Zap, TrendingUp, Filter, CheckCircle2 } from 'lucide-react';

export function PipelineMonitor() {
  const [activeTab, setActiveTab] = useState('Overview');
  const [events, setEvents] = useState([]);
  
  const { data: health } = useSWR('/pipeline/health', fetcher, { refreshInterval: 5000 });
  const { data: instrumentsData } = useSWR('/dashboard/instruments', fetcher, { refreshInterval: 5000 });

  useEffect(() => {
    const unsub = wsClient.subscribe((msg) => {
      if (msg.event === 'system.log' || msg.event === 'pipeline.metrics' || msg.event === 'strategy.ranking.changed') {
        const timestamp = msg.data?.timestamp ? new Date(msg.data.timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();
        let engine = 'System';
        let level = 'INFO';
        let text = JSON.stringify(msg.data);
        
        if (msg.event === 'system.log') {
          engine = msg.data.source || 'System';
          level = msg.data.level;
          text = msg.data.message;
        } else if (msg.event === 'pipeline.metrics') {
          engine = msg.data.engine;
          level = msg.data.status === 'error' ? 'ERROR' : 'INFO';
          text = `${msg.data.instrument ? msg.data.instrument + ' - ' : ''}${msg.data.event_name} (${msg.data.duration_ms}ms)`;
        } else if (msg.event === 'strategy.ranking.changed') {
          engine = 'Strategy';
          text = `${msg.data.symbol} scanned – Winner: ${msg.data.winner}`;
        }
        
        const formattedEvent = {
          time: timestamp,
          level,
          engine,
          text,
          raw: msg
        };
        
        setEvents((prev) => [formattedEvent, ...prev].slice(0, 200));
      }
    });
    return unsub;
  }, []);

  const tabs = ['Overview', 'Data Trace', 'Market Data', 'Indicators', 'Strategies', 'Logs', 'Performance'];

  if (!health) {
    return <div className="p-8 text-center animate-pulse">Loading Pipeline Health...</div>;
  }

  const { stages, throughput, latency } = health;

  return (
    <div className="space-y-6 animate-fade-in pb-10">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>Pipeline Monitor</h1>
          <div className="text-sm mt-1" style={{ color: 'var(--text-tertiary)' }}>Engineering system health and diagnostics</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b" style={{ borderColor: 'var(--border-primary)' }}>
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className="px-6 py-3 text-sm font-bold uppercase tracking-wider transition-colors"
            style={{
              color: activeTab === tab ? 'var(--accent-primary)' : 'var(--text-tertiary)',
              borderBottom: activeTab === tab ? '2px solid var(--accent-primary)' : '2px solid transparent',
              background: activeTab === tab ? 'var(--bg-elevated)' : 'transparent'
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="mt-6">
        {activeTab === 'Overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Stages Table */}
            <div className="glass-card-static lg:col-span-2">
              <div className="section-header">
                <div className="section-title"><Network size={16} style={{ color: 'var(--info)' }} /> Processing Stages</div>
              </div>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b" style={{ borderColor: 'var(--border-primary)' }}>
                    <th className="text-left p-3" style={{ color: 'var(--text-tertiary)' }}>Stage</th>
                    <th className="text-right p-3" style={{ color: 'var(--text-tertiary)' }}>Status</th>
                    <th className="text-right p-3" style={{ color: 'var(--text-tertiary)' }}>Freshness</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(stages || {}).map(([stageName, stageData], i) => (
                    <tr key={i} className="border-b" style={{ borderColor: 'var(--border-primary)' }}>
                      <td className="p-3 font-medium" style={{ color: 'var(--text-secondary)' }}>{stageName}</td>
                      <td className="p-3 text-right font-bold tracking-wide" style={{ color: stageData.color }}>
                        {stageData.status === 'Stale' ? <span className="flex items-center justify-end gap-1"><AlertTriangle size={14}/> STALE</span> : stageData.status}
                      </td>
                      <td className="p-3 text-right font-mono" style={{ color: stageData.status === 'Stale' ? 'var(--danger)' : 'var(--text-tertiary)' }}>
                        {stageData.freshness}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Throughput */}
            <div className="glass-card-static">
              <div className="section-header">
                <div className="section-title"><Activity size={16} style={{ color: 'var(--warning)' }} /> Throughput Metrics</div>
              </div>
              <div className="p-4 space-y-4">
                {Object.entries(throughput || {}).map(([metric, val], i) => (
                  <div key={i} className="flex justify-between items-center border-b pb-2" style={{ borderColor: 'var(--border-primary)' }}>
                    <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>{metric}</span>
                    <span className="font-mono font-bold" style={{ color: 'var(--text-primary)' }}>{val.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'Data Trace' && (
          <div className="space-y-6">
            <div className="glass-card-static">
              <div className="section-header">
                <div className="section-title"><Network size={16} style={{ color: 'var(--accent-cyan)' }} /> Candle Data Journey (Pipeline Trace)</div>
              </div>
              <div className="p-6">
                <div className="relative border-l-2 border-dashed ml-8 pb-8 space-y-10" style={{ borderColor: 'var(--border-primary)' }}>
                  
                  {/* Step 1: Broker / Data Collector */}
                  <div className="relative">
                    <div className="absolute -left-[45px] bg-slate-900 border-2 rounded-full p-2" style={{ borderColor: 'var(--accent-primary)', color: 'var(--accent-primary)' }}>
                      <Database size={24} />
                    </div>
                    <div className="pl-6">
                      <h3 className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>1. Data Acquisition</h3>
                      <p className="text-sm mt-1" style={{ color: 'var(--text-tertiary)' }}>Raw market ticks are collected from the Broker API (Capital.com).</p>
                      <div className="mt-3 bg-black/40 p-3 rounded text-xs font-mono inline-block border" style={{ borderColor: 'var(--border-primary)', color: 'var(--success)' }}>
                        <Zap size={12} className="inline mr-2" />
                        Streamed WebSocket / REST Polling → 1M Candles
                      </div>
                    </div>
                  </div>

                  {/* Step 2: Database / Orchestrator Fetch */}
                  <div className="relative">
                    <div className="absolute -left-[45px] bg-slate-900 border-2 rounded-full p-2" style={{ borderColor: 'var(--info)', color: 'var(--info)' }}>
                      <Server size={24} />
                    </div>
                    <div className="pl-6">
                      <h3 className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>2. Historical Context (Orchestrator)</h3>
                      <p className="text-sm mt-1" style={{ color: 'var(--text-tertiary)' }}>System Orchestrator retrieves the latest 1,440 x 1M candles (24h history) from PostgreSQL.</p>
                      <div className="mt-3 p-3 rounded text-xs bg-blue-900/10 border" style={{ borderColor: 'rgba(59, 130, 246, 0.2)', color: 'var(--info)' }}>
                        <span className="font-bold">Optimization:</span> Prevents memory bloat by strictly limiting history to active rolling windows.
                      </div>
                    </div>
                  </div>

                  {/* Step 3: Timeframe Builder & Validation */}
                  <div className="relative">
                    <div className="absolute -left-[45px] bg-slate-900 border-2 rounded-full p-2" style={{ borderColor: 'var(--warning)', color: 'var(--warning)' }}>
                      <Workflow size={24} />
                    </div>
                    <div className="pl-6">
                      <h3 className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>3. Timeframe Aggregation & Validation</h3>
                      <p className="text-sm mt-1" style={{ color: 'var(--text-tertiary)' }}>MultiTimeframeService projects 1M candles into higher timeframes (M5, M15, H1, H4, D1).</p>
                      <div className="mt-3 flex gap-4">
                        <div className="bg-yellow-900/10 border p-3 rounded text-xs flex-1" style={{ borderColor: 'rgba(234, 179, 8, 0.2)', color: 'var(--text-secondary)' }}>
                          <strong className="block text-yellow-500 mb-1">TimeframeBuilder</strong>
                          Aggregates lower timeframes mathematically perfectly into higher timeframes.
                        </div>
                        <div className="bg-yellow-900/10 border p-3 rounded text-xs flex-1" style={{ borderColor: 'rgba(234, 179, 8, 0.2)', color: 'var(--text-secondary)' }}>
                          <strong className="block text-yellow-500 mb-1">DataQualityValidator</strong>
                          Verifies gaps, minimum candle count (50), and invalid OHLC thresholds.
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Step 4: Market Intelligence (Indicator Engine) */}
                  <div className="relative">
                    <div className="absolute -left-[45px] bg-slate-900 border-2 rounded-full p-2" style={{ borderColor: 'var(--accent-purple)', color: 'var(--accent-purple)' }}>
                      <Activity size={24} />
                    </div>
                    <div className="pl-6">
                      <h3 className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>4. Market Intelligence (2-Tier Analysis)</h3>
                      <p className="text-sm mt-1 mb-3" style={{ color: 'var(--text-tertiary)' }}>Mathematical evaluation of price action across all timeframes.</p>
                      
                      <div className="grid grid-cols-2 gap-4">
                        <div className="bg-purple-900/10 border p-3 rounded text-xs" style={{ borderColor: 'rgba(168, 85, 247, 0.2)' }}>
                          <strong className="block text-purple-400 mb-2">Phase A: Base Indicators</strong>
                          <ul className="space-y-1 list-disc list-inside" style={{ color: 'var(--text-secondary)' }}>
                            <li>EMA (Trend Baselines)</li>
                            <li>ATR (Volatility)</li>
                            <li>ADX (Trend Strength)</li>
                            <li>Donchian Channels</li>
                          </ul>
                        </div>
                        <div className="bg-purple-900/10 border p-3 rounded text-xs" style={{ borderColor: 'rgba(168, 85, 247, 0.2)' }}>
                          <strong className="block text-purple-400 mb-2">Phase B: Contextual Intelligence</strong>
                          <ul className="space-y-1 list-disc list-inside" style={{ color: 'var(--text-secondary)' }}>
                            <li>Market Regime Detection</li>
                            <li>Trend Alignment Scoring</li>
                            <li>Momentum Profiling</li>
                            <li>Live Indicator Projection</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Step 5: Strategy Engine */}
                  <div className="relative">
                    <div className="absolute -left-[45px] bg-slate-900 border-2 rounded-full p-2" style={{ borderColor: 'var(--success)', color: 'var(--success)' }}>
                      <Filter size={24} />
                    </div>
                    <div className="pl-6">
                      <h3 className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>5. Strategy & Setup Evaluation</h3>
                      <p className="text-sm mt-1" style={{ color: 'var(--text-tertiary)' }}>Hard filters are applied to find active, executable trades.</p>
                      
                      <div className="mt-3 bg-green-900/10 border p-3 rounded text-xs" style={{ borderColor: 'rgba(34, 197, 94, 0.2)' }}>
                        <div className="flex items-start gap-3">
                          <CheckCircle2 size={16} className="text-green-500 mt-0.5" />
                          <p style={{ color: 'var(--text-secondary)' }}>
                            <strong className="text-green-400">Accuracy {'>'} Speed {'>'} Profit.</strong> Setup validation is binary. Strategies only pass if the context perfectly aligns with the strategy rules.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Step 6: Ranking & Execution */}
                  <div className="relative">
                    <div className="absolute -left-[45px] bg-slate-900 border-2 rounded-full p-2" style={{ borderColor: 'var(--danger)', color: 'var(--danger)' }}>
                      <TrendingUp size={24} />
                    </div>
                    <div className="pl-6">
                      <h3 className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>6. Ranking & Execution</h3>
                      <p className="text-sm mt-1" style={{ color: 'var(--text-tertiary)' }}>The Strategy Ranking Engine selects the strongest candidate.</p>
                      <div className="mt-3 p-3 rounded text-xs border" style={{ borderColor: 'var(--border-primary)', background: 'var(--bg-elevated)' }}>
                        <div className="flex justify-between items-center" style={{ color: 'var(--text-secondary)' }}>
                          <span>Historical Score (40%)</span>
                          <span>+</span>
                          <span>Compatibility Score (30%)</span>
                          <span>+</span>
                          <span>Setup Quality (30%)</span>
                          <ArrowRight size={14} className="mx-2 text-red-500" />
                          <strong className="text-red-400">Winner Candidate Routed to Broker</strong>
                        </div>
                      </div>
                    </div>
                  </div>

                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'Performance' && (
          <div className="glass-card-static max-w-4xl">
            <div className="section-header">
              <div className="section-title"><Clock size={16} style={{ color: 'var(--accent-cyan)' }} /> Latency Monitoring</div>
            </div>
            <div className="overflow-x-auto p-2">
              <table className="w-full text-sm text-left">
                <thead className="text-xs uppercase tracking-wider" style={{ color: 'var(--text-tertiary)', borderBottom: '1px solid var(--border-primary)' }}>
                  <tr>
                    <th className="p-3">Engine Stage</th>
                    <th className="p-3 text-right">Last</th>
                    <th className="p-3 text-right">Average</th>
                    <th className="p-3 text-right">Maximum</th>
                  </tr>
                </thead>
                <tbody className="divide-y" style={{ divideColor: 'var(--border-primary)' }}>
                  {Object.entries(latency || {}).length === 0 ? (
                    <tr><td colSpan="4" className="p-6 text-center" style={{ color: 'var(--text-tertiary)' }}>No execution metrics recorded yet.</td></tr>
                  ) : (
                    Object.entries(latency).map(([engine, metrics], i) => (
                      <tr key={i} className="hover:bg-opacity-50 transition-colors" style={{ hoverBackgroundColor: 'var(--bg-secondary)' }}>
                        <td className="p-3 font-mono font-bold" style={{ color: 'var(--text-secondary)' }}>{engine}</td>
                        <td className="p-3 text-right font-mono" style={{ color: 'var(--success)' }}>{metrics.last}</td>
                        <td className="p-3 text-right font-mono" style={{ color: 'var(--text-primary)' }}>{metrics.avg}</td>
                        <td className="p-3 text-right font-mono" style={{ color: 'var(--warning)' }}>{metrics.max}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'Logs' && (
          <div className="glass-card-static overflow-hidden">
            <div className="section-header">
              <div className="section-title"><FileText size={16} style={{ color: 'var(--info)' }} /> Formatted System Events</div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs uppercase tracking-wider" style={{ background: 'var(--bg-secondary)', color: 'var(--text-tertiary)' }}>
                  <tr>
                    <th className="p-3">Time</th>
                    <th className="p-3">Level</th>
                    <th className="p-3">Engine</th>
                    <th className="p-3">Event</th>
                    <th className="p-3 text-right">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y" style={{ divideColor: 'var(--border-primary)' }}>
                  {events.length === 0 ? (
                    <tr>
                      <td colSpan="5" className="p-8 text-center text-xs" style={{ color: 'var(--text-tertiary)' }}>
                        Waiting for events...
                      </td>
                    </tr>
                  ) : (
                    events.map((evt, i) => (
                      <tr key={i} className="hover:bg-opacity-50 transition-colors" style={{ hoverBackgroundColor: 'var(--bg-secondary)' }}>
                        <td className="p-3 font-mono text-xs" style={{ color: 'var(--text-tertiary)' }}>{evt.time}</td>
                        <td className="p-3 text-xs">
                          <span className={`px-2 py-1 rounded font-bold ${evt.level === 'ERROR' ? 'bg-red-900/30 text-red-400' : evt.level === 'WARN' ? 'bg-yellow-900/30 text-yellow-400' : evt.level === 'DEBUG' ? 'bg-gray-800 text-gray-400' : 'bg-blue-900/30 text-blue-400'}`}>
                            {evt.level === 'INFO' ? 'ℹ️ INFO' : evt.level === 'WARN' ? '⚠️ WARN' : evt.level === 'DEBUG' ? '🔍 DEBUG' : '🚨 ERROR'}
                          </span>
                        </td>
                        <td className="p-3 font-medium" style={{ color: 'var(--text-secondary)' }}>{evt.engine}</td>
                        <td className="p-3" style={{ color: 'var(--text-primary)' }}>{evt.text}</td>
                        <td className="p-3 text-right">
                          <button className="text-xs underline" style={{ color: 'var(--accent-primary)' }} onClick={() => console.log(evt.raw)}>
                            Expand
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {['Market Data', 'Indicators', 'Strategies'].includes(activeTab) && (
          <div className="space-y-6">
            <div className="glass-card-static overflow-hidden">
              <div className="section-header">
                <div className="section-title"><Cpu size={16} style={{ color: 'var(--info)' }} /> Current State: {activeTab}</div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="text-xs uppercase tracking-wider" style={{ background: 'var(--bg-secondary)', color: 'var(--text-tertiary)' }}>
                    <tr>
                      <th className="p-3">Symbol</th>
                      {activeTab === 'Market Data' && (
                        <>
                          <th className="p-3">Session</th>
                          <th className="p-3 text-right">Latest Price</th>
                        </>
                      )}
                      {activeTab === 'Indicators' && (
                        <>
                          <th className="p-3">Trend</th>
                          <th className="p-3">Regime</th>
                          <th className="p-3 text-right">ADX Strength</th>
                        </>
                      )}
                      {activeTab === 'Strategies' && (
                        <>
                          <th className="p-3">Top Strategy</th>
                          <th className="p-3">Signal</th>
                          <th className="p-3 text-right">Score</th>
                        </>
                      )}
                    </tr>
                  </thead>
                  <tbody className="divide-y" style={{ divideColor: 'var(--border-primary)' }}>
                    {!instrumentsData?.instruments || instrumentsData.instruments.length === 0 ? (
                      <tr>
                        <td colSpan="5" className="p-8 text-center text-xs" style={{ color: 'var(--text-tertiary)' }}>
                          No instruments active.
                        </td>
                      </tr>
                    ) : (
                      instrumentsData.instruments.map(inst => (
                        <tr key={inst.id} className="hover:bg-opacity-50 transition-colors" style={{ hoverBackgroundColor: 'var(--bg-secondary)' }}>
                          <td className="p-3 font-bold" style={{ color: 'var(--text-primary)' }}>{inst.symbol}</td>
                          
                          {activeTab === 'Market Data' && (
                            <>
                              <td className="p-3 text-xs"><span className={`badge-${inst.session === 'REGULAR' ? 'success' : 'neutral'}`}>{inst.session}</span></td>
                              <td className="p-3 text-right font-mono" style={{ color: 'var(--text-secondary)' }}>{inst.price ? `$${inst.price}` : '---'}</td>
                            </>
                          )}
                          
                          {activeTab === 'Indicators' && (
                            <>
                              <td className="p-3 text-xs"><span className={`badge-${inst.trend === 'UP' ? 'success' : inst.trend === 'DOWN' ? 'danger' : 'neutral'}`}>{inst.trend}</span></td>
                              <td className="p-3 text-xs"><span className="badge-info">{inst.regime}</span></td>
                              <td className="p-3 text-right font-mono" style={{ color: 'var(--text-secondary)' }}>{inst.adx || '---'}</td>
                            </>
                          )}

                          {activeTab === 'Strategies' && (
                            <>
                              <td className="p-3" style={{ color: 'var(--accent-cyan)' }}>{inst.top_strategy || 'Evaluating...'}</td>
                              <td className="p-3 text-xs"><span className={`badge-${inst.signal === 'SETUP_FOUND' ? 'success' : 'warning'}`}>{inst.signal}</span></td>
                              <td className="p-3 text-right font-mono" style={{ color: 'var(--text-secondary)' }}>{inst.strategy_score !== null ? `${inst.strategy_score}%` : '---'}</td>
                            </>
                          )}
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="glass-card-static overflow-hidden">
              <div className="section-header">
                <div className="section-title"><Activity size={16} style={{ color: 'var(--warning)' }} /> Live Event Stream</div>
              </div>
              <div className="overflow-x-auto max-h-[300px] overflow-y-auto">
                <table className="w-full text-sm text-left">
                  <thead className="text-xs uppercase tracking-wider sticky top-0" style={{ background: 'var(--bg-secondary)', color: 'var(--text-tertiary)' }}>
                    <tr>
                      <th className="p-3">Time</th>
                      <th className="p-3">Level</th>
                      <th className="p-3">Event</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y" style={{ divideColor: 'var(--border-primary)' }}>
                    {events.filter(e => activeTab === 'Market Data' ? e.engine === 'MarketData' : e.engine === activeTab.replace('Strategies', 'Strategy')).length === 0 ? (
                      <tr>
                        <td colSpan="3" className="p-8 text-center text-xs" style={{ color: 'var(--text-tertiary)' }}>
                          Waiting for {activeTab} events...
                        </td>
                      </tr>
                    ) : (
                      events.filter(e => activeTab === 'Market Data' ? e.engine === 'MarketData' : e.engine === activeTab.replace('Strategies', 'Strategy')).slice(0, 30).map((evt, i) => (
                        <tr key={i} className="hover:bg-opacity-50 transition-colors" style={{ hoverBackgroundColor: 'var(--bg-secondary)' }}>
                          <td className="p-3 font-mono text-xs" style={{ color: 'var(--text-tertiary)' }}>{evt.time}</td>
                          <td className="p-3 text-xs">
                            <span className={`px-2 py-1 rounded font-bold ${evt.level === 'ERROR' ? 'bg-red-900/30 text-red-400' : evt.level === 'WARN' ? 'bg-yellow-900/30 text-yellow-400' : evt.level === 'DEBUG' ? 'bg-gray-800 text-gray-400' : 'bg-blue-900/30 text-blue-400'}`}>
                              {evt.level === 'INFO' ? 'ℹ️ INFO' : evt.level === 'WARN' ? '⚠️ WARN' : evt.level === 'DEBUG' ? '🔍 DEBUG' : '🚨 ERROR'}
                            </span>
                          </td>
                          <td className="p-3" style={{ color: 'var(--text-primary)' }}>{evt.text}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}