import axios from 'axios';
import { z } from 'zod';
import { useAuthStore } from '@/state/authStore';

// =================================
// Zod Schemas
// =================================

const DisputeMessageSchema = z.object({
  id: z.string().uuid(),
  dispute_id: z.string().uuid(),
  sender_id: z.string().uuid(),
  content: z.string(),
  timestamp: z.string().datetime(),
});

const DisputeSchema = z.object({
    id: z.string().uuid(),
    order_id: z.string().uuid(),
    opened_by_id: z.string().uuid(),
    status: z.string(),
    resolution: z.string().nullable(),
    created_at: z.string().datetime(),
    resolved_at: z.string().datetime().nullable(),
    messages: z.array(DisputeMessageSchema),
});

export type Dispute = z.infer<typeof DisputeSchema>;

// =================================
// API Client Setup
// =================================

const apiClient = axios.create({
  baseURL: '/api/v1/disputes',
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

export const getDisputeByOrder = async (orderId: string): Promise<Dispute | null> => {
  try {
    const response = await apiClient.get(`/by-order/${orderId}`);
    return DisputeSchema.parse(response.data);
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 404) {
      return null; // No dispute exists for this order yet
    }
    throw error;
  }
};

export const openDispute = async (payload: { order_id: string, reason: string }): Promise<Dispute> => {
    const response = await apiClient.post('/', payload);
    return DisputeSchema.parse(response.data);
};

export const addDisputeMessage = async (disputeId: string, content: string): Promise<any> => {
    const response = await apiClient.post(`/${disputeId}/messages`, { content });
    return response.data;
}
