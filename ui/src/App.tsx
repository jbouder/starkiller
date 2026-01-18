import { useState, useCallback } from "react";
import { ThemeProvider } from "@/components/theme-provider";
import { QueryProvider, useQuery } from "@/context/QueryContext";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { Header } from "@/components/layout/Header";
import { MainContent } from "@/components/layout/MainContent";
import { useDataSources } from "@/hooks/useDataSources";
import type { DataSource } from "@/lib/types/api";

const DEFAULT_QUERY = "Show me an overview of this data";

function AppContent() {
  const [selectedDataSourceId, setSelectedDataSourceId] = useState<string | null>(null);
  const [selectedDataSourceName, setSelectedDataSourceName] = useState<string | undefined>();
  const { dataSources } = useDataSources();
  const { executeQuery } = useQuery();

  const handleDataSourceSelect = useCallback(
    async (dataSource: DataSource) => {
      setSelectedDataSourceId(dataSource.id);
      setSelectedDataSourceName(dataSource.name);
      await executeQuery(DEFAULT_QUERY, dataSource.id);
    },
    [executeQuery]
  );

  // Update selected data source name if data sources change
  const currentDataSource = dataSources.find((ds) => ds.id === selectedDataSourceId);
  const dataSourceName = currentDataSource?.name || selectedDataSourceName;

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header
        selectedDataSourceId={selectedDataSourceId}
        dataSourceName={dataSourceName}
      />
      <MainContent
        onDataSourceSelect={handleDataSourceSelect}
        selectedDataSourceId={selectedDataSourceId}
      />
    </div>
  );
}

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="starkiller-theme">
      <ErrorBoundary>
        <QueryProvider>
          <AppContent />
        </QueryProvider>
      </ErrorBoundary>
    </ThemeProvider>
  );
}

export default App;
