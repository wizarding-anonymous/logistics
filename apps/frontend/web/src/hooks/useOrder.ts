import { useQuery } from '@tanstack/react-query';
import { getOrderById } from '@/services/api';

export function useOrder(orderId: string) {
  return useQuery({
    queryKey: ['order', orderId],
    queryFn: () => getOrderById(orderId),
    // The query will not run if the orderId is not a valid string
    enabled: !!orderId,
  });
}
