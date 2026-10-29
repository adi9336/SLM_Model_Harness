import React from "react";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Cpu, Settings2, ShieldCheck, Cloud, Server } from "lucide-react";

export interface HeaderProps {
  status: {
    status?: string;
    active_backend?: string;
    reasoner_model?: string;
    formatter_model?: string;
    tinker_active?: boolean;
    ollama_local_online?: boolean;
    on_premise?: boolean;
  };
  onOpenSettings: () => void;
}

export function Header({ status, onOpenSettings }: HeaderProps) {
  const isCloud = status.tinker_active;

  return (
    <header className="border-b border-zinc-800 bg-zinc-950/90 backdrop-blur px-6 py-3.5 sticky top-0 z-40 flex items-center justify-between">
      {/* Title & Brand */}
      <div className="flex items-center space-x-3.5">
        <div className="w-9 h-9 rounded-lg bg-zinc-900 border border-zinc-700/80 flex items-center justify-center text-zinc-100 shadow-md">
          <Cpu className="w-5 h-5 text-emerald-400" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-base font-bold tracking-tight text-zinc-100 font-sans">
              TWO-LEVEL AGENT HARNESS
            </h1>
            <Badge variant="success" className="text-[10px] py-0 px-2">
              Tech Fest Demo
            </Badge>
          </div>
          <p className="text-xs text-zinc-400">
            Autonomous ETL & DevOps Test Execution Engine
          </p>
        </div>
      </div>

      {/* Center/Right Status Badges */}
      <div className="flex items-center space-x-2.5">
        <div className="hidden md:flex items-center space-x-1.5 bg-zinc-900/90 border border-zinc-800 px-3 py-1 rounded-md text-xs">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
          <span className="text-zinc-400 font-mono text-[11px]">
            <strong className="text-cyan-400">L1:</strong> {status.reasoner_model || "Qwen 8B"}
          </span>
        </div>

        <div className="hidden md:flex items-center space-x-1.5 bg-zinc-900/90 border border-zinc-800 px-3 py-1 rounded-md text-xs">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
          <span className="text-zinc-400 font-mono text-[11px]">
            <strong className="text-emerald-400">L2:</strong> {status.formatter_model || "xLAM 1B"}
          </span>
        </div>

        <div className="flex items-center space-x-1.5 bg-zinc-900/90 border border-zinc-800 px-3 py-1 rounded-md text-xs">
          {isCloud ? (
            <>
              <Cloud className="w-3.5 h-3.5 text-sky-400" />
              <span className="text-sky-300 font-medium text-[11px]">Tinker Cloud</span>
            </>
          ) : (
            <>
              <Server className="w-3.5 h-3.5 text-zinc-400" />
              <span className="text-zinc-300 font-medium text-[11px]">Local Host</span>
            </>
          )}
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={onOpenSettings}
          className="text-xs space-x-1.5 h-8 border-zinc-800 bg-zinc-900 hover:bg-zinc-800 text-zinc-200"
        >
          <Settings2 className="w-3.5 h-3.5 text-zinc-400" />
          <span>Config</span>
        </Button>
      </div>
    </header>
  );
}

