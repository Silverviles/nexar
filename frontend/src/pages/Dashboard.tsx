import { Target, TrendingUp, Zap, DollarSign } from "lucide-react";
import { MainLayout } from "@/components/layout/MainLayout";
import { SystemStatusCard } from "@/components/dashboard/SystemStatusCard";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { RecentDecisions } from "@/components/dashboard/RecentDecisions";
import { QuickActions } from "@/components/dashboard/QuickActions";
import { PerformanceChart } from "@/components/dashboard/PerformanceChart";

export default function Dashboard() {
  return (
    <MainLayout title="Dashboard" description="Quantum-Classical Code Router Overview">
      <div className="space-y-4 md:space-y-6">
        {/* Metrics Row */}
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4 md:gap-4">
          <MetricCard
            title="Decision Accuracy"
            value="92.4%"
            subtitle="Target: 85%"
            icon={Target}
            trend={{ value: "2.1%", positive: true }}
            variant="success"
          />
          <MetricCard
            title="Avg Response Time"
            value="145ms"
            subtitle="Last 24 hours"
            icon={Zap}
            trend={{ value: "12ms", positive: true }}
            variant="quantum"
          />
          <MetricCard
            title="Cost Savings"
            value="$2,847"
            subtitle="This month"
            icon={DollarSign}
            trend={{ value: "18.3%", positive: true }}
            variant="success"
          />
          <MetricCard
            title="Total Decisions"
            value="1,284"
            subtitle="This week"
            icon={TrendingUp}
            trend={{ value: "156", positive: true }}
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
          <PerformanceChart />
          <RecentDecisions />
        </div>
      </div>
    </MainLayout>
  );
}
