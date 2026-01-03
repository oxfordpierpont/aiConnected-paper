// API response types

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

// User types
export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  agency_id: string | null;
  created_at: string;
  updated_at: string;
}

export type UserRole = "super_admin" | "agency_admin" | "agency_member" | "client";

// Agency types
export interface Agency {
  id: string;
  name: string;
  slug: string;
  subdomain: string;
  custom_domain: string | null;
  website: string | null;
  logo_url: string | null;
  primary_color: string;
  secondary_color: string;
  is_active: boolean;
  plan_id: string | null;
  created_at: string;
  updated_at: string;
}

// Client types
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

// Document types
export interface Document {
  id: string;
  title: string;
  slug: string;
  topic: string;
  status: DocumentStatus;
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

export type DocumentStatus = "draft" | "generating" | "ready" | "distributed" | "failed";

// Template types
export interface Template {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  preview_url: string | null;
  is_public: boolean;
  is_pro: boolean;
  is_active: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
}

// Generation types
export interface GenerationJob {
  id: string;
  document_id: string;
  status: GenerationStatus;
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

export type GenerationStatus =
  | "pending"
  | "researching"
  | "writing"
  | "rendering"
  | "completed"
  | "failed";
