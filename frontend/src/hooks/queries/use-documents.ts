import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { documentsApi, type DocumentUpdate } from "@/lib/api/documents";
import { toast } from "sonner";

export function useDocuments(
  page = 1,
  perPage = 20,
  clientId?: string,
  status?: string
) {
  return useQuery({
    queryKey: ["documents", page, perPage, clientId, status],
    queryFn: () => documentsApi.list(page, perPage, clientId, status),
  });
}

export function useDocument(id: string) {
  return useQuery({
    queryKey: ["document", id],
    queryFn: () => documentsApi.get(id),
    enabled: !!id,
  });
}

export function useUpdateDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: DocumentUpdate }) =>
      documentsApi.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      queryClient.invalidateQueries({ queryKey: ["document", id] });
      toast.success("Document updated successfully");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to update document");
    },
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => documentsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      toast.success("Document deleted successfully");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to delete document");
    },
  });
}

export function useDownloadDocument() {
  return useMutation({
    mutationFn: async (id: string) => {
      const blob = await documentsApi.download(id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `document-${id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to download document");
    },
  });
}
