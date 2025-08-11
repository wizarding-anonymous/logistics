import axios from 'axios';
import { z } from 'zod';
import { useAuthStore } from '@/state/authStore';

// =================================
// Schemas to match the backend API
// =================================

const OfferSchema = z.object({
  id: z.string().uuid(),
  rfq_id: z.string().uuid(),
  supplier_organization_id: z.string().uuid(),
  price_amount: z.number(),
  price_currency: z.string(),
  notes: z.string().nullable(),
  status: z.enum(['pending', 'accepted', 'rejected']),
  created_at: z.string().datetime(),
});

const CargoSchema = z.object({
  id: z.string().uuid(),
  description: z.string(),
  weight_kg: z.number().nullable(),
  volume_cbm: z.number().nullable(),
  pallet_count: z.number().nullable(),
});

const ShipmentSegmentSchema = z.object({
    id: z.string().uuid(),
    sequence: z.number(),
    origin_address: z.string(),
    destination_address: z.string(),
});

export const RFQSchema = z.object({
  id: z.string().uuid(),
  organization_id: z.string().uuid(),
  user_id: z.string().uuid(),
  status: z.enum(['open', 'closed', 'cancelled']),
  created_at: z.string().datetime(),
  offers: z.array(OfferSchema),
  cargo: CargoSchema,
  segments: z.array(ShipmentSegmentSchema),
});

export const RFQListSchema = z.array(RFQSchema);

export type RFQ = z.infer<typeof RFQSchema>;

// This is the type for the data we send to the backend to create an RFQ
export type RFQCreatePayload = {
    cargo: {
        description: string;
        weight_kg?: number;
        volume_cbm?: number;
    };
    segments: {
        origin_address: string;
        destination_address: string;
    }[];
};


// =================================
// API Client Setup
// =================================

const rfqApiClient = axios.create({
  baseURL: '/api/v1/rfqs',
});

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

export const getRfqs = async (orgId: string): Promise<RFQ[]> => {
    const response = await rfqApiClient.get('/', { params: { org_id: orgId } });
    return RFQListSchema.parse(response.data);
}

export const createRfq = async (orgId: string, payload: RFQCreatePayload): Promise<RFQ> => {
    const response = await rfqApiClient.post('/', payload, { params: { org_id: orgId } });
    return RFQSchema.parse(response.data);
}

export const listOpenRfqs = async (): Promise<RFQ[]> => {
    const response = await rfqApiClient.get('/open-rfqs');
    return RFQListSchema.parse(response.data);
}

export type OfferCreatePayload = {
    price_amount: number;
    price_currency: string;
    notes?: string;
}

export const submitOffer = async (rfqId: string, payload: OfferCreatePayload): Promise<any> => {
    const response = await rfqApiClient.post(`/${rfqId}/offers`, payload);
    return response.data;
}

export const acceptOffer = async (offerId: string): Promise<any> => {
    // Note: The endpoint is on the root of the service, not nested under /rfqs/
    const response = await rfqApiClient.post(`/offers/${offerId}/accept`);
    return response.data;
}
