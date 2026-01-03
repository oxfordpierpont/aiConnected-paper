import { apiClient } from "./client";

export interface LoginRequest {
  email: string;
  password: string;
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
}

export const authApi = {
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const response = await apiClient.post("/auth/login", data);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post("/auth/logout");
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
