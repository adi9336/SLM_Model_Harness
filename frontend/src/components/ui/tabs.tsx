import * as React from "react";
import { cn } from "../../lib/utils";

interface TabsContextValue {
  activeTab: string;
  setActiveTab: (value: string) => void;
}

const TabsContext = React.createContext<TabsContextValue | null>(null);

export function Tabs({
  value,
  onValueChange,
  defaultValue,
  children,
  className,
}: {
  value?: string;
  onValueChange?: (val: string) => void;
  defaultValue?: string;
  children: React.ReactNode;
  className?: string;
}) {
  const [internalTab, setInternalTab] = React.useState(defaultValue || "");
  const activeTab = value !== undefined ? value : internalTab;
  const setActiveTab = onValueChange || setInternalTab;

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className={cn("w-full", className)}>{children}</div>
    </TabsContext.Provider>
  );
}

export function TabsList({ className, children }: { className?: string; children: React.ReactNode }) {
  return (
    <div
      className={cn(
        "inline-flex h-9 items-center justify-start rounded-lg bg-zinc-900/80 p-1 text-zinc-400 border border-zinc-800",
        className
      )}
    >
      {children}
    </div>
  );
}

export function TabsTrigger({
  value,
  children,
  className,
  badge,
}: {
  value: string;
  children: React.ReactNode;
  className?: string;
  badge?: string | number;
}) {
  const ctx = React.useContext(TabsContext);
  if (!ctx) throw new Error("TabsTrigger must be used within Tabs");
  const isActive = ctx.activeTab === value;

  return (
    <button
      type="button"
      onClick={() => ctx.setActiveTab(value)}
      className={cn(
        "inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1 text-xs font-medium transition-all focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50 select-none",
        isActive
          ? "bg-zinc-800 text-zinc-100 shadow-sm"
          : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/40",
        className
      )}
    >
      {children}
      {badge !== undefined && (
        <span
          className={cn(
            "ml-2 rounded-full px-1.5 py-0.2 text-[10px]",
            isActive ? "bg-zinc-700 text-zinc-100" : "bg-zinc-800 text-zinc-400"
          )}
        >
          {badge}
        </span>
      )}
    </button>
  );
}

export function TabsContent({
  value,
  children,
  className,
}: {
  value: string;
  children: React.ReactNode;
  className?: string;
}) {
  const ctx = React.useContext(TabsContext);
  if (!ctx) throw new Error("TabsContent must be used within Tabs");
  if (ctx.activeTab !== value) return null;

  return <div className={cn("mt-4 focus-visible:outline-none", className)}>{children}</div>;
}

