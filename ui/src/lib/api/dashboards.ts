import type {
  Dashboard,
  DashboardListResponse,
  GenerateRequest,
  GenerateResponse,
} from "@/lib/types/dashboard";
import { apiClient } from "./client";

export async function getDashboards(): Promise<DashboardListResponse> {
  return apiClient.get<DashboardListResponse>("/dashboards");
}

export async function getDashboard(id: string): Promise<Dashboard> {
  return apiClient.get<Dashboard>(`/dashboards/${id}`);
}

export async function generateDashboard(
  id: string,
  request?: GenerateRequest
): Promise<GenerateResponse> {
  return apiClient.post<GenerateResponse, GenerateRequest | Record<string, never>>(
    `/dashboards/${id}/generate`,
    request ?? {}
  );
}
