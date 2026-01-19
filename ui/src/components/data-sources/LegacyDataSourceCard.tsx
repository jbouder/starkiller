import { Database } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { DataSource } from "@/lib/types/api";

interface DataSourceCardProps {
  dataSource: DataSource;
  onClick: (dataSource: DataSource) => void;
}

export function LegacyDataSourceCard({ dataSource, onClick }: DataSourceCardProps) {
  const tableCount = dataSource.schema_info?.tables?.length;

  return (
    <Card
      className="cursor-pointer transition-colors hover:bg-accent"
      onClick={() => onClick(dataSource)}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <Database className="h-5 w-5 text-muted-foreground" />
            <CardTitle className="text-lg">{dataSource.name}</CardTitle>
          </div>
          <Badge variant="default">{dataSource.source_type}</Badge>
        </div>
        {dataSource.description && (
          <CardDescription className="line-clamp-2">{dataSource.description}</CardDescription>
        )}
      </CardHeader>
      <CardContent>
        <div className="text-sm text-muted-foreground">
          {tableCount !== undefined ? (
            <span>{tableCount} {tableCount === 1 ? "table" : "tables"}</span>
          ) : (
            <span>Schema not loaded</span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
