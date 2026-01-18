import type { ApiError } from "@/lib/types/api";

const API_BASE_URL = "/api/v1";

export class ApiClientError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = "ApiClientError";
    this.status = status;
    this.detail = detail;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail = "An unexpected error occurred";
    try {
      const error: ApiError = await response.json();
      detail = error.detail;
    } catch {
      detail = response.statusText || detail;
    }
    throw new ApiClientError(response.status, detail);
  }
  return response.json();
}

export async function get<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  return handleResponse<T>(response);
}

export async function post<T, B = unknown>(endpoint: string, body: B): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  return handleResponse<T>(response);
}

export const apiClient = {
  get,
  post,
};
