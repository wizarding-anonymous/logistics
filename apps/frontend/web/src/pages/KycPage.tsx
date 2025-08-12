import React, { useState } from 'react';
import { useKycDocuments, useSubmitKycDocument } from '@/hooks/useUser';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

function KycPage() {
  const { data: documents, isLoading, isError, error } = useKycDocuments();
  const submitDocument = useSubmitKycDocument();
  const [docType, setDocType] = useState('inn');
  const [fileKey, setFileKey] = useState(''); // This would come from a file upload service

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real app, you'd upload a file to S3/MinIO and get a key back.
    // We'll use a mock key.
    const mockFileKey = `kyc-docs/${docType}-${new Date().getTime()}.pdf`;
    submitDocument.mutate({ document_type: docType, file_storage_key: mockFileKey });
  };

  const getStatusClass = (status: string) => {
    switch (status) {
        case 'approved': return 'bg-green-100 text-green-800';
        case 'pending': return 'bg-yellow-100 text-yellow-800';
        case 'rejected': return 'bg-red-100 text-red-800';
        default: return 'bg-gray-100 text-gray-800';
    }
  }

  return (
    <div className="space-y-6 p-4 md:p-6 max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold tracking-tight">KYC Verification</h2>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
            <Card>
                <CardHeader>
                    <CardTitle>Submitted Documents</CardTitle>
                    <CardDescription>Here is a list of documents you have submitted for verification.</CardDescription>
                </CardHeader>
                <CardContent>
                    {isLoading && <p>Loading documents...</p>}
                    {isError && <p className="text-red-500">Error: {error.message}</p>}
                    {!isLoading && !isError && (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Document Type</TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead>Uploaded At</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {documents?.map((doc) => (
                                    <TableRow key={doc.id}>
                                        <TableCell className="font-medium uppercase">{doc.document_type}</TableCell>
                                        <TableCell>
                                            <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusClass(doc.status)}`}>
                                                {doc.status}
                                            </span>
                                        </TableCell>
                                        <TableCell>{new Date(doc.uploaded_at).toLocaleDateString()}</TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>
        </div>
        <div>
            <Card>
                <CardHeader>
                    <CardTitle>Upload New Document</CardTitle>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="doc-type">Document Type</Label>
                            <select id="doc-type" value={docType} onChange={(e) => setDocType(e.target.value)} className="w-full p-2 border rounded-md">
                                <option value="inn">ИНН</option>
                                <option value="ogrn">ОГРН</option>
                                <option value="passport">Passport</option>
                            </select>
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="file-upload">File</Label>
                            <Input id="file-upload" type="file" required />
                        </div>
                        <Button type="submit" className="w-full" disabled={submitDocument.isPending}>
                            {submitDocument.isPending ? 'Uploading...' : 'Upload Document'}
                        </Button>
                        {submitDocument.isSuccess && <p className="text-sm text-green-600">Document uploaded successfully!</p>}
                    </form>
                </CardContent>
            </Card>
        </div>
      </div>
    </div>
  );
}

export default KycPage;
