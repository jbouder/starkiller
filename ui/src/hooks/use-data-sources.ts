import { useState, useEffect, useCallback } from "react";
import type { DataSource } from "@/lib/types/api";
import { getDataSources } from "@/lib/api/data-sources";
import { ApiClientError } from "@/lib/api/client";

interface UseDataSourcesResult {
  dataSources: DataSource[];
  isLoading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useDataSources(): UseDataSourcesResult {
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchDataSources = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getDataSources();
      setDataSources(response.items);
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(err);
      } else {
        setError(new Error("Failed to fetch data sources"));
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDataSources();
  }, [fetchDataSources]);

  return {
    dataSources,
    isLoading,
    error,
    refetch: fetchDataSources,
  };
}
