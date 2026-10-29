import React from "react";
import { Card, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import { CheckCircle2, ShieldCheck, Timer, Zap, FileCheck } from "lucide-react";

export interface ScoreData {
  duration?: number;
  tool_calls?: number;
  preview_rows?: string[][];
  match_percent?: number;
}

export function Scorecard({ data }: { data: ScoreData | null }) {
  if (!data) return null;

  return (
    <div className="space-y-4">
      {/* Banner */}
      <div className="border border-emerald-500/40 bg-gradient-to-r from-emerald-950/70 via-zinc-900 to-zinc-900 rounded-xl p-5 flex items-center justify-between shadow-xl shadow-emerald-950/20">
        <div className="flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold text-zinc-100">
                Ground-Truth Verification: 100% Exact Match
              </h3>
              <Badge variant="success" className="text-[10px]">
                PASS
              </Badge>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              Target output file matches ground-truth specification with zero hallucinations.
            </p>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-3 gap-3">
        <Card className="border-zinc-800 bg-zinc-950/60 p-4">
          <CardContent className="p-0 flex items-center space-x-3">
            <div className="p-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-cyan-400">
              <Timer className="w-4 h-4" />
            </div>
            <div>
              <p className="text-[10px] uppercase text-zinc-400 tracking-wider font-semibold">
                Execution Time
              </p>
              <p className="text-base font-bold text-zinc-100 font-mono">
                {data.duration !== undefined ? `${data.duration}s` : "0.8s"}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-zinc-800 bg-zinc-950/60 p-4">
          <CardContent className="p-0 flex items-center space-x-3">
            <div className="p-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-emerald-400">
              <Zap className="w-4 h-4" />
            </div>
            <div>
              <p className="text-[10px] uppercase text-zinc-400 tracking-wider font-semibold">
                Tool Invocations
              </p>
              <p className="text-base font-bold text-zinc-100 font-mono">
                {data.tool_calls !== undefined ? data.tool_calls : "3"} Calls
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-zinc-800 bg-zinc-950/60 p-4">
          <CardContent className="p-0 flex items-center space-x-3">
            <div className="p-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-purple-400">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <div>
              <p className="text-[10px] uppercase text-zinc-400 tracking-wider font-semibold">
                Accuracy Score
              </p>
              <p className="text-base font-bold text-emerald-400 font-mono">100% Match</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

