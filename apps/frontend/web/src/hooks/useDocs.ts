import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listDocuments, getUploadUrl, confirmUpload } from '@/services/docsService';
import axios from 'axios';

export function useDocuments(entityType: string, entityId: string) {
  return useQuery({
    queryKey: ['documents', entityType, entityId],
    queryFn: () => listDocuments(entityType, entityId),
    enabled: !!entityType && !!entityId,
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (variables: { entityType: string; entityId: string; file: File; documentType: string }) => {
      const { entityType, entityId, file, documentType } = variables;

      // Step 1: Get a pre-signed URL from our backend
      const { upload_url, s3_path } = await getUploadUrl(entityType, entityId, file.name);

      // Step 2: Upload the file directly to S3/MinIO using the pre-signed URL
      // We use a plain axios PUT request here, not the API client with interceptors
      await axios.put(upload_url, file, {
        headers: {
          'Content-Type': file.type,
        },
      });

      // Step 3: Confirm the upload with our backend
      return await confirmUpload({
        s3_path,
        entity_type: entityType,
        entity_id: entityId,
        document_type: documentType,
        filename: file.name,
      });
    },
    onSuccess: (data) => {
      // When a document is uploaded, invalidate the list of documents for that entity
      queryClient.invalidateQueries({ queryKey: ['documents', data.related_entity_type, data.related_entity_id] });
    },
  });
}
