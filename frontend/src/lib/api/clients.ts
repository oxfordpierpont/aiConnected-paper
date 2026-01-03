import { apiClient } from "./client";

export interface Client {
  id: string;
  name: string;
  slug: string;
  industry: string | null;
  website: string | null;
  location: string | null;
  description: string | null;
  logo_url: string | null;
  services: string[] | null;
  keywords: string[] | null;
  tone: string;
  is_active: boolean;
  agency_id: string;
  created_at: string;
  updated_at: string;
}

export interface ClientCreate {
  name: string;
  industry?: string;
  website?: string;
  location?: string;
  description?: string;
  services?: string[];
  keywords?: string[];
  tone?: string;
}

export interface ClientUpdate {
  name?: string;
  industry?: string;
  website?: string;
  location?: string;
  description?: string;
  logo_url?: string;
  services?: string[];
  keywords?: string[];
  tone?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export const clientsApi = {
  list: async (
    page = 1,
    perPage = 20,
    search?: string
  ): Promise<PaginatedResponse<Client>> => {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString(),
    });
    if (search) params.append("search", search);

    const response = await apiClient.get(`/clients?${params}`);
    return response.data;
  },

  get: async (id: string): Promise<Client> => {
    const response = await apiClient.get(`/clients/${id}`);
    return response.data;
  },

  create: async (data: ClientCreate): Promise<Client> => {
    const response = await apiClient.post("/clients", data);
    return response.data;
  },

  update: async (id: string, data: ClientUpdate): Promise<Client> => {
    const response = await apiClient.patch(`/clients/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/clients/${id}`);
  },
};
