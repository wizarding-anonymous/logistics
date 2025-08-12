import axios from 'axios';
import { z } from 'zod';
import { useAuthStore } from '@/state/authStore';

// =================================
// Zod Schemas
// =================================

const KYCDocumentSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  document_type: z.string(),
  file_storage_key: z.string(),
  status: z.enum(['pending', 'approved', 'rejected']),
  rejection_reason: z.string().nullable(),
  uploaded_at: z.string().datetime(),
});

export type KYCDocument = z.infer<typeof KYCDocumentSchema>;
const KYCDocumentListSchema = z.array(KYCDocumentSchema);

// =================================
// API Client Setup
// =================================

// The KYC endpoints are under the /auth service
const apiClient = axios.create({
  baseURL: '/api/v1/auth',
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

export const getMyKycDocuments = async (): Promise<KYCDocument[]> => {
  const response = await apiClient.get('/users/me/kyc-documents');
  return KYCDocumentListSchema.parse(response.data);
};

export const submitKycDocument = async (formData: { document_type: string; file_storage_key: string }): Promise<KYCDocument> => {
  // In a real app, the file would be uploaded to S3 first, and the returned key
  // would be sent to this endpoint. We'll mock the key for now.
  const response = await apiClient.post('/users/me/kyc-documents', formData);
  return KYCDocumentSchema.parse(response.data);
};
