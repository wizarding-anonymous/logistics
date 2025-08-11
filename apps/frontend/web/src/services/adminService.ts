import axios from 'axios';
import { z } from 'zod';
import { useAuthStore } from '@/state/authStore';

// =================================
// Zod Schemas
// =================================

const KYCDocumentSchema = z.object({
  id: z.string().uuid(),
  document_type: z.string(),
  file_storage_key: z.string(),
  status: z.string(),
  rejection_reason: z.string().nullable(),
});

const UserWithKYCSchema = z.object({
  id: z.string().uuid(),
  email: z.string(),
  roles: z.array(z.string()),
  kyc_documents: z.array(KYCDocumentSchema),
});

export type UserWithKYC = z.infer<typeof UserWithKYCSchema>;
const PendingKycListSchema = z.array(UserWithKYCSchema);


// =================================
// API Client Setup
// =================================

const apiClient = axios.create({
  baseURL: '/api/v1/admin',
});

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// =================================
// API Functions
// =================================

export const getPendingKyc = async (): Promise<UserWithKYC[]> => {
  const response = await apiClient.get('/kyc/pending');
  return PendingKycListSchema.parse(response.data);
};

export const approveKycDocument = async (docId: string): Promise<any> => {
  const response = await apiClient.post(`/kyc/documents/${docId}/approve`);
  return response.data;
};

export const rejectKycDocument = async ({ docId, reason }: { docId: string; reason: string }): Promise<any> => {
    const response = await apiClient.post(`/kyc/documents/${docId}/reject`, { reason });
    return response.data;
};

// Payouts are managed via the payments service, but the endpoint is admin-only
const paymentsApiClient = axios.create({ baseURL: '/api/v1/payments' });

export const listPendingPayouts = async (): Promise<any[]> => {
    // This assumes an admin endpoint exists to get all payouts, which we then filter client-side.
    // A better approach would be a dedicated backend endpoint like `/payouts/pending`.
    // We will re-use the supplier-facing endpoint for now and filter on the client.
    const response = await paymentsApiClient.get('/payouts'); // This needs to be an admin endpoint in a real app
    return response.data.filter((p: any) => p.status === 'pending');
};

export const approvePayout = async (payoutId: string): Promise<any> => {
    const response = await paymentsApiClient.post(`/payouts/${payoutId}/approve`);
    return response.data;
};
