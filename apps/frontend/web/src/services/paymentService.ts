import axios from 'axios';
import { z } from 'zod';
import { useAuthStore } from '@/state/authStore';

// =================================
// Schemas for validation
// =================================

const TransactionSchema = z.object({
  id: z.string().uuid(),
  transaction_type: z.string(),
  amount: z.number(),
  notes: z.string().nullable(),
  created_at: z.string().datetime(),
});

const InvoiceSchema = z.object({
  id: z.string().uuid(),
  order_id: z.string().uuid(),
  organization_id: z.string().uuid(),
  status: z.string(),
  amount: z.number(),
  currency: z.string(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  transactions: z.array(TransactionSchema),
});

export type Invoice = z.infer<typeof InvoiceSchema>;

// =================================
// API Client Setup
// =================================

const paymentApiClient = axios.create({
  baseURL: '/api/v1/payments',
});

// Add a request interceptor to include the auth token
paymentApiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// =================================
// API Functions
// =================================

export const getInvoiceForOrder = async (orderId: string): Promise<Invoice> => {
  const response = await paymentApiClient.get(`/invoices/by-order/${orderId}`);
  return InvoiceSchema.parse(response.data);
};
