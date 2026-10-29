# Autonomous ETL Pipeline & DevOps Test Execution Agent

> **Two-Level Agent Architecture for 100% Reliable, On-Premise Tool Calling**  
> Built for Tech Fest live presentation. Scaffolded with **Genesis Kit**.  
> Features both an **Audience Terminal CLI** and a **FastAPI Interactive Web Dashboard**.

---

## 1. Executive Summary & The Core Breakthrough

### The Problem
Single small language models (SLMs, e.g., 1B–8B parameters) running locally on consumer hardware fail when given complex multi-step tool calling tasks:
1. **Multi-Entity Confusion:** When presented with multiple files or complex schemas, small models cross-wire arguments (swapping input/output paths or column names).
2. **Value Distortion:** Models abbreviate paths (emitting `sales.csv` instead of `tasks/t001_clean_dates/sales.csv`).
3. **Exploration Loops:** Planners repeatedly execute read-only queries instead of progressing to mutations.
4. **Premature Completion:** Planners declare "Done" before persisting the required output artifact.

### The Solution: The Two-Level Architecture
```
                                [ User Request / ETL Task ]
                                             │
                                             ▼
                 ┌────────────────────────────────────────────────────────┐
                 │     LEVEL 1: REASONER & PLANNER (Qwen 3 8B Local)      │
                 │   Sees tool names and parameters ONLY (lean context)   │
                 │   Decomposes task into 1 atomic intent at a time:      │
                 │   ACTION: clean_dates | table=sales, column=sale_date  │
                 └───────────────────────────┬────────────────────────────┘
                                             │ (Single Atomic Intent)
                                             ▼
                 ┌────────────────────────────────────────────────────────┐
                 │    LEVEL 2: FORMATTER & EXECUTOR (xLAM 1B Local)       │
                 │   Gated with ONLY that 1 tool's schema (no confusion)  │
                 │   Translates intent into verbatim, typed JSON call     │
                 └───────────────────────────┬────────────────────────────┘
                                             │
                 ┌───────────────────────────┴────────────────────────────┐
                 │              DETERMINISTIC HARNESS GUARDS              │
                 │   • Schema Validation & Repair Pass (catches errors)   │
                 │   • De-dup Guard (kills infinite loops)                │
                 │   • Completion Guard (proves artifact exists on disk)  │
                 └───────────────────────────┬────────────────────────────┘
                                             │
                                             ▼
                                [ Deterministic SQLite & FS ]
                                             │
                                             ▼
                         [ 100% Ground-Truth Verification Match ]
```

---

## 2. Repository Structure

```
SLM_Model_Harness/
├── backend/                  # FastAPI Backend & Agent Engine
│   ├── automation/           # Atomic ETL & DevOps tools + SQLite datastore
│   ├── static/               # Built production React bundle (served by FastAPI)
│   ├── tasks/                # 11 Benchmark evaluation scenarios (t001–t011)
│   ├── tests/                # Automated pytest unit tests (19 passed)
│   ├── agent.py              # Two-Level Agent Orchestrator (Qwen 8B + xLAM 1B)
│   ├── config.py             # Tinker Cloud API & Local Ollama configuration
│   ├── demo_runner.py        # Rich Terminal CLI presentation runner
│   ├── server.py             # FastAPI Web Server with Server-Sent Events (SSE)
│   └── requirements.txt      # Python dependencies
├── frontend/                 # Modular React + TypeScript application
│   ├── src/components/ui/    # shadcn/ui components: Button, Card, Badge, Tabs, etc.
│   ├── src/components/       # Domain views: Header, Sidebar, Stream, Scorecard
│   ├── package.json          # React, Vite, Tailwind CSS, Lucide icons
│   └── vite.config.ts        # Vite configuration (proxies to FastAPI :8000)
├── .env.example              # Environment variables template
├── pytest.ini                # Pytest configuration
├── README.md                 # Full technical and presentation guide
└── STITCH_SETUP.md           # Google Stitch MCP integration guide
```

---

## 3. Quickstart & Installation

### Step 1: Install Python Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 2: (Optional) Configure Tinker API or Ollama
- Copy `.env.example` to `.env` if you wish to customize models.
- If you have `TINKER_API_KEY` set in your environment, Qwen 8B reasoning is automatically offloaded to the cloud!
- If no keys or models are configured, the built-in **Rehearsal Demo mode** executes automatically so live stage presentations never fail.

---

## 4. Running the Live Demo

### Option A: Modern Web Dashboard (FastAPI + React shadcn/ui)
Launch the server from the project root:
```bash
py backend/server.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser to view:
- Interactive scenario selector (Clean Dates, Relational Join, Currency Cast, Deduplication, File Reorganization).
- Real-time animated step stream (Analyze $\rightarrow$ Qwen 8B $\rightarrow$ xLAM 1B $\rightarrow$ Datastore).
- Active reliability guard status.
- Instant 100% ground-truth scorecard and output data table preview.

### Option B: Terminal Presentation CLI (Rich Console)
Run the audience presentation CLI:
```bash
py backend/demo_runner.py
```
*(Interactive menu with direct options 1–5 or `[A]` to run all scenarios).*

Direct CLI flags:
```bash
# Run specific scenario
py backend/demo_runner.py --task tasks/t001_clean_dates

# Run full benchmark evaluation suite
py backend/demo_runner.py --all

# Run with live cloud / local models
py backend/demo_runner.py --live
```

### Option C: Frontend Development (HMR)
```bash
cd frontend
npm install
npm run dev
```
*(Runs on `http://localhost:5173` proxying to FastAPI on port 8000).*

---

## 4. Tech Fest Stage Presentation Script

### Slide 1: The Problem with AI Agents in Data & DevOps
> *"Everyone wants autonomous agents to do ETL and DevOps pipelines on-premise. But when you run a small local model (1B–8B), it either hallucinates column names, swaps file paths, or loops 12 times reading files without doing the work."*

### Slide 2: The Two-Level Architecture
> *"We solved this by dividing labor:  
> 1. We keep our reasoning model (**Qwen 8B**) clean: it never sees full JSON schemas. It only emits plain natural-language single steps.  
> 2. We give our formatter model (**xLAM 1B**) exactly ONE schema at a time. It cannot mix up parameters because it never sees the other tools!  
> 3. We wrap both in deterministic harness guards that catch loops and verify deliverables."*

### Slide 3: Live Demonstration
1. Open `http://localhost:8000` on the projector.
2. Select **ETL: Date Standardization** or **ETL: Multi-Table Relational Join**.
3. Click **Execute Pipeline Agent**.
4. Point out the live stream cards:
   - **Yellow Card:** `[1/4 ANALYZING]` — Agent parses input requirements and target deliverables.
   - **Cyan Card:** `[2/4 LEVEL 1 QWEN 8B]` — High-level intent decomposition.
   - **Green Card:** `[3/4 LEVEL 2 xLAM 1B]` — High-fidelity parameter formatting.
   - **Scorecard Banner:** `[4/4 100% EXACT MATCH]` — Verified against expected benchmark ground truth.

---

## 5. Automated Verification & Testing

Run the complete automated unit test suite:
```bash
py -m pytest tests/ -v
```

Check Genesis software-factory lifecycle:
```bash
node C:\Users\Adi\Desktop\genesis-kit\tools\genesis.mjs status .
```
