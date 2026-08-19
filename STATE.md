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
#   SIX DECISIONS LOCKED session 1: LD-1 (WoW ported), LD-2 (mechanical
#   escalation), LD-3 (calendar sources are schedule-only), LD-4 (PURPOSE:
#   bias, no money path), LD-5 (key levels in scope, TradingView MCP is the
#   price source), LD-6 (MCP boundary enforced in settings).
#
# 2026-08-19 - PROJECT DIRECTION RECEIVED. Jeff's draft landed in Idea_dump/
#   (Project_Plan.txt, Watch_list.txt, Sources.txt,
#   Macro_economic_indicators.txt), committed VERBATIM as input - never edited.
#   THREE MORE DECISIONS: LD-7 (LD-4 REAFFIRMED - Jeff declined to loosen the
#   boundary, so report section 4 was reshaped instead; my recommendation to
#   amend was REJECTED), LD-8 (carry is a swing-ranking tiebreak, not a
#   filter), LD-9 (P-2 CLOSED - TradingEconomics is the primary macro value
#   source, defended by the mandatory phantom-Actual guard).
#   DERIVED SPEC: docs/REPORT_SPEC.md is now the authoritative build spec for
#   the daily report. Where it and the draft differ, the SPEC wins and says
#   why. STILL NO EDITION PUBLISHED and no data landed.
#   ONE finding: F-1, corrected on evidence, STILL OPEN (the guard is a
#   procedure, not tooling).

## Environment note
Analysis-only repo. NO MONEY PATH by design (LD-4) - this project analyses
currency strength to form a BIAS and to spot KEY LEVELS. It never emits lot
sizes, entries, stops, targets, or orders; those belong to TRTM. T2 is
therefore a SCOPE ALARM here rather than an escalation path.
Sibling project TRTM_EA_Project holds the EA and its own separate ledger;
the two never share state, backlog, or decisions.
TradingView MCP is configured (~/.claude/.mcp.json + project .mcp.json) and
is the price/chart source per LD-5, CONNECTION VERIFIED 2026-08-12. Read and
draw allowed; replay_trade, alert_create/delete, Pine/watchlist/layout
mutators and raw ui_* are DENIED in project settings (LD-6).
Deliverable: a DAILY market sentiment report, refreshed at the start of the
trading session - spec in docs/REPORT_SPEC.md, source draft in Idea_dump/.
All times PHT (UTC+8); TradingView chart timezone must match.
Watchlist: 21 forex pairs (OANDA) + XAUUSD + BTCUSD. USOIL and 7 indices are
CONFLUENCE-ONLY inputs and never appear as tradeable instruments.

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

### LD-6 - LD-5's MCP boundary is ENFORCED in project settings, not just written (2026-08-12)
CONTEXT: LD-5 said alert_create/delete and replay_trade require an explicit
in-the-moment ask. Inspection of ~/.claude/settings.json showed all 78
TradingView tools AUTO-ALLOWED globally, including those three. LD-5 was a
rule with nothing behind it - exactly the gap TRTM closes with "the rules
explain the wall, the hook IS the wall".
DECISION: The restricted tools are DENIED in this project's
.claude/settings.json. Project deny beats global allow, so the boundary now
holds by configuration rather than by my compliance. Denied here:
  - EXECUTION-SHAPED: replay_trade.
  - UNATTENDED / OUTLIVES THE SESSION: alert_create, alert_delete.
  - MUTATES JEFF'S SAVED WORK: pine_set_source, pine_save, pine_new,
    pine_compile, pine_smart_compile, watchlist_add, watchlist_add_bulk,
    watchlist_remove, layout_new.
  - BLIND UI PUPPETEERING: ui_click, ui_mouse_click, ui_type_text,
    ui_keyboard, ui_evaluate. These can do anything the UI can do,
    including the above, which makes them a bypass of every other deny.
READ and DRAW remain allowed: data_get_*, quote_get, symbol_*, chart_get_*,
chart_set_* (navigation), draw_shape, draw_list, draw_remove_one,
capture_screenshot, tv_health_check.
SCOPE OF THE DENY: PROJECT-LEVEL ONLY. Jeff's other Claude Code session and
the global config are untouched - a tool he legitimately uses elsewhere is
not taken away from him there.
IF A DENIED TOOL IS GENUINELY NEEDED: Jeff asks in the moment and can allow
it for that action. The deny converts a silent capability into a decision.
REJECTED:
  (a) Trusting LD-5 as written, since I would simply follow it. Rejected:
      an unenforced rule survives exactly until a session where it is not
      re-read. The whole point of the TRTM hook pattern is that the wall
      does not depend on the agent remembering.
  (b) Narrowing the global allowlist instead. Rejected: it would change
      behaviour in Jeff's other session, which is out of scope for this
      repo's decisions and is his call, not mine.
RATIONALE: A boundary that exists only in prose is a preference. A boundary
in settings.json is a boundary.

### LD-7 - LD-4 REAFFIRMED against the project draft; section 4 reshaped instead (2026-08-19)
CONTEXT: Idea_dump/Project_Plan.txt section 4a asks the playbook to "propose
Forex Instruments for Swing Trades INCLUDING THEIR ENTRY AND TARGET LEVELS",
and 4c asks to monitor open swings for "already a loss or already reached the
target". Both collide head-on with LD-4 (no money path) and LD-5 (a level is
an observation; an EXECUTION ROLE assigned to it is not). Presented to Jeff as
a three-way choice: amend LD-4, keep it and reshape section 4, or split into
two layers. My recommendation was to AMEND, on the reasoning that the draft
plainly wants tradeable output and an explicit decision is not drift.
DECISION: JEFF CHOSE TO KEEP LD-4. The boundary stands exactly as locked. The
REPORT is reshaped to fit the boundary; the boundary is not moved to fit the
report. My recommendation was rejected and the record says so.
WHAT SECTION 4 (Conviction Playbook) THEREFORE IS:
  IN: which instruments are aligned (fundamental bias AND technical structure
      agreeing), the direction of that alignment, the conviction ranking with
      its reasoning, the KEY LEVELS around the instrument (support/resistance/
      swing/range boundary) published to the LD-5 evidence standard, and the
      falsifier - the observation that would void the alignment.
  OUT: entry price, target price, stop level, "buy here / sell there", risk
      per trade, lot size, R-multiples, and any label assigning a level an
      execution role.
  THE TEST, applied per line: does this sentence describe what the market has
      done, or instruct what to do about it? The first ships; the second does
      not.
SECTION 4c (monitor open swing trades) IS DROPPED. Tracking the P/L state of a
position is position management, which is the clearest money-path activity in
the whole draft. What REPLACES it and preserves the intent: the report
re-states each prior alignment CURRENT STATUS as analysis - does the
fundamental+technical alignment STILL HOLD, has the structure broken, has the
falsifier fired. That answers "is this thesis still good" without ever
tracking a trade.
SECTION 4a/4b CADENCE SURVIVES INTACT: Monday = swing-horizon alignments,
Tuesday-Friday = intraday-horizon alignments. The horizon distinction is
about which timeframe structure and which drivers dominate, not about
issuing orders, so it is untouched by this decision.
REJECTED:
  (a) AMEND LD-4 to allow entries/targets (MY RECOMMENDATION). Rejected by
      Jeff. Recorded in full because a future session WILL re-encounter
      section 4a as written and must not "helpfully" reinstate it: the draft
      predates this decision, and this decision wins.
  (b) Split into a separate execution layer. Rejected: more machinery to
      maintain for a boundary that a reshaped section 4 already holds.
RATIONALE (Jeff call, my reading of it): the draft was written before the
boundary existed. Given the choice between loosening a deliberate constraint
and adjusting a document, adjust the document. The analysis loses nothing
that matters - alignment plus levels plus falsifier is the whole analytical
content; the entry label was never the insight.

### LD-8 - Carry is a TIEBREAK for swing ranking, never a filter (2026-08-19)
CONTEXT: Project_Plan.txt section 4d says "For swing trades give more weight to
carry aligned trades to minimize swap fees." The watchlist is cross-heavy
(AUDCAD, AUDNZD, NZDCAD, NZDCHF, CADCHF, EURCHF, GBPCHF...) where positive
carry and fundamental/technical direction frequently point OPPOSITE ways -
so "more weight" needs a defined tiebreak or it becomes improvisation.
DECISION: Rank swing-horizon alignments by FUNDAMENTAL + TECHNICAL CONVICTION
FIRST. Carry enters only to separate candidates of SIMILAR conviction.
Negative carry is disclosed as a HOLDING COST on the alignment, never a veto.
MECHANICS: every swing-horizon line in section 4 shows the carry SIGN
(positive/negative/flat) derived from the two policy rates in section 2, and
names the cost direction. When conviction is close and carry breaks the tie,
the report SAYS that carry broke the tie - the tiebreak is visible, not
silent.
REJECTED:
  (a) Carry as a hard filter excluding negative-carry pairs from swing
      consideration. Rejected: swap is small next to a wrong directional
      call, and on a cross-heavy watchlist a hard filter would routinely
      discard the highest-conviction alignment on the board.
  (b) Show both with no weighting, resolve manually each time. Rejected: it
      is not a decision, it is a deferral - and it would have to be re-made
      every week.
RATIONALE: Carry is a cost input, not a directional signal. It should shade a
close call, never overrule the analysis.
NOTE: carry applies to SWING horizon only. Intraday alignments (Tue-Fri) hold
no position overnight, so swap is not a factor and carry is omitted there.

### LD-9 - P-2 RESOLVED: TradingEconomics is the primary macro VALUE source (2026-08-19)
CONTEXT: P-2 (canonical value source) has been parked since session 1. LD-3
made calendar sources SCHEDULE-only after F-1, which pushed toward an
agency-API spine. But Idea_dump/Sources.txt names tradingeconomics.com as the
macro data source - and, critically, states the guard against F-1 itself:
"If the data is tagged as Actual but the report schedule is on future date
then it is the Previous Actual Data not the current one."
DECISION: TradingEconomics is the PRIMARY macro value source, as Sources.txt
specifies. P-2 is CLOSED. The defence is the rule Jeff wrote, now MANDATORY:
  THE PHANTOM-ACTUAL GUARD - before using any TE figure, compare the row
  RELEASE SCHEDULE DATE against now. If the scheduled release is in the
  FUTURE but an Actual is displayed, that Actual is the PREVIOUS period
  print, NOT the current one. Use it as Previous, never as the new release,
  and label it so.
Central bank sites named in Sources.txt (federalreserve.gov, ecb.europa.eu,
bankofengland.co.uk, boj.or.jp, rba.gov.au, rbnz.govt.nz, bankofcanada.ca,
snb.ch) are the AUTHORITY for interest-rate decisions and policy language -
TE is not authoritative there. investing.com and investinglive.com are
corroboration for news and confluence, never a primary value.
RELATIONSHIP TO LD-3: LD-3 stands unchanged for the CALENDAR role (what
releases when). LD-9 additionally admits TE as a VALUE source for macro
prints, which LD-3 alone forbade - the difference is that the phantom-Actual
guard is now mandatory and mechanical, which is what LD-3 was protecting
against in the first place.
F-1 STAYS OPEN. The guard is a PROCEDURE, executed by me each morning. It is
not tooling and it can be forgotten under time pressure. F-1 closes only on
an automated check that flags schedule-date-vs-now mismatches. Do not mark
it closed because the guard exists.
REJECTED:
  (a) TE + FRED cross-check on high-impact US prints. Rejected by Jeff -
      correctly, for now: FRED covers US only, and the report spans 8
      currencies where FRED adds nothing. Revisit only if the guard is
      observed to fail on a US print.
  (b) TE alone with no guard. Never on the table - F-1 is reproduced daily.
RATIONALE: Use the source the workflow already uses, and make the defence
that was already working into a written, mandatory step.

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
| Project direction draft | RECEIVED + COMMITTED VERBATIM 2026-08-19 | Idea_dump/ (4 files). Jeff's INPUT - never edited by me. Derived spec lives in docs/REPORT_SPEC.md. |
| Daily report SPEC | DELIVERED 2026-08-19 | docs/REPORT_SPEC.md. Authoritative build spec; where it and the draft differ the SPEC wins (LD-7). O-4 RESOLVED - the draft's 6 sections supersede the reference artifact's 9. |
| First macro edition | NOT STARTED | Spec is ready. Blocked only on O-1 (output format) and O-3 (seal cadence). |
| Data source set | SETTLED - LD-3 + LD-9 | Calendar role = FF + TE (schedule). VALUE = TradingEconomics primary + mandatory phantom-Actual guard; central banks authoritative for rates. P-2 CLOSED. |
| Fundamental scoring model | SPECIFIED 2026-08-19 | 8 currencies x 6 categories with explicit thresholds, from Idea_dump/Macro_economic_indicators.txt. Transcribed into REPORT_SPEC.md section 3. NOT yet exercised on real data. |
| Calendar ingest | NOT STARTED | Fires T1 + T3. Access method for FF is P-4. |
| Key levels / TradingView MCP | IN SCOPE per LD-5, CONNECTION VERIFIED 2026-08-12 | tv_health_check: cdp_connected true, VANTAGE:EURCHF 15m, api_available true. chart_get_state + data_get_ohlcv both returned live data. NO CLONE NEEDED - server is registered globally and inherited. LD-5's restricted tools are now DENIED in project settings (they were auto-allowed globally - see LD-6). |
| Pipeline code | NOT STARTED | Fires T1 when it lands. |

---

## PARKED LIST
Items deliberately not being worked, with the reason. Parked is not
abandoned - each entry says what would un-park it.

- P-1: Report cadence and standing coverage (weekly? monthly? event-driven
  around releases?). UN-PARKS when Jeff states the intended rhythm; it
  shapes the reports/ layout and the continuation template.
- ~~P-2: Canonical source set and access method.~~ **CLOSED 2026-08-19 by
  LD-9.** TradingEconomics is the primary macro value source, defended by
  the mandatory phantom-Actual guard; central bank sites are authoritative
  for rate decisions and policy language.
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
