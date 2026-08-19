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
Resume Macro Economic Reporting. Run the section 0 resume protocol FIRST.

DO NOT compare against a hardcoded commit list - it goes stale the moment
anything commits, and it did exactly that on 2026-08-19 (F-8). Instead run:

    git log --oneline -5
    git rev-list --count HEAD
    git status -sb
    git log --oneline origin/main..HEAD | wc -l    # unpushed count

Then compare THOSE against STATE.md's header, which is the single authority
on edition identity. Aligned = say so in one line. A mismatch between the
header and the repo is a real STOP; a mismatch between this prompt and the
repo just means this prompt is older than the repo - read the newest
handover in docs/ and trust that instead.

Read docs/REPORT_SPEC.md FIRST - it is the authoritative build spec and
supersedes the Idea_dump draft wherever they differ. Then STATE.md.

THIRTEEN DECISIONS ARE LOCKED. Do not re-litigate. The ones that bind
daily work:
  LD-4  PURPOSE: currency strength -> BIAS + KEY LEVELS. NO MONEY PATH.
        No lot sizes, entries, stops, targets, orders. T2 is a SCOPE
        ALARM here, not an escalation path.
  LD-9  TradingEconomics is the primary macro VALUE source, defended by
        the MANDATORY phantom-Actual guard.
  LD-10 Ship as HTML artifact AND commit to reports/YYYY/QN/. The .md is
        the sealed source of truth; the .html is the deliverable.
  LD-12 Daily = LIGHT seal (P1+P2 still mandatory). Weekly = FULL seal,
        and only a FULL seal promotes to the established-facts ledger.
  LD-13 WEIGHTED scoring: Inflation 3, Employment 2, Production/Spending/
        Trade 1, split evenly among a currency's indicators in each
        category. Range +8.00 to -8.00. Generated from
        pipelines/score_model.py so tables and tally cannot drift.

SEVEN FINDINGS ARE OPEN. F-1 is the one that can cost money:
TradingEconomics publishes UNRELEASED figures in the ACTUAL field. Column-
checking CANNOT detect it - the phantom matches the forecast by
construction. ONLY a schedule check against the issuing agency catches it.
Run the guard FIRST, every run, before using any TE figure.

F-5, F-6 and F-7 share ONE shape and it is the most important lesson in
the repo: an ABSENCE asserted from a SINGLE failed attempt. Nine
indicators "unavailable" (all published), three central banks "blocking"
(all fine with browser headers), batch_run "broken" (called with invalid
action names). TWO OF THREE WERE MY OWN INPUTS. Before writing that
anything is unavailable, escalate and say WHICH STEP failed -
pipelines/fetch_headers.md has the ladder.

STATE OF THE 2026-08-19 EDITION: r9, UNSEALED, P1 PASS / P2 PASS. All 70
whitelist indicators published; all 8 central bank rates read primary;
Fear & Greed with all 7 components. CADCHF (+8.00, a perfect score) and
AUDCHF carry technical levels. 14 of 21 pairs remain unread - batch_run
is genuinely defective, single-symbol reads are the workaround.

FIRST TASK THIS SESSION:
{{PICK ONE}}
 (a) SEAL the 2026-08-19 edition as a fundamental read with technical
     confirmation on the two instruments carrying the call - or hold it
     for the remaining 14 pairs. My call either way; ask me.
 (b) RUN TODAY'S EDITION. It is a fresh day: re-run the phantom-Actual
     guard, re-verify the TE calendar timezone against one already-
     released event (do NOT assume +8h), re-pull all 70 indicators,
     re-score, and check whether AU employment (was due Thu 09:30 PHT
     with a phantom 76.3K showing) actually landed and what it printed.
 (c) Close the 14-pair coverage gap on the existing edition by pulling
     them one symbol at a time.

Track discipline: LEAN by default (sourced -> recomputed -> sealed).
Escalate to the FULL ladder when a section-2 trigger fires and name it by
number - T1 code producing an actionable number, T2 EXECUTABLE
INSTRUCTION (scope alarm: stop and say so), T3 automation, T4 revision to
a sealed conclusion. Expect T3/T1, not T2. One question per message,
concrete numbers, your rec each. Record every decision + rejected
alternatives in STATE.md's locked-decisions log. Raw data is immutable.
Recompute every derived figure and state the arithmetic; a key level is
recomputed by naming the bars that formed it.

ALL TIMES PHT (UTC+8). TradingEconomics calendar is UTC, so PHT = UTC+8 -
but VERIFY it each run against a known release rather than assuming; F-2
was a 4-hour error that corrupted the phantom guard in both directions.

Carried forward: as of the 2026-08-19 wrap, everything was PUSHED -
origin/main == HEAD == 8128a3c. Do not assert push state from this line;
CHECK it (`git log --oneline origin/main..HEAD`). Pushing remains my call:
ask before pushing anything new.
```
