import { Clock, Database, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { QueryResponse } from "@/lib/types/api";

interface ResultHeaderProps {
  queryResult: QueryResponse;
  dataSourceName?: string;
  onBack: () => void;
}

export function ResultHeader({ queryResult, dataSourceName, onBack }: ResultHeaderProps) {
  const { visualization, execution_time_ms, result_data } = queryResult;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={onBack}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold">
            {visualization?.title || "Query Results"}
          </h1>
          {visualization?.description && (
            <p className="text-muted-foreground">{visualization.description}</p>
          )}
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        {dataSourceName && (
          <Badge variant="outline" className="gap-1">
            <Database className="h-3 w-3" />
            {dataSourceName}
          </Badge>
        )}
        {execution_time_ms !== null && (
          <Badge variant="outline" className="gap-1">
            <Clock className="h-3 w-3" />
            {execution_time_ms}ms
          </Badge>
        )}
        {result_data && (
          <Badge variant="secondary">
            {result_data.row_count} rows
          </Badge>
        )}
        {visualization && (
          <Badge>{visualization.chart_type} chart</Badge>
        )}
      </div>
    </div>
  );
}
