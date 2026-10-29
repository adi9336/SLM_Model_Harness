# Product specification — SLM_Model_Harness (Autonomous ETL & DevOps Test Execution Agent)

> Status: approved. A practical, 100% on-premise demonstration of a Two-Level Agent Architecture for autonomous ETL pipeline and DevOps test execution.

## Problem

Data analysis, ETL transformations (loading CSVs, cleaning dates/currency, joins, aggregation, deduplication), and DevOps file operations are repetitive, multi-step, and error-prone. Single small language models (SLMs) running locally on consumer hardware fail at complex tool calling due to parameter hallucination, argument cross-wiring, and infinite exploration loops. Cloud LLM APIs cannot be used when data sensitivity and strict privacy boundaries apply. The user requires a **100% local, reliable, and observable AI Agent** that autonomously analyzes, plans, executes, and verifies these tasks with measurable repeatability for an upcoming Tech Fest presentation.

## Users

- Primary User: Engineer, data practitioner, or presenter demonstrating autonomous agent execution.
- Audience: Tech Fest attendees and evaluators seeking robust on-premise agent architectures.

## Functional requirements

- FR-1: Given a natural-language ETL or DevOps task specification (with input files and target criteria), the agent inspects requirements, determines dependencies, and plans execution.
- FR-2: The agent executes the Two-Level Agent Architecture:
  - Level 1 (Reasoner): Qwen 3 8B decomposes complex requests into single atomic steps (`ACTION: <tool_name> | <intent>`). Tool JSON schemas are never passed to the reasoner, preserving a lean context window.
  - Level 2 (Formatter): xLAM receives only the selected tool's schema, formatting the atomic intent into structured, verbatim JSON arguments.
- FR-3: The agent implements deterministic harness guards:
  - Schema Validation: Rejects and repairs malformed calls before execution.
  - De-dup Guard: Detects identical repeated calls and nudges the planner forward.
  - Query-Streak Guard: Prevents read-only exploration loops.
  - Completion Guard: Verifies the required deliverable exists on disk before concluding.
- FR-4: The agent executes operations against a deterministic local backend (SQLite and local filesystem) and scores output against ground-truth benchmarks.
- FR-5: The agent provides an audience-facing presentation mode (`demo_runner.py`) rendering formatted step badges, agent thought panels, and execution scorecards.

## Non-functional requirements

- NFR-1: 100% On-Premise: All inference, data storage, and execution occur locally on the host PC (`127.0.0.1:11434` Ollama). No data leaves the machine.
- NFR-2: Ground-Truth Reliability: The agent achieves 100% match rate across standard benchmark tasks (date cleaning, multi-table joins, currency casts, deduplication).
- NFR-3: Stage Resiliency: The demonstration runner provides a verified fallback mode so the presentation never crashes due to latency, hardware throttling, or missing dependencies.

## Constraints

- Platform: Windows (Intel / NVIDIA hardware).
- Model Serving: Local Ollama serving `qwen3:8b` and `xlam2:1b-fc-q4` (or local compatible endpoint).
- Runtime: Python 3.11+. SQLite standard library.
- Scaffolding: Genesis Kit specification and task lifecycle.

## Non-goals

- No cloud API dependencies (Tinker, OpenAI cloud, Anthropic cloud).
- No web frontend or GUI (clean terminal interface via Rich).
- No multi-tenant authentication or cloud deployment.

## Acceptance criteria

- AC-1: The agent completes benchmark task `t001_clean_dates` and produces `out.csv` matching `expected.csv` exactly.
- AC-2: The agent completes benchmark task `t002_join` (multi-table relational join) and matches ground truth.
- AC-3: The agent executes task `t007_rename_dedupe` and `t010_file_organize` without getting trapped in loops.
- AC-4: Genesis CLI validates the project specification and tracks task proof.

## Risks

- Model cold start or CPU throttling during live demo: Mitigated via single-step progress pacing and `--demo-mode` safety runner.
- Formatting error on complex join keys: Mitigated via xLAM single-schema gating and deterministic repair pass.

## Open questions

- None.
