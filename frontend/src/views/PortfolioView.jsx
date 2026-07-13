import React from 'react';
import useSWR from 'swr';
import { fetcher } from '../api';

export function PortfolioView() {
  const { data: summary, error: summaryError } = useSWR('/dashboard/summary', fetcher);
  const { data: positionsData, error: positionsError } = useSWR('/broker/positions/open', fetcher);

  const isLoading = !summary && !summaryError;
  const isPositionsLoading = !positionsData && !positionsError;

  // Defaults if no data — support both new nested structure and legacy flat keys
  const mode    = summary?.trading_mode || "Unknown";
  const balance = summary?.account?.balance   ?? summary?.account_balance   ?? 0;
  const margin  = summary?.account?.available_margin ?? summary?.available_margin ?? 0;
  const pnl     = summary?.account?.unrealized_pnl   ?? summary?.unrealized_pnl   ?? 0;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>Portfolio</h1>
        <div className="text-sm font-medium px-3 py-1 rounded" style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-primary)', color: 'var(--text-secondary)' }}>
          Current Account: <span style={{ color: 'var(--accent-primary)' }}>{mode}</span>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-card stat-card animate-fade-in-delay-1">
          <h2 className="stat-label">Total Equity</h2>
          <div className="stat-value">
            {isLoading ? "..." : `$${balance.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`}
          </div>
        </div>
        <div className="glass-card stat-card animate-fade-in-delay-2">
          <h2 className="stat-label">Available Margin</h2>
          <div className="stat-value">
            {isLoading ? "..." : `$${margin.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`}
          </div>
        </div>
        <div className="glass-card stat-card animate-fade-in-delay-3">
          <h2 className="stat-label">Unrealized PnL</h2>
          <div className="stat-value" style={{ color: pnl >= 0 ? 'var(--success)' : 'var(--danger)' }}>
            {isLoading ? "..." : `$${pnl.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`}
          </div>
        </div>
      </div>

      <div className="glass-card-static overflow-hidden mt-6 animate-fade-in-delay-4">
        <div className="section-header">
          <h2 className="section-title">Open Positions</h2>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Direction</th>
              <th>Size</th>
              <th>Entry Price</th>
              <th>Current Price</th>
              <th className="text-right">Unrealized PnL</th>
            </tr>
          </thead>
          <tbody>
            {isPositionsLoading ? (
              <tr>
                <td colSpan="6" className="text-center p-8"><div className="skeleton h-4 w-1/2 mx-auto" /></td>
              </tr>
            ) : (!positionsData || positionsData.length === 0) ? (
              <tr>
                <td colSpan="6" className="text-center p-8" style={{ color: 'var(--text-tertiary)' }}>No open positions.</td>
              </tr>
            ) : (
              positionsData.map((pos, idx) => (
                <tr key={idx}>
                  <td style={{ color: 'var(--text-primary)', fontWeight: 'bold' }}>{pos.symbol}</td>
                  <td>
                    <span className={pos.direction === 'LONG' ? 'badge-success' : 'badge-danger'}>
                      {pos.direction}
                    </span>
                  </td>
                  <td>{pos.size}</td>
                  <td>${pos.entry_price?.toFixed(2) || '--'}</td>
                  <td>${pos.current_price?.toFixed(2) || '--'}</td>
                  <td className="text-right font-bold" style={{ color: pos.unrealized_pnl >= 0 ? 'var(--success)' : 'var(--danger)' }}>
                    ${pos.unrealized_pnl?.toFixed(2) || '0.00'}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
