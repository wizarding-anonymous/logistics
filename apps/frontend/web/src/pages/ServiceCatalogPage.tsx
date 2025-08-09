import React from 'react';
import { useServices } from '@/hooks/useServices';

function ServiceCatalogPage() {
  const { data: services, isLoading, isError, error } = useServices();

  if (isLoading) {
    return <div>Loading service catalog...</div>;
  }

  if (isError) {
    return <div>Error loading catalog: {error?.message}</div>;
  }

  return (
    <div>
      <h2>Service Catalog</h2>
      <p>Browse available services from our trusted suppliers.</p>
      <div style={{ marginTop: '1rem' }}>
        {services && services.length > 0 ? (
          services.map((service) => (
            <div key={service.id} style={{ border: '1px solid #ccc', padding: '1rem', marginBottom: '1rem' }}>
              <h3>{service.name}</h3>
              <p>{service.description}</p>
              <p><strong>Type:</strong> {service.service_type}</p>
              <p><strong>Supplier Org ID:</strong> {service.supplier_organization_id}</p>
              <h4>Tariffs:</h4>
              <ul>
                {service.tariffs.map(tariff => (
                  <li key={tariff.id}>
                    {tariff.price} {tariff.currency} / {tariff.unit}
                  </li>
                ))}
              </ul>
            </div>
          ))
        ) : (
          <p>No services found in the catalog.</p>
        )}
      </div>
    </div>
  );
}

export default ServiceCatalogPage;
