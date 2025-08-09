import React from 'react';
import { useAuthStore } from '@/state/authStore';
import { useNavigate } from 'react-router-dom';

function DashboardPage() {
  const { clearTokens } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    clearTokens();
    navigate('/login');
  };

  return (
    <div>
      <h2>Dashboard</h2>
      <p>Welcome! You are logged in.</p>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}

export default DashboardPage;
