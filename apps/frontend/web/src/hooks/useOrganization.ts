import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getOrganizationDetails, createInvitation, removeMember } from '@/services/orgService';

export function useOrganization(orgId: string) {
  return useQuery({
    queryKey: ['organization', orgId],
    queryFn: () => getOrganizationDetails(orgId),
    enabled: !!orgId, // Only run the query if orgId is a valid string
  });
}

export function useInviteMember(orgId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ email, role }: { email: string; role: string }) => createInvitation(orgId, email, role),
    onSuccess: () => {
      // Invalidate and refetch the organization query to show the new member/invitation
      queryClient.invalidateQueries({ queryKey: ['organization', orgId] });
    },
  });
}

export function useRemoveMember(orgId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: string) => removeMember(orgId, userId),
    onSuccess: () => {
      // Invalidate and refetch the organization query to show the updated member list
      queryClient.invalidateQueries({ queryKey: ['organization', orgId] });
    },
  });
}
