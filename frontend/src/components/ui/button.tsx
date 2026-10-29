import * as React from "react";
import { cn } from "../../lib/utils";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link" | "emerald";
  size?: "default" | "sm" | "lg" | "icon";
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    const base = "inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-400 disabled:pointer-events-none disabled:opacity-50 select-none";
    
    const variants = {
      default: "bg-zinc-50 text-zinc-900 shadow hover:bg-zinc-200",
      destructive: "bg-red-500 text-white shadow-sm hover:bg-red-600",
      outline: "border border-zinc-800 bg-zinc-950 shadow-sm hover:bg-zinc-900 hover:text-zinc-50 text-zinc-300",
      secondary: "bg-zinc-800 text-zinc-50 shadow-sm hover:bg-zinc-800/80",
      ghost: "hover:bg-zinc-800 hover:text-zinc-50 text-zinc-400",
      link: "text-zinc-50 underline-offset-4 hover:underline",
      emerald: "bg-emerald-600 text-white shadow hover:bg-emerald-500 font-semibold",
    };

    const sizes = {
      default: "h-9 px-4 py-2",
      sm: "h-8 rounded-md px-3 text-xs",
      lg: "h-11 rounded-lg px-8 text-base",
      icon: "h-9 w-9",
    };

    return (
      <button
        ref={ref}
        className={cn(base, variants[variant], sizes[size], className)}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

