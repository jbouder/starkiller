import { LayoutDashboard, Database } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Dashboard } from "@/lib/types/dashboard";

interface DashboardCardProps {
  dashboard: Dashboard;
  onClick: (dashboard: Dashboard) => void;
}

export function DashboardCard({ dashboard, onClick }: DashboardCardProps) {
  const dataSourceCount = dashboard.data_sources.length;

  return (
    <Card
      className="cursor-pointer transition-colors hover:bg-accent"
      onClick={() => onClick(dashboard)}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <LayoutDashboard className="h-5 w-5 text-muted-foreground" />
            <CardTitle className="text-lg">{dashboard.title}</CardTitle>
          </div>
          <Badge variant="secondary">
            <Database className="h-3 w-3 mr-1" />
            {dataSourceCount}
          </Badge>
        </div>
        {dashboard.description && (
          <CardDescription className="line-clamp-2">{dashboard.description}</CardDescription>
        )}
      </CardHeader>
      <CardContent>
        <div className="text-sm text-muted-foreground">
          {dataSourceCount === 0 ? (
            <span>No data sources</span>
          ) : (
            <span>
              {dashboard.data_sources.map((ds) => ds.name).join(", ")}
            </span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
