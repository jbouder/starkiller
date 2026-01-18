// TypeScript types mirroring backend schemas

// Data Source Types
export type SourceType = "csv" | "postgresql";

export interface ConnectionConfig {
  file_path?: string;
  host?: string;
  port?: number;
  database?: string;
  username?: string;
  password?: string;
  ssl_mode?: string;
}

export interface SchemaColumn {
  name: string;
  data_type: string;
  nullable: boolean;
}

export interface SchemaTable {
  name: string;
  columns: SchemaColumn[];
}

export interface SchemaInfo {
  tables?: SchemaTable[];
  columns?: SchemaColumn[];
}

export interface DataSource {
  id: string;
  name: string;
  description: string | null;
  source_type: SourceType;
  schema_info: SchemaInfo | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DataSourceListResponse {
  items: DataSource[];
  total: number;
}

// Visualization Types
export type ChartType = "line" | "bar" | "pie" | "area" | "scatter" | "composed";

export interface AxisConfig {
  data_key: string;
  label?: string;
  type?: "number" | "category";
}

export interface SeriesConfig {
  data_key: string;
  name?: string;
  color?: string;
  type?: "line" | "bar" | "area";
}

export interface ChartConfig {
  x_axis: AxisConfig;
  y_axis?: AxisConfig;
  series: SeriesConfig[];
  legend?: boolean;
  tooltip?: boolean;
  grid?: boolean;
}

export interface DataConfig {
  aggregation?: string;
  group_by?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  limit?: number;
}

export interface Visualization {
  id: string;
  title: string;
  description: string | null;
  chart_type: ChartType;
  chart_config: ChartConfig;
  data_config: DataConfig;
  is_saved: boolean;
  query_id: string;
  created_at: string;
  updated_at: string;
}

// Query Types
export type QueryStatus = "pending" | "processing" | "completed" | "failed";

export interface QueryRequest {
  query: string;
  data_source_id?: string;
}

export interface QueryResultData {
  columns: string[];
  rows: Record<string, unknown>[];
  row_count: number;
}

export interface QueryResponse {
  id: string;
  natural_language_query: string;
  generated_query: string | null;
  query_type: string;
  status: QueryStatus;
  result_data: QueryResultData | null;
  error_message: string | null;
  execution_time_ms: number | null;
  data_source_id: string | null;
  visualization: Visualization | null;
  created_at: string;
  updated_at: string;
}

// API Error
export interface ApiError {
  detail: string;
}
