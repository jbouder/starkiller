import { Database, FileSpreadsheet } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { DataSource } from "@/lib/types/api";

interface DataSourceCardProps {
  dataSource: DataSource;
  onClick: (dataSource: DataSource) => void;
}

export function LegacyDataSourceCard({ dataSource, onClick }: DataSourceCardProps) {
  const Icon = dataSource.source_type === "postgresql" ? Database : FileSpreadsheet;
  const badgeVariant = dataSource.source_type === "postgresql" ? "default" : "secondary";

  const tableCount = dataSource.schema_info?.tables?.length;
  const columnCount = dataSource.schema_info?.columns?.length;

  return (
    <Card
      className="cursor-pointer transition-colors hover:bg-accent"
      onClick={() => onClick(dataSource)}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <Icon className="h-5 w-5 text-muted-foreground" />
            <CardTitle className="text-lg">{dataSource.name}</CardTitle>
          </div>
          <Badge variant={badgeVariant}>{dataSource.source_type}</Badge>
        </div>
        {dataSource.description && (
          <CardDescription className="line-clamp-2">{dataSource.description}</CardDescription>
        )}
      </CardHeader>
      <CardContent>
        <div className="text-sm text-muted-foreground">
          {tableCount !== undefined && (
            <span>{tableCount} {tableCount === 1 ? "table" : "tables"}</span>
          )}
          {columnCount !== undefined && (
            <span>{columnCount} {columnCount === 1 ? "column" : "columns"}</span>
          )}
          {tableCount === undefined && columnCount === undefined && (
            <span>Schema not loaded</span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
