# Reliability Guide — What Generalizes From the ETL Agent Harness

This is the takeaway manual from building a reliable tool-calling agent. It started
as two small local models (an 8B reasoner + a 1B formatter) driving SQL/CSV tools,
and went through many failures before it became trustworthy. The most useful thing
that came out is not the code — it is the list of *patterns* that made it reliable.
Most of them are not specific to ETL. You can reuse them to build a different agent
for a different job and get most of the same reliability.

The simple way to think about it: **LLM agents fail in four predictable ways —
they forget a field, they repeat a step, they stop too early, or they write a wrong
value. Every reliable harness is just a set of checks that catch those four things
before they matter.**

---

## Part 1 — The Generalized Toolkit

These are the patterns worth porting into any agent project. Each one is a small
deterministic check around a fallible model call.

### 1. Validate every tool call against its schema

Before executing anything, check the arguments against the tool's JSON schema.
If required fields are missing or types are wrong, refuse the call and say why.
This is the foundation everything else builds on — without it you cannot tell a
good call from a bad one.

*Failure class: a dropped or malformed parameter.*

### 2. Repair, don't just retry

When validation fails, do not blindly try again — that just re-rolls the same dice.
Instead, re-prompt the formatter with three pieces of information: the exact error,
the original request, and what recently happened in the tool environment. The model
can usually infer the missing value (for example, "you forgot `table` — recent tools
touched `orders`"). Try the repair once; if it still fails, let the caller (the
planner) see the error and re-issue — never fail silently.

*Failure class: a required parameter dropped by a weak formatter.*

### 3. Detect no-progress loops

A planner can get stuck pressing the same elevator button: calling the identical
tool with identical arguments twice in a row (sometimes many times). Catch exactly
that — same tool, same args — and interrupt with "you already did this, move on".
Caveat: this is only safe for tools that do not have side effects or are idempotent.
Before porting, check the tool semantics; a financial transaction must never be
deduplicated.

*Failure class: the planner looping on a completed step.*

### 4. Never believe "done" — verify the deliverable

Planners frequently announce completion before the work is finished: they do the
main step and forget to save, or they save half the files and call it a day. The
harness knows what deliverable the task requires. Refuse to accept "done" until
that artifact actually exists — a file, a database row, a directory with the
expected number of files. This single rule converts model promises into verifiable
facts.

*Failure class: premature completion.*

### 5. Give each task a step budget that fits the job

A two-step task and a forty-step batch job need different budgets. A fixed small
cap kills big jobs; a fixed big cap hides hangs. Make the budget per-task and
scale it with the job size, with a hard ceiling as the safety net.

*Failure class: running out of steps mid-job, or looping forever.*

### 6. Keep the reasoner's context lean, and one tool per call

The reasoning model should see a short menu of tool names and parameter names —
never the full JSON schemas. Schemas are large and irrelevant to planning; names
are enough. And when a formatter is a small model, hand it exactly one tool at a
time. Multi-tool prompts make small models cross-wire arguments between tools.

*Failure class: guessing argument names, small-model confusion.*

### 7. Put concrete value examples in schema descriptions

Models of every size abbreviate or guess values when nothing shows them the shape:
a file path becomes a bare filename, "Customer ID" becomes "Customer". A concrete
example in the parameter description ("`tasks/t004_cast_aggregate/orders.csv` —
never a bare filename") fixes most of this. Examples are cheap and help every model
we tested — local and API.

*Failure class: plausible-but-wrong values.*

### 8. Audit everything from day one

Write an append-only log of every step: tool name, arguments, validation result,
success or error, timestamp. Reliability is a number you measure, not a feeling.
With timestamps this log also gives you latency, tool-call counts, and failure
breakdowns for free, and it turns "the model failed" into "the model failed
on join_tables with a wrong column name, three times, at 14:02".

*Failure class (indirect): unmeasurable, undiagnosable systems.*

### 9. Fail loudly at every level, never silently

Every branch of the loop must produce visible feedback: validation error, repair
attempt, planner re-issue, or a final explicit "could not format this call". A
silent no-op is the worst failure mode because nothing — not the model, not the
user, not the logs — knows it happened.

*Failure class: silent partial execution.*

---

## Part 2 — What Was Project-Specific (port the principle, not the constants)

These parts of the harness were shaped by this project's ETL toolset and tasks.
They worked here; treat them as examples of a general principle, not drop-in rules.

| This project did | Why it was specific | The general principle to port |
|---|---|---|
| Query-tool repeat guard: `list_files`/`inspect_file`/`preview_table` called 3× in a row → nudge | The tool allowlist and threshold 3 fit this toolset; another agent might legitimately call a read-only search tool ten times | Repeated read-only calls with no visible new information = no-progress signal. Make the tool list and threshold configurable |
| Made `out_table` required on `dedupe`/`filter_rows` | Those exact tool schemas | Parameters that silently control side effects must be required, never optional-with-silent-default |
| "Full paths always" rule + path examples | This world is file-based | Put format examples in schemas; enforce strict formats in the system prompt |
| Step budgets 12 / 30 / 60 | Chosen per task | Budget scales with job size; numbers come from the domain |
| Repair/de-dup/completion nudge wording | Written for this task grammar | The checks are generic; adapt the messages to your domain |
| Low formatter temperature (0.2), single-tool formatting | Operational | Small formatters: low temperature, one call at a time |
| `FORMATTER_FALLBACK` switch | This harness's ACTION-line grammar | Design formatters as optional; define what happens when one is unavailable |

The one genuinely hybrid piece is the query-tool repeat guard: the *pattern* is
general (repeat-read-only = no progress), but the *constants* were tuned here.

---

## Part 3 — The Eight Rules, Distilled

1. Validate every call against its schema.
2. On failure: repair with error + intent + context, then degrade to the planner.
3. Detect no-progress (identical repeats) — only for idempotent tools.
4. Never accept "done" until the deliverable exists and is complete.
5. Budget steps per task, hard-capped.
6. Lean reasoner context; one tool per call for small formatters.
7. Examples in schemas for anything with a strict format.
8. Log everything; fix reliability in the harness, never by blaming the model.

---

## Part 4 — How These Rules Were Proven

Each pattern earned its place by catching a failure on a *different task* than the
one it was created for, and by reproducing across different models:

- The completion guard (created for a missing table save) also caught a task that
  moved only 8 of 12 files.
- The de-dup guard (created for a load_csv loop) underlies the fix for a directory
  re-listing exploration loop.
- Wrong-value errors reproduced on four different models (Qwen, Llama, Gemma,
  DeepSeek) in three different harness configurations — proving they are a
  property of models and agents in general, not of one setup.

What has NOT been proven: porting these to a completely different tool domain
(HTTP, search, email). The rules are generic; the *implementations* are shaped by
this project, and that is the honest limit of this guide.