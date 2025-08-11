import axios from 'axios';
import { z } from 'zod';
import { useAuthStore } from '@/state/authStore';

// =================================
// Zod Schemas
// =================================

const StatusHistorySchema = z.object({
    status: z.string(),
    notes: z.string().nullable(),
    timestamp: z.string().datetime(),
});

const ShipmentSegmentSchema = z.object({
    origin_address: z.string(),
    destination_address: z.string(),
});

const OrderSchema = z.object({
    id: z.string().uuid(),
    client_id: z.string().uuid(),
    supplier_id: z.string().uuid(),
    price_amount: z.number(),
    price_currency: z.string(),
    status: z.string(),
    created_at: z.string().datetime(),
    updated_at: z.string().datetime(),
    segments: z.array(ShipmentSegmentSchema),
    status_history: z.array(StatusHistorySchema),
});

export type Order = z.infer<typeof OrderSchema>;

// =================================
// API Client Setup
// =================================

const apiClient = axios.create({
  baseURL: '/api/v1/orders',
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

export const getOrderById = async (orderId: string): Promise<Order> => {
  const response = await apiClient.get(`/orders/${orderId}`);
  return OrderSchema.parse(response.data);
};

export type ReviewCreatePayload = {
    rating: number;
    comment?: string;
}

export const submitReview = async (orderId: string, payload: ReviewCreatePayload): Promise<any> => {
    const response = await apiClient.post(`/orders/${orderId}/review`, payload);
    return response.data;
}

export const updateOrderStatus = async ({ orderId, status, notes }: { orderId: string; status: string; notes?: string }): Promise<Order> => {
    const response = await apiClient.patch(`/orders/${orderId}/status`, { status, notes });
    return OrderSchema.parse(response.data);
};
