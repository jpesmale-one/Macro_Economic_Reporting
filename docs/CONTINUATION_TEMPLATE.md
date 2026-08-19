# Macro Economic Reporting - Session continuation prompt template

Standard way to resume this project after a session break. At each break
(when the handover is written), fill the `{{PLACEHOLDERS}}` below from
STATE.md's header + the handover you just wrote, then paste the filled
block as the FIRST message of the next session.

Keep the fixed scaffolding (resume protocol, gate order, provenance
boundary) verbatim - it protects against cold-start drift. Only the
`{{...}}` change.

---

## Template (copy, fill the placeholders, paste)

```
Resume Macro Economic Reporting. Run the section 0 resume protocol FIRST:
git status + STATE.md header + `git log --oneline -5`, all compared
(expect edition {{EDITION}}, data_asof {{DATA_ASOF}}, track {{TRACK}}).
Report aligned in one line, or STOP on mismatch.

Then read {{HANDOVER_FILE}} and STATE.md. {{STATUS_LINE}}

{{RESUME_TASK}}

Track discipline holds: LEAN by default (publish gate = sourced ->
recomputed -> sealed). Escalate to the FULL six-gate ladder the moment a
section-2 trigger fires, and name it by number when it does - T1 code
producing an actionable number, T2 trading decision, T3 automation, T4
revision to a sealed conclusion. One question per message, concrete
numbers, your rec each; record every decision + rejected alternatives in
STATE.md's locked-decisions log. Raw data is immutable - revisions land
as a new vintage, never an overwrite. Recompute every derived figure and
state the arithmetic before you publish it or call anything PASS.

{{OPEN_NOTES}}
```

---

## Placeholder key (where each value comes from)

| Placeholder | Fill from |
|---|---|
| `{{EDITION}}` / `{{DATA_ASOF}}` / `{{TRACK}}` | STATE.md header (`edition:` / `data_asof:` / `track:`). |
| `{{HANDOVER_FILE}}` | The handover just written, e.g. `docs/HANDOVER_YYYY-MM-DD_<topic>.md`. |
| `{{STATUS_LINE}}` | One line on where things stand, e.g. "2026-08 CPI edition sealed; Q3 growth read is next." |
| `{{RESUME_TASK}}` | The concrete next action. Two shapes: **(a) new item** - "Open {{ITEM}}. It is LEAN track / it fires T{{N}} so open Gate 1. Work its open sub-decisions ONE at a time, starting with the most foundational." **(b) resume mid-pipeline** - "Resume {{ITEM}} at Gate {{N}} ({{WHERE}}, e.g. matrix rows Mx-My unsealed / checklist at S-x). Do not re-plan sealed rows." |
| `{{OPEN_NOTES}}` | Carry-forwards: unpushed commits, open findings, pending revisions that may fire T4, parked items that may have un-parked. Delete if none. |

---

## Current instance - pre-filled for the NEXT break

```
Resume Macro Economic Reporting. Run the section 0 resume protocol FIRST:
git status + STATE.md header + `git log --oneline -5`, all compared
(expect edition none, data_asof n/a, track LEAN, and TWO local commits -
c9a9fbb "Initial Project Set-up" then the scope-boundary commit). Report
aligned in one line, or STOP on mismatch.

Then read docs/HANDOVER_2026-08-12_repo_established.md and STATE.md. The
repo scaffold landed 2026-08-12 and the SCOPE is locked: this project
analyses currency strength to form a BIAS and to spot KEY LEVELS, with NO
MONEY PATH (LD-4). There is NO analysis content, NO edition, and NO data
landed yet - that is expected, session 1 was governance only.

Five decisions are locked - LD-1 (WoW ported from TRTM), LD-2 (mechanical
escalation), LD-3 (ForexFactory + TradingEconomics are SCHEDULE-only,
never authoritative for a value), LD-4 (purpose: bias, no money path -
this rewrote T2 into a scope alarm), LD-5 (key levels in scope,
TradingView MCP is the price source; read + draw allowed, alert_create/
delete and replay_trade are not). Do NOT re-litigate these.

F-1 is OPEN and must not be quietly closed: TradingEconomics publishes
UNRELEASED figures in the ACTUAL field - a forecast wearing a print's
label, reproduced daily in my own reports. Column-checking CANNOT detect
it; only an independent schedule check against the issuing agency can. It
closes on evidence (an ingest that flags the mismatch), never on
inspection.

FIRST TASK THIS SESSION: I am giving you my draft of how I want this
project to turn out. READ IT FIRST and work from it. It may reshape or
supersede the open items O-1 (output format), O-3 (cadence vs seal
ritual), O-4 (which of the nine reference sections survive), and O-5
(automated price pulls) recorded in docs/REFERENCE_DAILY_ARTIFACT.md -
so do not start building against those before reading my draft. Treat
docs/REFERENCE_DAILY_ARTIFACT.md as REFERENCE, NEVER SPEC.

Track discipline holds: LEAN by default (publish gate = sourced ->
recomputed -> sealed). Escalate to the FULL six-gate ladder the moment a
section-2 trigger fires, and name it by number when it does - T1 code
producing an actionable number, T2 EXECUTABLE INSTRUCTION (a scope alarm
here - stop and say so, do not open Gate 1), T3 automation, T4 revision
to a sealed conclusion. In practice expect T3 and T1, not T2. One
question per message, concrete numbers, your rec each; record every
decision + rejected alternatives in STATE.md's locked-decisions log. Raw
data is immutable - revisions land as a new vintage, never an overwrite.
Recompute every derived figure and state the arithmetic before you
publish it; a key level is recomputed by naming the bars that formed it.

Carried forward: BOTH commits are LOCAL ONLY - origin/main has nothing at 
all. Pushing is my call, ask before doing it.
```
