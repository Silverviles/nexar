import { Play, Eye, Calculator, Zap } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

const actions = [
  {
    label: "New Code Analysis",
    description: "Submit code for routing decision",
    icon: Play,
    path: "/analysis",
    variant: "quantum" as const,
  },
  {
    label: "Hardware Status",
    description: "View all system statuses",
    icon: Eye,
    path: "/hardware",
    variant: "outline" as const,
  },
  {
    label: "Cost Calculator",
    description: "Estimate execution costs",
    icon: Calculator,
    path: "/costs",
    variant: "outline" as const,
  },
];

export function QuickActions() {
  const navigate = useNavigate();

  return (
    <Card variant="glass">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <Zap className="h-5 w-5 text-warning" />
          Quick Actions
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {actions.map((action) => {
            const Icon = action.icon;
            return (
              <Button
                key={action.label}
                variant={action.variant}
                className="w-full justify-start gap-3 h-auto py-3"
                onClick={() => navigate(action.path)}
              >
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-secondary/50">
                  <Icon className="h-4 w-4" />
                </div>
                <div className="text-left">
                  <p className="font-medium">{action.label}</p>
                  <p className="text-xs text-muted-foreground">{action.description}</p>
                </div>
              </Button>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
