import React from 'react';
import { TrendingUp, TrendingDown, Minus, Activity, Zap } from 'lucide-react';

const TREND_COLOR = {
  BULLISH: 'var(--success)',
  BEARISH: 'var(--danger)',
  NEUTRAL: 'var(--text-secondary)',
};

const TREND_ICON = {
  BULLISH: TrendingUp,
  BEARISH: TrendingDown,
  NEUTRAL: Minus,
};

function SessionBadge({ session }) {
  if (session === 'REGULAR' || session === 'EXTENDED')
    return <span className="badge-success">OPEN</span>;
  if (session === 'CLOSED')
    return <span className="badge-neutral">CLOSED</span>;
  if (session === 'UNKNOWN')
    return <span className="badge-neutral">--</span>;
  return <span className="badge-warning">{session}</span>;
}

function SignalBadge({ signal }) {
  const map = {
    SETUP_FOUND: 'badge-success',
    BUY_CANDIDATE: 'badge-success',
    SELL_CANDIDATE: 'badge-danger',
    WAITING: 'badge-warning',
    NONE: 'badge-neutral',
  };
  return <span className={map[signal] ?? map.NONE}>{signal ?? 'NONE'}</span>;
}

export function InstrumentCard({ data }) {
  const TrendIcon = TREND_ICON[data.trend] ?? Minus;
  const trendColor = TREND_COLOR[data.trend] ?? 'var(--text-secondary)';

  return (
    <div className="glass-card p-4 flex flex-col gap-3">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <div className="font-bold text-sm tracking-wide" style={{ color: 'var(--text-primary)' }}>{data.symbol}</div>
          <div className="text-[11px] mt-0.5" style={{ color: 'var(--text-muted)' }}>{data.asset_class}</div>
        </div>
        <SessionBadge session={data.session} />
      </div>

      {/* Price */}
      {data.price != null && (
        <div className="text-lg font-semibold leading-none" style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>
          {data.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 4 })}
        </div>
      )}

      {/* Trend + Regime */}
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="rounded-lg p-2" style={{ background: 'var(--bg-secondary)' }}>
          <div style={{ color: 'var(--text-muted)' }} className="mb-1">Trend</div>
          <div className="flex items-center gap-1 font-semibold" style={{ color: trendColor }}>
            <TrendIcon size={11} />
            {data.trend ?? 'NEUTRAL'}
          </div>
        </div>
        <div className="rounded-lg p-2" style={{ background: 'var(--bg-secondary)' }}>
          <div style={{ color: 'var(--text-muted)' }} className="mb-1">Regime</div>
          <div className="font-semibold" style={{ color: 'var(--text-secondary)' }}>{data.regime ?? 'UNKNOWN'}</div>
        </div>
      </div>

      {/* ADX */}
      <div className="flex items-center justify-between text-xs">
        <span style={{ color: 'var(--text-muted)' }}>ADX Strength</span>
        {data.adx != null ? (
          <span className="font-bold" style={{ color: data.adx >= 25 ? 'var(--accent-primary)' : 'var(--text-secondary)' }}>
            {data.adx}
          </span>
        ) : (
          <span style={{ color: 'var(--text-muted)' }}>--</span>
        )}
      </div>

      {/* Top Strategy */}
      {data.top_strategy && (
        <div className="flex items-center justify-between text-xs pt-2" style={{ borderTop: '1px solid var(--border-primary)' }}>
          <span className="flex items-center gap-1" style={{ color: 'var(--text-tertiary)' }}>
            <Activity size={10} /> {data.top_strategy}
          </span>
          {data.strategy_score != null && (
            <span className="font-bold" style={{ color: 'var(--accent-primary)' }}>{data.strategy_score}</span>
          )}
        </div>
      )}

      {/* Signal */}
      <div className="flex items-center justify-between">
        <span className="text-xs flex items-center gap-1" style={{ color: 'var(--text-muted)' }}>
          <Zap size={10} /> Signal
        </span>
        <SignalBadge signal={data.signal} />
      </div>
    </div>
  );
}
