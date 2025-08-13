import React from 'react';
// Assume hooks exist to fetch this data
// import { useAdminUsers, useAdminOrganizations, useDeactivateUser, useUpdateUserRoles } from '@/hooks/useAdmin';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';

// Mock data for UI development
const mockUsers = [
  { id: 'user-1', email: 'client@example.com', roles: ['client'], is_active: true },
  { id: 'user-2', email: 'supplier@example.com', roles: ['supplier'], is_active: true },
  { id: 'user-3', email: 'manager@example.com', roles: ['manager'], is_active: false },
];

const mockOrgs = [
    { id: 'org-1', name: 'Client Corp' },
    { id: 'org-2', name: 'Supplier Inc' },
];

function AdminUsersPage() {
  // const { data: users, isLoading: usersLoading } = useAdminUsers();
  // const { data: organizations, isLoading: orgsLoading } = useAdminOrganizations();
  const users = mockUsers;
  const organizations = mockOrgs;
  const usersLoading = false;
  const orgsLoading = false;

  // TODO: Implement these mutations
  const handleDeactivate = (userId: string) => {
    console.log(`TODO: Deactivate user ${userId}`);
  };

  const handleEditRoles = (userId: string) => {
    console.log(`TODO: Open role edit modal for user ${userId}`);
  };

  return (
    <div className="space-y-6 p-4 md:p-6">
      <h2 className="text-3xl font-bold tracking-tight">User & Organization Management</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Users</CardTitle>
            <CardDescription>List of all users on the platform.</CardDescription>
          </CardHeader>
          <CardContent>
            {usersLoading ? <p>Loading users...</p> : (
              <Table>
                <TableHeader><TableRow><TableHead>User</TableHead><TableHead>Status</TableHead><TableHead>Roles</TableHead><TableHead className="text-right">Actions</TableHead></TableRow></TableHeader>
                <TableBody>
                  {users?.map((user) => (
                    <TableRow key={user.id}>
                      <TableCell>{user.email}</TableCell>
                      <TableCell>
                        <Badge variant={user.is_active ? 'default' : 'destructive'}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </TableCell>
                      <TableCell>{user.roles.join(', ')}</TableCell>
                      <TableCell className="text-right space-x-2">
                        <Button variant="outline" size="sm" onClick={() => handleEditRoles(user.id)}>Edit Roles</Button>
                        {user.is_active && <Button variant="destructive" size="sm" onClick={() => handleDeactivate(user.id)}>Deactivate</Button>}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Organizations</CardTitle>
            <CardDescription>List of all organizations on the platform.</CardDescription>
          </CardHeader>
          <CardContent>
            {orgsLoading ? <p>Loading organizations...</p> : (
              <Table>
                <TableHeader><TableRow><TableHead>Name</TableHead><TableHead>ID</TableHead></TableRow></TableHeader>
                <TableBody>
                  {organizations?.map((org) => (
                    <TableRow key={org.id}>
                      <TableCell>{org.name}</TableCell>
                      <TableCell>{org.id}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default AdminUsersPage;
