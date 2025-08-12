import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listMyServices, createServiceOffering, ServiceOfferingCreatePayload } from '@/services/catalogService';

export function useMyServices() {
  return useQuery({
    queryKey: ['myServices'],
    queryFn: listMyServices,
  });
}

export function useCreateServiceOffering() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ServiceOfferingCreatePayload) => createServiceOffering(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myServices'] });
    },
  });
}
