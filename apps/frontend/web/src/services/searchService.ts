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

export const performSearch = async (query: string): Promise<SearchResult[]> => {
  const response = await apiClient.get('/', { params: { q: query } });
  return SearchResultsSchema.parse(response.data);
};
