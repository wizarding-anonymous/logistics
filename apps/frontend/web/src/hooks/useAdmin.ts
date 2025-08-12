import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getPendingKyc, approveKycDocument, rejectKycDocument } from '@/services/adminService';

export function usePendingKyc() {
  return useQuery({
    queryKey: ['pendingKyc'],
    queryFn: getPendingKyc,
  });
}

export function useApproveKycDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (docId: string) => approveKycDocument(docId),
    onSuccess: () => {
      // When a doc is approved, refetch the list of pending requests
      queryClient.invalidateQueries({ queryKey: ['pendingKyc'] });
    },
  });
}

import { listPendingPayouts, approvePayout } from '@/services/adminService';

export function useRejectKycDocument() {
    const queryClient = useQueryClient();

    return useMutation({
      mutationFn: ({ docId, reason }: { docId: string; reason: string }) => rejectKycDocument({ docId, reason }),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['pendingKyc'] });
      },
    });
  }

export function usePendingPayouts() {
    return useQuery({
        queryKey: ['pendingPayouts'],
        queryFn: listPendingPayouts,
    });
}

export function useApprovePayout() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (payoutId: string) => approvePayout(payoutId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['pendingPayouts'] });
        },
    });
}
