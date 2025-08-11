import React from 'react';
import { useSearchParams } from 'react-router-dom';
import { useSearch } from '@/hooks/useSearch';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

function SearchPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  const { data: results, isLoading, isError, error } = useSearch(query);

  return (
    <div className="space-y-6 p-4 md:p-6">
      <h2 className="text-3xl font-bold tracking-tight">Search Results for "{query}"</h2>

      <Card>
        <CardHeader>
          <CardTitle>Results</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <p>Searching...</p>}
          {isError && <p className="text-red-500">Error: {error.message}</p>}
          {!isLoading && !isError && (
            <div>
              {results && results.length > 0 ? (
                <ul className="space-y-4">
                  {results.map((result, index) => (
                    <li key={index} className="p-4 border rounded-md">
                      {/* We'll just display the raw JSON for now */}
                      <pre>{JSON.stringify(result, null, 2)}</pre>
                    </li>
                  ))}
                </ul>
              ) : (
                <p>No results found for your query.</p>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default SearchPage;
