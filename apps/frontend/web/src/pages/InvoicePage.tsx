import React from 'react';
import { useParams } from 'react-router-dom';
import { useInvoice } from '@/hooks/useInvoice';

function InvoicePage() {
  const { orderId } = useParams<{ orderId: string }>();
  const { data: invoice, isLoading, isError, error } = useInvoice(orderId || '');

  if (isLoading) {
    return <div>Loading invoice...</div>;
  }

  if (isError) {
    return <div>Error loading invoice: {error?.message}</div>;
  }

  if (!invoice) {
    return <div>No invoice found for this order.</div>;
  }

  return (
    <div>
      <h2>Invoice Details</h2>
      <p><strong>Invoice ID:</strong> {invoice.id}</p>
      <p><strong>Order ID:</strong> {invoice.order_id}</p>
      <p><strong>Status:</strong> {invoice.status}</p>
      <p><strong>Total Amount:</strong> {invoice.amount} {invoice.currency}</p>

      <hr style={{ margin: '1rem 0' }} />

      <h3>Transactions</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ border: '1px solid #ddd', padding: '8px' }}>Type</th>
            <th style={{ border: '1px solid #ddd', padding: '8px' }}>Amount</th>
            <th style={{ border: '1px solid #ddd', padding: '8px' }}>Notes</th>
            <th style={{ border: '1px solid #ddd', padding: '8px' }}>Date</th>
          </tr>
        </thead>
        <tbody>
          {invoice.transactions.map((tx) => (
            <tr key={tx.id}>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>{tx.transaction_type}</td>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>{tx.amount}</td>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>{tx.notes}</td>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>{new Date(tx.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default InvoicePage;
