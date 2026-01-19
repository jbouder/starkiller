import { AlertCircle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { DynamicChart } from "./dynamic-chart";
import { DataTable } from "./data-table";
import { ResultHeader } from "@/components/query/result-header";
import type { QueryResponse, ChartConfig } from "@/lib/types/api";

interface VisualizationViewProps {
  queryResult: QueryResponse | null;
  isLoading: boolean;
  error: Error | null;
  dataSourceName?: string;
  onBack: () => void;
}

function VisualizationSkeleton() {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-4 w-96" />
      </div>
      <div className="flex gap-2">
        <Skeleton className="h-6 w-24" />
        <Skeleton className="h-6 w-16" />
        <Skeleton className="h-6 w-20" />
      </div>
      <Skeleton className="h-[400px] w-full" />
      <Skeleton className="h-48 w-full" />
    </div>
  );
}

export function VisualizationView({
  queryResult,
  isLoading,
  error,
  dataSourceName,
  onBack,
}: VisualizationViewProps) {
  if (isLoading) {
    return <VisualizationSkeleton />;
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Query Failed</AlertTitle>
        <AlertDescription>{error.message}</AlertDescription>
      </Alert>
    );
  }

  if (!queryResult) {
    return null;
  }

  if (queryResult.status === "failed") {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Query Failed</AlertTitle>
        <AlertDescription>
          {queryResult.error_message || "An unknown error occurred"}
        </AlertDescription>
      </Alert>
    );
  }

  const { visualization, result_data } = queryResult;

  return (
    <div className="space-y-6">
      <ResultHeader
        queryResult={queryResult}
        dataSourceName={dataSourceName}
        onBack={onBack}
      />

      {visualization && result_data && (
        <Card>
          <CardHeader>
            <CardTitle>Visualization</CardTitle>
          </CardHeader>
          <CardContent>
            <DynamicChart
              chartType={visualization.chart_type}
              chartConfig={visualization.chart_config as ChartConfig}
              data={result_data}
            />
          </CardContent>
        </Card>
      )}

      {result_data && (
        <Card>
          <CardHeader>
            <CardTitle>Data</CardTitle>
          </CardHeader>
          <CardContent>
            <DataTable data={result_data} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
