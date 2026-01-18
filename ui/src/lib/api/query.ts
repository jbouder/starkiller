import type { QueryRequest, QueryResponse } from "@/lib/types/api";
import { apiClient } from "./client";

export async function executeQuery(request: QueryRequest): Promise<QueryResponse> {
  return apiClient.post<QueryResponse>("/query", request);
}

export async function getQuery(id: string): Promise<QueryResponse> {
  return apiClient.get<QueryResponse>(`/query/${id}`);
}
