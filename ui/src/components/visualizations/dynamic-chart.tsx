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
} from "recharts";
import type { ChartType, ChartConfig, QueryResultData } from "@/lib/types/api";

interface DynamicChartProps {
  chartType: ChartType;
  chartConfig: ChartConfig;
  data: QueryResultData;
}

const CHART_COLORS = [
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
];

function getSeriesColor(index: number, configColor?: string): string {
  if (configColor) return configColor;
  return CHART_COLORS[index % CHART_COLORS.length];
}

export function DynamicChart({ chartType, chartConfig, data }: DynamicChartProps) {
  const { x_axis, y_axis, series, legend = true, tooltip = true, grid = true } = chartConfig;

  const commonAxisProps = {
    tick: { fill: "hsl(var(--muted-foreground))" },
    axisLine: { stroke: "hsl(var(--border))" },
    tickLine: { stroke: "hsl(var(--border))" },
  };

  const renderXAxis = () => (
    <XAxis
      dataKey={x_axis.data_key}
      label={x_axis.label ? { value: x_axis.label, position: "bottom" } : undefined}
      type={x_axis.type === "number" ? "number" : "category"}
      {...commonAxisProps}
    />
  );

  const renderYAxis = () => (
    <YAxis
      label={y_axis?.label ? { value: y_axis.label, angle: -90, position: "insideLeft" } : undefined}
      type={y_axis?.type === "number" ? "number" : "number"}
      {...commonAxisProps}
    />
  );

  const renderGrid = () => grid && <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />;
  const renderTooltip = () => tooltip && <Tooltip contentStyle={{ backgroundColor: "hsl(var(--popover))", border: "1px solid hsl(var(--border))", borderRadius: "var(--radius)" }} />;
  const renderLegend = () => legend && <Legend />;

  switch (chartType) {
    case "line":
      return (
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={data.rows}>
            {renderGrid()}
            {renderXAxis()}
            {renderYAxis()}
            {renderTooltip()}
            {renderLegend()}
            {series.map((s, i) => (
              <Line
                key={s.data_key}
                type="monotone"
                dataKey={s.data_key}
                name={s.name || s.data_key}
                stroke={getSeriesColor(i, s.color)}
                strokeWidth={2}
                dot={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      );

    case "bar":
      return (
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={data.rows}>
            {renderGrid()}
            {renderXAxis()}
            {renderYAxis()}
            {renderTooltip()}
            {renderLegend()}
            {series.map((s, i) => (
              <Bar
                key={s.data_key}
                dataKey={s.data_key}
                name={s.name || s.data_key}
                fill={getSeriesColor(i, s.color)}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      );

    case "pie":
      return (
        <ResponsiveContainer width="100%" height={400}>
          <PieChart>
            {renderTooltip()}
            {renderLegend()}
            <Pie
              data={data.rows}
              dataKey={series[0]?.data_key || "value"}
              nameKey={x_axis.data_key}
              cx="50%"
              cy="50%"
              outerRadius={150}
              label
            >
              {data.rows.map((_, index) => (
                <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      );

    case "area":
      return (
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={data.rows}>
            {renderGrid()}
            {renderXAxis()}
            {renderYAxis()}
            {renderTooltip()}
            {renderLegend()}
            {series.map((s, i) => (
              <Area
                key={s.data_key}
                type="monotone"
                dataKey={s.data_key}
                name={s.name || s.data_key}
                stroke={getSeriesColor(i, s.color)}
                fill={getSeriesColor(i, s.color)}
                fillOpacity={0.3}
              />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      );

    case "scatter":
      return (
        <ResponsiveContainer width="100%" height={400}>
          <ScatterChart>
            {renderGrid()}
            {renderXAxis()}
            {renderYAxis()}
            {renderTooltip()}
            {renderLegend()}
            {series.map((s, i) => (
              <Scatter
                key={s.data_key}
                name={s.name || s.data_key}
                data={data.rows}
                fill={getSeriesColor(i, s.color)}
              />
            ))}
          </ScatterChart>
        </ResponsiveContainer>
      );

    case "composed":
      return (
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart data={data.rows}>
            {renderGrid()}
            {renderXAxis()}
            {renderYAxis()}
            {renderTooltip()}
            {renderLegend()}
            {series.map((s, i) => {
              const color = getSeriesColor(i, s.color);
              switch (s.type) {
                case "bar":
                  return (
                    <Bar
                      key={s.data_key}
                      dataKey={s.data_key}
                      name={s.name || s.data_key}
                      fill={color}
                    />
                  );
                case "area":
                  return (
                    <Area
                      key={s.data_key}
                      type="monotone"
                      dataKey={s.data_key}
                      name={s.name || s.data_key}
                      stroke={color}
                      fill={color}
                      fillOpacity={0.3}
                    />
                  );
                case "line":
                default:
                  return (
                    <Line
                      key={s.data_key}
                      type="monotone"
                      dataKey={s.data_key}
                      name={s.name || s.data_key}
                      stroke={color}
                      strokeWidth={2}
                    />
                  );
              }
            })}
          </ComposedChart>
        </ResponsiveContainer>
      );

    default:
      return <div className="text-muted-foreground">Unknown chart type: {chartType}</div>;
  }
}
