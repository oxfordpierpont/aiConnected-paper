import { apiClient } from "./client";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  agency_name?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  agency_id: string | null;
  is_active: boolean;
  is_verified: boolean;
}

export interface AgencyStats {
  total_clients: number;
  total_documents: number;
  documents_this_month: number;
  scheduled_content: number;
}

export const authApi = {
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const response = await apiClient.post("/auth/login", data);
    return response.data;
  },

  register: async (data: RegisterRequest): Promise<TokenResponse> => {
    const response = await apiClient.post("/auth/register", data);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post("/auth/logout");
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get("/auth/me");
    return response.data;
  },

  refreshToken: async (refreshToken: string): Promise<TokenResponse> => {
    const response = await apiClient.post("/auth/refresh", {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  requestPasswordReset: async (email: string): Promise<void> => {
    await apiClient.post("/auth/password-reset", { email });
  },

  confirmPasswordReset: async (token: string, newPassword: string): Promise<void> => {
    await apiClient.post("/auth/password-reset/confirm", {
      token,
      new_password: newPassword,
    });
  },
};

export const agencyApi = {
  getStats: async (): Promise<AgencyStats> => {
    const response = await apiClient.get("/agencies/me/stats");
    return response.data;
  },

  getCurrent: async () => {
    const response = await apiClient.get("/agencies/me");
    return response.data;
  },

  update: async (data: Record<string, unknown>) => {
    const response = await apiClient.patch("/agencies/me", data);
    return response.data;
  },
};
