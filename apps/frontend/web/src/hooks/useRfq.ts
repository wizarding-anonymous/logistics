import { useQuery } from '@tanstack/react-query';
import { getRfqDetails } from '@/services/rfqService';

export function useRfq(rfqId: string) {
  return useQuery({
    queryKey: ['rfq', rfqId],
    queryFn: () => getRfqDetails(rfqId),
    enabled: !!rfqId,
  });
}
