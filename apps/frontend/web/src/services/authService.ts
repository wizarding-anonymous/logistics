import axios from 'axios';
import { z } from 'zod';

// =================================
// Schemas for validation
// =================================

// Schema for user registration payload
export const RegisterSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
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

const authApiClient = axios.create({
  // The proxy in vite.config.ts will handle this
  baseURL: '/api/v1/auth',
});

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

  const response = await authApiClient.post('/token', params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });

  // Validate the response data at runtime
  return TokenSchema.parse(response.data);
};
