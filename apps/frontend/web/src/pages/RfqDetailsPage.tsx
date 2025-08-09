import React from 'react';
import { useParams } from 'react-router-dom';
import { useRfq } from '@/hooks/useRfq';

function RfqDetailsPage() {
  const { rfqId } = useParams<{ rfqId: string }>();
  const { data: rfq, isLoading, isError, error } = useRfq(rfqId || '');

  if (isLoading) {
    return <div>Loading RFQ details...</div>;
  }

  if (isError) {
    return <div>Error loading RFQ: {error?.message}</div>;
  }

  if (!rfq) {
    return <div>RFQ not found.</div>;
  }

  return (
    <div>
      <h2>RFQ Details: {rfq.id}</h2>
      <p>Status: <strong>{rfq.status}</strong></p>
      <p>From: {rfq.origin_address}</p>
      <p>To: {rfq.destination_address}</p>
      <p>Cargo: {rfq.cargo_description} ({rfq.cargo_weight_kg} kg)</p>

      <hr style={{ margin: '1rem 0' }} />

      <h3>Offers Received ({rfq.offers.length})</h3>
      {rfq.offers.length > 0 ? (
        <ul>
          {rfq.offers.map((offer) => (
            <li key={offer.id}>
              From Supplier Org {offer.supplier_organization_id}:
              <strong>{offer.price_amount} {offer.price_currency}</strong>
              <p>Notes: {offer.notes}</p>
              <p>Status: {offer.status}</p>
            </li>
          ))}
        </ul>
      ) : (
        <p>No offers have been submitted for this RFQ yet.</p>
      )}

      {/* TODO: Add form for suppliers to submit an offer */}
      {/* TODO: Add button for clients to accept an offer */}
    </div>
  );
}

export default RfqDetailsPage;
