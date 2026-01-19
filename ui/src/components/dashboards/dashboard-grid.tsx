import { AlertCircle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { DashboardCard } from "./dashboard-card";
import type { Dashboard } from "@/lib/types/dashboard";

interface DashboardGridProps {
  dashboards: Dashboard[];
  isLoading: boolean;
  error: Error | null;
  onDashboardClick: (dashboard: Dashboard) => void;
}

function DashboardCardSkeleton() {
  return (
    <div className="rounded-lg border bg-card p-6">
      <div className="flex items-start justify-between pb-3">
        <div className="flex items-center gap-2">
          <Skeleton className="h-5 w-5" />
          <Skeleton className="h-6 w-32" />
        </div>
        <Skeleton className="h-5 w-12" />
      </div>
      <Skeleton className="h-4 w-full mb-4" />
      <Skeleton className="h-4 w-24" />
    </div>
  );
}

export function DashboardGrid({
  dashboards,
  isLoading,
  error,
  onDashboardClick,
}: DashboardGridProps) {
  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>
          Failed to load dashboards: {error.message}
        </AlertDescription>
      </Alert>
    );
  }

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <DashboardCardSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (dashboards.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <p className="text-lg font-medium text-muted-foreground">No dashboards found</p>
        <p className="text-sm text-muted-foreground">
          Create a dashboard to get started
        </p>
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {dashboards.map((dashboard) => (
        <DashboardCard
          key={dashboard.id}
          dashboard={dashboard}
          onClick={onDashboardClick}
        />
      ))}
    </div>
  );
}
