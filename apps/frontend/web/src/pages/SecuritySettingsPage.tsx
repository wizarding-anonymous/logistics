import React, { useState } from 'react';
import { QRCodeCanvas } from 'qrcode.react';
import { setupTFA, enableTFA, disableTFA } from '@/services/authService';
import { useAuthStore } from '@/state/authStore';

// A mock to get the user's current 2FA status. In a real app,
// this would come from the user's profile/session data.
const useUser2FAStatus = () => {
    // This would be replaced by a real check, e.g., from a user profile query
    const [isTfaEnabled, setIsTfaEnabled] = useState(false);
    return { isTfaEnabled, setIsTfaEnabled };
};

function SecuritySettingsPage() {
  const { isTfaEnabled, setIsTfaEnabled } = useUser2FAStatus();
  const [setupData, setSetupData] = useState<{ secret: string; uri: string } | null>(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSetupClick = async () => {
    setError(null);
    setSuccess(null);
    try {
      const response = await setupTFA();
      setSetupData({ secret: response.secret, uri: response.provisioning_uri });
    } catch (err) {
      setError("Failed to start 2FA setup.");
    }
  };

  const handleEnableClick = async () => {
    setError(null);
    setSuccess(null);
    if (!verificationCode) {
      setError("Please enter the verification code.");
      return;
    }
    try {
      await enableTFA(verificationCode);
      setSuccess("2FA has been successfully enabled!");
      setIsTfaEnabled(true);
      setSetupData(null);
      setVerificationCode('');
    } catch (err) {
      setError("Failed to enable 2FA. The code may be incorrect.");
    }
  };

  const handleDisableClick = async () => {
    setError(null);
    setSuccess(null);
    try {
      await disableTFA();
      setSuccess("2FA has been successfully disabled.");
      setIsTfaEnabled(false);
    } catch (err) {
      setError("Failed to disable 2FA.");
    }
  };

  return (
    <div>
      <h2>Security Settings</h2>
      <h3>Two-Factor Authentication (2FA)</h3>

      {error && <p style={{ color: 'red' }}>{error}</p>}
      {success && <p style={{ color: 'green' }}>{success}</p>}

      {!isTfaEnabled && !setupData && (
        <div>
          <p>Protect your account with an extra layer of security.</p>
          <button onClick={handleSetupClick}>Enable 2FA</button>
        </div>
      )}

      {setupData && (
        <div>
          <h4>Step 1: Scan this QR code with your authenticator app</h4>
          <QRCodeCanvas value={setupData.uri} size={256} />
          <p>Or manually enter this secret key: <code>{setupData.secret}</code></p>

          <h4>Step 2: Enter the 6-digit code from your app</h4>
          <input
            type="text"
            value={verificationCode}
            onChange={(e) => setVerificationCode(e.target.value)}
            maxLength={6}
          />
          <button onClick={handleEnableClick}>Verify & Enable</button>
        </div>
      )}

      {isTfaEnabled && (
        <div>
          <p style={{ color: 'green' }}>2FA is currently enabled on your account.</p>
          <button onClick={handleDisableClick}>Disable 2FA</button>
        </div>
      )}
    </div>
  );
}

export default SecuritySettingsPage;
