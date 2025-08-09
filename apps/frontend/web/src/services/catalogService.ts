import axios from 'axios';
import { z } from 'zod';
import { useAuthStore } from '@/state/authStore';

// =================================
// Schemas for validation
// =================================

const TariffSchema = z.object({
  id: z.string().uuid(),
  price: z.number(),
  currency: z.string(),
  unit: z.string(),
});

const ServiceOfferingSchema = z.object({
  id: z.string().uuid(),
  supplier_organization_id: z.string().uuid(),
  name: z.string(),
  description: z.string().nullable(),
  service_type: z.string(),
  is_active: z.boolean(),
  tariffs: z.array(TariffSchema),
});

export type ServiceOffering = z.infer<typeof ServiceOfferingSchema>;

// =================================
// API Client Setup
// =================================

const apiClient = axios.create({
  baseURL: '/api/v1/catalog',
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

export const listServices = async (): Promise<ServiceOffering[]> => {
  const response = await apiClient.get('/services');
  return z.array(ServiceOfferingSchema).parse(response.data);
};

// Add createServiceOffering later
