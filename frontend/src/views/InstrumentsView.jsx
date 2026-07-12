import React, { useEffect, useState } from 'react';
import { Search, Filter, Play, Pause, AlertTriangle, Clock } from 'lucide-react';
import { fetcher, api, wsClient } from '../api';
import useSWR from 'swr';

export function InstrumentsView() {
  const [search, setSearch] = useState('');
  const [sessions, setSessions] = useState({});

  // Fetch instruments
  const { data: instruments, mutate: mutateInstruments } = useSWR('/instruments/', fetcher, { fallbackData: [] });
  
  // Fetch initial market sessions
  useEffect(() => {
    fetcher('/instruments/market-sessions').then(data => setSessions(data || {}));
  }, []);

  // Subscribe to real-time session changes
  useEffect(() => {
    wsClient.connect();
    const unsubscribe = wsClient.subscribe((msg) => {
      if (msg.type === 'SESSION_CHANGED') {
        // Find the symbol for this instrument_id
        const inst = instruments.find(i => i.id === msg.instrument_id);
        if (inst) {
          // Normalize REGULAR to OPEN for UI consistency with the old API
          const uiState = ['REGULAR', 'EXTENDED'].includes(msg.new_state) ? 'OPEN' : 'CLOSED';
          setSessions(prev => ({ ...prev, [inst.symbol]: uiState }));
        }
      }
    });

    return () => {
      unsubscribe();
    };
  }, [instruments]);

  const toggleStatus = async (inst) => {
    const newStatus = inst.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
    try {
      await api.patch(`/instruments/${inst.id}`, { status: newStatus });
      mutateInstruments();
    } catch (err) {
      console.error("Failed to update status", err);
    }
  };

  const filtered = instruments.filter(i => 
    i.symbol.toLowerCase().includes(search.toLowerCase()) || 
    i.name.toLowerCase().includes(search.toLowerCase())
  );

  const [isSearchModalOpen, setIsSearchModalOpen] = useState(false);
  const [brokerSearch, setBrokerSearch] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  const handleSearchBroker = async () => {
    if (!brokerSearch.trim()) return;
    setIsSearching(true);
    try {
      const res = await api.get(`/market/broker/search?query=${brokerSearch}`);
      setSearchResults(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsSearching(false);
    }
  };

  const handleAddInstrument = async (inst) => {
    try {
      await api.post('/instruments/', {
        symbol: inst.symbol,
        name: inst.name,
        market_type: inst.market_type
      });
      mutateInstruments();
      setIsSearchModalOpen(false);
    } catch (e) {
      console.error("Failed to add instrument", e);
      alert("Failed to add instrument or it already exists.");
    }
  };

  return (
    <div className="space-y-6 relative">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white tracking-tight">Instrument Universe</h1>
        <button 
          onClick={() => setIsSearchModalOpen(true)}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded shadow transition"
        >
          + Add Instrument
        </button>
      </div>

      {/* Toolbar */}
      <div className="flex items-center gap-4 bg-slate-950 p-4 rounded-xl border border-slate-800">
        <div className="relative flex-1 max-w-sm">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input 
            type="text" 
            placeholder="Search active symbols..." 
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-md py-2 pl-10 pr-4 text-sm text-white focus:outline-none focus:border-indigo-500"
          />
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-slate-900 border border-slate-700 rounded-md text-sm text-slate-300 hover:bg-slate-800 transition">
          <Filter size={16} /> Filters
        </button>
      </div>

      {/* Data Table */}
      <div className="bg-slate-950 rounded-xl border border-slate-800 overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-900/50 text-slate-400 border-b border-slate-800">
            <tr>
              <th className="p-4 font-medium">Symbol</th>
              <th className="p-4 font-medium">Name</th>
              <th className="p-4 font-medium">Market Session</th>
              <th className="p-4 font-medium">Component Status</th>
              <th className="p-4 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {filtered.map(inst => {
              const sessionState = sessions[inst.symbol] || 'UNKNOWN';
              return (
                <tr key={inst.id} className="hover:bg-slate-900/50 transition">
                  <td className="p-4 font-bold text-white">{inst.symbol}</td>
                  <td className="p-4 text-slate-400">
                    <div>{inst.name}</div>
                    <div className="text-xs text-slate-500">{inst.market_type}</div>
                  </td>
                  <td className="p-4">
                    {sessionState === 'OPEN' ? (
                      <span className="text-xs text-emerald-400 flex items-center gap-1"><Play size={12}/> OPEN</span>
                    ) : sessionState === 'CLOSED' ? (
                      <span className="text-xs text-slate-500 flex items-center gap-1"><Pause size={12}/> CLOSED</span>
                    ) : (
                      <span className="text-xs text-slate-500 flex items-center gap-1"><Clock size={12}/> {sessionState}</span>
                    )}
                  </td>
                  <td className="p-4">
                    <div className="flex gap-4 text-xs">
                      <div className="flex flex-col gap-1">
                        <span className="text-slate-400">Historical Data: <span className="text-emerald-400">✅</span></span>
                        <span className="text-slate-400">Live Feed: {inst.status === 'ACTIVE' ? <span className="text-emerald-400">🟢 Active</span> : <span className="text-red-400">🔴 Inactive</span>}</span>
                        <span className="text-slate-400">Analysis: {inst.status === 'ACTIVE' ? <span className="text-emerald-400">🟢 Active</span> : <span className="text-red-400">🔴 Inactive</span>}</span>
                      </div>
                      <div className="flex flex-col gap-1">
                        <span className="text-slate-400">Strategies: {inst.trading_enabled ? <span className="text-emerald-400">🟢 Evaluating</span> : <span className="text-red-400">🔴 Disabled</span>}</span>
                        <span className="text-slate-400">Trading: {inst.allow_new_positions ? <span className="text-emerald-400">🟢 Executing</span> : <span className="text-red-400">🔴 Disabled</span>}</span>
                      </div>
                    </div>
                  </td>
                  <td className="p-4 text-right flex items-center justify-end gap-2">
                    <button 
                      onClick={() => toggleStatus(inst)}
                      className={`text-xs font-medium px-3 py-1 rounded border ${
                        inst.status === 'ACTIVE' 
                          ? 'text-red-400 border-red-500/20 hover:bg-red-500/10' 
                          : 'text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/10'
                      }`}
                    >
                      {inst.status === 'ACTIVE' ? 'Stop Feed' : 'Start Feed'}
                    </button>
                  </td>
                </tr>
              )
            })}
            {filtered.length === 0 && (
              <tr>
                <td colSpan="5" className="p-8 text-center text-slate-500">No instruments found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {isSearchModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-950 border border-slate-800 rounded-xl shadow-2xl w-full max-w-lg overflow-hidden flex flex-col">
            <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900">
              <h2 className="font-semibold text-white">Search Broker Instruments</h2>
              <button onClick={() => setIsSearchModalOpen(false)} className="text-slate-400 hover:text-white">&times;</button>
            </div>
            <div className="p-4 flex gap-2">
              <input 
                type="text" 
                placeholder="Search symbol (e.g., BTC, AAPL)" 
                value={brokerSearch}
                onChange={e => setBrokerSearch(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSearchBroker()}
                className="flex-1 bg-slate-900 border border-slate-700 rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
              <button 
                onClick={handleSearchBroker}
                disabled={isSearching}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded text-sm transition"
              >
                {isSearching ? 'Searching...' : 'Search'}
              </button>
            </div>
            <div className="flex-1 overflow-y-auto max-h-64 p-4 border-t border-slate-800 bg-[#0a0a0a]">
              {searchResults.length === 0 ? (
                <div className="text-center text-slate-500 text-sm mt-4">Search to find instruments</div>
              ) : (
                <ul className="space-y-2">
                  {searchResults.map((res, i) => (
                    <li key={i} className="flex justify-between items-center p-3 bg-slate-900 rounded border border-slate-800">
                      <div>
                        <div className="font-bold text-white">{res.symbol}</div>
                        <div className="text-xs text-slate-400">{res.name} &middot; {res.market_type}</div>
                      </div>
                      <button 
                        onClick={() => handleAddInstrument(res)}
                        className="px-3 py-1 bg-indigo-600 hover:bg-indigo-700 text-white text-xs rounded transition"
                      >
                        Add
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
