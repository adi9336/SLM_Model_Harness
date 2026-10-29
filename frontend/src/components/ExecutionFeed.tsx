import React, { useEffect, useRef } from "react";
import { Badge } from "./ui/badge";
import {
  Search,
  Brain,
  Code2,
  Database,
  ShieldAlert,
  Wrench,
  CheckCircle2,
  Terminal,
} from "lucide-react";

export interface StreamEvent {
  phase: string;
  title: string;
  payload: any;
  timestamp?: number;
}

export interface ExecutionFeedProps {
  events: StreamEvent[];
  isRunning: boolean;
}

export function ExecutionFeed({ events, isRunning }: ExecutionFeedProps) {
  const feedEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    feedEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events]);

  if (events.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center text-zinc-500 space-y-3">
        <Terminal className="w-10 h-10 text-zinc-600 stroke-[1.5]" />
        <div>
          <p className="text-sm font-medium text-zinc-400">Execution Console Ready</p>
          <p className="text-xs text-zinc-500 mt-1">
            Select a scenario and click "Execute Pipeline Agent" to stream the live Two-Level Agent trace.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3 pr-1">
      {events.map((evt, idx) => {
        switch (evt.phase) {
          case "ANALYZE":
            return (
              <div
                key={idx}
                className="border border-amber-900/40 bg-amber-950/20 rounded-xl p-4 text-xs space-y-1.5 animate-in fade-in-50"
              >
                <div className="flex items-center space-x-2 text-amber-400 font-semibold uppercase tracking-wider text-[11px]">
                  <Search className="w-4 h-4" />
                  <span>[1/4] ANALYZE TASK REQUIREMENTS</span>
                </div>
                <div className="font-mono text-zinc-300 whitespace-pre-wrap pl-6 leading-relaxed">
                  {typeof evt.payload === "string" ? evt.payload : JSON.stringify(evt.payload, null, 2)}
                </div>
              </div>
            );

          case "PLAN":
            return (
              <div
                key={idx}
                className="border border-cyan-900/40 bg-cyan-950/20 rounded-xl p-4 text-xs space-y-2 animate-in fade-in-50"
              >
                <div className="flex items-center justify-between text-cyan-400 font-semibold uppercase tracking-wider text-[11px]">
                  <div className="flex items-center space-x-2">
                    <Brain className="w-4 h-4" />
                    <span>[2/4] LEVEL 1: QWEN 8B REASONING DECOMPOSITION</span>
                  </div>
                  <Badge variant="cyan" className="text-[10px] py-0 px-2">
                    Lean Context
                  </Badge>
                </div>
                <div className="bg-zinc-950/90 border border-zinc-800 rounded-lg p-3 font-mono text-cyan-200 text-xs overflow-x-auto whitespace-pre-wrap">
                  {typeof evt.payload === "string" ? evt.payload : JSON.stringify(evt.payload, null, 2)}
                </div>
              </div>
            );

          case "FORMAT":
            return (
              <div
                key={idx}
                className="border border-emerald-900/40 bg-emerald-950/20 rounded-xl p-4 text-xs space-y-2 animate-in fade-in-50"
              >
                <div className="flex items-center justify-between text-emerald-400 font-semibold uppercase tracking-wider text-[11px]">
                  <div className="flex items-center space-x-2">
                    <Code2 className="w-4 h-4" />
                    <span>[3/4] LEVEL 2: xLAM 1B ATOMIC TOOL FORMAT</span>
                  </div>
                  <Badge variant="success" className="text-[10px] py-0 px-2">
                    Single-Tool Gating
                  </Badge>
                </div>
                <div className="bg-zinc-950/90 border border-zinc-800 rounded-lg p-3 font-mono text-emerald-300 text-xs overflow-x-auto whitespace-pre-wrap">
                  {typeof evt.payload === "string" ? evt.payload : JSON.stringify(evt.payload, null, 2)}
                </div>
              </div>
            );

          case "EXEC":
            return (
              <div
                key={idx}
                className="border border-zinc-800 bg-zinc-900/60 rounded-xl p-4 text-xs space-y-1.5 animate-in fade-in-50"
              >
                <div className="flex items-center space-x-2 text-zinc-300 font-semibold uppercase tracking-wider text-[11px]">
                  <Database className="w-4 h-4 text-cyan-400" />
                  <span>DATASTORE / TOOL MUTATION</span>
                </div>
                <div className="font-mono text-zinc-400 pl-6 text-xs whitespace-pre-wrap">
                  {typeof evt.payload === "string" ? evt.payload : JSON.stringify(evt.payload, null, 2)}
                </div>
              </div>
            );

          case "GUARD":
            return (
              <div
                key={idx}
                className="border border-rose-900/60 bg-rose-950/30 rounded-xl p-4 text-xs space-y-1.5 animate-in fade-in-50"
              >
                <div className="flex items-center space-x-2 text-rose-400 font-semibold uppercase tracking-wider text-[11px]">
                  <ShieldAlert className="w-4 h-4" />
                  <span>RELIABILITY GUARD INTERRUPT</span>
                </div>
                <div className="font-mono text-rose-200 pl-6 text-xs">
                  <strong>{evt.title}:</strong> {typeof evt.payload === "string" ? evt.payload : JSON.stringify(evt.payload)}
                </div>
              </div>
            );

          case "REPAIR":
            return (
              <div
                key={idx}
                className="border border-amber-800/60 bg-amber-950/30 rounded-xl p-4 text-xs space-y-1.5 animate-in fade-in-50"
              >
                <div className="flex items-center space-x-2 text-amber-300 font-semibold uppercase tracking-wider text-[11px]">
                  <Wrench className="w-4 h-4" />
                  <span>DETERMINISTIC REPAIR PASS</span>
                </div>
                <div className="font-mono text-amber-200 pl-6 text-xs whitespace-pre-wrap">
                  {typeof evt.payload === "string" ? evt.payload : JSON.stringify(evt.payload)}
                </div>
              </div>
            );

          case "DONE":
            return (
              <div
                key={idx}
                className="border border-emerald-700/60 bg-emerald-950/40 rounded-xl p-4 text-xs space-y-2 animate-in fade-in-50"
              >
                <div className="flex items-center space-x-2 text-emerald-400 font-bold uppercase tracking-wider text-[11px]">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>[4/4] AGENT TASK DELIVERABLE VERIFIED & COMPLETE</span>
                </div>
                <div className="font-sans text-zinc-100 pl-6 text-xs leading-relaxed">
                  {typeof evt.payload === "string" ? evt.payload : JSON.stringify(evt.payload)}
                </div>
              </div>
            );

          default:
            return null;
        }
      })}
      {isRunning && (
        <div className="flex items-center space-x-2 py-3 px-4 text-xs text-zinc-400 animate-pulse bg-zinc-900/40 rounded-lg border border-zinc-800/40">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          <span className="font-mono">Synthesizing next action...</span>
        </div>
      )}
      <div ref={feedEndRef} />
    </div>
  );
}

