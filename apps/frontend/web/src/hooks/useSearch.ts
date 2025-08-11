import { useQuery } from '@tanstack/react-query';
import { performSearch } from '@/services/searchService';

export function useSearch(query: string) {
  return useQuery({
    queryKey: ['search', query],
    queryFn: () => performSearch(query),
    // Only run the query if the query string is not empty
    enabled: !!query,
  });
}
