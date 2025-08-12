import React from 'react';
import { usePendingKyc, useApproveKycDocument, useRejectKycDocument } from '@/hooks/useAdmin';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'; // Assuming Accordion is added

function KycVerificationPage() {
  const { data: users, isLoading, isError, error } = usePendingKyc();
  const approveMutation = useApproveKycDocument();
  const rejectMutation = useRejectKycDocument();

  const handleReject = (docId: string) => {
    const reason = prompt("Please provide a reason for rejection:");
    if (reason) {
        rejectMutation.mutate({ docId, reason });
    }
  };

  return (
    <div className="space-y-6 p-4 md:p-6">
      <h2 className="text-3xl font-bold tracking-tight">KYC Verification Requests</h2>

      <Card>
        <CardHeader>
          <CardTitle>Pending Submissions</CardTitle>
          <CardDescription>Review and action the document submissions below.</CardDescription>
        </CardHeader>
        <CardContent>
            {isLoading && <p>Loading requests...</p>}
            {isError && <p className="text-red-500">Error: {error.message}</p>}
            {!isLoading && !isError && (
                <Accordion type="single" collapsible className="w-full">
                    {users?.map(user => (
                        <AccordionItem value={user.id} key={user.id}>
                            <AccordionTrigger>{user.email}</AccordionTrigger>
                            <AccordionContent>
                                <div className="space-y-4">
                                    {user.kyc_documents.filter(d => d.status === 'pending').map(doc => (
                                        <div key={doc.id} className="flex justify-between items-center p-3 border rounded-md">
                                            <div>
                                                <p><strong>Type:</strong> {doc.document_type.toUpperCase()}</p>
                                                <p className="text-sm text-muted-foreground">File: {doc.file_storage_key}</p>
                                            </div>
                                            <div className="flex gap-2">
                                                <Button size="sm" variant="outline" onClick={() => approveMutation.mutate(doc.id)}>Approve</Button>
                                                <Button size="sm" variant="destructive" onClick={() => handleReject(doc.id)}>Reject</Button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </AccordionContent>
                        </AccordionItem>
                    ))}
                </Accordion>
            )}
        </CardContent>
      </Card>
    </div>
  );
}

export default KycVerificationPage;
