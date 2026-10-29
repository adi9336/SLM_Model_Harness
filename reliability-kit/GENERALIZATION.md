# What Generalizes From This Experiment

A classification of everything this project hit, split into what is **general**
(any LLM agent with tool calling, especially with a small formatter, will hit it)
and what is **project-specific** (this project's skin: file-based ETL tasks,
SQLite datastore, Qwen+xLAM split).

**Short answer: the issues are mostly general. The guardrails are general patterns
wearing project-specific clothes (~70% reusable as-is).**

---

## Part 1 — Issues found: general vs specific

### General (will hit ANY LLM agent)

| Issue | Why it is general |
|---|---|
| Small formatter drops required params (`aggregate` missing `table`) | Instruction-following weakness of small models — every small-formatter architecture |
| Formatter value errors (bare `orders.csv` instead of full path) | Small models fill boxes with plausible-looking *wrong* values, not just missing ones |
| Multi-tool schema confusion | Small models degrade sharply as schema count grows; single-tool restriction is the standard answer |
| Planner loops on a completed step (12× `load_csv`) | No progress detection in LLM agents — repeats calls, burns the step budget. Big models do this too |
| Planner stops before the final save | Premature completion — the #1 real-world agent failure ("agent thinks it is done") |
| One "100%" run is an anecdote | LLM non-determinism — re-runs are the measurement |
| Repair only fires on *validation* errors, not *wrong values* | Schema checks catch missing/typed params; semantic value errors surface only at runtime |

### Project-specific (this project's skin)

| Issue | Why specific |
|---|---|
| CWD-relative file paths in tool args | Tasks are file-based; a general agent would have the harness resolve paths itself |
| `out_table` dropped on `dedupe`/`filter_rows` | Lives in *these* tool schemas (side-effectful write tools). The underlying issue — "optional side-effect params are dangerous" — IS general |
| SQLite quirks: TEXT ranks > REAL (textual `> '100'` compare), `$1,234.56` CSV quoting | SQLite-as-datastore + this data shape; a Postgres/API agent would not hit them |
| Ollama server crashes mid-benchmark | Infra flakiness of one machine, not the architecture |
| `spec["out_path"]` threaded into the agent as `required_output` | Tied to the benchmark's task-file format |

---

## Part 2 — Guardrails: general vs project-specific

### General (reusable as-is in any agent project)

| Guardrail | General form |
|---|---|
| **Single-tool restriction** | One intent → exactly ONE tool schema per call. Universal rule for small formatters |
| **Repair pass** | Validate → re-prompt formatter with (error + original intent + recent tool context). Any JSON-schema-validated agent; a standard production pattern |
| **De-dup guard** | Same tool + same args twice in a row → "you already did this". Works on pure/idempotent tools; needs adaptation for non-idempotent tools (a bank transfer should run twice if genuinely intended) |
| **Completion guard** | Refuse "done" until the deliverable actually exists. The general principle: *verify the artifact, never trust the word "done"* |
| **Harness-only fixes** | Fix reliability with deterministic guards, never model changes |

### Project-specific (would need reshaping elsewhere)

| Fix | Specific form | The general principle behind it |
|---|---|---|
| `out_table` made required on `dedupe`/`filter_rows` | These two tool schemas | Fail loudly on ambiguous/side-effect-bearing params |
| Full-path examples in `load_csv`/`inspect_file` schemas + "full paths always" prompt rule | File-tool world | Put concrete value examples in schema descriptions |
| `required_output` piped from the task spec | This benchmark's `spec["out_path"]` | Task-spec-driven agents (cf. Anthropic TaskSpec) |

---

## Part 3 — Still open

- **Repair pass itself can fail** — a single-shot repair is not guaranteed; today it
  degrades to returning the error to the planner, who re-issues correctly. Never
  fatal, but wastes a step. General fix: 2-shot repair or planner-first fallback.
- **Value-level errors cannot be repaired by schema validation** — a wrong file
  path is only caught at runtime by the tool. General fix: harness-level value
  checks (e.g. canonicalize/resolve paths before executing).
- **Small n** — 3–5 runs per task; larger n needed for tight confidence intervals.
- **No real business dataset plugged in yet** — the data is synthetic, shaped like
  real work but not real.

---

## Part 4 — The reusable rule set (distilled)

1. Small formatters: one schema per call, never a batch.
2. Validate every call against its schema; on failure, repair with
   error + intent + context — never a blind retry.
3. Detect no-progress (identical repeat) and force progress.
4. Never believe "done": verify the required artifact exists.
5. Make side-effect-bearing parameters required.
6. Give schemas concrete value examples where a strict format exists.
7. Re-run: one clean run is an anecdote; the re-run is the measurement.
8. Fix reliability in the harness, not the model.