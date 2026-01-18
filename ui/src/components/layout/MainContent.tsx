import { DataSourceGrid } from "@/components/data-sources/DataSourceGrid";
import { VisualizationView } from "@/components/visualizations/VisualizationView";
import { useQuery } from "@/context/QueryContext";
import { useDataSources } from "@/hooks/useDataSources";
import type { DataSource } from "@/lib/types/api";

interface MainContentProps {
  onDataSourceSelect: (dataSource: DataSource) => void;
  selectedDataSourceId: string | null;
}

export function MainContent({ onDataSourceSelect, selectedDataSourceId }: MainContentProps) {
  const { dataSources, isLoading, error } = useDataSources();
  const { queryResult, isExecuting, error: queryError, clearQuery } = useQuery();

  const selectedDataSource = dataSources.find((ds) => ds.id === selectedDataSourceId);
  const showVisualization = queryResult !== null || isExecuting || queryError !== null;

  if (showVisualization) {
    return (
      <main className="container py-6">
        <VisualizationView
          queryResult={queryResult}
          isLoading={isExecuting}
          error={queryError}
          dataSourceName={selectedDataSource?.name}
          onBack={clearQuery}
        />
      </main>
    );
  }

  return (
    <main className="container py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Data Sources</h1>
        <p className="text-muted-foreground">
          Select a data source to explore your data
        </p>
      </div>
      <DataSourceGrid
        dataSources={dataSources}
        isLoading={isLoading}
        error={error}
        onDataSourceClick={onDataSourceSelect}
      />
    </main>
  );
}
