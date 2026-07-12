import React from 'react';
import { 
  LayoutDashboard, 
  LineChart, 
  PieChart, 
  ListTree, 
  BrainCircuit, 
  ShieldAlert, 
  Link2, 
  Settings, 
  Terminal
} from 'lucide-react';

const navItems = [
  { name: 'Overview', icon: LayoutDashboard, id: 'overview' },
  { name: 'Market', icon: LineChart, id: 'market' },
  { name: 'Portfolio', icon: PieChart, id: 'portfolio' },
  { name: 'Instruments', icon: ListTree, id: 'instruments' },
  { name: 'Strategies', icon: BrainCircuit, id: 'strategies' },
  { name: 'Risk', icon: ShieldAlert, id: 'risk' },
  { name: 'Connections', icon: Link2, id: 'connections' },
  { name: 'Settings', icon: Settings, id: 'settings' },
  { name: 'System', icon: Terminal, id: 'system' },
];

export function Sidebar({ currentView, setCurrentView }) {
  return (
    <div className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col h-screen">
      <div className="h-16 flex items-center px-6 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-indigo-500 rounded flex items-center justify-center">
            <span className="text-white font-bold text-xs tracking-tighter">ATS</span>
          </div>
          <span className="text-slate-200 font-semibold tracking-wide">Aegis Trading</span>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto py-4">
        <nav className="space-y-1 px-3">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => setCurrentView(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 text-sm rounded-md transition-colors ${
                  isActive 
                    ? 'bg-indigo-500/10 text-indigo-400' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <Icon size={18} className={isActive ? 'text-indigo-400' : 'text-slate-500'} />
                {item.name}
              </button>
            );
          })}
        </nav>
      </div>
      
      <div className="p-4 border-t border-slate-800">
        <div className="bg-slate-900 rounded px-3 py-2 flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
          <span className="text-xs text-slate-400">System Online</span>
        </div>
      </div>
    </div>
  );
}
