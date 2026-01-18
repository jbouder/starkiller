import type { DataSource, DataSourceListResponse } from "@/lib/types/api";
import { apiClient } from "./client";

export async function getDataSources(activeOnly = true): Promise<DataSourceListResponse> {
  const params = activeOnly ? "?active_only=true" : "";
  return apiClient.get<DataSourceListResponse>(`/data-sources${params}`);
}

export async function getDataSource(id: string): Promise<DataSource> {
  return apiClient.get<DataSource>(`/data-sources/${id}`);
}
