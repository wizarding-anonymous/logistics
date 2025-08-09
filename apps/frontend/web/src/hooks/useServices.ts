import { useQuery } from '@tanstack/react-query';
import { listServices } from '@/services/catalogService';

export function useServices() {
  return useQuery({
    queryKey: ['services'],
    queryFn: listServices,
  });
}
