import axios from 'axios';
import { z } from 'zod';
import { useAuthStore } from '@/state/authStore';

// =================================
// Schemas for validation
// =================================

const OfferSchema = z.object({
  id: z.string().uuid(),
  rfq_id: z.string().uuid(),
  supplier_organization_id: z.string().uuid(),
  price_amount: z.number(),
  price_currency: z.string(),
  notes: z.string().nullable(),
  status: z.string(),
  created_at: z.string().datetime(),
});

const RFQSchema = z.object({
  id: z.string().uuid(),
  organization_id: z.string().uuid(),
  user_id: z.string().uuid(),
  status: z.string(),
  origin_address: z.string(),
  destination_address: z.string(),
  cargo_description: z.string(),
  cargo_weight_kg: z.number().nullable(),
  created_at: z.string().datetime(),
  offers: z.array(OfferSchema),
});

export type RFQ = z.infer<typeof RFQSchema>;

// =================================
// API Client Setup
// =================================

const rfqApiClient = axios.create({
  baseURL: '/api/v1/rfqs',
});

// Add a request interceptor to include the auth token
rfqApiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// =================================
// API Functions
// =================================

export const getRfqDetails = async (rfqId: string): Promise<RFQ> => {
  const response = await rfqApiClient.get(`/${rfqId}`);
  return RFQSchema.parse(response.data);
};

// Add other functions like createRfq, submitOffer, acceptOffer later...
