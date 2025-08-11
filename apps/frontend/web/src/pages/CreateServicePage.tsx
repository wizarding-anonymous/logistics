import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useCreateServiceOffering } from '@/hooks/useCatalog';

function CreateServicePage() {
  const navigate = useNavigate();
  const createService = useCreateServiceOffering();

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [serviceType, setServiceType] = useState('FTL');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createService.mutate(
      {
        name,
        description,
        service_type: serviceType,
        is_active: true,
        // For simplicity, we'll create a default tariff
        tariffs: [{ price: 100, currency: 'USD', unit: 'per_km' }],
      },
      {
        onSuccess: () => {
          navigate('/my-services');
        },
      }
    );
  };

  return (
    <div className="space-y-6 p-4 md:p-6 max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold tracking-tight">Create New Service Offering</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Service Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Service Name</Label>
              <Input id="name" value={name} onChange={(e) => setName(e.target.value)} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea id="description" value={description} onChange={(e) => setDescription(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="service-type">Service Type</Label>
              <Input id="service-type" value={serviceType} onChange={(e) => setServiceType(e.target.value)} required />
            </div>
          </CardContent>
        </Card>

        {/* TODO: Add a dynamic form for adding multiple tariffs */}

        <div className="flex justify-end">
          <Button type="submit" disabled={createService.isPending}>
            {createService.isPending ? 'Creating...' : 'Create Service'}
          </Button>
        </div>
      </form>
    </div>
  );
}

export default CreateServicePage;
