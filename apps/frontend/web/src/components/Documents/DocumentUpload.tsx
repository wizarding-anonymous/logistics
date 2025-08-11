import React, { useState } from 'react';
import { useUploadDocument } from '@/hooks/useDocs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export function DocumentUpload({ entityType, entityId, documentType }: { entityType: string; entityId: string; documentType: string }) {
  const [file, setFile] = useState<File | null>(null);
  const uploadMutation = useUploadDocument();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = () => {
    if (file) {
      uploadMutation.mutate({ entityType, entityId, file, documentType });
    }
  };

  return (
    <div className="mt-6 border-t pt-6">
      <h4 className="text-lg font-medium mb-2">Upload New Document</h4>
      <div className="flex w-full max-w-sm items-center space-x-2">
        <Input id="file-upload" type="file" onChange={handleFileChange} />
        <Button onClick={handleUpload} disabled={!file || uploadMutation.isPending}>
          {uploadMutation.isPending ? 'Uploading...' : 'Upload'}
        </Button>
      </div>
      {uploadMutation.isSuccess && <p className="text-sm text-green-600 mt-2">Upload successful!</p>}
      {uploadMutation.isError && <p className="text-sm text-red-600 mt-2">Upload failed: {uploadMutation.error.message}</p>}
    </div>
  );
}
