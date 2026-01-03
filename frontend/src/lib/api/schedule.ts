import { apiClient } from "./client";
import type { PaginatedResponse } from "./clients";

export interface ScheduledContent {
  id: string;
  topic: string;
  scheduled_date: string;
  status: "pending" | "processing" | "completed" | "failed";
  client_id: string;
  template_id: string | null;
  document_id: string | null;
  auto_distribute: boolean;
  distribution_platforms: string[] | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface ScheduleCreate {
  topic: string;
  scheduled_date: string;
  client_id: string;
  template_id?: string;
  auto_distribute?: boolean;
  distribution_platforms?: string[];
}

export interface ScheduleUpdate {
  topic?: string;
  scheduled_date?: string;
  template_id?: string;
  auto_distribute?: boolean;
}

export const scheduleApi = {
  list: async (
    page = 1,
    perPage = 20,
    clientId?: string
  ): Promise<PaginatedResponse<ScheduledContent>> => {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString(),
    });
    if (clientId) params.append("client_id", clientId);

    const response = await apiClient.get(`/schedule?${params}`);
    return response.data;
  },

  get: async (id: string): Promise<ScheduledContent> => {
    const response = await apiClient.get(`/schedule/${id}`);
    return response.data;
  },

  create: async (data: ScheduleCreate): Promise<ScheduledContent> => {
    const response = await apiClient.post("/schedule", data);
    return response.data;
  },

  update: async (id: string, data: ScheduleUpdate): Promise<ScheduledContent> => {
    const response = await apiClient.patch(`/schedule/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/schedule/${id}`);
  },
};
