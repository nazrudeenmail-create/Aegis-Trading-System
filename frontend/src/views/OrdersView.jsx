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
    <div className="space-y-6 animate-fade-in">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>Orders</h1>
        <span className="text-sm font-medium px-3 py-1 rounded" style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-primary)', color: 'var(--text-secondary)' }}>
          Broker: <span style={{ color: 'var(--accent-primary)' }}>{brokerName}</span>
        </span>
      </div>

      <div className="glass-card-static overflow-hidden animate-fade-in-delay-1">
        <div className="section-header">
          <h2 className="section-title">
            <ShoppingCart size={18} style={{ color: 'var(--accent-primary)' }}/> Recent Orders
          </h2>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Symbol</th>
              <th>Direction</th>
              <th>Type</th>
              <th>Status</th>
              <th>Fill Price</th>
              <th>Quantity</th>
            </tr>
          </thead>
          <tbody>
            {isOrdersLoading ? (
              <tr>
                <td colSpan="7" className="text-center p-8"><div className="skeleton h-4 w-1/2 mx-auto" /></td>
              </tr>
            ) : (!ordersData || ordersData.length === 0) ? (
              <tr>
                <td colSpan="7" className="text-center p-8" style={{ color: 'var(--text-tertiary)' }}>
                  <Clock size={24} className="mx-auto mb-2" style={{ color: 'var(--text-muted)' }} />
                  No orders found for this session.
                </td>
              </tr>
            ) : (
              ordersData.map((order, idx) => (
                <tr key={idx}>
                  <td className="font-mono text-xs" style={{ color: 'var(--text-secondary)' }}>{order.id}</td>
                  <td style={{ color: 'var(--text-primary)', fontWeight: 'bold' }}>{order.symbol}</td>
                  <td>
                    <span className={order.direction === 'BUY' ? 'badge-success' : 'badge-danger'}>
                      {order.direction}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-secondary)' }}>{order.type}</td>
                  <td>
                    <span className="badge-info">
                      {order.status}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-secondary)' }}>{order.fill_price ? `$${order.fill_price.toFixed(2)}` : '--'}</td>
                  <td style={{ color: 'var(--text-secondary)' }}>{order.quantity}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}