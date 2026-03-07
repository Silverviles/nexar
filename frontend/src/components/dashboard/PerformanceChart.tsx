import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart3, Loader2 } from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface ChartDataPoint {
  day: string;
  quantum: number;
  classical: number;
  hybrid: number;
}

interface PerformanceChartProps {
  data: ChartDataPoint[];
  isLoading: boolean;
}

export function PerformanceChart({ data, isLoading }: PerformanceChartProps) {
  const hasData = data.some(
    (d) => d.quantum > 0 || d.classical > 0 || d.hybrid > 0,
  );

  return (
    <Card variant="glass" className="col-span-2">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-primary" />
          Weekly Routing Distribution
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center h-[250px]">
            <Loader2 className="h-6 w-6 animate-spin text-primary" />
            <span className="ml-2 text-sm text-muted-foreground">
              Loading...
            </span>
          </div>
        ) : !hasData ? (
          <div className="flex items-center justify-center h-[250px] text-sm text-muted-foreground">
            No routing data yet. Make predictions to see the distribution chart.
          </div>
        ) : (
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={data}
                margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
              >
                <defs>
                  <linearGradient
                    id="quantumGradient"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop
                      offset="5%"
                      stopColor="hsl(187, 100%, 50%)"
                      stopOpacity={0.4}
                    />
                    <stop
                      offset="95%"
                      stopColor="hsl(187, 100%, 50%)"
                      stopOpacity={0}
                    />
                  </linearGradient>
                  <linearGradient
                    id="classicalGradient"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop
                      offset="5%"
                      stopColor="hsl(280, 60%, 55%)"
                      stopOpacity={0.4}
                    />
                    <stop
                      offset="95%"
                      stopColor="hsl(280, 60%, 55%)"
                      stopOpacity={0}
                    />
                  </linearGradient>
                  <linearGradient
                    id="hybridGradient"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop
                      offset="5%"
                      stopColor="hsl(142, 76%, 45%)"
                      stopOpacity={0.4}
                    />
                    <stop
                      offset="95%"
                      stopColor="hsl(142, 76%, 45%)"
                      stopOpacity={0}
                    />
                  </linearGradient>
                </defs>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="hsl(222, 30%, 18%)"
                  vertical={false}
                />
                <XAxis
                  dataKey="day"
                  stroke="hsl(215, 20%, 55%)"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  stroke="hsl(215, 20%, 55%)"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                  allowDecimals={false}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(222, 47%, 8%)",
                    border: "1px solid hsl(222, 30%, 18%)",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                  labelStyle={{ color: "hsl(210, 40%, 98%)" }}
                />
                <Area
                  type="monotone"
                  dataKey="quantum"
                  stroke="hsl(187, 100%, 50%)"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#quantumGradient)"
                />
                <Area
                  type="monotone"
                  dataKey="classical"
                  stroke="hsl(280, 60%, 55%)"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#classicalGradient)"
                />
                <Area
                  type="monotone"
                  dataKey="hybrid"
                  stroke="hsl(142, 76%, 45%)"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#hybridGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
        <div className="mt-4 flex justify-center gap-6">
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-quantum" />
            <span className="text-xs text-muted-foreground">Quantum</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-classical" />
            <span className="text-xs text-muted-foreground">Classical</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-hybrid" />
            <span className="text-xs text-muted-foreground">Hybrid</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
