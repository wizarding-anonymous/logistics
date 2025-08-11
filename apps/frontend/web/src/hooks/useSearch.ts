import { useQuery } from '@tanstack/react-query';
import { performSearch, SearchFilters } from '@/services/searchService';

export function useSearch(query: string, filters: SearchFilters) {
  return useQuery({
    // The query key now includes the filters object to ensure queries are refetched when filters change
    queryKey: ['search', query, filters],
    queryFn: () => performSearch(query, filters),
    // Only run the query if the query string is not empty
    enabled: !!query,
  });
}
