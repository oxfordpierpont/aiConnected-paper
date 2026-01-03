import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { clientsApi, type ClientCreate, type ClientUpdate } from "@/lib/api/clients";
import { toast } from "sonner";

export function useClients(page = 1, perPage = 20, search?: string) {
  return useQuery({
    queryKey: ["clients", page, perPage, search],
    queryFn: () => clientsApi.list(page, perPage, search),
  });
}

export function useClient(id: string) {
  return useQuery({
    queryKey: ["client", id],
    queryFn: () => clientsApi.get(id),
    enabled: !!id,
  });
}

export function useCreateClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ClientCreate) => clientsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      toast.success("Client created successfully");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to create client");
    },
  });
}

export function useUpdateClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ClientUpdate }) =>
      clientsApi.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      queryClient.invalidateQueries({ queryKey: ["client", id] });
      toast.success("Client updated successfully");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to update client");
    },
  });
}

export function useDeleteClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => clientsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      toast.success("Client deleted successfully");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to delete client");
    },
  });
}
