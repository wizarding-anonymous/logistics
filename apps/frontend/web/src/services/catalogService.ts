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

export const ServiceOfferingSchema = z.object({
  id: z.string().uuid(),
  supplier_organization_id: z.string().uuid(),
  name: z.string(),
  description: z.string().nullable(),
  service_type: z.string(),
  is_active: z.boolean(),
  tariffs: z.array(TariffSchema),
});

export const ServiceOfferingListSchema = z.array(ServiceOfferingSchema);

export type ServiceOffering = z.infer<typeof ServiceOfferingSchema>;

export type TariffCreatePayload = {
    price: number;
    currency: string;
    unit: string;
};

export type ServiceOfferingCreatePayload = {
    name: string;
    description?: string;
    service_type: string;
    is_active: boolean;
    tariffs: TariffCreatePayload[];
};

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

export const listPublicServices = async (): Promise<ServiceOffering[]> => {
  const response = await apiClient.get('/services');
  return ServiceOfferingListSchema.parse(response.data);
};

export const listMyServices = async (): Promise<ServiceOffering[]> => {
    // This is the authenticated endpoint for suppliers
    const response = await apiClient.get('/supplier/services');
    return ServiceOfferingListSchema.parse(response.data);
}

export const createServiceOffering = async (payload: ServiceOfferingCreatePayload): Promise<ServiceOffering> => {
    const response = await apiClient.post('/services', payload);
    return ServiceOfferingSchema.parse(response.data);
}
