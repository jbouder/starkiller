import { AlertCircle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { DataSourceCard } from "./DataSourceCard";
import type { DataSource } from "@/lib/types/api";

interface DataSourceGridProps {
  dataSources: DataSource[];
  isLoading: boolean;
  error: Error | null;
  onDataSourceClick: (dataSource: DataSource) => void;
}

function DataSourceCardSkeleton() {
  return (
    <div className="rounded-lg border bg-card p-6">
      <div className="flex items-start justify-between pb-3">
        <div className="flex items-center gap-2">
          <Skeleton className="h-5 w-5" />
          <Skeleton className="h-6 w-32" />
        </div>
        <Skeleton className="h-5 w-20" />
      </div>
      <Skeleton className="h-4 w-full mb-4" />
      <Skeleton className="h-4 w-24" />
    </div>
  );
}

export function DataSourceGrid({
  dataSources,
  isLoading,
  error,
  onDataSourceClick,
}: DataSourceGridProps) {
  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>
          Failed to load data sources: {error.message}
        </AlertDescription>
      </Alert>
    );
  }

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <DataSourceCardSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (dataSources.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <p className="text-lg font-medium text-muted-foreground">No data sources found</p>
        <p className="text-sm text-muted-foreground">
          Connect a data source to get started
        </p>
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {dataSources.map((dataSource) => (
        <DataSourceCard
          key={dataSource.id}
          dataSource={dataSource}
          onClick={onDataSourceClick}
        />
      ))}
    </div>
  );
}
