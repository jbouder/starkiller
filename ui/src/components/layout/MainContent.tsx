import { DashboardGrid } from "@/components/dashboards/DashboardGrid";
import { DynamicDashboard } from "@/components/dynamic/DynamicDashboard";
import { useDashboards } from "@/hooks/useDashboards";
import { useDashboardGeneration } from "@/hooks/useDashboardGeneration";
import type { Dashboard } from "@/lib/types/dashboard";

export function MainContent() {
  const { dashboards, isLoading, error } = useDashboards();
  const {
    generatedDashboard,
    isGenerating,
    error: generationError,
    generate,
    clear,
  } = useDashboardGeneration();

  const showGeneratedDashboard =
    generatedDashboard !== null || isGenerating || generationError !== null;

  const handleDashboardClick = async (dashboard: Dashboard) => {
    await generate(dashboard.id);
  };

  if (showGeneratedDashboard) {
    return (
      <main className="container py-6">
        <DynamicDashboard
          generatedDashboard={generatedDashboard}
          isLoading={isGenerating}
          error={generationError}
          onBack={clear}
        />
      </main>
    );
  }

  return (
    <main className="container py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Dashboards</h1>
        <p className="text-muted-foreground">
          Select a dashboard to generate visualizations
        </p>
      </div>
      <DashboardGrid
        dashboards={dashboards}
        isLoading={isLoading}
        error={error}
        onDashboardClick={handleDashboardClick}
      />
    </main>
  );
}
