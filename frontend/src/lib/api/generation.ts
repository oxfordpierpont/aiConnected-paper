import { apiClient } from "./client";

export interface GenerationRequest {
  topic: string;
  client_id: string;
  template_id?: string;
  tone?: string;
  keywords?: string[];
  services?: string[];
  custom_direction?: string;
  auto_distribute?: boolean;
  distribution_platforms?: string[];
}

export interface GenerationStatus {
  job_id: string;
  document_id: string;
  status: string;
  current_step: string | null;
  progress_percent: number;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

export interface GenerationJob {
  id: string;
  document_id: string;
  status: string;
  current_step: string | null;
  progress_percent: number;
  steps: Record<string, unknown> | null;
  started_at: string | null;
  completed_at: string | null;
  tokens_used: number | null;
  api_cost: number | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export const generationApi = {
  generate: async (data: GenerationRequest): Promise<GenerationStatus> => {
    const response = await apiClient.post("/generation/generate", data);
    return response.data;
  },

  getJob: async (jobId: string): Promise<GenerationJob> => {
    const response = await apiClient.get(`/generation/jobs/${jobId}`);
    return response.data;
  },

  cancelJob: async (jobId: string): Promise<void> => {
    await apiClient.post(`/generation/jobs/${jobId}/cancel`);
  },

  retryJob: async (jobId: string): Promise<void> => {
    await apiClient.post(`/generation/jobs/${jobId}/retry`);
  },
};
