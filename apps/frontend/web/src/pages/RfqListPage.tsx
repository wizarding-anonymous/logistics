import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { useRfqs } from '@/hooks/useRfq';

// TODO: Replace with the actual organization ID from user's context/state
const MOCK_ORG_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6";

function RfqListPage() {
  const { data: rfqs, isLoading, isError, error } = useRfqs(MOCK_ORG_ID);

  const getStatusClass = (status: string) => {
    switch (status) {
        case 'open': return 'bg-green-100 text-green-800';
        case 'closed': return 'bg-gray-100 text-gray-800';
        case 'cancelled': return 'bg-red-100 text-red-800';
        default: return 'bg-yellow-100 text-yellow-800';
    }
  }

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">My Requests for Quotation</h2>
          <p className="text-muted-foreground">View and manage all your RFQs.</p>
        </div>
        <Link to="/rfqs/new">
          <Button>Create New RFQ</Button>
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>RFQ History</CardTitle>
          <CardDescription>A list of your past and current RFQs.</CardDescription>
        </CardHeader>
        <CardContent>
            {isLoading && <p>Loading RFQs...</p>}
            {isError && <p className="text-red-500">Error loading RFQs: {error.message}</p>}
            {!isLoading && !isError && (
                <Table>
                    <TableHeader>
                    <TableRow>
                        <TableHead>RFQ ID</TableHead>
                        <TableHead>Origin</TableHead>
                        <TableHead>Destination</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                    </TableHeader>
                    <TableBody>
                    {rfqs?.map((rfq) => (
                        <TableRow key={rfq.id}>
                        <TableCell className="font-medium">{rfq.id.substring(0, 8)}...</TableCell>
                        <TableCell>{rfq.segments[0]?.origin_address || 'N/A'}</TableCell>
                        <TableCell>{rfq.segments[0]?.destination_address || 'N/A'}</TableCell>
                        <TableCell>
                            <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusClass(rfq.status)}`}>
                            {rfq.status}
                            </span>
                        </TableCell>
                        <TableCell className="text-right">
                            <Link to={`/rfqs/${rfq.id}`}>
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

export default RfqListPage;
