import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useCreateRfq } from '@/hooks/useRfq';

// TODO: Replace with the actual organization ID from user's context/state
const MOCK_ORG_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6";

function CreateRfqPage() {
  const navigate = useNavigate();
  const createRfq = useCreateRfq();

  // Simple state management for the form
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      cargo: { description },
      segments: [{ origin_address: origin, destination_address: destination }],
    };

    createRfq.mutate(
      { orgId: MOCK_ORG_ID, payload },
      {
        onSuccess: () => {
          // Navigate to the RFQ list page on success
          navigate('/rfqs');
        },
      }
    );
  };

  return (
    <div className="space-y-6 p-4 md:p-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Create a New RFQ</h2>
          <p className="text-muted-foreground">Fill out the details below to get quotes from suppliers.</p>
        </div>
        <Link to="/rfqs">
            <Button variant="outline">Cancel</Button>
        </Link>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle>Shipment Route</CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <Label htmlFor="origin">Origin Address</Label>
                        <Input id="origin" value={origin} onChange={e => setOrigin(e.target.value)} required />
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="destination">Destination Address</Label>
                        <Input id="destination" value={destination} onChange={e => setDestination(e.target.value)} required />
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Cargo Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="space-y-2">
                        <Label htmlFor="cargo-description">Description of Goods</Label>
                        <Textarea id="cargo-description" value={description} onChange={e => setDescription(e.target.value)} required />
                    </div>
                </CardContent>
            </Card>

            <div className="flex justify-end space-x-2">
                <Button type="submit" disabled={createRfq.isPending}>
                  {createRfq.isPending ? 'Submitting...' : 'Submit RFQ'}
                </Button>
            </div>
            {createRfq.isError && (
                <p className="text-red-500 text-right">Error: {createRfq.error.message}</p>
            )}
        </div>
      </form>
    </div>
  );
}

export default CreateRfqPage;
