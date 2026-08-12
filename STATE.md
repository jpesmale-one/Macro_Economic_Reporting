# MACRO SYNC MANIFEST - update with EVERY delivery
# Resume protocol (repo-based; see CLAUDE.md section 0). First action on
# resume: git status + this header + `git log --oneline -5`, all compared.
# Match = aligned in one line. Disk + git are truth, never conversation or
# auto memory.

edition: none
date: 2026-08-12
data_asof: n/a
track: LEAN (no section-2 trigger has fired yet)

# 2026-08-12 - REPO ESTABLISHED. Ways-of-working scaffold ported from
#   TRTM_EA_Project (CLAUDE.md protocol, STATE.md manifest, rules, hooks,
#   handover + continuation templates, directory skeleton). NO analysis
#   content yet, NO edition published, NO data landed.
#   The gate ladder is LEAN by default; the full six-gate ladder is written
#   and dormant, triggered per CLAUDE.md section 2 (T1 code-producing-numbers,
#   T2 executable instruction / SCOPE ALARM, T3 automation, T4 sealed-
#   conclusion revision). In practice the full ladder is expected to be
#   reached by T3 and T1, not T2 - see LD-4.
#   FIVE DECISIONS LOCKED this session: LD-1 (WoW ported), LD-2 (mechanical
#   escalation), LD-3 (calendar sources are schedule-only), LD-4 (PURPOSE:
#   bias, no money path), LD-5 (key levels in scope, TradingView MCP is the
#   price source). ONE finding: F-1, corrected on evidence.

## Environment note
Analysis-only repo. NO MONEY PATH by design (LD-4) - this project analyses
currency strength to form a BIAS and to spot KEY LEVELS. It never emits lot
sizes, entries, stops, targets, or orders; those belong to TRTM. T2 is
therefore a SCOPE ALARM here rather than an escalation path.
Sibling project TRTM_EA_Project holds the EA and its own separate ledger;
the two never share state, backlog, or decisions.
TradingView MCP is configured (~/.claude/.mcp.json, 78 tools) and is the
price/chart source per LD-5: read and draw allowed; alert_create/delete and
replay_trade are NOT, absent an explicit in-the-moment ask.

---

## LOCKED DECISIONS LOG
Every decision that must never be re-litigated. Format: ID, date, the
decision, the rejected alternatives, the rationale. New evidence may
reopen an entry - nothing else may.

### LD-1 - Ways of working ported from TRTM (2026-08-12)
DECISION: This repo runs the same protocol as TRTM_EA_Project - same gate
vocabulary, same seal discipline, same STATE.md/handover/continuation
mechanics - with the gate ANCHOR changed from "compiled build + sha" to
"dated edition + data vintage", and with the heavy gates dormant until a
section-2 trigger fires.
REJECTED:
  (a) Full six-gate ladder on every artifact from day one. Rejected: most
      early work here is written analysis with no money path; matrix and
      checklist files on a one-page macro note is ceremony that would get
      abandoned, and an abandoned protocol is worse than a lean one.
  (b) A fresh lightweight protocol unrelated to TRTM. Rejected: Jeff moves
      between the two repos in the same week; a different rhythm in each
      imposes a context-switch cost and invites cross-contamination of
      habits. Same vocabulary in both is the point.
RATIONALE: Keep one set of habits across both projects. Pay the ceremony
cost only where a number can cost money.

### LD-2 - Trigger-based escalation, mechanical not discretionary (2026-08-12)
DECISION: Escalation from LEAN to FULL track is decided by the four named
triggers in CLAUDE.md section 2, stated explicitly by number when one
fires. Not by in-the-moment judgment about whether a change "looks big".
REJECTED: Case-by-case judgment on each artifact. Rejected: the failure
mode of a lean default is a money-path change slipping through because it
arrived inside a small edit - the same hazard CLAUDE.md guards against in
TRTM. A mechanical trigger removes the discretion that would be abused
under time pressure.
RATIONALE: The trigger must fire on the CHANGE's nature, not on its size.

### LD-3 - Calendar sources are SCHEDULE authorities, never VALUE authorities (2026-08-12)
CONTEXT: ForexFactory has no accessible API. Trading Economics is reachable
but its Previous column is revised in place and sits adjacent to Actual -
see F-1. Jeff proposed using both as sources.
DECISION: ForexFactory and Trading Economics are ADOPTED, both of them, but
scoped to a SCHEDULE role only:
  - AUTHORITATIVE for: what releases when, release time and timezone,
    consensus/forecast, and the event calendar generally.
  - NEVER AUTHORITATIVE for: the value of a print that feeds an analysis
    conclusion or a position. That number comes from the issuing agency
    (FRED/BLS/Census/etc.), which carries a real vintage.
  - Where the two calendars DISAGREE (time, consensus, or a value), the
    disagreement is recorded as a finding, not silently resolved. Two
    sources exist to surface conflict, not to average it away.
  - Any value taken from a calendar for commentary is labelled with its
    source inline and marked UNVERIFIED until cross-checked against the
    agency print.
REJECTED:
  (a) Trading Economics as the single source. Rejected: no vintage, and
      F-1(b) means its Previous column cannot be trusted retrospectively.
      A single source also removes the cross-check that would have caught
      F-1 in the first place.
  (b) Scraping ForexFactory to replace the missing API. Rejected AS A
      VALUE SOURCE for the same vintage reason - a scraper returns today's
      rendered cell, not the print with its as-of. Not rejected outright
      as a SCHEDULE source; see P-4.
  (c) Dropping calendar sources and using agency APIs alone. Rejected:
      agencies publish the number but are poor at forward schedule and
      carry no consensus at all. Consensus-vs-actual is most of the
      trading signal around a release, so losing it defeats the purpose.
RATIONALE: Separate the two questions these sources answer. "When does it
land and what is expected" is what a calendar is genuinely good at. "What
was the number, as of when" is what a statistical agency is genuinely good
at. Conflating them is what produced F-1.

### LD-4 - PROJECT PURPOSE AND SCOPE BOUNDARY: bias, not execution (2026-08-12)
DECISION: This project exists to analyse CURRENCY STRENGTH in order to form
a BIAS. That is the whole purpose. There is NO MONEY PATH in this repo.
  IN SCOPE: relative currency strength, the drivers behind it, rate
  differentials and policy divergence, the event calendar, and a directional
  BIAS with its confidence and its falsifier.
  OUT OF SCOPE: lot sizes, entry prices, stop levels, take-profits, order
  instructions, risk-per-trade, position management, and anything that
  computes or recommends an amount of money at risk.
  THE LINE: "AUD is strongest, tone favours AUD longs" is IN SCOPE and runs
  LEAN. "Buy 0.5 lots AUDUSD at 0.6520, stop 0.6480" is OUT OF SCOPE - it
  does not get built here, on any track.
CONSEQUENCE FOR T2: T2 was originally written to fire on "sizing, BIAS,
entry/exit timing" - which would have fired on every single edition and made
the LEAN default meaningless. T2 is REWRITTEN to fire only on an EXECUTABLE
INSTRUCTION. Bias no longer triggers it.
CONSEQUENCE FOR THE FULL LADDER: it is now expected to be reached mainly by
T3 (automation) and T1 (code producing numbers) - a reliability concern -
rather than by T2. T2 in this repo is a SCOPE ALARM, not an escalation path:
the right response is to stop and say so, not to open Gate 1.
CONSEQUENCE FOR THE REFERENCE ARTIFACT: O-2 is RESOLVED. The existing §6
"Conviction Playbook" emits directional BUY/SELL calls per pair. As pure
directional bias with no size, level, or order, it stays in scope and lean.
It must NOT acquire entry/stop/target columns - that is the specific way
this repo would drift across the line, and it would drift one column at a
time.
REJECTED:
  (a) Keeping bias inside T2 and running the full ladder on every edition.
      Rejected: a daily product cannot carry a scenario matrix per edition;
      the protocol would be abandoned within a week, and an abandoned
      protocol is worse than a lean one.
  (b) Dropping T2 entirely, since there is no money path by definition.
      Rejected: the boundary needs an ALARM precisely because the artifact
      already contains directional calls (§6) and would drift toward levels
      naturally. A trigger that never fires still does work by being there.
RATIONALE: Analysis quality and execution safety are different problems.
This repo owns the first. TRTM owns the second. Keeping them apart is what
lets this project stay lean without lowering any bar that matters.

### LD-5 - KEY LEVELS are in scope; TradingView MCP is the price source (2026-08-12)
DECISION: Spotting KEY LEVELS is an explicit goal of this project and is IN
SCOPE. The TradingView MCP server (already configured at
~/.claude/.mcp.json, 78 tools, OHLCV + quote + drawing) is the price and
chart source for that work.
  IN SCOPE: identifying levels and saying WHY they matter - swing highs and
  lows, prior day/week/month H-L, round numbers, prior consolidation edges,
  gap boundaries, VWAP/session anchors, and levels that have been tested or
  rejected. Stating how many times a level was touched, when, and what
  happened there. Drawing those levels on the chart via MCP.
  OUT OF SCOPE (unchanged by this decision): assigning a level an EXECUTION
  ROLE. "Stop above 4,435", "entry on a break of 4,435", "target 4,500",
  "risk 20 points to 4,415".
THE DISTINCTION THAT MATTERS - the level is in scope, the ROLE is not.
The same number can be either:
  IN SCOPE:  "4,435 is the swing high; rejected twice, Mon and Tue."
  OUT:       "Stop above 4,435."
Identical figure. The first is an observation about price structure and is
verifiable from OHLCV. The second is an instruction. This is the way this
repo would most plausibly cross LD-4's line - not by adding a lot size, but
by quietly re-labelling a level as a stop.
LEVELS ARE EVIDENCE, NOT OPINION: a published level states the timeframe it
was derived from, the lookback window, and what happened at it (touch count
and dates). "Support at 4,373" with no derivation is not publishable - it
is unauditable, and P2 applies to a level exactly as it applies to a YoY
calculation. The recompute for a level is: name the bars that formed it.
MCP CONSTRAINTS (money-risk boundary, mirroring TRTM section 3a):
  - READ freely: data_get_ohlcv, quote_get, symbol_info, chart state,
    indicator values, screenshots.
  - DRAW: allowed for levels and annotation. It is display-only and touches
    no account.
  - NEVER: alert_create / alert_delete without Jeff asking in the moment
    (an alert is an unattended action that outlives the session), replay_trade
    (it places simulated orders and is execution-shaped), and anything that
    would modify Jeff's saved layouts or Pine scripts without him asking.
  - The MCP drives Jeff's OWN RUNNING CHART. Chart state is his workspace,
    not a scratchpad - do not reorganise panes, swap symbols, or clear
    drawings beyond what was asked.
REJECTED:
  (a) Treating key levels as out of scope because they resemble trade
      levels. Rejected: it would gut the project's stated purpose. Levels
      are structural observations; the analysis is incomplete without them.
  (b) Allowing levels to carry entry/stop/target labels since "Jeff knows
      it is not advice". Rejected: LD-4's boundary has to be legible in the
      ARTIFACT, not just in intent. A level labelled "stop" is an execution
      instruction regardless of who reads it, and the drift is one word
      wide.
RATIONALE: Where price has repeatedly turned is a fact. What to do about it
is a decision, and this repo does not make decisions with money attached.

---

## ESTABLISHED FACTS LEDGER
What the data has settled, with source and vintage. Only SEALED editions
contribute here. Later work may cite these; unsealed drafts may not be
cited as settled.

(empty - no sealed edition yet)

---

## DISPOSITION
| Item | Status | Notes |
|---|---|---|
| Repo scaffold | DELIVERED 2026-08-12 | Not yet committed at time of writing; commit is Jeff's call. |
| Reference daily artifact | RECORDED 2026-08-12 | docs/REFERENCE_DAILY_ARTIFACT.md. REFERENCE, NEVER SPEC - Jeff has said this project does things differently. Carries O-1..O-5 open decisions. |
| First macro edition | NOT STARTED | Needs scope: coverage, cadence, source set. O-4 asks which of the existing nine sections survive. |
| Data source set | PARTIAL - LD-3 locked | Calendar role settled (FF + TE, schedule only). VALUE source still open = P-2. |
| Calendar ingest | NOT STARTED | Fires T1 + T3. Access method for FF is P-4. |
| Key levels / TradingView MCP | IN SCOPE per LD-5 | MCP already configured (78 tools). Read + draw allowed; alerts and replay_trade are not. Rules in .claude/rules/levels-and-tradingview.md. |
| Pipeline code | NOT STARTED | Fires T1 when it lands. |

---

## PARKED LIST
Items deliberately not being worked, with the reason. Parked is not
abandoned - each entry says what would un-park it.

- P-1: Report cadence and standing coverage (weekly? monthly? event-driven
  around releases?). UN-PARKS when Jeff states the intended rhythm; it
  shapes the reports/ layout and the continuation template.
- P-2: Canonical source set and access method (FRED API, BLS, direct CSV,
  vendor). UN-PARKS at the first data pull; it is a Gate 1 decision
  because it determines what "traceable to a release" means in practice.
- P-3: Whether historical analysis produced before this repo existed gets
  back-filled as sealed editions or landed as unsealed archive. UN-PARKS
  when Jeff brings the first legacy artifact in.
- P-4: ForexFactory ACCESS METHOD, given there is no accessible API.
  Options not yet worked: scrape the calendar page, an unofficial
  third-party wrapper, a paid calendar vendor, or manual entry of the week
  ahead. LD-3 already confines it to the SCHEDULE role, so the money-path
  exposure is bounded whatever we pick - this is a reliability and
  maintenance question, not a correctness one. UN-PARKS at the first
  calendar ingest, which fires T1 + T3 and runs the full ladder.

---

## OPEN FINDINGS

### F-1 - Trading Economics publishes UNRELEASED figures as "Actual" (2026-08-12)
*** CORRECTED 2026-08-12 on evidence from the sample artifact (see F-1 note
at the end). The original entry blamed this on my column misreading. The
artifact shows the primary mechanism is a SOURCE defect, reproduced daily. ***

OBSERVED - REPRODUCED DAILY, NOT ANECDOTAL: the ShadowTradeMonitor daily
report (sample: "Market Sentiment - Wed 12 Aug 2026 (Early AM)") records in
its own §4 alerts and §2 caveat that TradingEconomics displayed US CPI,
Thursday's PPI, and Friday's Retail Sales as already "Actual" while all
three were still UNRELEASED. It further states this is "the same recurring
staleness pattern seen EVERY SINGLE DAY this reporting cycle" and "caught
every day this reporting cycle WITHOUT EXCEPTION". One instance is quoted
with a value: CPI shown as 3.5% YoY "actual" when BLS's own schedule had it
releasing that evening.

MECHANISM - THREE failure modes, in descending order of danger:
  (a) PHANTOM ACTUAL (PRIMARY, source-side). TE populates the ACTUAL field
      for events that have NOT yet released - apparently carrying the
      forecast/consensus value into the Actual slot. The number is not a
      print at all. It is a forecast wearing a print's label. Nothing in
      the row's own presentation reveals this; only an independent schedule
      check does.
  (b) PREVIOUS IS NOT STABLE (source-side). TE updates the Previous cell
      IN PLACE when a prior period is revised, without consistently marking
      original vs revised. A row read after the fact can report a Previous
      that was never the print at the time.
  (c) COLUMN MISREAD (mine). Actual/Previous/Consensus/Forecast render
      adjacent; reading the neighbouring cell puts the wrong period's
      number where the new print belongs. Real, but SECONDARY - and note
      that (a) makes (c) nearly undetectable by inspection, because the
      phantom Actual and the forecast agree by construction.

WHY IT MATTERS: (a) defeats the ordinary defence. A careful reader who
checks that they took the value from the ACTUAL column still gets a
forecast, and it will look confirmed. This is worse than a misread: it is
a number that asserts a release happened. (b) is the vintage problem
CLAUDE.md section 6 exists for - an in-place overwrite is exactly what the
raw-data immutability rule forbids.

WHY THE ARTIFACT DID NOT LOSE MONEY TO IT: the daily report already
defends correctly - it cross-checks against the issuing agency's schedule
(BLS), states the conflict in the report itself, and treats every
not-yet-released figure as a forecast. That defence is now protocol, not
habit: it is LD-3 plus the schedule-cross-check rule.

STATUS: OPEN, and now EVIDENCED rather than reported. Mitigation is LD-3
(calendar sources are never authoritative for a VALUE) plus the mandatory
release-occurred check: before any calendar "Actual" is used or repeated,
confirm against the issuing agency's own schedule that the release has in
fact happened. Hardening is a matrix row family when the calendar ingest
lands and fires T1/T3 - at minimum: phantom-Actual detection (release
timestamp vs now), column-alignment assertion, and revision detection that
treats a changed Previous as a vintage event rather than a correction.
NOT CLOSED BY LD-3. LD-3 removes the money-path exposure; it does not stop
a phantom Actual being repeated in commentary. Closes on evidence - an
ingest that flags the mismatch automatically - never on inspection.
