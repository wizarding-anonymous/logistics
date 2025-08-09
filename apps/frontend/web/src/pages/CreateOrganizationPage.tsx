import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createOrganization } from '@/services/orgService';

function CreateOrganizationPage() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      const newOrg = await createOrganization(name, description);
      // Redirect to the new organization's settings page
      navigate(`/organization/${newOrg.id}/settings`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create organization.');
    }
  };

  return (
    <div>
      <h2>Create a New Organization</h2>
      <p>This will be your company or team on the platform.</p>
      <form onSubmit={handleSubmit} style={{ marginTop: '1rem' }}>
        <div>
          <label htmlFor="name">Organization Name:</label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div style={{ marginTop: '0.5rem' }}>
          <label htmlFor="description">Description:</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
        <button type="submit" style={{ marginTop: '1rem' }}>Create Organization</button>
      </form>
      {error && <p style={{ color: 'red', marginTop: '1rem' }}>{error}</p>}
    </div>
  );
}

export default CreateOrganizationPage;
