import React, { useState, useEffect, useMemo, useCallback } from "react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  AreaChart,
  Area,
  ScatterChart,
  Scatter,
  ComposedChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  RadialBarChart,
  RadialBar,
  Treemap,
  Funnel,
  FunnelChart,
} from "recharts";

// All Recharts components available to generated code
export const rechartsScope = {
  // Charts
  LineChart,
  BarChart,
  PieChart,
  AreaChart,
  ScatterChart,
  ComposedChart,
  RadialBarChart,
  FunnelChart,
  Treemap,
  // Chart elements
  Line,
  Bar,
  Pie,
  Area,
  Scatter,
  Cell,
  RadialBar,
  Funnel,
  // Axes and grid
  XAxis,
  YAxis,
  CartesianGrid,
  // Utilities
  Tooltip,
  Legend,
  ResponsiveContainer,
};

// Chart colors matching the theme
export const CHART_COLORS = [
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
];

/**
 * Prepares generated React code for execution with react-live.
 * Strips imports, exports, and require statements since dependencies are provided via scope.
 */
export function prepareCodeForExecution(code: string): string {
  let prepared = code;

  // Remove import statements (single and multi-line)
  prepared = prepared.replace(/import\s+.*?from\s+['"][^'"]+['"];?\s*/g, "");
  prepared = prepared.replace(/import\s+['"][^'"]+['"];?\s*/g, "");
  prepared = prepared.replace(/import\s*\{[^}]*\}\s*from\s*['"][^'"]+['"];?\s*/g, "");

  // Remove require statements
  prepared = prepared.replace(/const\s+\{[^}]*\}\s*=\s*require\s*\(['"][^'"]+['"]\);?\s*/g, "");
  prepared = prepared.replace(/const\s+\w+\s*=\s*require\s*\(['"][^'"]+['"]\);?\s*/g, "");
  prepared = prepared.replace(/require\s*\(['"][^'"]+['"]\);?\s*/g, "");

  // Remove export statements
  prepared = prepared.replace(/export\s+default\s+/g, "");
  prepared = prepared.replace(/export\s+/g, "");

  // Remove any "use client" or "use server" directives
  prepared = prepared.replace(/['"]use client['"];?\s*/g, "");
  prepared = prepared.replace(/['"]use server['"];?\s*/g, "");

  // Clean up multiple blank lines
  prepared = prepared.replace(/\n{3,}/g, "\n\n").trim();

  // Find the main component name to render
  // Look for function declarations or arrow functions assigned to a const
  const functionMatch = prepared.match(/function\s+([A-Z]\w*)\s*\(/);
  const constMatch = prepared.match(/const\s+([A-Z]\w*)\s*=\s*(?:\([^)]*\)|[^=])*=>/);
  const componentName = functionMatch?.[1] || constMatch?.[1];

  if (componentName) {
    // Add a render call at the end
    prepared = `${prepared}\n\nrender(<${componentName} />);`;
  }

  return prepared;
}

/**
 * Creates the complete scope object for react-live,
 * including React, Recharts components, and sample data.
 */
export function createScope(sampleData: Record<string, unknown>) {
  return {
    // React core
    React,
    useState,
    useEffect,
    useMemo,
    useCallback,
    // Recharts components
    ...rechartsScope,
    // Colors
    COLORS: CHART_COLORS,
    // Data - available under multiple names for flexibility
    data: sampleData,
    sample_data: sampleData,
    sampleData: sampleData,
  };
}
