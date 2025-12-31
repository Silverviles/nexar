import { Calendar, Filter, Search, Download, FileText, ChevronDown, CheckCircle, XCircle, Clock } from "lucide-react";
import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

const executions = [
  {
    id: "EXE-001",
    date: "2024-01-15 14:32:18",
    hardware: "quantum",
    status: "completed",
    predictedTime: "2.4s",
    actualTime: "2.1s",
    predictedCost: "$0.42",
    actualCost: "$0.38",
    confidence: 94,
  },
  {
    id: "EXE-002",
    date: "2024-01-15 14:28:05",
    hardware: "classical",
    status: "completed",
    predictedTime: "1.2s",
    actualTime: "1.5s",
    predictedCost: "$0.08",
    actualCost: "$0.08",
    confidence: 88,
  },
  {
    id: "EXE-003",
    date: "2024-01-15 14:15:42",
    hardware: "hybrid",
    status: "completed",
    predictedTime: "5.8s",
    actualTime: "6.2s",
    predictedCost: "$0.25",
    actualCost: "$0.28",
    confidence: 91,
  },
  {
    id: "EXE-004",
    date: "2024-01-15 13:58:31",
    hardware: "quantum",
    status: "failed",
    predictedTime: "3.1s",
    actualTime: "—",
    predictedCost: "$0.55",
    actualCost: "$0.00",
    confidence: 76,
  },
  {
    id: "EXE-005",
    date: "2024-01-15 13:45:12",
    hardware: "classical",
    status: "completed",
    predictedTime: "0.8s",
    actualTime: "0.7s",
    predictedCost: "$0.05",
    actualCost: "$0.05",
    confidence: 97,
  },
];

const statusConfig = {
  completed: { icon: CheckCircle, color: "text-success", badge: "success" as const },
  failed: { icon: XCircle, color: "text-destructive", badge: "destructive" as const },
  pending: { icon: Clock, color: "text-warning", badge: "warning" as const },
};

export default function ExecutionHistory() {
  return (
    <MainLayout title="Execution History" description="Historical data and performance tracking">
      <div className="space-y-4 md:space-y-6">
        {/* Filters */}
        <Card variant="glass">
          <CardContent className="flex flex-col gap-3 p-4 sm:flex-row sm:flex-wrap sm:items-center sm:gap-4">
            <div className="relative w-full flex-1 sm:min-w-[200px]">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Search executions..." className="pl-10 bg-secondary/30" />
            </div>
            <Select defaultValue="all">
              <SelectTrigger className="w-[150px] bg-secondary/30">
                <SelectValue placeholder="Hardware" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Hardware</SelectItem>
                <SelectItem value="quantum">Quantum</SelectItem>
                <SelectItem value="classical">Classical</SelectItem>
                <SelectItem value="hybrid">Hybrid</SelectItem>
              </SelectContent>
            </Select>
            <Select defaultValue="all">
              <SelectTrigger className="w-[150px] bg-secondary/30">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" className="gap-2">
              <Calendar className="h-4 w-4" />
              Date Range
            </Button>
            <Button variant="outline" className="gap-2">
              <Download className="h-4 w-4" />
              Export
            </Button>
          </CardContent>
        </Card>

        {/* Execution List */}
        <div className="space-y-3">
          {executions.map((execution) => {
            const status = statusConfig[execution.status];
            const StatusIcon = status.icon;
            
            return (
              <Card key={execution.id} variant="glass" className="transition-all hover:border-primary/30">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <StatusIcon className={cn("h-5 w-5", status.color)} />
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-mono font-medium">{execution.id}</p>
                          <Badge variant={execution.hardware as "quantum" | "classical" | "hybrid"} className="capitalize">
                            {execution.hardware}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">{execution.date}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-8">
                      <div className="text-center">
                        <p className="text-xs text-muted-foreground">Confidence</p>
                        <p className="font-mono font-medium">{execution.confidence}%</p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-muted-foreground">Time</p>
                        <p className="font-mono font-medium">
                          <span className="text-muted-foreground">{execution.predictedTime}</span>
                          <span className="mx-1">→</span>
                          <span className={execution.actualTime !== "—" ? "text-success" : "text-destructive"}>
                            {execution.actualTime}
                          </span>
                        </p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-muted-foreground">Cost</p>
                        <p className="font-mono font-medium">
                          <span className="text-muted-foreground">{execution.predictedCost}</span>
                          <span className="mx-1">→</span>
                          <span className={execution.status === "completed" ? "text-success" : "text-muted-foreground"}>
                            {execution.actualCost}
                          </span>
                        </p>
                      </div>
                      <Button variant="ghost" size="sm" className="gap-1">
                        <FileText className="h-4 w-4" />
                        Details
                        <ChevronDown className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">Showing 1-5 of 1,284 executions</p>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" disabled>Previous</Button>
            <Button variant="outline" size="sm">Next</Button>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
