import React, { useState } from 'react';
import { Sidebar } from '../components/Sidebar';

export function DashboardLayout({ children, currentView, setCurrentView }) {
  return (
    <div className="flex h-screen bg-slate-900 text-slate-50 overflow-hidden font-sans">
      <Sidebar currentView={currentView} setCurrentView={setCurrentView} />
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Header / Topbar could go here if needed */}
        <div className="flex-1 overflow-y-auto bg-slate-900 p-6">
          {children}
        </div>
      </main>
    </div>
  );
}
