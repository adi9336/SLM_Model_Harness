import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Switch } from "./ui/switch";
import {
  Layers,
  Calendar,
  Link2,
  Calculator,
  Filter,
  FolderArchive,
  Play,
  RotateCw,
  Sliders,
  ShieldCheck,
} from "lucide-react";

export interface TaskItem {
  id: string;
  name: string;
  category: string;
  description: string;
  icon?: string;
  input_file: string;
  output_file: string;
  prompt?: string;
}

export interface ScenarioSidebarProps {
  tasks: TaskItem[];
  selectedTaskId: string;
  onSelectTask: (id: string) => void;
  pacingDelay: number;
  onPacingDelayChange: (val: number) => void;
  isLive: boolean;
  onLiveChange: (val: boolean) => void;
  isRunning: boolean;
  onExecute: () => void;
}

export function ScenarioSidebar({
  tasks,
  selectedTaskId,
  onSelectTask,
  pacingDelay,
  onPacingDelayChange,
  isLive,
  onLiveChange,
  isRunning,
  onExecute,
}: ScenarioSidebarProps) {
  const getIcon = (iconName?: string) => {
    switch (iconName) {
      case "calendar":
        return <Calendar className="w-4 h-4 text-cyan-400" />;
      case "link-2":
        return <Link2 className="w-4 h-4 text-emerald-400" />;
      case "calculator":
        return <Calculator className="w-4 h-4 text-purple-400" />;
      case "filter":
        return <Filter className="w-4 h-4 text-amber-400" />;
      case "folder-archive":
        return <FolderArchive className="w-4 h-4 text-rose-400" />;
      default:
        return <Layers className="w-4 h-4 text-zinc-400" />;
    }
  };

  return (
    <div className="flex flex-col space-y-4">
      {/* Scenario Picker Card */}
      <Card className="border-zinc-800 bg-zinc-950/70">
        <CardHeader className="p-4 pb-2 border-b border-zinc-800/80">
          <div className="flex items-center justify-between">
            <CardTitle className="text-xs uppercase tracking-wider text-zinc-300 flex items-center space-x-2">
              <Layers className="w-3.5 h-3.5 text-cyan-400" />
              <span>Select Scenario</span>
            </CardTitle>
            <Badge variant="outline" className="text-[10px] text-zinc-400 font-mono">
              {tasks.length} Scenarios
            </Badge>
          </div>
        </CardHeader>

        <CardContent className="p-3 space-y-2">
          {tasks.map((t) => {
            const isSelected = t.id === selectedTaskId;
            return (
              <div
                key={t.id}
                onClick={() => !isRunning && onSelectTask(t.id)}
                className={`p-3 rounded-lg border transition-all cursor-pointer flex items-start space-x-3 ${
                  isSelected
                    ? "bg-zinc-800/80 border-cyan-500/60 shadow-md text-zinc-100"
                    : "bg-zinc-900/50 border-zinc-800/60 hover:bg-zinc-900 hover:border-zinc-700 text-zinc-300"
                } ${isRunning ? "opacity-60 cursor-not-allowed" : ""}`}
              >
                <div
                  className={`p-2 rounded-md shrink-0 mt-0.5 ${
                    isSelected ? "bg-zinc-900 border border-zinc-700" : "bg-zinc-950/80"
                  }`}
                >
                  {getIcon(t.icon)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold truncate">{t.name}</span>
                    <span className="text-[10px] text-zinc-400 font-mono ml-2 shrink-0">
                      {t.category.split(" ")[0]}
                    </span>
                  </div>
                  <p className="text-[11px] text-zinc-400 mt-1 line-clamp-2 leading-relaxed">
                    {t.description}
                  </p>
                </div>
              </div>
            );
          })}
        </CardContent>

        {/* Presentation Controls */}
        <div className="p-4 pt-2 border-t border-zinc-800/80 space-y-3.5 text-xs">
          <div>
            <div className="flex justify-between text-zinc-400 mb-1.5 font-medium">
              <span className="flex items-center space-x-1.5">
                <Sliders className="w-3.5 h-3.5 text-zinc-400" />
                <span>Pacing Delay</span>
              </span>
              <span className="font-mono text-cyan-400">{pacingDelay.toFixed(1)}s</span>
            </div>
            <input
              type="range"
              min="0.1"
              max="1.2"
              step="0.1"
              value={pacingDelay}
              disabled={isRunning}
              onChange={(e) => onPacingDelayChange(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-cyan-400 disabled:opacity-50"
            />
          </div>

          <div className="flex items-center justify-between pt-1">
            <span className="text-zinc-400 font-medium">Inference Backend</span>
            <div className="flex items-center space-x-2">
              <span className="text-[11px] font-mono text-zinc-300">
                {isLive ? "Live Inference" : "Rehearsal Demo"}
              </span>
              <Switch
                checked={isLive}
                onCheckedChange={onLiveChange}
                className="disabled:opacity-50"
              />
            </div>
          </div>

          {/* Big Execution CTA */}
          <Button
            variant="emerald"
            disabled={isRunning}
            onClick={onExecute}
            className="w-full py-5 text-sm font-semibold text-zinc-950 bg-emerald-400 hover:bg-emerald-300 shadow-md shadow-emerald-500/20 active:scale-[0.99] transition-all space-x-2"
          >
            {isRunning ? (
              <>
                <RotateCw className="w-4 h-4 animate-spin text-zinc-950" />
                <span>Agent Executing...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current text-zinc-950" />
                <span>Execute Pipeline Agent</span>
              </>
            )}
          </Button>
        </div>
      </Card>

      {/* Reliability Guards Overview */}
      <Card className="border-zinc-800 bg-zinc-950/60 p-4 text-xs space-y-2.5">
        <div className="flex items-center space-x-2 text-zinc-300 font-semibold uppercase tracking-wider text-[11px]">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Active Reliability Guards</span>
        </div>
        <ul className="space-y-1.5 text-zinc-400 text-[11px] leading-relaxed">
          <li className="flex items-start space-x-1.5">
            <span className="text-emerald-400 font-bold">•</span>
            <span><strong>Single-Tool Gating:</strong> xLAM sees 1 tool schema only.</span>
          </li>
          <li className="flex items-start space-x-1.5">
            <span className="text-emerald-400 font-bold">•</span>
            <span><strong>Deterministic Repair Pass:</strong> Recovers dropped args.</span>
          </li>
          <li className="flex items-start space-x-1.5">
            <span className="text-emerald-400 font-bold">•</span>
            <span><strong>De-dup & Query Guards:</strong> Eliminates loops.</span>
          </li>
        </ul>
      </Card>
    </div>
  );
}

