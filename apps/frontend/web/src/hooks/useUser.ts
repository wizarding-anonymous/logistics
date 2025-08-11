import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMyKycDocuments, submitKycDocument } from '@/services/userService'; // Assuming these will be in a new userService

// We need to create userService.ts and add the functions there.
// For now, let's define the hooks assuming the service exists.

export function useKycDocuments() {
  return useQuery({
    queryKey: ['kycDocuments'],
    queryFn: getMyKycDocuments,
  });
}

export function useSubmitKycDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (formData: { document_type: string; file_storage_key: string }) => submitKycDocument(formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['kycDocuments'] });
    },
  });
}
