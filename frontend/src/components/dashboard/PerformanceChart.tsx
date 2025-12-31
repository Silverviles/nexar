import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart3 } from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const data = [
  { name: "Mon", quantum: 24, classical: 18, hybrid: 8 },
  { name: "Tue", quantum: 28, classical: 22, hybrid: 12 },
  { name: "Wed", quantum: 32, classical: 19, hybrid: 15 },
  { name: "Thu", quantum: 26, classical: 25, hybrid: 10 },
  { name: "Fri", quantum: 35, classical: 20, hybrid: 18 },
  { name: "Sat", quantum: 22, classical: 15, hybrid: 8 },
  { name: "Sun", quantum: 18, classical: 12, hybrid: 6 },
];

export function PerformanceChart() {
  return (
    <Card variant="glass" className="col-span-2">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-primary" />
          Weekly Routing Distribution
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[250px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="quantumGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(187, 100%, 50%)" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="hsl(187, 100%, 50%)" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="classicalGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(280, 60%, 55%)" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="hsl(280, 60%, 55%)" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="hybridGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(142, 76%, 45%)" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="hsl(142, 76%, 45%)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="hsl(222, 30%, 18%)"
                vertical={false}
              />
              <XAxis
                dataKey="name"
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
