import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "border-transparent bg-primary text-primary-foreground",
        secondary: "border-transparent bg-secondary text-secondary-foreground",
        destructive: "border-transparent bg-destructive text-destructive-foreground",
        success: "border-transparent bg-success text-success-foreground",
        warning: "border-transparent bg-warning text-warning-foreground",
        outline: "text-foreground border-border",
        quantum: "border-[hsl(187,100%,50%,0.5)] bg-[hsl(187,100%,50%,0.1)] text-[hsl(187,100%,50%)]",
        classical: "border-[hsl(280,60%,55%,0.5)] bg-[hsl(280,60%,55%,0.1)] text-[hsl(280,60%,55%)]",
        hybrid: "border-[hsl(142,76%,45%,0.5)] bg-[hsl(142,76%,45%,0.1)] text-[hsl(142,76%,45%)]",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
