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
