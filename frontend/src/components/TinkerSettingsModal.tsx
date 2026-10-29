import React, { useState } from "react";
import { Dialog, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "./ui/dialog";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { KeyRound, Server, CheckCircle2, AlertCircle } from "lucide-react";

export interface TinkerSettingsModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  currentModel?: string;
  isConfigured?: boolean;
  onSaved: () => void;
}

export function TinkerSettingsModal({
  open,
  onOpenChange,
  currentModel,
  isConfigured,
  onSaved,
}: TinkerSettingsModalProps) {
  const [apiKey, setApiKey] = useState("");
  const [model, setModel] = useState(
    currentModel || "tinker://5165c05b-e5bc-591b-99f4-d732ef85b72e:train:0/sampler_weights/final"
  );
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      const res = await fetch("/api/config/tinker", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: apiKey, model }),
      });
      const data = await res.json();
      if (data.success) {
        setMessage({ type: "success", text: "Tinker API configuration updated successfully!" });
        setTimeout(() => {
          onSaved();
          onOpenChange(false);
        }, 1200);
      } else {
        setMessage({ type: "error", text: "Failed to update configuration." });
      }
    } catch (err: any) {
      setMessage({ type: "error", text: err.message || "Network error" });
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogHeader>
        <div className="flex items-center space-x-2">
          <KeyRound className="w-5 h-5 text-cyan-400" />
          <DialogTitle>Tinker API & Inference Settings</DialogTitle>
        </div>
        <DialogDescription>
          Configure your Thinking Machines Tinker cloud API key and model endpoint for sub-second Qwen reasoning.
        </DialogDescription>
      </DialogHeader>

      <div className="space-y-4 py-2 text-xs">
        {/* Status preview */}
        <div className="p-3 rounded-lg border border-zinc-800 bg-zinc-900/60 flex items-center justify-between">
          <span className="text-zinc-400">Current Status:</span>
          {isConfigured ? (
            <Badge variant="success" className="text-[10px] space-x-1">
              <CheckCircle2 className="w-3 h-3" />
              <span>Active & Connected</span>
            </Badge>
          ) : (
            <Badge variant="secondary" className="text-[10px]">
              Offline Rehearsal Mode
            </Badge>
          )}
        </div>

        {/* API Key */}
        <div className="space-y-1.5">
          <label className="text-zinc-300 font-semibold flex justify-between">
            <span>Tinker API Key</span>
            <span className="text-zinc-500 font-normal">Leave blank to keep existing</span>
          </label>
          <input
            type="password"
            placeholder="tml-..."
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            className="w-full px-3 py-2 bg-zinc-900 border border-zinc-800 rounded-lg text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:border-cyan-500 font-mono text-xs"
          />
        </div>

        {/* Model ID */}
        <div className="space-y-1.5">
          <label className="text-zinc-300 font-semibold">Tinker Model Checkpoint / URI</label>
          <input
            type="text"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="w-full px-3 py-2 bg-zinc-900 border border-zinc-800 rounded-lg text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:border-cyan-500 font-mono text-xs"
          />
        </div>

        {message && (
          <div
            className={`p-3 rounded-lg border text-xs flex items-center space-x-2 ${
              message.type === "success"
                ? "border-emerald-800/60 bg-emerald-950/40 text-emerald-300"
                : "border-rose-800/60 bg-rose-950/40 text-rose-300"
            }`}
          >
            {message.type === "success" ? (
              <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
            ) : (
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            )}
            <span>{message.text}</span>
          </div>
        )}
      </div>

      <DialogFooter>
        <Button variant="outline" size="sm" onClick={() => onOpenChange(false)}>
          Cancel
        </Button>
        <Button variant="default" size="sm" disabled={saving} onClick={handleSave}>
          {saving ? "Saving..." : "Save Configuration"}
        </Button>
      </DialogFooter>
    </Dialog>
  );
}

