import React, { useState, useEffect } from "react";
import { Header } from "./components/Header";
import { ScenarioSidebar, TaskItem } from "./components/ScenarioSidebar";
import { ExecutionFeed, StreamEvent } from "./components/ExecutionFeed";
import { Scorecard, ScoreData } from "./components/Scorecard";
import { DataPreviewTable } from "./components/DataPreviewTable";
import { TinkerSettingsModal } from "./components/TinkerSettingsModal";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "./components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "./components/ui/tabs";
import { Badge } from "./components/ui/badge";
import { Button } from "./components/ui/button";
import {
  Terminal,
  FileCheck,
  Table as TableIcon,
  Shield,
  Trash2,
  ExternalLink,
  Info,
} from "lucide-react";

export function App() {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [selectedTaskId, setSelectedTaskId] = useState<string>("t001_clean_dates");
  const [status, setStatus] = useState<any>({});
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [isLive, setIsLive] = useState<boolean>(false);
  const [pacingDelay, setPacingDelay] = useState<number>(0.4);
  const [scoreData, setScoreData] = useState<ScoreData | null>(null);
  const [settingsOpen, setSettingsOpen] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<string>("stream");

  // Fetch initial tasks and system status
  const loadStatus = async () => {
    try {
      const res = await fetch("/api/status");
      const data = await res.json();
      setStatus(data);
    } catch (err) {
      console.error("Failed to load status", err);
    }
  };

  const loadTasks = async () => {
    try {
      const res = await fetch("/api/tasks");
      const data = await res.json();
      setTasks(data);
      if (data.length > 0 && !selectedTaskId) {
        setSelectedTaskId(data[0].id);
      }
    } catch (err) {
      console.error("Failed to load tasks", err);
    }
  };

  useEffect(() => {
    loadTasks();
    loadStatus();
  }, []);

  const selectedTask = tasks.find((t) => t.id === selectedTaskId);

  // Execute Agent via Server-Sent Events
  const handleExecute = () => {
    if (isRunning) return;
    setIsRunning(true);
    setEvents([]);
    setScoreData(null);
    setActiveTab("stream");

    const sse = new EventSource(
      `/api/stream/${selectedTaskId}?live=${isLive}&delay=${pacingDelay}`
    );

    sse.onmessage = (event) => {
      if (!event.data) return;
      try {
        const msg = JSON.parse(event.data);
        if (msg.phase === "SCORECARD") {
          setScoreData(msg.payload);
        } else {
          setEvents((prev) => [...prev, msg]);
        }
      } catch (e) {
        console.error("Parse error", e);
      }
    };

    sse.addEventListener("end", () => {
      sse.close();
      setIsRunning(false);
    });

    sse.onerror = (err) => {
      console.error("SSE stream error", err);
      sse.close();
      setIsRunning(false);
    };
  };

  const handleClear = () => {
    setEvents([]);
    setScoreData(null);
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Header */}
      <Header status={status} onOpenSettings={() => setSettingsOpen(true)} />

      {/* Main Grid Layout */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-5 grid grid-cols-12 gap-5">
        {/* Left Column: Scenarios & Controls (4 Cols) */}
        <div className="col-span-12 lg:col-span-4">
          <ScenarioSidebar
            tasks={tasks}
            selectedTaskId={selectedTaskId}
            onSelectTask={setSelectedTaskId}
            pacingDelay={pacingDelay}
            onPacingDelayChange={setPacingDelay}
            isLive={isLive}
            onLiveChange={setIsLive}
            isRunning={isRunning}
            onExecute={handleExecute}
          />
        </div>

        {/* Right Column: Active Task Details, Tabs, Live Stream & Outputs (8 Cols) */}
        <div className="col-span-12 lg:col-span-8 flex flex-col space-y-4">
          {/* Active Scenario Banner */}
          <Card className="border-zinc-800 bg-zinc-900/40 p-4">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center space-x-2">
                  <Badge variant="cyan" className="text-[10px]">
                    {selectedTask?.category || "ETL Pipeline"}
                  </Badge>
                  <h2 className="text-sm font-bold text-zinc-100">
                    {selectedTask?.name || "Scenario"}
                  </h2>
                </div>
                <p className="text-xs text-zinc-400 mt-1.5 leading-relaxed">
                  {selectedTask?.prompt || selectedTask?.description}
                </p>
                <div className="flex flex-wrap items-center gap-3 mt-3 text-[11px] font-mono text-zinc-400">
                  <span className="bg-zinc-950 px-2.5 py-1 rounded border border-zinc-800 text-zinc-300">
                    📁 Input: {selectedTask?.input_file}
                  </span>
                  <span className="bg-zinc-950 px-2.5 py-1 rounded border border-zinc-800 text-emerald-400">
                    🎯 Target: {selectedTask?.output_file}
                  </span>
                </div>
              </div>

              <Button
                variant="ghost"
                size="sm"
                onClick={handleClear}
                disabled={isRunning || events.length === 0}
                className="text-zinc-500 hover:text-zinc-300 h-8 px-2"
                title="Clear feed"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </Button>
            </div>
          </Card>

          {/* Scorecard (when available) */}
          {scoreData && <Scorecard data={scoreData} />}

          {/* Multi-Tab Workspace */}
          <Card className="border-zinc-800 bg-zinc-950/70 flex-1 flex flex-col min-h-[460px]">
            <CardHeader className="p-3.5 pb-0 border-b border-zinc-800/80">
              <div className="flex items-center justify-between">
                <Tabs value={activeTab} onValueChange={setActiveTab}>
                  <TabsList>
                    <TabsTrigger value="stream" badge={events.length}>
                      <Terminal className="w-3.5 h-3.5 mr-1.5 text-cyan-400" />
                      <span>Execution Stream</span>
                    </TabsTrigger>
                    <TabsTrigger value="table">
                      <TableIcon className="w-3.5 h-3.5 mr-1.5 text-emerald-400" />
                      <span>Output Dataset</span>
                    </TabsTrigger>
                    <TabsTrigger value="guards">
                      <Shield className="w-3.5 h-3.5 mr-1.5 text-purple-400" />
                      <span>Guards Architecture</span>
                    </TabsTrigger>
                  </TabsList>
                </Tabs>

                <div className="flex items-center space-x-2 text-xs">
                  {isRunning ? (
                    <Badge variant="cyan" className="animate-pulse space-x-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
                      <span>Agent Running</span>
                    </Badge>
                  ) : scoreData ? (
                    <Badge variant="success">100% Match Verified</Badge>
                  ) : (
                    <Badge variant="outline">Ready</Badge>
                  )}
                </div>
              </div>
            </CardHeader>

            <CardContent className="p-4 flex-1 overflow-y-auto max-h-[560px]">
              {activeTab === "stream" && (
                <ExecutionFeed events={events} isRunning={isRunning} />
              )}

              {activeTab === "table" && (
                <DataPreviewTable rows={scoreData?.preview_rows} />
              )}

              {activeTab === "guards" && (
                <div className="space-y-3.5 text-xs text-zinc-300">
                  <div className="border border-zinc-800 rounded-lg p-4 bg-zinc-900/40 space-y-1.5">
                    <h4 className="font-bold text-emerald-400 flex items-center space-x-2">
                      <Shield className="w-4 h-4" />
                      <span>1. Single-Tool Gating (v4 Architecture)</span>
                    </h4>
                    <p className="text-zinc-400 text-xs leading-relaxed">
                      Small language models (1B) experience argument cross-talk and drop parameters when exposed to multiple schemas simultaneously.
                      Single-tool gating presents xLAM with exactly ONE schema at a time, completely eliminating cross-schema hallucinations.
                    </p>
                  </div>

                  <div className="border border-zinc-800 rounded-lg p-4 bg-zinc-900/40 space-y-1.5">
                    <h4 className="font-bold text-amber-400 flex items-center space-x-2">
                      <Shield className="w-4 h-4" />
                      <span>2. Deterministic Repair Pass</span>
                    </h4>
                    <p className="text-zinc-400 text-xs leading-relaxed">
                      If validation flags missing required parameters or type mismatch, the repair pass re-prompts the formatter with the exact error details and context instead of failing the pipeline.
                    </p>
                  </div>

                  <div className="border border-zinc-800 rounded-lg p-4 bg-zinc-900/40 space-y-1.5">
                    <h4 className="font-bold text-cyan-400 flex items-center space-x-2">
                      <Shield className="w-4 h-4" />
                      <span>3. De-dup & Streak Guards</span>
                    </h4>
                    <p className="text-zinc-400 text-xs leading-relaxed">
                      Prevents infinite tool inspection loops by detecting repeated calls and capping consecutive read-only queries, automatically forcing the Reasoner forward.
                    </p>
                  </div>

                  <div className="border border-zinc-800 rounded-lg p-4 bg-zinc-900/40 space-y-1.5">
                    <h4 className="font-bold text-purple-400 flex items-center space-x-2">
                      <Shield className="w-4 h-4" />
                      <span>4. Deliverable Completion Guard</span>
                    </h4>
                    <p className="text-zinc-400 text-xs leading-relaxed">
                      The agent engine refuses to conclude until the final requested file deliverable (e.g., <code>out.csv</code> or partition files) is physically verified on disk.
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Tinker Configuration Modal */}
      <TinkerSettingsModal
        open={settingsOpen}
        onOpenChange={setSettingsOpen}
        currentModel={status?.tinker_model}
        isConfigured={status?.tinker_active}
        onSaved={loadStatus}
      />
    </div>
  );
}

