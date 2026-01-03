import { apiClient } from "./client";
import type { PaginatedResponse } from "./clients";

export interface Document {
  id: string;
  title: string;
  slug: string;
  topic: string;
  status: "draft" | "generating" | "ready" | "distributed" | "failed";
  pdf_url: string | null;
  cover_image_url: string | null;
  word_count: number | null;
  page_count: number | null;
  statistics_count: number | null;
  sources_count: number | null;
  template_id: string | null;
  agency_id: string;
  client_id: string;
  created_by_id: string | null;
  expires_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentUpdate {
  title?: string;
  status?: string;
}

export const documentsApi = {
  list: async (
    page = 1,
    perPage = 20,
    clientId?: string,
    status?: string
  ): Promise<PaginatedResponse<Document>> => {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString(),
    });
    if (clientId) params.append("client_id", clientId);
    if (status) params.append("status", status);

    const response = await apiClient.get(`/documents?${params}`);
    return response.data;
  },

  get: async (id: string): Promise<Document> => {
    const response = await apiClient.get(`/documents/${id}`);
    return response.data;
  },

  update: async (id: string, data: DocumentUpdate): Promise<Document> => {
    const response = await apiClient.patch(`/documents/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/documents/${id}`);
  },

  download: async (id: string): Promise<Blob> => {
    const response = await apiClient.get(`/documents/${id}/download`, {
      responseType: "blob",
    });
    return response.data;
  },
};
