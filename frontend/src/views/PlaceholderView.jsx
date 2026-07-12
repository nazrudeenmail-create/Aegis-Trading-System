import React from 'react';

export function PlaceholderView({ title }) {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white tracking-tight">{title}</h1>
      <div className="bg-slate-950 p-8 rounded-xl border border-slate-800 text-slate-500 text-center">
        This view is under construction for Phase 12.
      </div>
    </div>
  );
}
