import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getRfqDetails, getRfqs, createRfq, RFQCreatePayload } from '@/services/rfqService';

export function useRfq(rfqId: string) {
  return useQuery({
    queryKey: ['rfq', rfqId],
    queryFn: () => getRfqDetails(rfqId),
    enabled: !!rfqId,
  });
}

export function useRfqs(orgId: string) {
  return useQuery({
    queryKey: ['rfqs', orgId],
    queryFn: () => getRfqs(orgId),
    enabled: !!orgId,
  });
}

export function useCreateRfq() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ orgId, payload }: { orgId: string; payload: RFQCreatePayload }) => createRfq(orgId, payload),
    onSuccess: (data) => {
      // When a new RFQ is created, invalidate the list of RFQs to trigger a refetch
      queryClient.invalidateQueries({ queryKey: ['rfqs', data.organization_id] });
    },
  });
}

export function useOpenRfqs() {
    return useQuery({
        queryKey: ['openRfqs'],
        queryFn: listOpenRfqs,
    });
}

export function useSubmitOffer(rfqId: string) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (payload: OfferCreatePayload) => submitOffer(rfqId, payload),
        onSuccess: () => {
            // When an offer is submitted, refetch the details of that specific RFQ
            // to show the new offer. Also refetch the list of open RFQs.
            queryClient.invalidateQueries({ queryKey: ['rfq', rfqId] });
            queryClient.invalidateQueries({ queryKey: ['openRfqs'] });
        },
    });
}

export function useAcceptOffer() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (offerId: string) => acceptOffer(offerId),
        onSuccess: (data) => {
            // The accepted offer data contains the rfq_id
            // Invalidate the specific RFQ to update its status to "closed"
            if (data && data.rfq_id) {
                queryClient.invalidateQueries({ queryKey: ['rfq', data.rfq_id] });
            }
        },
    });
}
