import { ArrowLeft, Clock, Database, BarChart3, Code } from "lucide-react";
import { LiveProvider, LivePreview, LiveError } from "react-live";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";
import type { GenerateResponse } from "@/lib/types/dashboard";
import { prepareCodeForExecution, createScope } from "./DynamicDashboardScope";

interface DynamicDashboardProps {
  generatedDashboard: GenerateResponse | null;
  isLoading: boolean;
  error: Error | null;
  onBack: () => void;
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Skeleton className="h-10 w-24" />
        <Skeleton className="h-8 w-48" />
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <Skeleton className="h-24" />
        <Skeleton className="h-24" />
        <Skeleton className="h-24" />
      </div>
      <Skeleton className="h-[400px]" />
    </div>
  );
}

export function DynamicDashboard({
  generatedDashboard,
  isLoading,
  error,
  onBack,
}: DynamicDashboardProps) {
  if (isLoading) {
    return (
      <div className="space-y-6">
        <Button variant="ghost" onClick={onBack} className="gap-2">
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboards
        </Button>
        <LoadingSkeleton />
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <Button variant="ghost" onClick={onBack} className="gap-2">
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboards
        </Button>
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Generation Failed</AlertTitle>
          <AlertDescription>{error.message}</AlertDescription>
        </Alert>
      </div>
    );
  }

  if (!generatedDashboard) {
    return null;
  }

  const { dashboard_title, react_code, components, data_sources_used, execution_time_ms, sample_data } =
    generatedDashboard;

  const preparedCode = prepareCodeForExecution(react_code);
  const scope = createScope(sample_data);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={onBack} className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back
          </Button>
          <h1 className="text-2xl font-bold">{dashboard_title}</h1>
        </div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Clock className="h-4 w-4" />
          <span>{execution_time_ms}ms</span>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Data Sources</CardDescription>
            <CardTitle className="text-2xl flex items-center gap-2">
              <Database className="h-5 w-5" />
              {data_sources_used.length}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Components</CardDescription>
            <CardTitle className="text-2xl flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              {components.length}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Generated Code</CardDescription>
            <CardTitle className="text-2xl flex items-center gap-2">
              <Code className="h-5 w-5" />
              {react_code.split("\n").length} lines
            </CardTitle>
          </CardHeader>
        </Card>
      </div>

      {components.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {components.map((component) => (
            <Badge key={component.name} variant="outline">
              {component.chart_type}: {component.name}
            </Badge>
          ))}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Generated Visualization</CardTitle>
          <CardDescription>
            Dynamically rendered from AI-generated React code
          </CardDescription>
        </CardHeader>
        <CardContent>
          <LiveProvider code={preparedCode} scope={scope} noInline>
            <div className="min-h-[400px]">
              <LivePreview />
            </div>
            <LiveError className="mt-4 p-4 bg-destructive/10 text-destructive rounded-md text-sm font-mono" />
          </LiveProvider>
        </CardContent>
      </Card>
    </div>
  );
}
