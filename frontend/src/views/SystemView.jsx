import React, { useState } from 'react';
import useSWR from 'swr';
import { Activity, Database, Server, RefreshCw } from 'lucide-react';

export function SystemView() {
  const { data: status, error } = useSWR('/system/status');
  const isLoading = !status && !error;
  
  const mktHealth = status?.engines?.market || "Offline";
  const stratHealth = status?.engines?.strategy || "Offline";
  const riskHealth = status?.engines?.risk || "Offline";
  const execHealth = status?.engines?.execution || "Offline";

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white tracking-tight">System & Diagnostics</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Backend Health */}
        <div className="bg-slate-950 p-6 rounded-xl border border-slate-800">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
            <Server size={18} className="text-indigo-400" /> Backend Services
          </h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-slate-900 rounded border border-slate-800">
              <span className="text-sm font-medium text-slate-300">Market Data Engine</span>
              <span className={`px-2 py-1 border rounded text-xs ${mktHealth === 'Healthy' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'}`}>{isLoading ? "..." : mktHealth}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-slate-900 rounded border border-slate-800">
              <span className="text-sm font-medium text-slate-300">Strategy Engine</span>
              <span className={`px-2 py-1 border rounded text-xs ${stratHealth === 'Healthy' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'}`}>{isLoading ? "..." : stratHealth}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-slate-900 rounded border border-slate-800">
              <span className="text-sm font-medium text-slate-300">Risk Engine</span>
              <span className={`px-2 py-1 border rounded text-xs ${riskHealth === 'Healthy' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'}`}>{isLoading ? "..." : riskHealth}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-slate-900 rounded border border-slate-800">
              <span className="text-sm font-medium text-slate-300">Execution Engine</span>
              <span className={`px-2 py-1 border rounded text-xs ${execHealth === 'Healthy' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'}`}>{isLoading ? "..." : execHealth}</span>
            </div>
          </div>
        </div>

        {/* Database & Caching */}
        <div className="bg-slate-950 p-6 rounded-xl border border-slate-800">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
            <Database size={18} className="text-indigo-400" /> Infrastructure
          </h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-slate-900 rounded border border-slate-800">
              <span className="text-sm font-medium text-slate-300">PostgreSQL</span>
              <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded text-xs">Connected</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-slate-900 rounded border border-slate-800">
              <span className="text-sm font-medium text-slate-300">TimescaleDB Ext</span>
              <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded text-xs">Active</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
