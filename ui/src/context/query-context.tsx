import { createContext, useContext, useState, useCallback, type ReactNode } from "react";
import type { QueryResponse } from "@/lib/types/api";
import { executeQuery } from "@/lib/api/query";
import { ApiClientError } from "@/lib/api/client";

interface QueryState {
  currentQuery: string | null;
  queryResult: QueryResponse | null;
  selectedDataSourceId: string | null;
  isExecuting: boolean;
  error: Error | null;
  executeQuery: (query: string, dataSourceId: string) => Promise<void>;
  clearQuery: () => void;
}

const QueryContext = createContext<QueryState | null>(null);

interface QueryProviderProps {
  children: ReactNode;
}

export function QueryProvider({ children }: QueryProviderProps) {
  const [currentQuery, setCurrentQuery] = useState<string | null>(null);
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null);
  const [selectedDataSourceId, setSelectedDataSourceId] = useState<string | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const handleExecuteQuery = useCallback(async (query: string, dataSourceId: string) => {
    setCurrentQuery(query);
    setSelectedDataSourceId(dataSourceId);
    setIsExecuting(true);
    setError(null);
    setQueryResult(null);

    try {
      const result = await executeQuery({
        query,
        data_source_id: dataSourceId,
      });
      setQueryResult(result);
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(err);
      } else {
        setError(new Error("Failed to execute query"));
      }
    } finally {
      setIsExecuting(false);
    }
  }, []);

  const clearQuery = useCallback(() => {
    setCurrentQuery(null);
    setQueryResult(null);
    setSelectedDataSourceId(null);
    setError(null);
  }, []);

  return (
    <QueryContext.Provider
      value={{
        currentQuery,
        queryResult,
        selectedDataSourceId,
        isExecuting,
        error,
        executeQuery: handleExecuteQuery,
        clearQuery,
      }}
    >
      {children}
    </QueryContext.Provider>
  );
}

export function useQuery() {
  const context = useContext(QueryContext);
  if (!context) {
    throw new Error("useQuery must be used within a QueryProvider");
  }
  return context;
}
