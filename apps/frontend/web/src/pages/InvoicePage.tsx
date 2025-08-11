import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useMyInvoices, usePayInvoice } from '@/hooks/usePayments';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

function InvoicePage() {
  const { invoiceId } = useParams<{ invoiceId: string }>();
  const { data: invoices, isLoading } = useMyInvoices();
  const payInvoice = usePayInvoice();

  // Find the specific invoice from the list
  const invoice = invoices?.find((inv) => inv.id === invoiceId);

  if (isLoading) {
    return <div>Loading invoice...</div>;
  }

  if (!invoice) {
    return <div>Invoice not found.</div>;
  }

  const handlePayment = () => {
    payInvoice.mutate(invoice.id);
  };

  return (
    <div className="space-y-6 p-4 md:p-6 max-w-2xl mx-auto">
      <Link to="/invoices">
        <Button variant="outline">&larr; Back to Invoices</Button>
      </Link>
      <Card>
        <CardHeader>
          <CardTitle>Invoice #{invoice.id.substring(0, 8)}</CardTitle>
          <CardDescription>
            For Order #{invoice.order_id.substring(0, 8)}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Status</span>
            <span className="font-semibold">{invoice.status.toUpperCase()}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Date Issued</span>
            <span>{new Date(invoice.created_at).toLocaleDateString()}</span>
          </div>
          <hr />
          <div className="flex justify-between text-xl font-bold">
            <span>Total Amount</span>
            <span>${invoice.amount.toFixed(2)} {invoice.currency}</span>
          </div>
          <hr />
          {invoice.status === 'issued' && (
            <Button onClick={handlePayment} disabled={payInvoice.isPending} className="w-full">
              {payInvoice.isPending ? 'Processing Payment...' : 'Pay Now'}
            </Button>
          )}
           {payInvoice.isSuccess && (
                <p className="text-sm text-green-600 text-center">Payment successful!</p>
            )}
        </CardContent>
      </Card>
    </div>
  );
}

export default InvoicePage;
