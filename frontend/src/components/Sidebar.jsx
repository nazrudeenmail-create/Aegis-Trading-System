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
  Radio,
  Zap
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
      { name: 'Strategy Center', icon: BrainCircuit, id: 'strategies' },
    ]
  },
  {
    label: 'Trading',
    items: [
      { name: 'Portfolio', icon: Briefcase, id: 'positions' },
      { name: 'Orders', icon: ShoppingCart, id: 'orders' },
      { name: 'Risk Manager', icon: ShieldAlert, id: 'risk' },
    ]
  },
  {
    label: 'System',
    items: [
      { name: 'Decision Journal', icon: ScrollText, id: 'journal' },
      { name: 'Connections', icon: Link2, id: 'connections' },
      { name: 'Health', icon: Terminal, id: 'system' },
      { name: 'Settings', icon: Settings, id: 'settings' },
    ]
  },
];

export function Sidebar({ currentView, setCurrentView }) {
  return (
    <div
      className="w-64 flex flex-col h-screen shrink-0"
      style={{
        background: 'linear-gradient(180deg, #080a16 0%, #0a0c18 100%)',
        borderRight: '1px solid var(--border-primary)',
      }}
    >
      {/* Logo */}
      <div
        className="h-16 flex items-center px-5 gap-3 shrink-0"
        style={{ borderBottom: '1px solid var(--border-primary)' }}
      >
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center"
          style={{
            background: 'linear-gradient(135deg, var(--accent-primary), #4f46e5)',
            boxShadow: '0 2px 10px rgba(99, 102, 241, 0.35)',
          }}
        >
          <Zap size={16} className="text-white" />
        </div>
        <div>
          <div className="text-sm font-bold tracking-wide" style={{ color: 'var(--text-primary)' }}>Aegis</div>
          <div className="text-[10px] font-medium tracking-widest uppercase" style={{ color: 'var(--text-tertiary)' }}>Trading System</div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto py-4 px-3">
        {navGroups.map((group) => (
          <div key={group.label} className="mb-5">
            <div
              className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-[0.12em]"
              style={{ color: 'var(--text-muted)' }}
            >
              {group.label}
            </div>
            <nav className="space-y-1">
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive = currentView === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setCurrentView(item.id)}
                    className={`sidebar-nav-item ${isActive ? 'active' : ''}`}
                  >
                    <Icon size={17} className="nav-icon" style={{ color: isActive ? 'var(--accent-primary)' : 'var(--text-tertiary)' }} />
                    {item.name}
                  </button>
                );
              })}
            </nav>
          </div>
        ))}
      </div>

      {/* Footer Status */}
      <div className="p-3 shrink-0" style={{ borderTop: '1px solid var(--border-primary)' }}>
        <div
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg"
          style={{ background: 'var(--bg-secondary)' }}
        >
          <div className="pulse-dot" style={{ background: 'var(--success)' }} />
          <div>
            <div className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>System Online</div>
            <div className="text-[10px]" style={{ color: 'var(--text-muted)' }}>All engines operational</div>
          </div>
        </div>
      </div>
    </div>
  );
}