/* ------------------------------------------------------------------ */
/*  Core domain types – mirrors the backend Pydantic schemas          */
/* ------------------------------------------------------------------ */

// ---- Job ----

export interface JobSource {
  id: string;
  platform: string;
  url: string;
  posted_at: string | null;
  indexed_at: string;
}

export interface JobBrief {
  id: string;
  title: string;
  company_name: string;
  company_logo: string | null;
  location: string;
  work_mode: "remote" | "hybrid" | "onsite";
  job_type: "full_time" | "part_time" | "contract" | "internship";
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string;
  skills: string[];
  source_count: number;
  posted_at: string;
  slug: string;
}

export interface JobDetail extends JobBrief {
  description: string;
  ai_summary: string | null;
  experience_min: number | null;
  experience_max: number | null;
  apply_mode: "redirect" | "direct";
  apply_url: string | null;
  sources: JobSource[];
  company_slug: string;
}

export type Job = JobBrief;

// ---- Company ----

export interface CompanyBrief {
  id: string;
  name: string;
  slug: string;
  logo: string | null;
  industry: string | null;
  location: string | null;
  job_count: number;
}

export interface CompanyDetail extends CompanyBrief {
  description: string | null;
  website: string | null;
  career_page_url: string | null;
  employee_count: string | null;
  founded_year: number | null;
  ats_platform: string | null;
}

export type Company = CompanyBrief;

// ---- User ----

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  role: "user" | "hr" | "admin";
}

export interface UserProfile extends User {
  phone: string | null;
  resume_url: string | null;
  preferred_locations: string[];
  preferred_roles: string[];
  created_at: string;
}

// ---- Job Alert ----

export interface JobAlert {
  id: string;
  name: string;
  query: string | null;
  location: string | null;
  job_type: string | null;
  work_mode: string | null;
  skills: string[];
  frequency: "daily" | "weekly" | "instant";
  is_active: boolean;
  created_at: string;
}

export interface CreateAlertPayload {
  name: string;
  query?: string;
  location?: string;
  job_type?: string;
  work_mode?: string;
  skills?: string[];
  frequency: "daily" | "weekly" | "instant";
}

export interface UpdateAlertPayload extends Partial<CreateAlertPayload> {
  is_active?: boolean;
}

// ---- Search ----

export interface SearchParams {
  q?: string;
  location?: string;
  job_type?: string;
  work_mode?: string;
  experience_min?: number;
  experience_max?: number;
  salary_min?: number;
  skills?: string;
  sort_by?: "relevance" | "date" | "salary";
  page?: number;
  page_size?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export type SearchResponse = PaginatedResponse<JobBrief>;

// ---- Auth ----

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// ---- HR ----

export interface RegisterCompanyPayload {
  company_name: string;
  career_page_url: string;
  ats_platform: string;
  feed_url?: string;
  contact_email: string;
  contact_name: string;
}
