import React from 'react';
import useSWR from 'swr';
import { fetcher } from '../api';
import { ShoppingCart, Clock, CheckCircle2, XCircle } from 'lucide-react';

export function OrdersView() {
  const { data: brokerStatus } = useSWR('/system/status', fetcher);
  const { data: ordersData, error: ordersError } = useSWR('/broker/orders/recent', fetcher);
  const isOrdersLoading = !ordersData && !ordersError;

  const brokerName = brokerStatus?.broker || 'Unknown';

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white tracking-tight">Orders</h1>
        <span className="text-sm text-slate-400 bg-slate-900 px-3 py-1 rounded border border-slate-700">
          Broker: <span className="text-indigo-400">{brokerName}</span>
        </span>
      </div>

      <div className="bg-slate-950 rounded-xl border border-slate-800 overflow-hidden">
        <div className="p-4 border-b border-slate-800">
          <h2 className="font-semibold text-white flex items-center gap-2">
            <ShoppingCart size={18} className="text-indigo-400"/> Recent Orders
          </h2>
        </div>
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-900/50 text-slate-400 border-b border-slate-800">
            <tr>
              <th className="p-4 font-medium">Order ID</th>
              <th className="p-4 font-medium">Symbol</th>
              <th className="p-4 font-medium">Direction</th>
              <th className="p-4 font-medium">Type</th>
              <th className="p-4 font-medium">Status</th>
              <th className="p-4 font-medium">Fill Price</th>
              <th className="p-4 font-medium">Quantity</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {isOrdersLoading ? (
              <tr>
                <td colSpan="7" className="p-8 text-center text-slate-500">Loading orders...</td>
              </tr>
            ) : (!ordersData || ordersData.length === 0) ? (
              <tr>
                <td colSpan="7" className="p-8 text-center text-slate-500">
                  <Clock size={24} className="mx-auto mb-2 text-slate-600" />
                  No orders found for this session.
                </td>
              </tr>
            ) : (
              ordersData.map((order, idx) => (
                <tr key={idx} className="hover:bg-slate-900/50 transition">
                  <td className="p-4 text-slate-300 font-mono text-xs">{order.id}</td>
                  <td className="p-4 font-bold text-white">{order.symbol}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${order.direction === 'BUY' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                      {order.direction}
                    </span>
                  </td>
                  <td className="p-4 text-slate-300">{order.type}</td>
                  <td className="p-4">
                    <span className="text-indigo-400 font-medium text-xs px-2 py-1 rounded border border-indigo-500/20 bg-indigo-500/10">
                      {order.status}
                    </span>
                  </td>
                  <td className="p-4 text-slate-300">{order.fill_price ? `$${order.fill_price.toFixed(2)}` : '--'}</td>
                  <td className="p-4 text-slate-300">{order.quantity}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}