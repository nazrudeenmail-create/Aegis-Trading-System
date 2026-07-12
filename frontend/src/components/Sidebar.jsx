import React from 'react';
import { 
  LayoutDashboard, 
  ListTree,
  Activity,
  BrainCircuit,
  ShieldAlert,
  ShoppingCart,
  Briefcase,
  ScrollText,
  Link2,
  Settings,
  Terminal,
  Radio
} from 'lucide-react';

const navGroups = [
  {
    label: 'Dashboard',
    items: [
      { name: 'Overview', icon: LayoutDashboard, id: 'overview' },
      { name: 'Pipeline Monitor', icon: Radio, id: 'pipeline' },
    ]
  },
  {
    label: 'Market',
    items: [
      { name: 'Instruments', icon: ListTree, id: 'instruments' },
      { name: 'Market Analysis', icon: Activity, id: 'market' },
    ]
  },
  {
    label: 'Strategies',
    items: [
      { name: 'Strategy Monitor', icon: BrainCircuit, id: 'strategies' },
    ]
  },
  {
    label: 'Trading',
    items: [
      { name: 'Risk', icon: ShieldAlert, id: 'risk' },
      { name: 'Orders', icon: ShoppingCart, id: 'orders' },
      { name: 'Positions', icon: Briefcase, id: 'positions' },
    ]
  },
  {
    label: 'System',
    items: [
      { name: 'Decision Journal', icon: ScrollText, id: 'journal' },
      { name: 'Health', icon: Terminal, id: 'system' },
      { name: 'Settings', icon: Settings, id: 'settings' },
    ]
  },
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
        {navGroups.map((group) => (
          <div key={group.label} className="mb-4">
            <div className="px-6 py-1 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              {group.label}
            </div>
            <nav className="space-y-1 px-3 mt-1">
              {group.items.map((item) => {
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
        ))}
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