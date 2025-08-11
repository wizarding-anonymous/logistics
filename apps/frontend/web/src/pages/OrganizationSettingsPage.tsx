import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useOrganization, useInviteMember, useRemoveMember } from '@/hooks/useOrganization';

// Import shadcn/ui components
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useAuthStore } from '@/state/authStore';

function OrganizationSettingsPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const { id: currentUserId } = useAuthStore(); // Get current user's ID
  const [inviteEmail, setInviteEmail] = useState('');

  // React Query hooks
  const { data: org, isLoading, isError, error } = useOrganization(orgId!);
  const inviteMember = useInviteMember(orgId!);
  const removeMember = useRemoveMember(orgId!);

  const handleInviteSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteEmail) return;
    inviteMember.mutate({ email: inviteEmail, role: 'member' });
    setInviteEmail('');
  };

  if (isLoading) {
    return <div className="p-6">Loading organization details...</div>;
  }

  if (isError) {
    return <div className="p-6 text-red-500">Error loading organization: {error?.message}</div>;
  }

  // The backend now returns a list of members with user_id and role.
  // We'll create placeholder data for name and email for the UI.
  const membersForDisplay = org?.members.map(member => ({
      ...member,
      name: `User ${member.user_id.substring(0, 6)}...`,
      email: `user-${member.user_id.substring(0, 6)}@example.com` // This is a placeholder
  })) || [];

  return (
    <div className="space-y-6 p-4 md:p-6">
      <h2 className="text-3xl font-bold tracking-tight">Settings for {org?.name}</h2>

      <Tabs defaultValue="team" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="team">Team</TabsTrigger>
        </TabsList>

        <TabsContent value="general">
          <Card>
            <CardHeader>
              <CardTitle>Organization Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="orgName">Organization Name</Label>
                <Input id="orgName" defaultValue={org?.name} disabled />
              </div>
              <div className="space-y-2">
                <Label htmlFor="orgDesc">Description</Label>
                <Input id="orgDesc" defaultValue={org?.description || ''} disabled />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="team">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>Team Members</CardTitle>
                  <CardDescription>View and manage who has access to this organization.</CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Role</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {membersForDisplay.map((member) => (
                        <TableRow key={member.user_id}>
                          <TableCell className="font-medium">{member.name}</TableCell>
                          <TableCell className="capitalize">{member.role}</TableCell>
                          <TableCell className="text-right">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeMember.mutate(member.user_id)}
                              disabled={removeMember.isPending || member.user_id === currentUserId}
                            >
                              {removeMember.isPending ? 'Removing...' : 'Remove'}
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </div>
            <div>
              <Card>
                <CardHeader>
                  <CardTitle>Invite New Member</CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleInviteSubmit} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="email">Email Address</Label>
                      <Input
                        id="email"
                        type="email"
                        placeholder="user@example.com"
                        value={inviteEmail}
                        onChange={(e) => setInviteEmail(e.target.value)}
                        required
                      />
                    </div>
                    <Button type="submit" className="w-full" disabled={inviteMember.isPending}>
                      {inviteMember.isPending ? 'Sending Invitation...' : 'Send Invitation'}
                    </Button>
                    {inviteMember.isSuccess && <p className="text-sm text-green-600">Invitation sent successfully!</p>}
                    {inviteMember.isError && <p className="text-sm text-red-600">Failed to send invitation.</p>}
                  </form>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default OrganizationSettingsPage;
