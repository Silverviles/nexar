import { useState, useEffect } from "react";
import { Target, TrendingUp, Zap, DollarSign, Loader2 } from "lucide-react";
import { MainLayout } from "@/components/layout/MainLayout";
import { SystemStatusCard } from "@/components/dashboard/SystemStatusCard";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { RecentDecisions } from "@/components/dashboard/RecentDecisions";
import { QuickActions } from "@/components/dashboard/QuickActions";
import { PerformanceChart } from "@/components/dashboard/PerformanceChart";
import { decisionEngineService } from "@/services/decision-engine-service";
import type { DashboardStats } from "@/types/decision-engine.tp";

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const data = await decisionEngineService.getDashboardStats();
        setStats(data);
      } catch (err) {
        console.error("Failed to fetch dashboard stats:", err);
      } finally {
        setIsLoading(false);
      }
    }
    fetchStats();
  }, []);

  const metrics = stats?.metrics;

  return (
    <MainLayout
      title="Dashboard"
      description="Quantum-Classical Code Router Overview"
    >
      <div className="space-y-4 md:space-y-6">
        {/* Metrics Row */}
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4 md:gap-4">
          <MetricCard
            title="Decision Accuracy"
            value={
              isLoading
                ? "..."
                : metrics && metrics.totalWithFeedback > 0
                  ? `${metrics.decisionAccuracy}%`
                  : "N/A"
            }
            subtitle={
              metrics
                ? `${metrics.totalWithFeedback} with feedback`
                : "Loading..."
            }
            icon={Target}
            variant="success"
          />
          <MetricCard
            title="Avg Response Time"
            value={
              isLoading
                ? "..."
                : metrics && metrics.avgResponseTime > 0
                  ? `${metrics.avgResponseTime}ms`
                  : "N/A"
            }
            subtitle="Estimated execution"
            icon={Zap}
            variant="quantum"
          />
          <MetricCard
            title="Cost Savings"
            value={
              isLoading
                ? "..."
                : metrics && metrics.costSavings !== 0
                  ? `$${Math.abs(metrics.costSavings).toFixed(2)}`
                  : "N/A"
            }
            subtitle={
              metrics && metrics.costSavings > 0
                ? "Saved vs actual"
                : metrics && metrics.costSavings < 0
                  ? "Over estimated"
                  : "No feedback yet"
            }
            icon={DollarSign}
            variant="success"
          />
          <MetricCard
            title="Total Decisions"
            value={
              isLoading ? "..." : metrics ? `${metrics.totalDecisions}` : "0"
            }
            subtitle="All time"
            icon={TrendingUp}
            variant="default"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 gap-4 md:gap-6 lg:grid-cols-3">
          <SystemStatusCard />
          <QuickActions />
        </div>

        {/* Charts and Recent Decisions */}
        <div className="grid grid-cols-1 gap-4 md:gap-6 lg:grid-cols-3">
          <PerformanceChart
            data={stats?.weeklyDistribution ?? []}
            isLoading={isLoading}
          />
          <RecentDecisions
            decisions={stats?.recentDecisions ?? []}
            isLoading={isLoading}
          />
        </div>
      </div>
    </MainLayout>
  );
}
