import { useQuery } from '@tanstack/react-query';
import { getOrganizationDetails } from '@/services/orgService';

export function useOrganization(orgId: string) {
  return useQuery({
    queryKey: ['organization', orgId],
    queryFn: () => getOrganizationDetails(orgId),
    enabled: !!orgId, // Only run the query if orgId is a valid string
  });
}
