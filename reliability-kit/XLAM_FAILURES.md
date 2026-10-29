# xLAM Formatter — Failure Log

Every failure mode observed in the 1B formatter (xLAM-2) so far, how it was
found, and the deterministic fix that landed.

**The pattern:** xLAM's failures are *form-filling* errors — a missing box or a
wrong value — never reasoning errors. All of them are caught and repaired by
harness guards, with **zero model changes**.

---

## 1. Multi-tool confusion (v2 era)

**Symptom:** given several tool schemas at once, xLAM mixes up or guesses
argument names — low arg fidelity.

**Fix:** single-tool restriction — one intent → exactly ONE tool schema per call.

**Status:** solved by design (v3).

## 2. Drops a required parameter

**Symptom:** `aggregate` called with `agg_column`, `agg_func`, `group_by`,
`out_table` but **no `table`** → validation failed (t004).

**Fix:** repair pass — on validation failure, re-prompt xLAM with the specific
error, the original intent, and recent tool results so it can infer the missing
value.

**Status:** mostly solved; the repair itself sometimes fails (see #5), and then
Qwen re-issues the call correctly on its own.

## 3. Drops an optional parameter

**Symptom:** `dedupe`/`filter_rows` called without `out_table` → ran in-place
**silently** (no validation error), later `save_table("clean")` failed with
"no such table: clean".

**Fix:** made `out_table` **required** on both tools, so a dropped output table is
caught by validation and repaired instead of corrupting the source.

**Status:** solved.

## 4. Wrong value for a parameter (path fidelity)

**Symptom:** `load_csv` path emitted as bare `orders.csv` instead of
`tasks/t004_cast_aggregate/orders.csv` → FileNotFoundError, desynced the run.

**Fix:** full-path examples in the `load_csv`/`inspect_file` schemas + a
"file paths are ALWAYS full paths" rule in Qwen's prompt.

**Status:** solved (no wrong-path loads after the fix).

## 5. Repair pass itself can fail

**Symptom:** after a repair re-prompt, xLAM still returns the call missing
`table`; the harness falls back to returning the validation error to Qwen, who
re-issues the call correctly.

**Status:** always recovers via Qwen; wastes a step but never fatal. This is the
only residual flake still visible in the audit logs.

---

## Related — but NOT xLAM

Qwen-side failures are a different class: *planner* issues.

- **Looping on a completed step** (re-loading the same file 12×) → de-dup guard.
- **Stopping before writing the output file** (t004 completion flake) → completion guard.

## Summary

| # | Class | Example | Guard |
|---|-------|---------|-------|
| 1 | Multi-tool arg mix-up | wrong args with many schemas | single-tool restriction |
| 2 | Missing required param | `aggregate` without `table` | repair pass |
| 3 | Missing optional param | `dedupe` without `out_table` | made required |
| 4 | Wrong value | bare filename instead of full path | schema examples + prompt rule |
| 5 | Repair failure | still missing `table` after re-prompt | Qwen fallback re-issue |

xLAM forgets a box. Qwen repeats or stops early. The harness double-checks both —
"is anything missing? did we just do this? does the output exist?" — and that is
where the reliability comes from.