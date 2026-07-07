import { Brain, BarChart, Star, Database, Calendar, RefreshCw, TestTube } from 'lucide-react'
import { MainLayout } from '@/components/layout/MainLayout'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

const models = [
  { name: 'Random Forest', version: 'v2.3.1', accuracy: 91.2, precision: 89.5, recall: 92.8, f1Score: 91.1, lastTrained: '2024-01-10', status: 'active' },
  { name: 'XGBoost', version: 'v1.8.0', accuracy: 93.5, precision: 92.1, recall: 94.2, f1Score: 93.1, lastTrained: '2024-01-12', status: 'active' },
  { name: 'Neural Network', version: 'v3.1.2', accuracy: 92.8, precision: 91.4, recall: 93.6, f1Score: 92.5, lastTrained: '2024-01-08', status: 'active' },
]

const featureImportance = [
  { feature: 'Algorithm Pattern', importance: 0.28 },
  { feature: 'Qubit Requirements', importance: 0.22 },
  { feature: 'Complexity Score', importance: 0.18 },
  { feature: 'Data Size', importance: 0.15 },
  { feature: 'Gate Count', importance: 0.1 },
  { feature: 'Entanglement Depth', importance: 0.07 },
]

export default function MLModels() {
  return (
    <MainLayout title="ML Model Management" description="Monitor and manage machine learning models">
      <div className="space-y-4 md:space-y-6">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 md:gap-4 lg:grid-cols-3">
          {models.map((model) => (
            <Card key={model.name} variant="glass" className="hover:border-primary/40 transition-colors">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Brain className="h-4 w-4 text-primary" />
                    {model.name}
                  </CardTitle>
                  <Badge variant="success">{model.status}</Badge>
                </div>
                <CardDescription>Version {model.version}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm">
                      <span className="text-ink-muted">Accuracy</span>
                      <span className="font-mono font-medium text-ink">{model.accuracy}%</span>
                    </div>
                    <Progress value={model.accuracy} className="h-2 mt-1" />
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-center text-xs">
                    <div>
                      <p className="text-ink-muted">Precision</p>
                      <p className="font-mono font-medium text-ink">{model.precision}%</p>
                    </div>
                    <div>
                      <p className="text-ink-muted">Recall</p>
                      <p className="font-mono font-medium text-ink">{model.recall}%</p>
                    </div>
                    <div>
                      <p className="text-ink-muted">F1</p>
                      <p className="font-mono font-medium text-ink">{model.f1Score}%</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 text-xs text-ink-muted pt-2 border-t border-hairline">
                    <Calendar className="h-3 w-3" />
                    Last trained: {model.lastTrained}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card variant="glass">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Star className="h-5 w-5 text-ink" />
                Feature Importance
              </CardTitle>
              <CardDescription>Top factors influencing routing decisions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {featureImportance.map((item) => (
                  <div key={item.feature}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-ink">{item.feature}</span>
                      <span className="font-mono text-ink-muted">{(item.importance * 100).toFixed(0)}%</span>
                    </div>
                    <div className="h-2 bg-surface-2 overflow-hidden">
                      <div className="h-full bg-primary" style={{ width: `${item.importance * 100}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card variant="glass">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5 text-primary" />
                Training Status
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="border border-hairline bg-surface-1 p-3">
                  <p className="text-sm text-ink-muted">Training Dataset</p>
                  <p className="font-mono text-lg font-semibold text-ink">124,582</p>
                  <p className="text-xs text-ink-muted">samples</p>
                </div>
                <div className="border border-hairline bg-surface-1 p-3">
                  <p className="text-sm text-ink-muted">Validation Split</p>
                  <p className="font-mono text-lg font-semibold text-ink">20%</p>
                  <p className="text-xs text-ink-muted">24,916 samples</p>
                </div>
              </div>
              <div className="border border-success/40 bg-success/5 p-3">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-success animate-pulse" />
                  <span className="text-sm font-medium text-ink">No training in progress</span>
                </div>
                <p className="mt-1 text-xs text-ink-muted">Last training completed 2 days ago</p>
              </div>
              <div className="flex gap-2">
                <Button variant="quantum" className="flex-1 gap-2">
                  <RefreshCw className="h-4 w-4" />
                  Trigger Retraining
                </Button>
                <Button variant="outline" className="gap-2">
                  <TestTube className="h-4 w-4" />
                  A/B Test
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        <Card variant="glass">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart className="h-5 w-5 text-primary" />
              Model Comparison
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Model</TableHead>
                  <TableHead>Version</TableHead>
                  <TableHead className="text-right">Accuracy</TableHead>
                  <TableHead className="text-right">Precision</TableHead>
                  <TableHead className="text-right">Recall</TableHead>
                  <TableHead className="text-right">F1 Score</TableHead>
                  <TableHead className="text-right">Inference Time</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {models.map((model) => (
                  <TableRow key={model.name}>
                    <TableCell className="font-medium">{model.name}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{model.version}</Badge>
                    </TableCell>
                    <TableCell className="text-right font-mono">{model.accuracy}%</TableCell>
                    <TableCell className="text-right font-mono">{model.precision}%</TableCell>
                    <TableCell className="text-right font-mono">{model.recall}%</TableCell>
                    <TableCell className="text-right font-mono">{model.f1Score}%</TableCell>
                    <TableCell className="text-right font-mono text-ink-muted">
                      {model.name === 'Neural Network' ? '45ms' : model.name === 'XGBoost' ? '12ms' : '8ms'}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  )
}
