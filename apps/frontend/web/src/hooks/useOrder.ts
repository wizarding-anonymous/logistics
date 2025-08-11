import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getOrderById, updateOrderStatus } from '@/services/orderService';

export function useOrder(orderId: string) {
  return useQuery({
    queryKey: ['order', orderId],
    queryFn: () => getOrderById(orderId),
    enabled: !!orderId,
  });
}

export function useUpdateOrderStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ orderId, status, notes }: { orderId: string; status: string; notes?: string }) =>
      updateOrderStatus({ orderId, status, notes }),
    onSuccess: (data) => {
      // When status is updated, refetch the order details
      queryClient.invalidateQueries({ queryKey: ['order', data.id] });
    },
  });
}

export function useSubmitReview() {
    const queryClient = useQueryClient();

    return useMutation({
      mutationFn: ({ orderId, payload }: { orderId: string; payload: { rating: number; comment?: string } }) =>
        submitReview(orderId, payload),
      onSuccess: (data) => {
        // When a review is submitted, refetch the order details to show the new review
        if (data && data.order_id) {
            queryClient.invalidateQueries({ queryKey: ['order', data.order_id] });
        }
      },
    });
  }
