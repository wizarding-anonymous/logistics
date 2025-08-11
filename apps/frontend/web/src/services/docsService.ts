import axios from 'axios';
import { z } from 'zod';
import { useAuthStore } from '@/state/authStore';

// =================================
// Zod Schemas
// =================================

const DocumentSchema = z.object({
  id: z.string().uuid(),
  filename: z.string(),
  document_type: z.string(),
  download_url: z.string().url(),
  created_at: z.string().datetime(),
});

export type Document = z.infer<typeof DocumentSchema>;
const DocumentListSchema = z.array(DocumentSchema);

const PresignedUrlSchema = z.object({
    upload_url: z.string().url(),
    s3_path: z.string(),
});

// =================================
// API Client Setup
// =================================

const apiClient = axios.create({
  baseURL: '/api/v1/docs',
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

export const listDocuments = async (entityType: string, entityId: string): Promise<Document[]> => {
    const response = await apiClient.get(`/documents/entity/${entityType}/${entityId}`);
    return DocumentListSchema.parse(response.data);
};

export const getUploadUrl = async (entityType: string, entityId: string, filename: string): Promise<{ upload_url: string; s3_path: string }> => {
    const response = await apiClient.get('/documents/upload-url', {
        params: { entity_type: entityType, entity_id: entityId, filename },
    });
    return PresignedUrlSchema.parse(response.data);
};

export const confirmUpload = async (payload: { s3_path: string; entity_type: string; entity_id: string; document_type: string; filename: string }): Promise<Document> => {
    const response = await apiClient.post('/documents/register', null, { params: payload });
    return DocumentSchema.parse(response.data);
};
