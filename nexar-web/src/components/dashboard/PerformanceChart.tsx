import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart3, Loader2 } from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface ChartDataPoint {
  day: string
  quantum: number
  classical: number
  hybrid: number
}

interface PerformanceChartProps {
  data: ChartDataPoint[]
  isLoading: boolean
}

export function PerformanceChart({ data, isLoading }: PerformanceChartProps) {
  const hasData = data.some((d) => d.quantum > 0 || d.classical > 0 || d.hybrid > 0)

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
            <span className="ml-2 text-sm text-ink-muted">Loading...</span>
          </div>
        ) : !hasData ? (
          <div className="flex items-center justify-center h-[250px] text-sm text-ink-muted">
            No routing data yet. Make predictions to see the distribution chart.
          </div>
        ) : (
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="quantumGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0f62fe" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#0f62fe" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="classicalGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#525252" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#525252" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="hybridGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#24a148" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#24a148" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" vertical={false} />
                <XAxis dataKey="day" stroke="#8c8c8c" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#8c8c8c" fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e0e0e0',
                    borderRadius: 0,
                    fontSize: '12px',
                  }}
                  labelStyle={{ color: '#161616' }}
                />
                <Area type="monotone" dataKey="quantum" stroke="#0f62fe" strokeWidth={2} fillOpacity={1} fill="url(#quantumGradient)" />
                <Area type="monotone" dataKey="classical" stroke="#525252" strokeWidth={2} fillOpacity={1} fill="url(#classicalGradient)" />
                <Area type="monotone" dataKey="hybrid" stroke="#24a148" strokeWidth={2} fillOpacity={1} fill="url(#hybridGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
        <div className="mt-4 flex justify-center gap-6">
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-quantum" />
            <span className="text-xs text-ink-muted">Quantum</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-classical" />
            <span className="text-xs text-ink-muted">Classical</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-hybrid" />
            <span className="text-xs text-ink-muted">Hybrid</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
