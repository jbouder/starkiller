import { useState, useCallback } from "react";
import type { GenerateRequest, GenerateResponse } from "@/lib/types/dashboard";
import { generateDashboard } from "@/lib/api/dashboards";
import { ApiClientError } from "@/lib/api/client";

interface UseDashboardGenerationResult {
  generatedDashboard: GenerateResponse | null;
  isGenerating: boolean;
  error: Error | null;
  generate: (dashboardId: string, request?: GenerateRequest) => Promise<void>;
  clear: () => void;
}

export function useDashboardGeneration(): UseDashboardGenerationResult {
  const [generatedDashboard, setGeneratedDashboard] = useState<GenerateResponse | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const generate = useCallback(async (dashboardId: string, request?: GenerateRequest) => {
    setIsGenerating(true);
    setError(null);
    setGeneratedDashboard(null);
    try {
      const response = await generateDashboard(dashboardId, request);
      setGeneratedDashboard(response);
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(err);
      } else {
        setError(new Error("Failed to generate dashboard"));
      }
    } finally {
      setIsGenerating(false);
    }
  }, []);

  const clear = useCallback(() => {
    setGeneratedDashboard(null);
    setError(null);
  }, []);

  return {
    generatedDashboard,
    isGenerating,
    error,
    generate,
    clear,
  };
}
