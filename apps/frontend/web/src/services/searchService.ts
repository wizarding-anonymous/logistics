import axios from 'axios';
import { z } from 'zod';

// For now, we don't know the exact shape of the search results,
// so we'll use a generic schema.
const SearchResultSchema = z.record(z.any());
const SearchResultsSchema = z.array(SearchResultSchema);

export type SearchResult = z.infer<typeof SearchResultSchema>;

// =================================
// API Client Setup
// =================================

const apiClient = axios.create({
  baseURL: '/api/v1/search',
});

// Note: Search might be a public endpoint, so no auth token is added for now.

// =================================
// API Functions
// =================================

export interface SearchFilters {
    status?: string;
    min_price?: number;
    max_price?: number;
}

export const performSearch = async (query: string, filters: SearchFilters): Promise<SearchResult[]> => {
  const params = { q: query, ...filters };
  const response = await apiClient.get('/', { params });
  return SearchResultsSchema.parse(response.data);
};
