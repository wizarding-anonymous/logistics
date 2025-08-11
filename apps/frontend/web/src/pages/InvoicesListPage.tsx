import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { useMyInvoices } from '@/hooks/usePayments';

function InvoicesListPage() {
  const { data: invoices, isLoading, isError, error } = useMyInvoices();

  const getStatusClass = (status: string) => {
    switch (status) {
        case 'paid': return 'bg-green-100 text-green-800';
        case 'issued': return 'bg-yellow-100 text-yellow-800';
        case 'overdue': return 'bg-red-100 text-red-800';
        default: return 'bg-gray-100 text-gray-800';
    }
  }

  return (
    <div className="space-y-6 p-4 md:p-6">
      <h2 className="text-3xl font-bold tracking-tight">Invoices</h2>

      <Card>
        <CardHeader>
          <CardTitle>Invoice History</CardTitle>
          <CardDescription>A list of all your past and current invoices.</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading && <p>Loading invoices...</p>}
          {isError && <p className="text-red-500">Error: {error.message}</p>}
          {!isLoading && !isError && (
            <Table>
                <TableHeader>
                <TableRow>
                    <TableHead>Invoice ID</TableHead>
                    <TableHead>Order ID</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Date Issued</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                </TableRow>
                </TableHeader>
                <TableBody>
                {invoices?.map((invoice) => (
                    <TableRow key={invoice.id}>
                    <TableCell className="font-medium">{invoice.id.substring(0,8)}...</TableCell>
                    <TableCell>{invoice.order_id.substring(0,8)}...</TableCell>
                    <TableCell>${invoice.amount.toFixed(2)} {invoice.currency}</TableCell>
                    <TableCell>{new Date(invoice.created_at).toLocaleDateString()}</TableCell>
                    <TableCell>
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusClass(invoice.status)}`}>
                        {invoice.status}
                        </span>
                    </TableCell>
                    <TableCell className="text-right">
                        <Link to={`/invoices/${invoice.id}`}>
                            <Button variant="outline" size="sm">View Details</Button>
                        </Link>
                    </TableCell>
                    </TableRow>
                ))}
                </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default InvoicesListPage;
