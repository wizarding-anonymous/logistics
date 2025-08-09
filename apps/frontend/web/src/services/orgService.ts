import axios from 'axios';
import { z } from 'zod';
import { useAuthStore } from '@/state/authStore';

// =================================
// Schemas for validation
// =================================

const OrgMemberSchema = z.object({
  user_id: z.string().uuid(),
  role: z.string(),
});

const OrganizationSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  description: z.string().nullable(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export const OrganizationWithMembersSchema = OrganizationSchema.extend({
  members: z.array(OrgMemberSchema),
});

export type OrganizationWithMembers = z.infer<typeof OrganizationWithMembersSchema>;

// =================================
// API Client Setup
// =================================

const orgApiClient = axios.create({
  baseURL: '/api/v1/orgs',
});

// Add a request interceptor to include the auth token
orgApiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// =================================
// API Functions
// =================================

export const createOrganization = async (name: string, description?: string) => {
  const response = await orgApiClient.post('/', { name, description });
  return OrganizationSchema.parse(response.data);
};

export const getOrganizationDetails = async (orgId: string): Promise<OrganizationWithMembers> => {
  const response = await orgApiClient.get(`/${orgId}`);
  return OrganizationWithMembersSchema.parse(response.data);
};

export const createInvitation = async (orgId: string, email: string, role: string) => {
  const response = await orgApiClient.post(`/organizations/${orgId}/invitations`, { email, role });
  return response.data; // Assuming the backend returns the created invitation
};

export const acceptInvitation = async (token: string) => {
  const response = await orgApiClient.post(`/invitations/${token}/accept`);
  return response.data; // Assuming the backend returns the new membership details
};
