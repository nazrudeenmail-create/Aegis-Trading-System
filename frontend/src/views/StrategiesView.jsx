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
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-950 border border-slate-800 rounded-xl shadow-2xl w-full max-w-lg overflow-hidden flex flex-col">
        <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900">
          <h2 className="font-semibold text-white">Edit Profile: {name}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white"><X size={18}/></button>
        </div>
        <div className="p-4 flex-1 overflow-y-auto space-y-4 max-h-[60vh]">
          {Object.entries(config).map(([k, v]) => {
            if (Array.isArray(v)) {
              return (
                <div key={k}>
                  <label className="block text-xs text-slate-400 mb-1">{k}</label>
                  <input 
                    type="text"
                    value={v.join(', ')}
                    onChange={(e) => setConfig({ ...config, [k]: e.target.value.split(',').map(s => s.trim()) })}
                    className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm text-white"
                  />
                  <div className="text-[10px] text-slate-500 mt-1">Comma-separated list</div>
                </div>
              );
            }
            if (typeof v === 'boolean') {
              return (
                <div key={k} className="flex items-center gap-2">
                  <input 
                    type="checkbox"
                    checked={v}
                    onChange={(e) => setConfig({ ...config, [k]: e.target.checked })}
                    className="accent-indigo-500"
                  />
                  <label className="text-sm text-slate-300">{k}</label>
                </div>
              );
            }
            if (typeof v === 'number') {
              return (
                <div key={k}>
                  <label className="block text-xs text-slate-400 mb-1">{k}</label>
                  <input 
                    type="number"
                    step="0.01"
                    value={v}
                    onChange={(e) => setConfig({ ...config, [k]: parseFloat(e.target.value) })}
                    className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm text-white"
                  />
                </div>
              );
            }
            return (
              <div key={k}>
                <label className="block text-xs text-slate-400 mb-1">{k}</label>
                <input 
                  type="text"
                  value={v}
                  onChange={(e) => setConfig({ ...config, [k]: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm text-white"
                />
              </div>
            );
          })}
        </div>
        <div className="p-4 border-t border-slate-800 flex justify-end gap-2 bg-slate-900">
          <button onClick={onClose} className="px-4 py-2 text-slate-400 hover:text-white transition">Cancel</button>
          <button 
            onClick={handleSave} 
            disabled={isSaving}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded transition flex items-center gap-2"
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
  const TREND_COLOR = { BULLISH: 'text-emerald-400', BEARISH: 'text-rose-400', NEUTRAL: 'text-slate-400' };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white tracking-tight">Strategy Center</h1>

      {/* ── Active Scans — all instruments ── */}
      <div className="bg-slate-950 rounded-xl border border-slate-800 overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex justify-between items-center">
          <h2 className="font-semibold text-white">Active Scans</h2>
          <span className="text-xs text-slate-500">{instruments.length} instruments monitored</span>
        </div>

        {instruments.length === 0 ? (
          <div className="p-8 text-center text-slate-500">
            {watchError ? 'Failed to load instruments.' : 'No instruments tracked. Add and activate instruments first.'}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-900/50 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="p-3 font-medium">Symbol</th>
                  <th className="p-3 font-medium">Trend</th>
                  <th className="p-3 font-medium">Regime</th>
                  <th className="p-3 font-medium">ADX</th>
                  <th className="p-3 font-medium">Top Strategy</th>
                  <th className="p-3 font-medium text-right">Score</th>
                  <th className="p-3 font-medium text-right">Signal</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {instruments.map(inst => {
                  const Icon = TREND_ICON[inst.trend] ?? Minus;
                  const trendCls = TREND_COLOR[inst.trend] ?? 'text-slate-400';
                  const signalColors = {
                    SETUP_FOUND: 'text-emerald-400 bg-emerald-500/10',
                    NONE: 'text-slate-500 bg-slate-800',
                  };
                  const signalCls = signalColors[inst.signal] ?? signalColors.NONE;
                  const isSelected = inst.symbol === selectedSymbol;
                  return (
                    <tr
                      key={inst.id}
                      onClick={() => setSelectedSymbol(inst.symbol)}
                      className={`cursor-pointer transition ${isSelected ? 'bg-indigo-600/10 border-l-2 border-indigo-500' : 'hover:bg-slate-900/50'}`}
                    >
                      <td className="p-3 font-bold text-white">{inst.symbol}</td>
                      <td className="p-3">
                        <span className={`flex items-center gap-1 font-medium ${trendCls}`}>
                          <Icon size={12} /> {inst.trend}
                        </span>
                      </td>
                      <td className="p-3 text-slate-300">{inst.regime}</td>
                      <td className="p-3">
                        {inst.adx != null ? (
                          <span className={inst.adx >= 25 ? 'text-indigo-400 font-bold' : 'text-slate-400'}>
                            {inst.adx}
                          </span>
                        ) : <span className="text-slate-600">--</span>}
                      </td>
                      <td className="p-3 text-slate-400">{inst.top_strategy ?? 'No Setup'}</td>
                      <td className="p-3 text-right font-bold text-indigo-400">
                        {inst.strategy_score != null ? inst.strategy_score : '--'}
                      </td>
                      <td className="p-3 text-right">
                        <span className={`text-xs font-bold px-2 py-0.5 rounded ${signalCls}`}>
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
        <div className="bg-slate-950 rounded-xl border border-slate-800 overflow-hidden flex flex-col">
          <div className="p-4 border-b border-slate-800">
            <h2 className="font-semibold text-white">
              Strategy Rankings{' '}
              {selectedSymbol && (
                <span className="text-indigo-400">— {selectedSymbol}</span>
              )}
            </h2>
            <p className="text-xs text-slate-500 mt-1">Click any row above to view detailed scores</p>
          </div>
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-900/50 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="p-4 font-medium">Strategy</th>
                <th className="p-4 font-medium text-right">Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50 text-slate-300">
              {!rankingData && !rankingError ? (
                <tr>
                  <td colSpan="2" className="p-8 text-center text-slate-500">Loading rankings...</td>
                </tr>
              ) : rankingData?.ranking ? (
                rankingData.ranking.map((s, i) => (
                  <tr key={i} className="hover:bg-slate-900/50 transition">
                    <td className="p-4 font-medium text-white">
                      {s.strategy}
                      {rankingData.winner === s.strategy && (
                        <span className="ml-2 text-xs bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded">Winner</span>
                      )}
                    </td>
                    <td className="p-4 text-right font-bold text-indigo-400">{s.total?.toFixed(1) ?? 0}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="2" className="p-8 text-center text-slate-500">
                    {selectedSymbol ? 'No ranking data yet for this instrument.' : 'Select an instrument above.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Strategy Configurations */}
        <div className="bg-slate-950 rounded-xl border border-slate-800 overflow-hidden flex flex-col">
          <div className="p-4 border-b border-slate-800">
            <h2 className="font-semibold text-white">Strategy Configurations</h2>
          </div>
          <div className="p-4 space-y-4 overflow-y-auto">
            {!profilesData ? (
              <div className="text-center text-slate-500 py-8">Loading profiles...</div>
            ) : Object.keys(profilesData).length === 0 ? (
              <div className="text-center text-slate-500 py-8">No profiles found.</div>
            ) : (
              Object.entries(profilesData).map(([name, config]) => (
                <div key={name} className="bg-slate-900 border border-slate-800 rounded p-4 flex justify-between items-start">
                  <div>
                    <h3 className="font-bold text-white mb-1">{name}</h3>
                    <div className="text-xs text-slate-400 flex flex-wrap gap-2 mt-2">
                      {Object.keys(config).slice(0, 3).map(k => (
                        <span key={k} className="bg-slate-800 px-2 py-1 rounded">
                          {k}: {Array.isArray(config[k]) ? config[k].join(', ') : config[k].toString()}
                        </span>
                      ))}
                      {Object.keys(config).length > 3 && (
                        <span className="bg-slate-800 px-2 py-1 rounded">+{Object.keys(config).length - 3} more</span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => setEditingProfile({ name, config })}
                    className="p-2 bg-slate-800 hover:bg-indigo-600 text-slate-300 hover:text-white rounded transition"
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
