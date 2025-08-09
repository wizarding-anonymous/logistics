import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { acceptInvitation } from '@/services/orgService';

function AcceptInvitationPage() {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleAccept = async () => {
    if (!token) {
      setError('No invitation token provided.');
      return;
    }
    setError(null);

    try {
      await acceptInvitation(token);
      setSuccess('Invitation accepted successfully! Redirecting...');
      // In a real app, you might refetch user data to update their org list
      setTimeout(() => navigate('/dashboard'), 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to accept invitation.');
    }
  };

  return (
    <div>
      <h2>Accept Invitation</h2>
      <p>You have been invited to join an organization.</p>
      <p>Token: <code>{token}</code></p>

      <button onClick={handleAccept} disabled={!!success}>
        Accept Invitation
      </button>

      {error && <p style={{ color: 'red', marginTop: '1rem' }}>{error}</p>}
      {success && <p style={{ color: 'green', marginTop: '1rem' }}>{success}</p>}
    </div>
  );
}

export default AcceptInvitationPage;
