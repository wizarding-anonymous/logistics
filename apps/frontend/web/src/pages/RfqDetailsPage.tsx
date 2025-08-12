import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useRfq, useSubmitOffer, useAcceptOffer } from '@/hooks/useRfq';
import { useAuthStore } from '@/state/authStore';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

function SubmitOfferForm({ rfqId }: { rfqId: string }) {
    const { mutate: submitOffer, isPending } = useSubmitOffer(rfqId);
    const [price, setPrice] = useState('');
    const [notes, setNotes] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        submitOffer({
            price_amount: parseFloat(price),
            price_currency: 'USD', // Hardcoded for now
            notes,
        });
    };

    return (
        <Card className="mt-6">
            <CardHeader>
                <CardTitle>Submit Your Offer</CardTitle>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="space-y-2">
                        <Label htmlFor="price">Your Price (USD)</Label>
                        <Input id="price" type="number" value={price} onChange={(e) => setPrice(e.target.value)} required />
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="notes">Notes (Optional)</Label>
                        <Textarea id="notes" value={notes} onChange={(e) => setNotes(e.target.value)} />
                    </div>
                    <Button type="submit" className="w-full" disabled={isPending}>
                        {isPending ? 'Submitting...' : 'Submit Offer'}
                    </Button>
                </form>
            </CardContent>
        </Card>
    );
}

function RfqDetailsPage() {
  const { rfqId } = useParams<{ rfqId: string }>();
  const { data: rfq, isLoading, isError, error } = useRfq(rfqId!);
  const { roles, organizationId } = useAuthStore();
  const acceptOffer = useAcceptOffer();

  const isSupplier = roles.includes('supplier');
  const isOwner = rfq?.organization_id === organizationId;

  if (isLoading) return <div className="p-6">Loading RFQ details...</div>;
  if (isError) return <div className="p-6 text-red-500">Error: {error.message}</div>;
  if (!rfq) return <div className="p-6">RFQ not found.</div>;

  return (
    <div className="space-y-6 p-4 md:p-6 max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold tracking-tight">RFQ Details #{rfq.id.substring(0, 8)}</h2>

      <Card>
        <CardHeader><CardTitle>Shipment Details</CardTitle></CardHeader>
        <CardContent className="grid grid-cols-2 gap-4">
            <div><strong>From:</strong> {rfq.segments[0]?.origin_address}</div>
            <div><strong>To:</strong> {rfq.segments[0]?.destination_address}</div>
            <div><strong>Status:</strong> {rfq.status}</div>
            <div className="col-span-2"><strong>Cargo:</strong> {rfq.cargo.description}</div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Offers Received ({rfq.offers.length})</CardTitle></CardHeader>
        <CardContent>
            {rfq.offers.length > 0 ? (
                <ul className="space-y-4">
                    {rfq.offers.map((offer) => (
                        <li key={offer.id} className="p-4 border rounded-md flex justify-between items-center">
                            <div>
                                <p>From Supplier Org: <span className="font-semibold">{offer.supplier_organization_id.substring(0, 8)}...</span></p>
                                <p className="text-lg font-bold">{offer.price_amount} {offer.price_currency}</p>
                                {offer.notes && <p className="text-sm text-muted-foreground">Notes: {offer.notes}</p>}
                            </div>
                            {isOwner && rfq.status === 'open' && (
                                <Button
                                    onClick={() => acceptOffer.mutate(offer.id)}
                                    disabled={acceptOffer.isPending}
                                >
                                    {acceptOffer.isPending ? 'Accepting...' : 'Accept Offer'}
                                </Button>
                            )}
                            {offer.status === 'accepted' && (
                                <span className="font-semibold text-green-600">Accepted</span>
                            )}
                        </li>
                    ))}
                </ul>
            ) : (
                <p>No offers submitted yet.</p>
            )}
        </CardContent>
      </Card>

      {isSupplier && rfq.status === 'open' && (
        <SubmitOfferForm rfqId={rfq.id} />
      )}
    </div>
  );
}

export default RfqDetailsPage;
