import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { QueryResultData } from "@/lib/types/api";

interface DataTableProps {
  data: QueryResultData;
}

export function DataTable({ data }: DataTableProps) {
  const { columns, rows, row_count } = data;

  if (rows.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No data to display
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              {columns.map((column) => (
                <TableHead key={column}>{column}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((row, rowIndex) => (
              <TableRow key={rowIndex}>
                {columns.map((column) => (
                  <TableCell key={column}>
                    {formatCellValue(row[column])}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      <p className="text-sm text-muted-foreground">
        Showing {rows.length} of {row_count} rows
      </p>
    </div>
  );
}

function formatCellValue(value: unknown): string {
  if (value === null || value === undefined) return "-";
  if (typeof value === "number") {
    return Number.isInteger(value) ? value.toString() : value.toFixed(2);
  }
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (value instanceof Date) return value.toLocaleDateString();
  return String(value);
}
