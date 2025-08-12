import React from 'react';
import { Link } from 'react-router-dom';
import { useOpenRfqs } from '@/hooks/useRfq';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

function AvailableRfqsPage() {
  const { data: rfqs, isLoading, isError, error } = useOpenRfqs();

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Available RFQs</h2>
          <p className="text-muted-foreground">Browse and bid on open shipping requests.</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Open for Bidding</CardTitle>
        </CardHeader>
        <CardContent>
            {isLoading && <p>Loading available RFQs...</p>}
            {isError && <p className="text-red-500">Error: {error.message}</p>}
            {!isLoading && !isError && (
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Route</TableHead>
                            <TableHead>Cargo</TableHead>
                            <TableHead>Date Posted</TableHead>
                            <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {rfqs?.map((rfq) => (
                            <TableRow key={rfq.id}>
                                <TableCell className="font-medium">
                                    {rfq.segments[0]?.origin_address} to {rfq.segments[0]?.destination_address}
                                </TableCell>
                                <TableCell>{rfq.cargo.description}</TableCell>
                                <TableCell>{new Date(rfq.created_at).toLocaleDateString()}</TableCell>
                                <TableCell className="text-right">
                                    <Link to={`/rfqs/${rfq.id}`}>
                                        <Button variant="outline" size="sm">View & Bid</Button>
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

export default AvailableRfqsPage;
