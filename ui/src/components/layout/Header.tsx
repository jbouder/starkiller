import { Sparkles } from "lucide-react";
import { QueryInput } from "@/components/query/QueryInput";

interface HeaderProps {
  selectedDataSourceId: string | null;
  dataSourceName?: string;
}

export function Header({ selectedDataSourceId, dataSourceName }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center gap-4">
        <div className="flex items-center gap-2">
          <Sparkles className="h-6 w-6 text-primary" />
          <span className="text-xl font-bold">Starkiller</span>
        </div>
        <div className="flex-1 max-w-2xl">
          <QueryInput
            selectedDataSourceId={selectedDataSourceId}
            dataSourceName={dataSourceName}
          />
        </div>
      </div>
    </header>
  );
}
