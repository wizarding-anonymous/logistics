import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { loginUser, loginUserWithTFA } from '@/services/authService';
import { useAuthStore } from '@/state/authStore';

function LoginPage() {
  const navigate = useNavigate();
  const setTokens = useAuthStore((state) => state.setTokens);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [tfaCode, setTfaCode] = useState('');
  const [isTfaRequired, setIsTfaRequired] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      const tokenResponse = await loginUser(email, password);
      setTokens({
        accessToken: tokenResponse.access_token,
        refreshToken: tokenResponse.refresh_token,
      });
      navigate('/dashboard');
    } catch (err: any) {
      if (err.message === 'TFA_REQUIRED') {
        setIsTfaRequired(true);
      } else {
        setError(err.response?.data?.detail || 'Failed to log in.');
      }
    }
  };

  const handleTfaSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      const tokenResponse = await loginUserWithTFA(email, password, tfaCode);
      setTokens({
        accessToken: tokenResponse.access_token,
        refreshToken: tokenResponse.refresh_token,
      });
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to verify TFA code.');
    }
  };

  if (isTfaRequired) {
    return (
      <div>
        <h2>Enter Verification Code</h2>
        <form onSubmit={handleTfaSubmit}>
          <div>
            <label htmlFor="tfaCode">6-Digit Code:</label>
            <input
              type="text"
              id="tfaCode"
              value={tfaCode}
              onChange={(e) => setTfaCode(e.target.value)}
              required
              maxLength={6}
            />
          </div>
          <button type="submit">Verify & Login</button>
        </form>
        {error && <p style={{ color: 'red' }}>{error}</p>}
      </div>
    );
  }

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={handleLoginSubmit}>
        <div>
          <label htmlFor="email">Email:</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Login</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <p>
        Don't have an account? <Link to="/register">Register here</Link>
      </p>
    </div>
  );
}

export default LoginPage;
