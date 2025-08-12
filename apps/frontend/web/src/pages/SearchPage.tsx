import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useSearch } from '@/hooks/useSearch';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { SearchFilters } from '@/services/searchService';

function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [filters, setFilters] = useState<SearchFilters>({
    status: searchParams.get('status') || undefined,
  });

  const { data: results, isLoading, isError, error } = useSearch(query, filters);

  useEffect(() => {
    // Update the URL when filters change
    const newParams = new URLSearchParams();
    if (query) newParams.set('q', query);
    if (filters.status) newParams.set('status', filters.status);
    setSearchParams(newParams);
  }, [query, filters, setSearchParams]);

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value || undefined }));
  };

  return (
    <div className="grid md:grid-cols-4 gap-6 p-4 md:p-6">
      {/* Filters Panel */}
      <div className="md:col-span-1">
        <Card>
            <CardHeader><CardTitle>Filters</CardTitle></CardHeader>
            <CardContent className="space-y-4">
                <div className="space-y-2">
                    <Label htmlFor="status">Status</Label>
                    <Input
                        id="status"
                        name="status"
                        value={filters.status || ''}
                        onChange={handleFilterChange}
                        placeholder="e.g., open, closed"
                    />
                </div>
                {/* Add more filters for price etc. here */}
            </CardContent>
        </Card>
      </div>

      {/* Results Panel */}
      <div className="md:col-span-3">
        <h2 className="text-3xl font-bold tracking-tight mb-4">Search Results for "{query}"</h2>
        <Card>
          <CardContent>
            {isLoading && <p>Searching...</p>}
            {isError && <p className="text-red-500">Error: {error.message}</p>}
            {!isLoading && !isError && (
              <div>
                {results && results.length > 0 ? (
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>ID</TableHead>
                                <TableHead>Type</TableHead>
                                <TableHead>Description / Status</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {results.map((result, index) => (
                                <TableRow key={index}>
                                    <TableCell>{(result.order_id || result.rfq_id)?.substring(0,8)}...</TableCell>
                                    <TableCell>{result.type}</TableCell>
                                    <TableCell>{result.description || result.status}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                ) : (
                  <p>No results found for your query.</p>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default SearchPage;
