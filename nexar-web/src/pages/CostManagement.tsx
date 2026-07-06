import { Wallet, TrendingDown, AlertCircle, Bell, Lightbulb, TrendingUp, Target, PieChart, BarChart3 } from 'lucide-react'
import { MainLayout } from '@/components/layout/MainLayout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart as RechartsPieChart, Pie, Cell } from 'recharts'

const monthlyData = [
  { month: 'Aug', quantum: 1200, classical: 450, hybrid: 320 },
  { month: 'Sep', quantum: 1450, classical: 520, hybrid: 410 },
  { month: 'Oct', quantum: 1680, classical: 480, hybrid: 380 },
  { month: 'Nov', quantum: 1520, classical: 510, hybrid: 450 },
  { month: 'Dec', quantum: 1890, classical: 540, hybrid: 520 },
  { month: 'Jan', quantum: 1650, classical: 490, hybrid: 480 },
]

const pieData = [
  { name: 'Quantum', value: 1650, color: '#0f62fe' },
  { name: 'Classical', value: 490, color: '#525252' },
  { name: 'Hybrid', value: 480, color: '#24a148' },
]

const alerts = [
  { type: 'warning', message: 'Quantum spending approaching 80% of monthly budget', time: '2h ago' },
  { type: 'info', message: 'New cost-saving opportunity: Batch similar jobs', time: '5h ago' },
  { type: 'success', message: 'Achieved 15% cost reduction vs. last month', time: '1d ago' },
]

export default function CostManagement() {
  const totalBudget = 5000
  const currentSpend = 2620
  const remaining = totalBudget - currentSpend
  const percentUsed = (currentSpend / totalBudget) * 100

  return (
    <MainLayout title="Cost Management" description="Budget tracking and cost optimization">
      <div className="space-y-4 md:space-y-6">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 md:gap-4 lg:grid-cols-4">
          <Card variant="glow" className="md:col-span-2">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2">
                <Wallet className="h-5 w-5 text-primary" />
                Monthly Budget
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-end justify-between">
                  <div>
                    <p className="text-3xl font-semibold font-mono text-ink">${currentSpend.toLocaleString()}</p>
                    <p className="text-sm text-ink-muted">of ${totalBudget.toLocaleString()} budget</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xl font-semibold font-mono text-success">${remaining.toLocaleString()}</p>
                    <p className="text-sm text-ink-muted">remaining</p>
                  </div>
                </div>
                <Progress value={percentUsed} className="h-3" />
                <div className="flex justify-between text-xs text-ink-muted">
                  <span>{percentUsed.toFixed(1)}% used</span>
                  <span>17 days left in cycle</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card variant="glass">
            <CardContent className="p-5">
              <div className="flex h-10 w-10 items-center justify-center bg-success/10">
                <TrendingDown className="h-5 w-5 text-success" />
              </div>
              <p className="mt-3 text-sm text-ink-muted">Cost Savings</p>
              <p className="font-mono text-2xl font-semibold text-success">$847</p>
              <p className="text-xs text-ink-muted">This month vs. last</p>
            </CardContent>
          </Card>

          <Card variant="glass">
            <CardContent className="p-5">
              <div className="flex h-10 w-10 items-center justify-center bg-primary/10">
                <Target className="h-5 w-5 text-primary" />
              </div>
              <p className="mt-3 text-sm text-ink-muted">Avg Cost/Execution</p>
              <p className="font-mono text-2xl font-semibold text-ink">$0.24</p>
              <p className="text-xs text-success">↓ 12% from last month</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <Card variant="glass" className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-primary" />
                Monthly Spending Breakdown
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={monthlyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" vertical={false} />
                    <XAxis dataKey="month" stroke="#8c8c8c" fontSize={12} tickLine={false} />
                    <YAxis stroke="#8c8c8c" fontSize={12} tickLine={false} tickFormatter={(v) => `$${v}`} />
                    <Tooltip contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #e0e0e0', borderRadius: 0 }} formatter={(value) => [`$${value}`, '']} />
                    <Bar dataKey="quantum" fill="#0f62fe" />
                    <Bar dataKey="classical" fill="#525252" />
                    <Bar dataKey="hybrid" fill="#24a148" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
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

          <Card variant="glass">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PieChart className="h-5 w-5 text-primary" />
                Current Month Distribution
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <RechartsPieChart>
                    <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={2} dataKey="value">
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #e0e0e0', borderRadius: 0 }} formatter={(value) => [`$${value}`, '']} />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-2 mt-4">
                {pieData.map((item) => (
                  <div key={item.name} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full" style={{ backgroundColor: item.color }} />
                      <span className="text-ink">{item.name}</span>
                    </div>
                    <span className="font-mono text-ink">${item.value}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card variant="glass">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5 text-ink" />
                Budget Alerts
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {alerts.map((alert, index) => (
                <div
                  key={index}
                  className={`flex items-start gap-3 border p-3 ${
                    alert.type === 'warning' ? 'border-warning/50 bg-warning/10' : alert.type === 'success' ? 'border-success/40 bg-success/5' : 'border-hairline bg-surface-1'
                  }`}
                >
                  {alert.type === 'warning' ? (
                    <AlertCircle className="h-4 w-4 text-ink mt-0.5" />
                  ) : alert.type === 'success' ? (
                    <TrendingUp className="h-4 w-4 text-success mt-0.5" />
                  ) : (
                    <Lightbulb className="h-4 w-4 text-primary mt-0.5" />
                  )}
                  <div className="flex-1">
                    <p className="text-sm text-ink">{alert.message}</p>
                    <p className="text-xs text-ink-muted mt-1">{alert.time}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card variant="glass">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-primary" />
                Cost-Saving Opportunities
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="border border-primary/30 bg-primary/5 p-4">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-ink">Batch Similar Jobs</span>
                  <Badge variant="success">Save ~$120/mo</Badge>
                </div>
                <p className="mt-1 text-sm text-ink-muted">Group similar quantum computations to reduce queue overhead</p>
                <Button variant="outline" size="sm" className="mt-3">
                  Learn More
                </Button>
              </div>
              <div className="border border-hairline bg-surface-1 p-4">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-ink">Off-Peak Scheduling</span>
                  <Badge variant="outline">Save ~$85/mo</Badge>
                </div>
                <p className="mt-1 text-sm text-ink-muted">Schedule non-urgent jobs during off-peak hours</p>
                <Button variant="outline" size="sm" className="mt-3">
                  Configure
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  )
}
