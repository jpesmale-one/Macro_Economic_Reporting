# Handover — 2026-08-12 — Repo established, scope locked

Session 1. The repository was empty (bare `.git`, remote configured, no
commits) at the start of this session.

STATE.md's header is the authority on edition identity. This file restates
it for convenience and goes stale the moment the next edition lands.

---

## 1. Resume protocol
Expect: edition `none`, data_asof `n/a`, track `LEAN`.
Run `git status` + STATE.md header + `git log --oneline -5`. Aligned = say
so in one line. Mismatch = STOP (CLAUDE.md section 0 step 2).

There is no analysis content, no edition, and no data landed. A resume that
finds any of those has found a real mismatch.

## 2. Where we are

The ways of working are ported from TRTM_EA_Project and the project's SCOPE
is locked. Nothing analytical has been produced yet — deliberately. This
session was governance only.

The shape that emerged: this repo analyses **currency strength to form a
bias, and spots key levels**. It has **no money path**. That single fact
reshaped the trigger design mid-session (see §5, LD-4) and is now the first
thing CLAUDE.md and README.md state.

Jeff is drafting a fuller statement of how he wants the project to turn out,
to be given at the start of the next session. **That draft is expected to
reshape or supersede parts of the open list below — do not treat O-1..O-5
as settled requirements, and do not start building against them before
reading it.**

## 3. Delivered this session

All LEAN track; no gate ladder was triggered. Nothing here is analysis, so
the publish gate does not apply.

| Item | What it is |
|---|---|
| `CLAUDE.md` | Protocol. 10 sections + a PURPOSE AND SCOPE preamble. |
| `STATE.md` | Manifest header, 5 locked decisions, facts ledger, disposition, parked list, 1 open finding. |
| `.claude/rules/analysis-evidence.md` | Evidence/audit rules. Scoped to `reports/`, `docs/`, `data/`. |
| `.claude/rules/levels-and-tradingview.md` | Key-level evidence standard + MCP boundary. |
| `.claude/hooks/guard_raw.sh` | PreToolUse. Denies edits to an existing `data/raw/` file. |
| `.claude/hooks/check_provenance.sh` | PostToolUse. Flags a data file with no `.provenance.md` sidecar. |
| `.claude/settings.json` | Plan mode default; deny rules for `data/raw/` and `.env`. |
| `docs/CONTINUATION_TEMPLATE.md` | Session-resume prompt, pre-filled for next session. |
| `docs/HANDOVER_TEMPLATE.md` | This file's template. |
| `docs/REPORT_TEMPLATE.md` | Lean-track edition skeleton with P1/P2/P3 mapped. |
| `docs/REFERENCE_DAILY_ARTIFACT.md` | The existing daily product, recorded as REFERENCE NEVER SPEC. |
| `README.md` | Purpose, layout, two tracks, hard rules, enforcement. |
| `.gitignore` / `.gitattributes` | Credentials excluded; data files exempt from EOL normalization. |
| Skeleton | `reports/`, `data/raw/`, `data/derived/`, `pipelines/` |

## 4. Empirical facts established

Nothing about markets — no data was landed and no edition written, so the
established-facts ledger in STATE.md is still empty and that is correct.

Two facts about the WORKING ENVIRONMENT were established by inspection:

- **TradingView MCP is live and configured** at `~/.claude/.mcp.json`
  (`node .../tradingview-mcp/src/server.js`), 78 tools, with ~80 tool
  permissions pre-allowed in `~/.claude/settings.json`. Covers OHLCV,
  quotes, symbol info, chart control, drawing, alerts, replay, screenshots.
- **No plugins are installed** (`~/.claude/plugins/` holds only a
  blocklist). WebFetch/WebSearch are built in and are the current web path.

## 5. Decisions locked

| ID | Decision |
|---|---|
| **LD-1** | Ways of working ported from TRTM, with the gate ANCHOR changed from "build + sha" to "edition + data vintage", heavy gates dormant. Rejected: full ladder day one; a fresh unrelated protocol. |
| **LD-2** | Escalation LEAN→FULL is MECHANICAL via numbered triggers, not in-the-moment judgment. Rejected: case-by-case judgment. |
| **LD-3** | ForexFactory + Trading Economics ADOPTED but SCHEDULE-ONLY. Never authoritative for a VALUE. Disagreement between them is a finding, not something to average. Rejected: TE alone; scraping FF as a value source; agency APIs alone (they carry no consensus). |
| **LD-4** | **PURPOSE: bias, NO MONEY PATH.** Forced a rewrite of T2, which originally fired on "sizing, BIAS, entry/exit" — that would have fired on every edition and made the lean default meaningless. T2 now fires only on an EXECUTABLE INSTRUCTION and is a SCOPE ALARM, not an escalation path. Rejected: keeping bias inside T2; deleting T2 entirely. |
| **LD-5** | KEY LEVELS in scope; TradingView MCP is the price source. The LEVEL is in scope, the EXECUTION ROLE is not — same number, different side of the line. Levels are evidence: timeframe, lookback, type, touch history, venue-prefixed symbol. Rejected: levels out of scope; levels carrying entry/stop/target labels. |

## 6. Publish-gate disposition

Not applicable — no analysis was produced. No P1/P2/P3 claims to audit.

**Closed on INSPECTION rather than evidence, and flagged as such:**
- The two hooks were **tested** (11/11 across new-vs-existing,
  relative-vs-Windows-absolute, raw-vs-derived, data-vs-docs) — that part
  is evidence, and it caught a real bug (below).
- Everything else in this delivery is prose and has never been exercised.
  **The protocol has not yet survived a single real edition.** Its first
  contact with actual work is the real test.

## 7. Remaining — WITH RECIPES

**R-1. Read Jeff's project-direction draft FIRST.** He is writing it between
sessions. It may reshape O-1..O-5 and parts of the reference doc. Read it
before opening any open item.

**R-2. O-4 — which sections survive.** The reference artifact has nine
(§1 strength, §2 rates+odds, §3 drivers, §4 alerts, §5 pair-by-pair,
§6 conviction playbook, §7 gold levels, §8 sessions, §9 news+calendar).
With currency strength and key levels as the two stated goals, §1/§3 and
§7 are core; the rest is open. Recipe: work it as a Gate 1 decision, one
question at a time, with a rec each. Expect Jeff's draft to answer much of
this already.

**R-3. O-1 — output format.** HTML artifact, repo markdown edition, or both
(markdown sealed in `reports/`, artifact rendered from it). Consequence:
decides whether `reports/` holds the source of truth or a copy.

**R-4. O-3 — cadence vs the seal ritual.** A daily edition sealed by
explicit word is a real daily cost. Options: light seal for dailies with
full sealing reserved for weekly/thematic editions, or seal every one.
Relates to P-1.

**R-5. O-5 / P-2 — price + macro data sourcing.** MCP is settled as the
price source (LD-5). Still open: whether it runs AUTOMATED (fires T1+T3 →
full ladder), and the canonical macro VALUE source (P-2, FRED favoured for
vintage support but never worked as a Gate 1 decision).

**R-6. P-4 — ForexFactory access method.** No API. LD-3 bounds it to the
schedule role, so this is a reliability question, not a correctness one.

## 8. Queued / parked

- **P-1** report cadence and standing coverage — un-parks on Jeff's rhythm.
- **P-2** canonical VALUE source set — un-parks at the first data pull.
- **P-3** legacy pre-repo analysis: sealed back-fill or unsealed archive.
- **P-4** ForexFactory access method — un-parks at the first calendar ingest.
- **O-1, O-3, O-4, O-5** in `docs/REFERENCE_DAILY_ARTIFACT.md`.
  **O-2 is RESOLVED** by LD-4 (§6 stays in scope and lean, with a standing
  guard: it must never acquire entry/stop/target columns).

## 9. Open findings

**F-1 — Trading Economics publishes UNRELEASED figures as "Actual".**
OPEN, and **corrected mid-session on evidence.** Originally recorded as my
misreading of the Previous column. The sample artifact showed the primary
mechanism is a SOURCE defect, reproduced daily: TE populates the ACTUAL
field for events that have not released — a forecast wearing a print's
label. Jeff's own report documents it as caught "every single day this
reporting cycle without exception", once with a value (CPI shown as 3.5%
YoY "actual" while BLS had it releasing that evening).

Why it matters: **column-checking cannot detect it**, because the phantom
Actual matches the forecast by construction. The only defence is an
independent schedule check against the issuing agency — now a hard rule in
`.claude/rules/analysis-evidence.md`.

Closes on EVIDENCE (an ingest that flags the mismatch automatically), never
on inspection. LD-3 bounds the exposure but does not close it.

## 10. Working agreements confirmed or changed

- **The protocol is maintained, not fixed.** Two rules were rewritten in
  their first hours: T2 (LD-4) and F-1's mechanism. Both changed because
  evidence contradicted them. Expect more of this on first contact with
  real work.
- **Jeff's existing daily artifact already practises several protocol
  habits** — schedule cross-checks against BLS, confirmed-vs-scheduled
  tagging, timezone declared once, public self-correction, revisions
  surfaced with the print, baselines stated, thin evidence self-flagged.
  The protocol is making an existing good instinct enforceable, not
  correcting bad work. Say so plainly rather than implying otherwise.
- **REFERENCE, NEVER SPEC** applies to the daily artifact, mirroring TRTM's
  handling of the Shadow reference EA.

## 11. Git state

Branch `main`, remote `origin` =
`https://github.com/jpesmale-one/Macro_Economic_Reporting.git`.

**TWO commits, both local-only, oldest first:**
1. `c9a9fbb` "Initial Project Set-up" — committed by Jeff mid-session,
   covering the scaffold as it stood at that point.
2. This session's second commit — the scope work: LD-4 (no money path,
   T2 rewritten), LD-5 (key levels + MCP boundary), F-1's correction to a
   source defect, the reference-artifact record, and this handover.

**NOTHING IS PUSHED** — `origin/main` has no commits at all. Pushing is
Jeff's call; ask before doing it.

Verify with `git log --oneline` and `git status`.
