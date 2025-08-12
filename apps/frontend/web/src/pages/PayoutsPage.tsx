import React from 'react';
import { useMyPayouts } from '@/hooks/usePayments';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

function PayoutsPage() {
  const { data: payouts, isLoading, isError, error } = useMyPayouts();

  const getStatusClass = (status: string) => {
    switch (status) {
        case 'completed': return 'bg-green-100 text-green-800';
        case 'pending': return 'bg-yellow-100 text-yellow-800';
        case 'failed': return 'bg-red-100 text-red-800';
        default: return 'bg-gray-100 text-gray-800';
    }
  }

  return (
    <div className="space-y-6 p-4 md:p-6">
      <h2 className="text-3xl font-bold tracking-tight">My Payouts</h2>

      <Card>
        <CardHeader>
          <CardTitle>Payout History</CardTitle>
          <CardDescription>A list of all your payouts from completed orders.</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading && <p>Loading payouts...</p>}
          {isError && <p className="text-red-500">Error: {error.message}</p>}
          {!isLoading && !isError && (
            <Table>
                <TableHeader>
                <TableRow>
                    <TableHead>Payout ID</TableHead>
                    <TableHead>Order ID</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Date Created</TableHead>
                </TableRow>
                </TableHeader>
                <TableBody>
                {payouts?.map((payout) => (
                    <TableRow key={payout.id}>
                        <TableCell className="font-medium">{payout.id.substring(0,8)}...</TableCell>
                        <TableCell>{payout.order_id.substring(0,8)}...</TableCell>
                        <TableCell>${payout.amount.toFixed(2)} {payout.currency}</TableCell>
                        <TableCell>
                            <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusClass(payout.status)}`}>
                                {payout.status}
                            </span>
                        </TableCell>
                        <TableCell>{new Date(payout.created_at).toLocaleDateString()}</TableCell>
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

export default PayoutsPage;
