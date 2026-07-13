import React, { useState } from 'react';
import useSWR from 'swr';
import { fetcher, api } from '../api';
import { Settings, Save, X, TrendingUp, TrendingDown, Minus, Activity } from 'lucide-react';

function ProfileEditor({ name, initialConfig, onClose, onSave }) {
  const [config, setConfig] = useState(initialConfig);
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await api.patch(`/strategy/${name}/profile`, { config });
      onSave();
    } catch (e) {
      console.error(e);
      alert('Failed to save strategy profile');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="glass-card-static w-full max-w-lg overflow-hidden flex flex-col shadow-2xl">
        <div className="section-header">
          <h2 className="section-title">Edit Profile: {name}</h2>
          <button onClick={onClose} style={{ color: 'var(--text-secondary)' }} className="hover:text-white transition"><X size={18}/></button>
        </div>
        <div className="p-5 flex-1 overflow-y-auto space-y-4 max-h-[60vh]">
          {Object.entries(config).map(([k, v]) => {
            if (Array.isArray(v)) {
              return (
                <div key={k}>
                  <label className="block text-xs mb-1" style={{ color: 'var(--text-tertiary)' }}>{k}</label>
                  <input 
                    type="text"
                    value={v.join(', ')}
                    onChange={(e) => setConfig({ ...config, [k]: e.target.value.split(',').map(s => s.trim()) })}
                    className="input-dark"
                  />
                  <div className="text-[10px] mt-1" style={{ color: 'var(--text-muted)' }}>Comma-separated list</div>
                </div>
              );
            }
            if (typeof v === 'boolean') {
              return (
                <div key={k} className="flex items-center gap-3 metric-row">
                  <label className="text-sm" style={{ color: 'var(--text-secondary)' }}>{k}</label>
                  <input 
                    type="checkbox"
                    checked={v}
                    onChange={(e) => setConfig({ ...config, [k]: e.target.checked })}
                    className="accent-indigo-500 w-4 h-4"
                  />
                </div>
              );
            }
            if (typeof v === 'number') {
              return (
                <div key={k}>
                  <label className="block text-xs mb-1" style={{ color: 'var(--text-tertiary)' }}>{k}</label>
                  <input 
                    type="number"
                    step="0.01"
                    value={v}
                    onChange={(e) => setConfig({ ...config, [k]: parseFloat(e.target.value) })}
                    className="input-dark"
                  />
                </div>
              );
            }
            return (
              <div key={k}>
                <label className="block text-xs mb-1" style={{ color: 'var(--text-tertiary)' }}>{k}</label>
                <input 
                  type="text"
                  value={v}
                  onChange={(e) => setConfig({ ...config, [k]: e.target.value })}
                  className="input-dark"
                />
              </div>
            );
          })}
        </div>
        <div className="p-4 border-t flex justify-end gap-3" style={{ borderColor: 'var(--border-primary)', background: 'var(--bg-secondary)' }}>
          <button onClick={onClose} className="btn-ghost">Cancel</button>
          <button 
            onClick={handleSave} 
            disabled={isSaving}
            className="btn-primary flex items-center gap-2"
          >
            <Save size={16} /> {isSaving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
}

export function StrategiesView() {
  // Multi-instrument scanner — all instruments from dashboard endpoint
  const { data: watchData, error: watchError } = useSWR('/dashboard/instruments', fetcher, {
    refreshInterval: 15000,
    fallbackData: { instruments: [] },
  });

  // Detailed ranking for a selected instrument
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const instruments = watchData?.instruments ?? [];

  // Auto-select first instrument for detail view
  React.useEffect(() => {
    if (instruments.length > 0 && !instruments.find(i => i.symbol === selectedSymbol)) {
      setSelectedSymbol(instruments[0].symbol);
    }
  }, [instruments, selectedSymbol]);

  const { data: rankingData, error: rankingError } = useSWR(
    selectedSymbol ? `/strategy/ranking?symbol=${selectedSymbol}` : null,
    fetcher
  );
  const { data: profilesData, mutate: mutateProfiles } = useSWR('/strategy/profiles', fetcher);

  const [editingProfile, setEditingProfile] = useState(null);

  const TREND_ICON = { BULLISH: TrendingUp, BEARISH: TrendingDown, NEUTRAL: Minus };
  const TREND_COLOR = { BULLISH: 'var(--success)', BEARISH: 'var(--danger)', NEUTRAL: 'var(--text-secondary)' };

  return (
    <div className="space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>Strategy Center</h1>

      {/* ── Active Scans — all instruments ── */}
      <div className="glass-card-static overflow-hidden">
        <div className="section-header">
          <h2 className="section-title">Active Scans</h2>
          <span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>{instruments.length} instruments monitored</span>
        </div>

        {instruments.length === 0 ? (
          <div className="p-8 text-center" style={{ color: 'var(--text-tertiary)' }}>
            {watchError ? 'Failed to load instruments.' : 'No instruments tracked. Add and activate instruments first.'}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Trend</th>
                  <th>Regime</th>
                  <th>ADX</th>
                  <th>Top Strategy</th>
                  <th className="text-right">Score</th>
                  <th className="text-right">Signal</th>
                </tr>
              </thead>
              <tbody>
                {instruments.map(inst => {
                  const Icon = TREND_ICON[inst.trend] ?? Minus;
                  const trendCls = TREND_COLOR[inst.trend] ?? 'var(--text-secondary)';
                  const signalClasses = {
                    SETUP_FOUND: 'badge-success',
                    NONE: 'badge-neutral',
                  };
                  const signalCls = signalClasses[inst.signal] ?? signalClasses.NONE;
                  const isSelected = inst.symbol === selectedSymbol;
                  
                  return (
                    <tr
                      key={inst.id}
                      onClick={() => setSelectedSymbol(inst.symbol)}
                      className="cursor-pointer"
                      style={isSelected ? { background: 'var(--accent-primary-dim)', borderLeft: '2px solid var(--accent-primary)' } : {}}
                    >
                      <td style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{inst.symbol}</td>
                      <td>
                        <span className="flex items-center gap-1 font-medium" style={{ color: trendCls }}>
                          <Icon size={12} /> {inst.trend}
                        </span>
                      </td>
                      <td>{inst.regime}</td>
                      <td>
                        {inst.adx != null ? (
                          <span style={{ color: inst.adx >= 25 ? 'var(--accent-primary)' : 'var(--text-secondary)', fontWeight: inst.adx >= 25 ? 600 : 400 }}>
                            {inst.adx}
                          </span>
                        ) : <span>--</span>}
                      </td>
                      <td>{inst.top_strategy ?? 'No Setup'}</td>
                      <td className="text-right font-bold" style={{ color: 'var(--accent-primary)' }}>
                        {inst.strategy_score != null ? inst.strategy_score : '--'}
                      </td>
                      <td className="text-right">
                        <span className={signalCls}>
                          {inst.signal ?? 'NONE'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Detailed Rankings for selected instrument */}
        <div className="glass-card-static overflow-hidden flex flex-col animate-fade-in-delay-1">
          <div className="section-header flex-col items-start gap-1">
            <h2 className="section-title">
              Strategy Rankings{' '}
              {selectedSymbol && (
                <span style={{ color: 'var(--accent-primary)' }}>— {selectedSymbol}</span>
              )}
            </h2>
            <p className="text-xs" style={{ color: 'var(--text-tertiary)' }}>Click any row above to view detailed scores</p>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>Strategy</th>
                <th className="text-right">Score</th>
              </tr>
            </thead>
            <tbody>
              {!rankingData && !rankingError ? (
                <tr>
                  <td colSpan="2" className="text-center p-8"><div className="skeleton h-4 w-1/2 mx-auto" /></td>
                </tr>
              ) : rankingData?.ranking ? (
                rankingData.ranking.map((s, i) => (
                  <tr key={i}>
                    <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>
                      {s.strategy}
                      {rankingData.winner === s.strategy && (
                        <span className="ml-2 badge-success">Winner</span>
                      )}
                    </td>
                    <td className="text-right font-bold" style={{ color: 'var(--accent-primary)' }}>{s.total?.toFixed(1) ?? 0}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="2" className="text-center p-8" style={{ color: 'var(--text-tertiary)' }}>
                    {selectedSymbol ? 'No ranking data yet for this instrument.' : 'Select an instrument above.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Strategy Configurations */}
        <div className="glass-card-static overflow-hidden flex flex-col animate-fade-in-delay-2">
          <div className="section-header">
            <h2 className="section-title">Strategy Configurations</h2>
          </div>
          <div className="p-4 space-y-4 overflow-y-auto">
            {!profilesData ? (
              <div className="text-center py-8" style={{ color: 'var(--text-tertiary)' }}>Loading profiles...</div>
            ) : Object.keys(profilesData).length === 0 ? (
              <div className="text-center py-8" style={{ color: 'var(--text-tertiary)' }}>No profiles found.</div>
            ) : (
              Object.entries(profilesData).map(([name, config]) => (
                <div key={name} className="metric-row">
                  <div>
                    <h3 className="font-bold mb-1" style={{ color: 'var(--text-primary)' }}>{name}</h3>
                    <div className="text-xs flex flex-wrap gap-2 mt-2">
                      {Object.keys(config).slice(0, 3).map(k => (
                        <span key={k} className="px-2 py-1 rounded" style={{ background: 'var(--bg-primary)', color: 'var(--text-secondary)' }}>
                          {k}: {Array.isArray(config[k]) ? config[k].join(', ') : config[k].toString()}
                        </span>
                      ))}
                      {Object.keys(config).length > 3 && (
                        <span className="px-2 py-1 rounded" style={{ background: 'var(--bg-primary)', color: 'var(--text-secondary)' }}>+{Object.keys(config).length - 3} more</span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => setEditingProfile({ name, config })}
                    className="btn-ghost px-3"
                  >
                    <Settings size={16} />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

      </div>

      {editingProfile && (
        <ProfileEditor
          name={editingProfile.name}
          initialConfig={editingProfile.config}
          onClose={() => setEditingProfile(null)}
          onSave={() => {
            setEditingProfile(null);
            mutateProfiles();
          }}
        />
      )}
    </div>
  );
}
