# Reliability Kit — for rebuilding this agent in another project

This folder is the portable part of the Two-Level Agent project. Copy it into a
new project and you have the failure knowledge plus the check list, without the
ETL-specific code.

**Setup this kit assumes:** a reasoning model (8B-class, e.g. Qwen) + a small
formatter model (1B-class, e.g. xLAM) served locally via Ollama, where the
reasoner decomposes requests and the formatter writes the tool calls — so tool
schemas never enter the reasoner's context.

- [`RELIABILITY_GUIDE.md`](RELIABILITY_GUIDE.md) — the full plain-language guide:
  generalized patterns vs project-specific choices.
- [`XLAM_FAILURES.md`](XLAM_FAILURES.md) — every formatter failure mode observed
  and the guard that fixed it.
- [`GENERALIZATION.md`](GENERALIZATION.md) — what generalizes from this experiment
  vs what is project-specific (issues AND guardrails).

---

# The Important Changes, Ranked

Everything below is what turned the harness from 33% to 100% reliability. Build in
this order.

## Tier 1 — architecture essentials (must have)

1. **Single-tool restriction.** The reasoner decomposes a task into one atomic
   step at a time; the formatter receives exactly ONE tool schema per call.
   Without this, a 1B model cross-wires arguments between tools (this one change
   was worth 33% → 100%).
2. **Lean reasoner context.** The reasoner sees a short menu of
   `name(param1, param2)` one-liners — never full JSON schemas. Keeps context
   small, stops arg-name guessing.
3. **Low formatter temperature (~0.2).** Makes the 1B's output deterministic
   instead of creative.
4. **Schema validation on every call.** The foundation all guards stand on — you
   cannot repair what you cannot check.

## Tier 2 — reliability guards (86% → 100%)

5. **Repair pass.** On validation failure, re-prompt the formatter with the exact
   error + the original intent + recent tool results, so it can infer the missing
   value. One retry, then degrade to letting the planner re-issue. Kills: dropped
   required parameters.
6. **Completion guard.** Refuse to accept "done" until the task's deliverable
   actually exists — a file, or a directory containing the expected number of
   files. Kills: premature completion (missing save, partial moves) — the most
   common real-world agent failure.
7. **De-dup guard.** Same tool + same args twice in a row → nudge "you already did
   this, move on". Only for idempotent tools. Kills: planner loops (12× repeated
   load).
8. **Per-task step budget.** Budget scales with job size (2-step task vs 40-step
   batch), hard-capped. Kills: multi-step jobs dying on a fixed small cap.
9. **Query-repeat guard.** A read-only tool called 3× in a row with ANY args →
   nudge "use what you have, move on". Make the tool list and threshold
   configurable for your domain. Kills: exploration loops (re-listing a directory
   instead of working).

## Tier 3 — cheap wins (add whenever convenient)

10. **Value examples in schema descriptions** + format rules in the system prompt.
    A concrete example ("tasks/.../orders.csv — never a bare filename") kills
    wrong-value errors. Helps every model, API models included.
11. **Side-effect parameters required.** A parameter that silently controls where
    output goes (e.g. `out_table`) must be required — optional-with-silent-default
    corrupts state invisibly.
12. **Formatter-optional switch.** A flag that disables the formatter fallback and
    instead nudges the reasoner to re-emit strict key=value calls. Lets the same
    harness run single-model (API) without 404ing on a missing formatter.
13. **Audit log with timestamps** (validation / execution / errors, one JSON line
    per event). Measures accuracy, latency, tool-call counts and failures — makes
    debugging a look-up, not a guess.
14. **Env-driven model config.** `PRIORITY_MODEL` / `FORMATTER_MODEL` / base URL
    as environment variables. The harness becomes model-agnostic with zero code
    changes (Qwen → Gemma → DeepSeek was a one-liner).

## The 30-second summary

Build the split (1–4), bolt on the five guards (5–9), add the config and audit
layer (10–14). A new project starting from this kit should land around 86% and
close to ~100% once the guards are re-tuned to its own tools — and the failure
itself becomes the measurement, because the audit log tells you exactly what to
fix next.