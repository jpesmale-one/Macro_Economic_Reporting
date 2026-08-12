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
(expect edition none, data_asof n/a, track LEAN). Report aligned in one
line, or STOP on mismatch.

Then read STATE.md. The repo scaffold landed 2026-08-12 - CLAUDE.md
protocol, STATE.md manifest, evidence rules, raw-data + provenance hooks,
templates, directory skeleton - ported from TRTM_EA_Project with the gate
anchor changed from "build + sha" to "edition + data vintage". There is NO
analysis content, NO edition, and NO data landed yet. LD-1 and LD-2 are
locked; P-1 (cadence/coverage), P-2 (canonical source set), and P-3
(legacy artifact handling) are PARKED awaiting my input.

First task: decide P-2, the canonical source set and access method - it is
the foundational one, because it defines what "traceable to a release"
means for every later artifact. Give me options with concrete series
examples and your rec, one question at a time.

Track discipline holds: LEAN by default (publish gate = sourced ->
recomputed -> sealed). Escalate to the FULL six-gate ladder the moment a
section-2 trigger fires, and name it by number when it does - T1 code
producing an actionable number, T2 trading decision, T3 automation, T4
revision to a sealed conclusion. One question per message, concrete
numbers, your rec each; record every decision + rejected alternatives in
STATE.md's locked-decisions log. Raw data is immutable - revisions land
as a new vintage, never an overwrite. Recompute every derived figure and
state the arithmetic before you publish it or call anything PASS.

Carried forward: nothing is committed yet - the scaffold is unstaged in
the working tree and origin/main has no commits. Committing and pushing
is my call, ask before doing it.
```
