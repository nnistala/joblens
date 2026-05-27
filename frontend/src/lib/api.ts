import axios from "axios";
import type {
  AuthResponse,
  CompanyBrief,
  CompanyDetail,
  CreateAlertPayload,
  JobAlert,
  JobBrief,
  JobDetail,
  LoginPayload,
  PaginatedResponse,
  RegisterCompanyPayload,
  RegisterPayload,
  SearchParams,
  SearchResponse,
  UpdateAlertPayload,
  User,
} from "@/types";

/* ------------------------------------------------------------------ */
/*  Axios instance                                                     */
/* ------------------------------------------------------------------ */

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
  headers: { "Content-Type": "application/json" },
});

// Attach the auth token on every request when available (client-side only)
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("joblens_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

/* ------------------------------------------------------------------ */
/*  Jobs                                                               */
/* ------------------------------------------------------------------ */

export async function searchJobs(params: SearchParams): Promise<SearchResponse> {
  const { data } = await api.get<SearchResponse>("/jobs", { params });
  return data;
}

export async function getJob(id: string): Promise<JobDetail> {
  const { data } = await api.get<JobDetail>(`/jobs/${id}`);
  return data;
}

/* ------------------------------------------------------------------ */
/*  Companies                                                          */
/* ------------------------------------------------------------------ */

export async function getCompanies(
  params?: { page?: number; page_size?: number; q?: string }
): Promise<PaginatedResponse<CompanyBrief>> {
  const { data } = await api.get<PaginatedResponse<CompanyBrief>>("/companies", { params });
  return data;
}

export async function getCompany(slug: string): Promise<CompanyDetail> {
  const { data } = await api.get<CompanyDetail>(`/companies/${slug}`);
  return data;
}

/* ------------------------------------------------------------------ */
/*  Auth                                                               */
/* ------------------------------------------------------------------ */

export async function login(payload: LoginPayload): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>("/auth/login", payload);
  return data;
}

export async function register(payload: RegisterPayload): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>("/auth/register", payload);
  return data;
}

export async function googleAuth(credential: string): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>("/auth/google", { credential });
  return data;
}

export async function getMe(): Promise<User> {
  const { data } = await api.get<User>("/auth/me");
  return data;
}

/* ------------------------------------------------------------------ */
/*  Saved jobs                                                         */
/* ------------------------------------------------------------------ */

export async function getSavedJobs(
  params?: { page?: number; page_size?: number }
): Promise<PaginatedResponse<JobBrief>> {
  const { data } = await api.get<PaginatedResponse<JobBrief>>("/saved-jobs", { params });
  return data;
}

export async function saveJob(jobId: string): Promise<void> {
  await api.post(`/saved-jobs/${jobId}`);
}

export async function unsaveJob(jobId: string): Promise<void> {
  await api.delete(`/saved-jobs/${jobId}`);
}

/* ------------------------------------------------------------------ */
/*  Alerts                                                             */
/* ------------------------------------------------------------------ */

export async function getAlerts(): Promise<JobAlert[]> {
  const { data } = await api.get<JobAlert[]>("/alerts");
  return data;
}

export async function createAlert(payload: CreateAlertPayload): Promise<JobAlert> {
  const { data } = await api.post<JobAlert>("/alerts", payload);
  return data;
}

export async function updateAlert(
  id: string,
  payload: UpdateAlertPayload
): Promise<JobAlert> {
  const { data } = await api.patch<JobAlert>(`/alerts/${id}`, payload);
  return data;
}

export async function deleteAlert(id: string): Promise<void> {
  await api.delete(`/alerts/${id}`);
}

/* ------------------------------------------------------------------ */
/*  HR / Company registration                                          */
/* ------------------------------------------------------------------ */

export async function registerCompany(
  payload: RegisterCompanyPayload
): Promise<{ message: string }> {
  const { data } = await api.post<{ message: string }>("/hr/register", payload);
  return data;
}

export default api;
