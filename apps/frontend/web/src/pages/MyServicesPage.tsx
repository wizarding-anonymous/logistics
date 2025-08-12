import React from 'react';
import { Link } from 'react-router-dom';
import { useMyServices } from '@/hooks/useCatalog';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

function MyServicesPage() {
  const { data: services, isLoading, isError, error } = useMyServices();

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">My Service Offerings</h2>
          <p className="text-muted-foreground">Manage the services your organization provides.</p>
        </div>
        <Link to="/my-services/new">
          <Button>Create New Service</Button>
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Your Services</CardTitle>
        </CardHeader>
        <CardContent>
            {isLoading && <p>Loading services...</p>}
            {isError && <p className="text-red-500">Error: {error.message}</p>}
            {!isLoading && !isError && (
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Service Name</TableHead>
                            <TableHead>Type</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {services?.map((service) => (
                            <TableRow key={service.id}>
                                <TableCell className="font-medium">{service.name}</TableCell>
                                <TableCell>{service.service_type}</TableCell>
                                <TableCell>{service.is_active ? 'Active' : 'Inactive'}</TableCell>
                                <TableCell className="text-right">
                                    <Button variant="outline" size="sm">Edit</Button>
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

export default MyServicesPage;
