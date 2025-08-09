import { useQuery } from '@tanstack/react-query';
import { getInvoiceForOrder } from '@/services/paymentService';

export function useInvoice(orderId: string) {
  return useQuery({
    queryKey: ['invoice', orderId],
    queryFn: () => getInvoiceForOrder(orderId),
    enabled: !!orderId,
  });
}
