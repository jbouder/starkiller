// Dashboard types matching backend schemas

import type { DataSource } from "./api";

export interface Dashboard {
  id: string;
  title: string;
  description: string | null;
  data_sources: DataSource[];
  created_at: string;
  updated_at: string;
}

// API returns array directly for list endpoint
export type DashboardListResponse = Dashboard[];

// Generation types matching api/schemas/generation.py

export interface VisualizationPreferences {
  chart_types?: ("line" | "bar" | "pie" | "area" | "scatter" | "composed")[];
  color_scheme?: string;
  layout?: "grid" | "stacked" | "single";
}

export interface GenerateRequest {
  query?: string;
  visualization_preferences?: VisualizationPreferences;
}

export interface GeneratedComponent {
  name: string;
  chart_type: string;
  description: string;
  data_keys: string[];
}

export interface GeneratedQuery {
  data_source_id: string;
  data_source_name: string;
  query: string;
  query_type: string;
  row_count: number;
}

export interface GenerateResponse {
  dashboard_id: string;
  dashboard_title: string;
  react_code: string;
  components: GeneratedComponent[];
  data_sources_used: string[];
  queries_generated: GeneratedQuery[];
  sample_data: Record<string, unknown>;
  execution_time_ms: number;
  metadata: Record<string, unknown>;
}
