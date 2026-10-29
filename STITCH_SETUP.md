# Stitch MCP & React shadcn/ui Guide

This project features a clean **React UI** engineered with **shadcn/ui** design patterns (`https://ui.shadcn.com/`) and supports the **Google Stitch Model Context Protocol (MCP)** workflow.

---

## 1. React + shadcn/ui Component Architecture

All UI components are organized into modular, reusable primitives inside `frontend/src/components/`:

### UI Primitives (`frontend/src/components/ui/`)
- **`button.tsx`**: Versatile button variants (`default`, `emerald`, `outline`, `ghost`, `secondary`).
- **`card.tsx`**: `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, and `CardFooter`.
- **`badge.tsx`**: High-contrast badges for tags and statuses (`success`, `cyan`, `purple`, `amber`, `destructive`, `outline`).
- **`tabs.tsx`**: Tabbed workspace switcher (`TabsList`, `TabsTrigger`, `TabsContent`) with active indicators and counters.
- **`table.tsx`**: Sleek tabular viewer (`TableHeader`, `TableHead`, `TableRow`, `TableCell`) for ETL CSV datasets.
- **`switch.tsx`**: Accessible toggle switch for Live Inference vs. Demo Rehearsal mode.
- **`dialog.tsx`**: Accessible modal overlay for Tinker API and model configuration.

### Application Components (`frontend/src/components/`)
- **`Header.tsx`**: Top navigation with system status, active Reasoner/Formatter badges, and Tinker Cloud indicator.
- **`ScenarioSidebar.tsx`**: Multi-scenario selector with category tags, presentation pacing delay slider, and primary execution CTA.
- **`ExecutionFeed.tsx`**: Real-time event streaming viewer with animated cards for all 4 agent lifecycle phases.
- **`Scorecard.tsx`**: 100% Ground-Truth Verification banner, duration timer, tool invocation counter, and zero-hallucination score.
- **`DataPreviewTable.tsx`**: Clean dataset preview table displaying generated outputs.
- **`TinkerSettingsModal.tsx`**: Dialog to inspect or update the cloud Tinker API key and model URI on the fly.
- **`App.tsx`**: Root React coordinator connecting Server-Sent Events (SSE) from FastAPI (`/api/stream/{task_id}`).

---

## 2. Serving & Running the UI

The UI is accessible immediately with **zero node_modules setup** needed for live demos:

### Option A: Out-of-the-Box (FastAPI Server)
FastAPI automatically serves the complete React application at:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

```powershell
py -m uvicorn server:app --host 127.0.0.1 --port 8000
```

### Option B: Vite Dev Server (HMR Development)
If you want to edit and develop individual components with Hot Module Replacement (HMR):
```powershell
cd frontend
npm install
npm run dev
```
Vite runs at `http://localhost:5173` and proxies API calls to `127.0.0.1:8000`.

---

## 3. Stitch MCP Integration (Google Stitch)

**Google Stitch** (`https://stitch.withgoogle.com`) is Google's AI-powered UI design tool.

To connect this repository to Google Stitch using MCP:

1. **Install Stitch MCP CLI**:
   ```bash
   npx -y @_davideast/stitch-mcp init
   ```
2. **Add to Antigravity / Claude MCP Configuration**:
   ```json
   {
     "mcpServers": {
       "stitch": {
         "command": "npx",
         "args": ["-y", "@_davideast/stitch-mcp", "serve"]
       }
     }
   }
   ```
3. **Using Stitch Skills**:
   You can install the official Google Labs Stitch Skills (`google-labs-code/stitch-skills`) to pull design tokens and screens from Stitch projects directly into the React `shadcn/ui` components:
   - `stitch::generate-design`: Generates screens and exports design tokens.
   - `stitch::code-to-design`: Exports current React components back into Stitch for visual review.

