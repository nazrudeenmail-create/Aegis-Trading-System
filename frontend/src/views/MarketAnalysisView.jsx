import React, { useState } from 'react';
import useSWR from 'swr';
import { fetcher } from '../api';
import { Activity, TrendingUp, BarChart2, Gauge, Clock } from 'lucide-react';
import { Chart } from '../components/Chart';

const timeframes = ['1m', '5m', '15m', '1h', '4h', '1d'];

export function MarketAnalysisView() {
  const [symbol, setSymbol] = useState('');
  const [timeframe, setTimeframe] = useState('1h');
  
  const { data: instruments = [] } = useSWR('/instruments/', fetcher);
  const activeInstruments = instruments.filter(i => ['ACTIVE', 'WATCHLIST'].includes(i.status));
  
  React.useEffect(() => {
    if (activeInstruments.length > 0 && !activeInstruments.some(i => i.symbol === symbol)) {
      setSymbol(activeInstruments[0].symbol);
    }
  }, [activeInstruments, symbol]);

  const { data: analysisData, error: analysisError, isLoading: isAnalysisLoading } = useSWR(symbol ? `/market/current?symbol=${symbol}` : null, fetcher, { refreshInterval: 15000 });
  const { data: candlesData, error: candlesError } = useSWR(symbol ? `/market/candles?symbol=${symbol}&timeframe=${timeframe}&limit=200` : null, fetcher, { refreshInterval: 60000 });

  if (isAnalysisLoading) return <div className="p-8 text-slate-400">Loading market analysis for {symbol}...</div>;
  if (analysisError) {
    if (analysisError?.response?.status === 404) {
      return (
        <div className="p-8 space-y-4">
          <div className="text-amber-400 font-bold">No Data for {symbol} Yet</div>
          <p className="text-slate-400 text-sm">
            The symbol <strong>{symbol}</strong> was not found in the latest market intelligence snapshot. 
          </p>
          <ul className="list-disc pl-5 text-slate-500 text-sm space-y-1 mt-2">
            <li>Ensure you have added the instrument in the <strong>Instruments</strong> tab.</li>
            <li>Ensure the instrument's tracking status is <strong>ACTIVE</strong>.</li>
            <li>Ensure the backend orchestrator is running and streaming market data.</li>
          </ul>
        </div>
      );
    }
    return <div className="p-8 text-rose-400">Failed to load market data. Ensure the orchestrator is running.</div>;
  }
  if (!analysisData) return <div className="p-8 text-slate-400">No market data available yet. Add instruments and start the orchestrator.</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white tracking-tight">Market Analysis</h1>
        <select
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          className="bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 w-40"
        >
          {activeInstruments.map(inst => (
            <option key={inst.symbol} value={inst.symbol}>{inst.symbol}</option>
          ))}
          {activeInstruments.length === 0 && <option value={symbol}>{symbol}</option>}
        </select>
      </div>

      {/* Price Header & Chart Container */}
      <div className="bg-slate-950 rounded-xl border border-slate-800 overflow-hidden">
        <div className="p-6 border-b border-slate-800 flex justify-between items-end">
          <div className="flex items-end gap-4">
            <h2 className="text-3xl font-bold text-white">{analysisData.symbol || symbol}</h2>
            <span className="text-2xl font-mono text-emerald-400">${analysisData.price?.toFixed(2) || '--'}</span>
          </div>
          
          <div className="flex items-center gap-2 bg-slate-900 rounded p-1 border border-slate-700">
            {timeframes.map(tf => (
              <button 
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-3 py-1 text-xs font-medium rounded ${timeframe === tf ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}
              >
                {tf.toUpperCase()}
              </button>
            ))}
          </div>
        </div>
        
        {/* Chart */}
        <div className="p-4" style={{ height: '400px' }}>
          {(!candlesData && !candlesError) ? (
            <div className="h-full flex items-center justify-center text-slate-500"><Clock className="animate-spin mr-2" size={16}/> Loading chart...</div>
          ) : candlesError ? (
            <div className="h-full flex items-center justify-center text-red-400">Failed to load candles</div>
          ) : (
            <Chart data={candlesData} />
          )}
        </div>
      </div>

      {/* Trend & Regime Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-950 p-5 rounded-xl border border-slate-800">
          <div className="flex items-center gap-2 text-slate-400 mb-3">
            <TrendingUp size={16} />
            <span className="text-sm font-medium">Trend Direction</span>
          </div>
          <div className={`text-xl font-bold ${
            analysisData.trend?.direction === 'bullish' ? 'text-emerald-400' :
            analysisData.trend?.direction === 'bearish' ? 'text-rose-400' : 'text-slate-300'
          }`}>
            {analysisData.trend?.direction?.toUpperCase() || 'NEUTRAL'}
          </div>
          <div className="text-xs text-slate-500 mt-1">Strength: {analysisData.trend?.strength?.toUpperCase() || 'NONE'}</div>
        </div>

        <div className="bg-slate-950 p-5 rounded-xl border border-slate-800">
          <div className="flex items-center gap-2 text-slate-400 mb-3">
            <Gauge size={16} />
            <span className="text-sm font-medium">Market Regime</span>
          </div>
          <div className="text-xl font-bold text-indigo-400">
            {analysisData.regime?.toUpperCase() || 'UNKNOWN'}
          </div>
        </div>

        <div className="bg-slate-950 p-5 rounded-xl border border-slate-800">
          <div className="flex items-center gap-2 text-slate-400 mb-3">
            <BarChart2 size={16} />
            <span className="text-sm font-medium">Volatility</span>
          </div>
          <div className="text-xl font-bold text-slate-200">
            {analysisData.indicators?.atr ? `ATR: ${analysisData.indicators.atr.toFixed(4)}` : 'N/A'}
          </div>
        </div>
      </div>

      {/* Indicator Table */}
      <div className="bg-slate-950 rounded-xl border border-slate-800 overflow-hidden">
        <div className="p-4 border-b border-slate-800">
          <h2 className="font-semibold text-white flex items-center gap-2">
            <Activity size={18} className="text-indigo-400"/> Technical Indicators ({analysisData.timeframe || '1H'})
          </h2>
        </div>
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-900/50 text-slate-400 border-b border-slate-800">
            <tr>
              <th className="p-4 font-medium">Indicator</th>
              <th className="p-4 font-medium">Value</th>
              <th className="p-4 font-medium">Signal</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {analysisData.indicators?.ema20 && (
              <tr><td className="p-4 text-white font-medium">EMA 20</td><td className="p-4 text-slate-300">{analysisData.indicators.ema20.toFixed(4)}</td><td className="p-4 text-slate-400">-</td></tr>
            )}
            {analysisData.indicators?.ema50 && (
              <tr><td className="p-4 text-white font-medium">EMA 50</td><td className="p-4 text-slate-300">{analysisData.indicators.ema50.toFixed(4)}</td><td className="p-4 text-slate-400">-</td></tr>
            )}
            {analysisData.indicators?.adx !== undefined && (
              <tr>
                <td className="p-4 text-white font-medium">ADX</td>
                <td className="p-4 text-slate-300">{analysisData.indicators.adx.toFixed(1)}</td>
                <td className={`p-4 ${analysisData.indicators.adx >= 25 ? 'text-emerald-400' : 'text-slate-500'}`}>
                  {analysisData.indicators.adx >= 25 ? 'STRONG' : 'WEAK'}
                </td>
              </tr>
            )}
            {analysisData.indicators?.atr !== undefined && (
              <tr><td className="p-4 text-white font-medium">ATR</td><td className="p-4 text-slate-300">{analysisData.indicators.atr.toFixed(4)}</td><td className="p-4 text-slate-400">-</td></tr>
            )}
            {!analysisData.indicators && (
              <tr><td colSpan="3" className="p-8 text-center text-slate-500">No indicator data available. Ensure market data is flowing.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}