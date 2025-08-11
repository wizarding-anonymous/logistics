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
