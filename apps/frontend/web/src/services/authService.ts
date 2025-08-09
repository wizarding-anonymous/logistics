import axios from 'axios';
import { z } from 'zod';

// =================================
// Schemas for validation
// =================================

// Schema for user registration payload
export const RegisterSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  recaptcha_token: z.string(), // Added reCAPTCHA token
  roles: z.array(z.string()).optional().default(['client']),
});
export type RegisterPayload = z.infer<typeof RegisterSchema>;

// Schema for the token response from the backend
const TokenSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
  token_type: z.literal('bearer'),
});
export type TokenResponse = z.infer<typeof TokenSchema>;

// =================================
// API Client
// =================================

import { useAuthStore } from '@/state/authStore';

const authApiClient = axios.create({
  // The proxy in vite.config.ts will handle this
  baseURL: '/api/v1/auth',
});

// Add a request interceptor to include the token in headers
authApiClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const TfaSetupSchema = z.object({
  secret: z.string(),
  provisioning_uri: z.string().url(),
});
export type TfaSetupResponse = z.infer<typeof TfaSetupSchema>;

// =================================
// API Functions
// =================================

export const registerUser = async (payload: RegisterPayload) => {
  const response = await authApiClient.post('/register', payload);
  return response.data;
};

export const loginUser = async (email: string, password: string): Promise<TokenResponse> => {
  // The OAuth2PasswordRequestForm expects data in a URL-encoded form format
  const params = new URLSearchParams();
  params.append('username', email);
  params.append('password', password);

  try {
    const response = await authApiClient.post('/token', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    // Validate the response data at runtime
    return TokenSchema.parse(response.data);
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 403) {
      // This is a special case where the backend is telling us TFA is required.
      // We can re-throw a custom error or return a specific object.
      throw new Error('TFA_REQUIRED');
    }
    // For all other errors, re-throw them as is.
    throw error;
  }
};

export const loginUserWithTFA = async (email: string, password: string, tfa_code: string): Promise<TokenResponse> => {
  const payload = {
    username: email,
    password,
    tfa_code,
  };

  const response = await authApiClient.post('/token/2fa', payload);
  return TokenSchema.parse(response.data);
};

// =================================
// 2FA Management Functions
// =================================

export const setupTFA = async (): Promise<TfaSetupResponse> => {
  const response = await authApiClient.post('/2fa/setup');
  return TfaSetupSchema.parse(response.data);
};

export const enableTFA = async (code: string): Promise<{ message: string }> => {
  const response = await authApiClient.post('/2fa/enable', { code });
  return response.data;
};

export const disableTFA = async (): Promise<{ message: string }> => {
  const response = await authApiClient.post('/2fa/disable');
  return response.data;
};
