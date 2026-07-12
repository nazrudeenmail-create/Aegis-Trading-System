import React, { useEffect, useState, useRef } from 'react';
import { Terminal, X, Minimize2, Maximize2 } from 'lucide-react';
import { wsClient } from '../api';

export function SystemConsole() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [logs, setLogs] = useState([]);
  const logsEndRef = useRef(null);

  useEffect(() => {
    // Only connect if not already connected (managed globally typically, but we ensure it here)
    if (!wsClient.ws || wsClient.ws.readyState !== WebSocket.OPEN) {
      wsClient.connect();
    }

    const unsubscribe = wsClient.subscribe((msg) => {
      if (msg.event === 'system.log') {
        setLogs((prev) => [...prev, msg.data].slice(-100)); // Keep last 100 logs
      } else if (msg.event === 'trade.opened' || msg.event === 'trade.closed' || msg.event === 'strategy.ranking.changed') {
        // Also log these important events
        setLogs((prev) => [...prev, {
          level: 'INFO',
          source: 'EventBus',
          message: `${msg.event}: ${JSON.stringify(msg.data)}`,
          timestamp: Date.now()
        }].slice(-100));
      }
    });

    return () => unsubscribe();
  }, []);

  useEffect(() => {
    if (!isMinimized && isOpen) {
      logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, isMinimized, isOpen]);

  if (!isOpen) {
    return (
      <button 
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 bg-slate-900 border border-slate-700 text-slate-300 p-3 rounded-full shadow-lg hover:bg-slate-800 transition z-50 flex items-center gap-2"
        title="Open System Console"
      >
        <Terminal size={20} />
        <span className="text-sm font-medium pr-2 hidden md:block">System Console</span>
      </button>
    );
  }

  return (
    <div className={`fixed right-4 bottom-4 bg-slate-950 border border-slate-800 shadow-2xl rounded-xl z-50 flex flex-col transition-all duration-300 ${isMinimized ? 'w-72 h-14' : 'w-[32rem] h-96'}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-slate-800 bg-slate-900 rounded-t-xl cursor-pointer" onClick={() => setIsMinimized(!isMinimized)}>
        <div className="flex items-center gap-2 text-slate-300">
          <Terminal size={16} />
          <span className="text-sm font-semibold">Glass Box Console</span>
          {!isMinimized && <span className="text-xs px-2 py-0.5 bg-emerald-500/10 text-emerald-400 rounded">Live</span>}
        </div>
        <div className="flex items-center gap-2">
          <button 
            onClick={(e) => { e.stopPropagation(); setIsMinimized(!isMinimized); }}
            className="text-slate-500 hover:text-slate-300"
          >
            {isMinimized ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
          </button>
          <button 
            onClick={(e) => { e.stopPropagation(); setIsOpen(false); }}
            className="text-slate-500 hover:text-rose-400"
          >
            <X size={16} />
          </button>
        </div>
      </div>

      {/* Body */}
      {!isMinimized && (
        <div className="flex-1 overflow-y-auto p-4 font-mono text-xs space-y-2 bg-[#0a0a0a] rounded-b-xl">
          {logs.length === 0 ? (
            <div className="text-slate-600 text-center mt-10">Awaiting system events...</div>
          ) : (
            logs.map((log, i) => (
              <div key={i} className="flex gap-3">
                <span className="text-slate-500 shrink-0">
                  {new Date(log.timestamp).toISOString().split('T')[1].slice(0, -1)}
                </span>
                <span className={`shrink-0 font-bold ${
                  log.level === 'INFO' ? 'text-blue-400' :
                  log.level === 'WARN' ? 'text-yellow-400' :
                  log.level === 'ERROR' ? 'text-red-400' : 'text-slate-400'
                }`}>
                  [{log.source}]
                </span>
                <span className="text-slate-300 break-all">{log.message}</span>
              </div>
            ))
          )}
          <div ref={logsEndRef} />
        </div>
      )}
    </div>
  );
}
