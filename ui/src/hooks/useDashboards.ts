import { useState, useEffect, useCallback } from "react";
import type { Dashboard } from "@/lib/types/dashboard";
import { getDashboards } from "@/lib/api/dashboards";
import { ApiClientError } from "@/lib/api/client";

interface UseDashboardsResult {
  dashboards: Dashboard[];
  isLoading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useDashboards(): UseDashboardsResult {
  const [dashboards, setDashboards] = useState<Dashboard[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchDashboards = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getDashboards();
      setDashboards(response);
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(err);
      } else {
        setError(new Error("Failed to fetch dashboards"));
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboards();
  }, [fetchDashboards]);

  return {
    dashboards,
    isLoading,
    error,
    refetch: fetchDashboards,
  };
}
