import axios from 'axios';
import { z } from 'zod';

// Define a Zod schema for the Order object for runtime validation
const OrderSchema = z.object({
  id: z.string().uuid(),
  client_id: z.string().uuid(),
  supplier_id: z.string().uuid(),
  status: z.string(),
  price_amount: z.number(),
  price_currency: z.string(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

// Define the type from the schema
export type Order = z.infer<typeof OrderSchema>;

const apiClient = axios.create({
  // The proxy in vite.config.ts will handle this request in development
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getOrderById = async (orderId: string): Promise<Order> => {
  const response = await apiClient.get(`/orders/${orderId}`);
  // Validate the response data at runtime
  return OrderSchema.parse(response.data);
};
