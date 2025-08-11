import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getDisputeByOrder, openDispute, addDisputeMessage } from '@/services/disputeService';

export function useDispute(orderId: string) {
  return useQuery({
    queryKey: ['dispute', orderId],
    queryFn: () => getDisputeByOrder(orderId),
    enabled: !!orderId,
  });
}

export function useOpenDispute() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: { order_id: string, reason: string }) => openDispute(payload),
    onSuccess: (data) => {
      // When a dispute is opened, invalidate the query for that order's dispute
      queryClient.invalidateQueries({ queryKey: ['dispute', data.order_id] });
    },
  });
}

export function useAddDisputeMessage() {
    const queryClient = useQueryClient();

    return useMutation({
      mutationFn: ({ disputeId, content }: { disputeId: string, content: string }) => addDisputeMessage(disputeId, content),
      onSuccess: (data) => {
        // This assumes the message data contains the order_id or dispute_id to invalidate
        // A better approach might be to pass the orderId to the hook.
        // For now, we'll refetch all disputes as a simple solution.
        queryClient.invalidateQueries({ queryKey: ['dispute'] });
      },
    });
  }
