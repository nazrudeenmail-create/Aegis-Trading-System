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

  const { data: analysisData, error: analysisError, isLoading: isAnalysisLoading } = useSWR(symbol ? `/market/current?symbol=${symbol}` : null, fetcher, { refreshInterval: 5000 });
  const { data: candlesData, error: candlesError } = useSWR(symbol ? `/market/candles?symbol=${symbol}&timeframe=${timeframe}&limit=200` : null, fetcher, { refreshInterval: 15000 });

  if (isAnalysisLoading) return <div className="p-8" style={{ color: 'var(--text-secondary)' }}>Loading market analysis for {symbol}...</div>;
  if (analysisError) {
    if (analysisError?.response?.status === 404) {
      return (
        <div className="p-8 space-y-4">
          <div className="font-bold" style={{ color: 'var(--warning)' }}>No Data for {symbol} Yet</div>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            The symbol <strong>{symbol}</strong> was not found in the latest market intelligence snapshot. 
          </p>
          <ul className="list-disc pl-5 text-sm space-y-1 mt-2" style={{ color: 'var(--text-tertiary)' }}>
            <li>Ensure you have added the instrument in the <strong>Instruments</strong> tab.</li>
            <li>Ensure the instrument's tracking status is <strong>ACTIVE</strong>.</li>
            <li>Ensure the backend orchestrator is running and streaming market data.</li>
          </ul>
        </div>
      );
    }
    return <div className="p-8" style={{ color: 'var(--danger)' }}>Failed to load market data. Ensure the orchestrator is running.</div>;
  }
  if (!analysisData) return <div className="p-8" style={{ color: 'var(--text-secondary)' }}>No market data available yet. Add instruments and start the orchestrator.</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center animate-fade-in">
        <h1 className="text-2xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>Market Analysis</h1>
        <select
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          className="input-dark w-40"
        >
          {activeInstruments.map(inst => (
            <option key={inst.symbol} value={inst.symbol}>{inst.symbol}</option>
          ))}
          {activeInstruments.length === 0 && <option value={symbol}>{symbol}</option>}
        </select>
      </div>

      {/* Price Header & Chart Container */}
      <div className="glass-card-static overflow-hidden animate-fade-in animate-fade-in-delay-1">
        <div className="p-6 border-b flex justify-between items-end" style={{ borderColor: 'var(--border-primary)' }}>
          <div className="flex items-end gap-4">
            <h2 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>{analysisData.symbol || symbol}</h2>
            <span className="text-2xl font-mono" style={{ color: 'var(--success)' }}>${analysisData.price?.toFixed(2) || '--'}</span>
          </div>
          
          <div className="flex items-center gap-1 rounded p-1" style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-primary)' }}>
            {timeframes.map(tf => (
              <button 
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-3 py-1 text-xs font-medium rounded transition ${timeframe === tf ? 'btn-primary' : ''}`}
                style={timeframe !== tf ? { color: 'var(--text-secondary)' } : {}}
              >
                {tf.toUpperCase()}
              </button>
            ))}
          </div>
        </div>
        
        {/* Chart */}
        <div className="p-4" style={{ height: '400px' }}>
          {(!candlesData && !candlesError) ? (
            <div className="h-full flex items-center justify-center" style={{ color: 'var(--text-tertiary)' }}><Clock className="animate-spin mr-2" size={16}/> Loading chart...</div>
          ) : candlesError ? (
            <div className="h-full flex items-center justify-center" style={{ color: 'var(--danger)' }}>Failed to load candles</div>
          ) : (
            <Chart data={candlesData} />
          )}
        </div>
      </div>

      {/* Trend & Regime Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-card stat-card animate-fade-in animate-fade-in-delay-2">
          <div className="flex items-center gap-2 mb-3 stat-label" style={{ color: 'var(--text-tertiary)' }}>
            <TrendingUp size={16} />
            <span>Trend Direction</span>
          </div>
          <div className="stat-value" style={{
            color: analysisData.trend?.direction === 'bullish' ? 'var(--success)' :
                   analysisData.trend?.direction === 'bearish' ? 'var(--danger)' : 'var(--text-secondary)'
          }}>
            {analysisData.trend?.direction?.toUpperCase() || 'NEUTRAL'}
          </div>
          <div className="stat-sub">Strength: {analysisData.trend?.strength?.toUpperCase() || 'NONE'}</div>
        </div>

        <div className="glass-card stat-card animate-fade-in animate-fade-in-delay-3">
          <div className="flex items-center gap-2 mb-3 stat-label" style={{ color: 'var(--text-tertiary)' }}>
            <Gauge size={16} />
            <span>Market Regime</span>
          </div>
          <div className="stat-value" style={{ color: 'var(--accent-primary)' }}>
            {analysisData.regime?.toUpperCase() || 'UNKNOWN'}
          </div>
        </div>

        <div className="glass-card stat-card animate-fade-in animate-fade-in-delay-4">
          <div className="flex items-center gap-2 mb-3 stat-label" style={{ color: 'var(--text-tertiary)' }}>
            <BarChart2 size={16} />
            <span>Volatility</span>
          </div>
          <div className="stat-value" style={{ color: 'var(--text-primary)' }}>
            {analysisData.indicators?.atr?.atr != null ? `ATR: ${Number(analysisData.indicators.atr.atr).toFixed(4)}` : 'N/A'}
          </div>
        </div>
      </div>

      {/* Indicator Table */}
      <div className="glass-card-static overflow-hidden animate-fade-in animate-fade-in-delay-4">
        <div className="section-header">
          <h2 className="section-title">
            <Activity size={18} style={{ color: 'var(--accent-primary)' }}/> Technical Indicators ({analysisData.timeframe || '1H'})
          </h2>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Indicator</th>
              <th>Value</th>
              <th>Signal</th>
            </tr>
          </thead>
          <tbody>
            {analysisData.indicators?.ema?.ema_20 != null && (
              <tr>
                <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>EMA 20</td>
                <td>{Number(analysisData.indicators.ema.ema_20).toFixed(4)}</td>
                <td>-</td>
              </tr>
            )}
            {analysisData.indicators?.ema?.ema_50 != null && (
              <tr>
                <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>EMA 50</td>
                <td>{Number(analysisData.indicators.ema.ema_50).toFixed(4)}</td>
                <td>-</td>
              </tr>
            )}
            {analysisData.indicators?.adx?.adx != null && (
              <tr>
                <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>ADX</td>
                <td>{Number(analysisData.indicators.adx.adx).toFixed(1)}</td>
                <td style={{ color: Number(analysisData.indicators.adx.adx) >= 25 ? 'var(--success)' : 'var(--text-secondary)' }}>
                  {Number(analysisData.indicators.adx.adx) >= 25 ? 'STRONG' : 'WEAK'}
                </td>
              </tr>
            )}
            {analysisData.indicators?.atr?.atr != null && (
              <tr>
                <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>ATR</td>
                <td>{Number(analysisData.indicators.atr.atr).toFixed(4)}</td>
                <td>-</td>
              </tr>
            )}
            {analysisData.indicators?.swing?.swing_high != null && (
              <tr>
                <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>Swing High</td>
                <td>{Number(analysisData.indicators.swing.swing_high).toFixed(4)}</td>
                <td>-</td>
              </tr>
            )}
            {analysisData.indicators?.swing?.swing_low != null && (
              <tr>
                <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>Swing Low</td>
                <td>{Number(analysisData.indicators.swing.swing_low).toFixed(4)}</td>
                <td>-</td>
              </tr>
            )}
            {analysisData.indicators?.pullback?.is_pullback && (
              <tr>
                <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>Pullback Distance</td>
                <td>{analysisData.indicators.pullback.distance_from_ema20 != null ? Number(analysisData.indicators.pullback.distance_from_ema20).toFixed(4) : '--'}</td>
                <td style={{ color: 'var(--info)' }}>ACTIVE</td>
              </tr>
            )}
            {analysisData.indicators?.donchian?.channel_width != null && (
              <tr>
                <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>Donchian Width</td>
                <td>{Number(analysisData.indicators.donchian.channel_width).toFixed(4)}</td>
                <td>
                  {analysisData.indicators.donchian.is_breakout_up ? <span style={{ color: 'var(--success)' }}>BRK UP</span> : 
                   analysisData.indicators.donchian.is_breakout_down ? <span style={{ color: 'var(--danger)' }}>BRK DOWN</span> : '-'}
                </td>
              </tr>
            )}
            {!analysisData.indicators && (
              <tr>
                <td colSpan="3" className="text-center" style={{ padding: '2rem', color: 'var(--text-tertiary)' }}>
                  No indicator data available. Ensure market data is flowing.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}