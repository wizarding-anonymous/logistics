import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listMyInvoices, payInvoice } from '@/services/paymentService';

export function useMyInvoices() {
  return useQuery({
    queryKey: ['myInvoices'],
    queryFn: listMyInvoices,
  });
}

export function usePayInvoice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (invoiceId: string) => payInvoice(invoiceId),
    onSuccess: () => {
      // When an invoice is paid, refetch the list of invoices to update its status
      queryClient.invalidateQueries({ queryKey: ['myInvoices'] });
    },
  });
}

export function useMyPayouts() {
    return useQuery({
      queryKey: ['myPayouts'],
      queryFn: listMyPayouts,
    });
}

export function useApprovePayout() {
    const queryClient = useQueryClient();

    return useMutation({
      mutationFn: (payoutId: string) => approvePayout(payoutId),
      onSuccess: () => {
        // When a payout is approved, we should refetch any lists of payouts.
        // A more specific query key could be used if we had one for pending payouts.
        queryClient.invalidateQueries({ queryKey: ['myPayouts'] });
        // Potentially refetch an admin-specific query for pending payouts too
        queryClient.invalidateQueries({ queryKey: ['pendingPayouts'] });
      },
    });
  }
