import React from 'react';
import { TrendingUp, TrendingDown, Minus, Activity, Zap } from 'lucide-react';

const TREND_COLOR = {
  BULLISH: 'text-emerald-400',
  BEARISH: 'text-rose-400',
  NEUTRAL: 'text-slate-400',
};

const TREND_ICON = {
  BULLISH: TrendingUp,
  BEARISH: TrendingDown,
  NEUTRAL: Minus,
};

function SessionBadge({ session }) {
  if (session === 'REGULAR' || session === 'EXTENDED')
    return <span className="text-xs font-medium text-emerald-400">● OPEN</span>;
  if (session === 'CLOSED')
    return <span className="text-xs font-medium text-slate-500">● CLOSED</span>;
  if (session === 'UNKNOWN')
    return <span className="text-xs font-medium text-slate-600">● --</span>;
  return <span className="text-xs font-medium text-amber-400">● {session}</span>;
}

function SignalBadge({ signal }) {
  const styles = {
    SETUP_FOUND:   'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    BUY_CANDIDATE: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    SELL_CANDIDATE:'bg-rose-500/10   text-rose-400   border-rose-500/30',
    WAITING:       'bg-amber-500/10  text-amber-400  border-amber-500/30',
    NONE:          'bg-slate-800     text-slate-500  border-slate-700',
  };
  const cls = styles[signal] ?? styles.NONE;
  return (
    <span className={`text-xs font-bold px-2 py-0.5 rounded border ${cls}`}>
      {signal ?? 'NONE'}
    </span>
  );
}

export function InstrumentCard({ data }) {
  const TrendIcon = TREND_ICON[data.trend] ?? Minus;
  const trendCls  = TREND_COLOR[data.trend] ?? 'text-slate-400';

  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex flex-col gap-3 hover:border-slate-600 transition-colors">

      {/* Header row */}
      <div className="flex justify-between items-start">
        <div>
          <div className="font-bold text-white text-sm tracking-wide">{data.symbol}</div>
          <div className="text-xs text-slate-500 mt-0.5">{data.asset_class}</div>
        </div>
        <SessionBadge session={data.session} />
      </div>

      {/* Price */}
      {data.price != null && (
        <div className="text-lg font-mono font-semibold text-white leading-none">
          {data.price.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 4,
          })}
        </div>
      )}

      {/* Trend + Regime */}
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="bg-slate-900 rounded-lg p-2">
          <div className="text-slate-500 mb-1">Trend</div>
          <div className={`flex items-center gap-1 font-semibold ${trendCls}`}>
            <TrendIcon size={11} />
            {data.trend ?? 'NEUTRAL'}
          </div>
        </div>
        <div className="bg-slate-900 rounded-lg p-2">
          <div className="text-slate-500 mb-1">Regime</div>
          <div className="font-semibold text-slate-300">{data.regime ?? 'UNKNOWN'}</div>
        </div>
      </div>

      {/* ADX */}
      <div className="flex items-center justify-between text-xs">
        <span className="text-slate-500">ADX Strength</span>
        {data.adx != null ? (
          <span className={`font-bold ${data.adx >= 25 ? 'text-indigo-400' : 'text-slate-400'}`}>
            {data.adx}
          </span>
        ) : (
          <span className="text-slate-600">--</span>
        )}
      </div>

      {/* Top Strategy */}
      {data.top_strategy && (
        <div className="flex items-center justify-between text-xs border-t border-slate-800 pt-2">
          <span className="text-slate-500 flex items-center gap-1">
            <Activity size={10} />
            {data.top_strategy}
          </span>
          {data.strategy_score != null && (
            <span className="font-bold text-indigo-400">{data.strategy_score}</span>
          )}
        </div>
      )}

      {/* Signal */}
      <div className="flex items-center justify-between">
        <span className="text-xs text-slate-500 flex items-center gap-1">
          <Zap size={10} /> Signal
        </span>
        <SignalBadge signal={data.signal} />
      </div>

    </div>
  );
}
