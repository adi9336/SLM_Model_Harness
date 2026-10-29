import React from "react";
import { Table, TableHeader, TableBody, TableHead, TableRow, TableCell } from "./ui/table";
import { Table as TableIcon, FileText } from "lucide-react";

export function DataPreviewTable({ rows }: { rows?: string[][] }) {
  if (!rows || rows.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center text-zinc-500 space-y-2">
        <FileText className="w-8 h-8 text-zinc-600" />
        <p className="text-xs text-zinc-400">No tabular CSV preview available for this scenario.</p>
        <p className="text-[11px] text-zinc-500">
          (e.g., file reorganization tasks write files directly to output directories).
        </p>
      </div>
    );
  }

  const header = rows[0] || [];
  const bodyRows = rows.slice(1);

  return (
    <div className="border border-zinc-800 rounded-xl overflow-hidden bg-zinc-950/60 shadow-lg">
      <div className="p-3 bg-zinc-900/80 border-b border-zinc-800 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2 text-zinc-300 font-semibold">
          <TableIcon className="w-4 h-4 text-cyan-400" />
          <span>Output Dataset Preview</span>
        </div>
        <span className="text-zinc-500 font-mono text-[11px]">
          Showing {bodyRows.length} rows • {header.length} columns
        </span>
      </div>

      <div className="max-h-72 overflow-y-auto">
        <Table>
          <TableHeader>
            <TableRow>
              {header.map((col, idx) => (
                <TableHead key={idx}>{col}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {bodyRows.map((row, rIdx) => (
              <TableRow key={rIdx}>
                {row.map((cell, cIdx) => (
                  <TableCell key={cIdx}>{cell}</TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

