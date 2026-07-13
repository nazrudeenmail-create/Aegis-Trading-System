import React from 'react';
import useSWR from 'swr';
import { fetcher } from '../api';
import { Activity, Database, Server, RefreshCw } from 'lucide-react';

export function SystemView() {
  const { data: status, error } = useSWR('/system/status', fetcher);
  const isLoading = !status && !error;
  
  const mktHealth = status?.engines?.market || "Offline";
  const stratHealth = status?.engines?.strategy || "Offline";
  const riskHealth = status?.engines?.risk || "Offline";
  const execHealth = status?.engines?.execution || "Offline";

  return (
    <div className="space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>System & Diagnostics</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Backend Health */}
        <div className="glass-card p-6 animate-fade-in-delay-1">
          <h2 className="text-lg font-semibold flex items-center gap-2 mb-4" style={{ color: 'var(--text-primary)' }}>
            <Server size={18} style={{ color: 'var(--accent-primary)' }} /> Backend Services
          </h2>
          <div className="space-y-3">
            <div className="metric-row">
              <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>Market Data Engine</span>
              <span className={mktHealth === 'Healthy' ? 'badge-success' : 'badge-danger'}>{isLoading ? "..." : mktHealth}</span>
            </div>
            <div className="metric-row">
              <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>Strategy Engine</span>
              <span className={stratHealth === 'Healthy' ? 'badge-success' : 'badge-danger'}>{isLoading ? "..." : stratHealth}</span>
            </div>
            <div className="metric-row">
              <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>Risk Engine</span>
              <span className={riskHealth === 'Healthy' ? 'badge-success' : 'badge-danger'}>{isLoading ? "..." : riskHealth}</span>
            </div>
            <div className="metric-row">
              <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>Execution Engine</span>
              <span className={execHealth === 'Healthy' ? 'badge-success' : 'badge-danger'}>{isLoading ? "..." : execHealth}</span>
            </div>
          </div>
        </div>

        {/* Database & Caching */}
        <div className="glass-card p-6 animate-fade-in-delay-2">
          <h2 className="text-lg font-semibold flex items-center gap-2 mb-4" style={{ color: 'var(--text-primary)' }}>
            <Database size={18} style={{ color: 'var(--accent-primary)' }} /> Infrastructure
          </h2>
          <div className="space-y-3">
            <div className="metric-row">
              <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>PostgreSQL</span>
              <span className="badge-success">Connected</span>
            </div>
            <div className="metric-row">
              <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>TimescaleDB Ext</span>
              <span className="badge-success">Active</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
