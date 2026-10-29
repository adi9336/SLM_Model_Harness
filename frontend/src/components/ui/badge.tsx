import * as React from "react";
import { cn } from "../../lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "destructive" | "outline" | "success" | "cyan" | "purple" | "amber";
}

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  const variants = {
    default: "border-transparent bg-zinc-50 text-zinc-900 shadow",
    secondary: "border-zinc-700 bg-zinc-800 text-zinc-300",
    destructive: "border-transparent bg-red-950 text-red-400 border border-red-800/60",
    outline: "border-zinc-800 text-zinc-300",
    success: "border-emerald-800/60 bg-emerald-950/60 text-emerald-400",
    cyan: "border-cyan-800/60 bg-cyan-950/60 text-cyan-400",
    purple: "border-purple-800/60 bg-purple-950/60 text-purple-400",
    amber: "border-amber-800/60 bg-amber-950/60 text-amber-400",
  };

  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none",
        variants[variant],
        className
      )}
      {...props}
    />
  );
}

