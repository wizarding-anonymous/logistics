import React from 'react';
import { usePendingPayouts, useApprovePayout } from '@/hooks/useAdmin';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

function PayoutApprovalsPage() {
  const { data: payouts, isLoading, isError, error } = usePendingPayouts();
  const approveMutation = useApprovePayout();

  return (
    <div className="space-y-6 p-4 md:p-6">
      <h2 className="text-3xl font-bold tracking-tight">Payout Approvals</h2>

      <Card>
        <CardHeader>
          <CardTitle>Pending Payouts</CardTitle>
          <CardDescription>Review and approve pending payouts to suppliers.</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading && <p>Loading pending payouts...</p>}
          {isError && <p className="text-red-500">Error: {error.message}</p>}
          {!isLoading && !isError && (
            <Table>
                <TableHeader>
                <TableRow>
                    <TableHead>Payout ID</TableHead>
                    <TableHead>Supplier Org ID</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                </TableRow>
                </TableHeader>
                <TableBody>
                {payouts?.map((payout) => (
                    <TableRow key={payout.id}>
                        <TableCell className="font-medium">{payout.id.substring(0,8)}...</TableCell>
                        <TableCell>{payout.supplier_organization_id.substring(0,8)}...</TableCell>
                        <TableCell>${payout.amount.toFixed(2)} {payout.currency}</TableCell>
                        <TableCell className="text-right">
                            <Button
                                size="sm"
                                onClick={() => approveMutation.mutate(payout.id)}
                                disabled={approveMutation.isPending}
                            >
                                {approveMutation.isPending ? 'Approving...' : 'Approve'}
                            </Button>
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

export default PayoutApprovalsPage;
