import axios from 'axios';
import { z } from 'zod';
import { useAuthStore } from '@/state/authStore';

// =================================
// Zod Schemas
// =================================

export const InvoiceSchema = z.object({
  id: z.string().uuid(),
  order_id: z.string().uuid(),
  organization_id: z.string().uuid(),
  status: z.string(),
  amount: z.number(),
  currency: z.string(),
  created_at: z.string().datetime(),
});

export type Invoice = z.infer<typeof InvoiceSchema>;
const InvoiceListSchema = z.array(InvoiceSchema);

// =================================
// API Client Setup
// =================================

const apiClient = axios.create({
  baseURL: '/api/v1/payments',
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

export const listMyInvoices = async (): Promise<Invoice[]> => {
  const response = await apiClient.get('/invoices');
  return InvoiceListSchema.parse(response.data);
};

export const payInvoice = async (invoiceId: string): Promise<Invoice> => {
  const response = await apiClient.post(`/invoices/${invoiceId}/pay`);
  return InvoiceSchema.parse(response.data);
};

export const getInvoiceById = async (invoiceId: string): Promise<Invoice> => {
    // This endpoint doesn't exist yet, but we'll need it for the InvoiceDetailsPage
    // For now, it will fail, but we'll add the endpoint later if needed.
    const response = await apiClient.get(`/invoices/${invoiceId}`);
    return InvoiceSchema.parse(response.data);
}
