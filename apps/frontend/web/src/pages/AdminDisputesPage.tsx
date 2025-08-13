import React from 'react';
import { Link } from 'react-router-dom';
// Assume a hook exists to fetch open disputes, we'll need to create it.
// import { useOpenDisputes } from '@/hooks/useAdmin';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

// Mock data for now, as the hook doesn't exist yet.
const mockDisputes = [
  { id: '123e4567-e89b-12d3-a456-426614174000', order_id: 'a1b2c3d4', status: 'open', created_at: new Date().toISOString() },
  { id: '123e4567-e89b-12d3-a456-426614174001', order_id: 'e5f6g7h8', status: 'open', created_at: new Date().toISOString() },
];

function AdminDisputesPage() {
  // const { data: disputes, isLoading, isError, error } = useOpenDisputes();

  // Using mock data for UI development
  const disputes = mockDisputes;
  const isLoading = false;
  const isError = false;

  return (
    <div className="space-y-6 p-4 md:p-6">
      <h2 className="text-3xl font-bold tracking-tight">Dispute Moderation</h2>

      <Card>
        <CardHeader>
          <CardTitle>Open Disputes</CardTitle>
          <CardDescription>Review and resolve open disputes between users.</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading && <p>Loading open disputes...</p>}
          {isError && <p className="text-red-500">Error fetching disputes</p>}
          {!isLoading && !isError && (
            <Table>
                <TableHeader>
                <TableRow>
                    <TableHead>Dispute ID</TableHead>
                    <TableHead>Order ID</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Created At</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                </TableRow>
                </TableHeader>
                <TableBody>
                {disputes?.map((dispute) => (
                    <TableRow key={dispute.id}>
                        <TableCell className="font-medium">{dispute.id.substring(0,8)}...</TableCell>
                        <TableCell>{dispute.order_id.substring(0,8)}...</TableCell>
                        <TableCell>{dispute.status}</TableCell>
                        <TableCell>{new Date(dispute.created_at).toLocaleDateString()}</TableCell>
                        <TableCell className="text-right">
                            <Link to={`/disputes/${dispute.id}`}>
                                <Button size="sm" variant="outline">
                                    View Details
                                </Button>
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

export default AdminDisputesPage;
