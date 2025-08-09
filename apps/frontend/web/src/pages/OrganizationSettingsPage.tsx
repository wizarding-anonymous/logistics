import React from 'react';
import { useParams } from 'react-router-dom';
import { useOrganization } from '@/hooks/useOrganization';

function OrganizationSettingsPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const { data: org, isLoading, isError, error } = useOrganization(orgId || '');

  if (isLoading) {
    return <div>Loading organization details...</div>;
  }

  if (isError) {
    return <div>Error loading organization: {error?.message}</div>;
  }

  if (!org) {
    return <div>Organization not found.</div>;
  }

  return (
    <div>
      <h2>{org.name} - Settings</h2>
      <p>{org.description}</p>
      <hr />
      <h3>Members</h3>
      {org.members.length > 0 ? (
        <ul>
          {org.members.map((member) => (
            <li key={member.user_id}>
              User ID: {member.user_id} - Role: {member.role}
            </li>
          ))}
        </ul>
      ) : (
        <p>No members found.</p>
      )}

      <hr style={{ margin: '1rem 0' }} />

      <h3>Invite New Member</h3>
      {/* A real implementation of this form would be a separate component */}
      <form>
        <input type="email" placeholder="user@example.com" />
        <select>
          <option value="member">Member</option>
          <option value="admin">Admin</option>
        </select>
        <button type="submit">Send Invitation</button>
      </form>
      <p><small>Note: This form is a placeholder and not yet functional.</small></p>
    </div>
  );
}

export default OrganizationSettingsPage;
