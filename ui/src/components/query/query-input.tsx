import { useState, type FormEvent } from "react";
import { Send, Loader2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useQuery } from "@/context/query-context";

interface QueryInputProps {
  selectedDataSourceId: string | null;
  dataSourceName?: string;
}

export function QueryInput({ selectedDataSourceId, dataSourceName }: QueryInputProps) {
  const [inputValue, setInputValue] = useState("");
  const { executeQuery, isExecuting } = useQuery();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || !selectedDataSourceId || isExecuting) return;

    await executeQuery(inputValue.trim(), selectedDataSourceId);
    setInputValue("");
  };

  const placeholder = selectedDataSourceId
    ? `Ask about ${dataSourceName || "your data"}...`
    : "Select a data source first";

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <Input
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        placeholder={placeholder}
        disabled={!selectedDataSourceId || isExecuting}
        className="flex-1"
      />
      <Button
        type="submit"
        size="icon"
        disabled={!inputValue.trim() || !selectedDataSourceId || isExecuting}
      >
        {isExecuting ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Send className="h-4 w-4" />
        )}
      </Button>
    </form>
  );
}
