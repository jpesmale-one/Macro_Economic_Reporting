# Macro_Economic_Reporting

Repository for macro market analysis: the written reads, the data behind
them, the pipelines that pull that data, and the record of what was
decided and why.

**Purpose:** analyse currency strength to form a **bias**, and spot **key
levels**. There is **no money path in this repo** — no lot sizes, entry
prices, stops, targets, or order instructions. "AUD is strongest, tone
favours AUD longs" is in scope; "buy 0.5 lots at 0.6520, stop 0.6480" is
not, and belongs in TRTM. Locked as LD-4 in [STATE.md](STATE.md).

**Key levels are in scope; execution roles are not** (LD-5). A level is an
observation about price structure — "4,435 is the swing high, rejected
twice" — and it is published with its timeframe, lookback, type, and touch
history. The same number labelled "stop above 4,435" is an instruction, and
that is the line. Price and chart data come from the
[TradingView MCP](https://github.com/tradesdontlie/tradingview-mcp): read
and draw are allowed, alerts and `replay_trade` are not. See
[.claude/rules/levels-and-tradingview.md](.claude/rules/levels-and-tradingview.md).

It runs the same ways of working as the sibling project
`TRTM_EA_Project` — same gate vocabulary, same seal discipline, same
STATE.md / handover / continuation mechanics. What differs is the anchor.
TRTM anchors on a compiled build and its sha; this repo anchors on a
**dated edition and a data vintage**. The two repos never share state,
backlog, or decisions.

---

## Start here

| File | What it is |
|---|---|
| [CLAUDE.md](CLAUDE.md) | The protocol. Read fully before working. |
| [STATE.md](STATE.md) | Current state: edition header, locked decisions, established facts, disposition, parked list. The single authority on where things stand. |
| [.claude/rules/analysis-evidence.md](.claude/rules/analysis-evidence.md) | Evidence and audit rules. Loads automatically in `reports/`, `docs/`, `data/`. |
| [docs/CONTINUATION_TEMPLATE.md](docs/CONTINUATION_TEMPLATE.md) | Fill and paste as the first message of a new session. |
| [docs/HANDOVER_TEMPLATE.md](docs/HANDOVER_TEMPLATE.md) | Written at the end of every working session. |
| [docs/REPORT_TEMPLATE.md](docs/REPORT_TEMPLATE.md) | Starting point for a new analysis edition. |

---

## Layout

```
reports/       Dated analysis editions (YYYY-MM-DD_<topic>.md). Sealed
               editions are never rewritten in place.
data/raw/      Landed source data. IMMUTABLE. Each file has a
               <file>.provenance.md sidecar. Revisions land as a new
               vintage alongside, never as an overwrite.
data/derived/  Reproducible from raw. Safe to regenerate.
pipelines/     Code that pulls and transforms. Its arrival fires
               trigger T1 (see below).
docs/          Templates, handovers, plans, matrices, checklists.
.claude/       Protocol enforcement: rules and hooks.
```

---

## How the work runs: two tracks

**LEAN track — the default.** A written analysis runs the three-step
publish gate:

1. **SOURCED** — every claim carries series ID, release date, and as-of
   date. Estimates and derivations are labelled, never dressed as prints.
2. **RECOMPUTED** — every derived number is recomputed and the arithmetic
   stated. A mismatch against a published figure is a finding.
3. **SEALED** — Jeff says so. Only then is the edition citable by later
   work.

**FULL track — the six-gate ladder**, dormant until it is triggered.
Triggers are mechanical, not judgment calls, and are named by number when
they fire:

- **T1** — code that produces a number Jeff will act on
- **T2** — an **executable instruction** (a size, an entry, a stop, an
  order). In this repo T2 is a **scope alarm**, not an escalation path:
  the right response is to stop and say the artifact left scope. Bias
  does *not* fire it.
- **T3** — anything scheduled, automated, or re-run unattended
- **T4** — a revision to an already-sealed edition's conclusions

In practice the full ladder gets reached by **T3 and T1** — automation and
reliability — not by T2.

The full ladder is: locked decisions → sealed scenario matrix → confirmed
code plan → build → evidence-audited verification → seal and handover.
No gate is skipped, and none is entered before the previous one is sealed.

---

## The hard rules (short version)

- No number is published without its source and vintage.
- No derived figure is published without being recomputed, arithmetic
  shown.
- `data/raw/` is immutable — corrections land as a new vintage.
- A sealed edition is history; revisions become new editions.
- Forecasts, nowcasts, and consensus are never presented as prints.
- Every macro read states its confidence and its falsifier.
- No credentials in the repo.

Full detail in [CLAUDE.md](CLAUDE.md).

---

## Enforcement

Two hooks back the rules that cost money if broken:

- `guard_raw.sh` (PreToolUse) — denies edits to an existing file under
  `data/raw/`. Creating a new vintage file is allowed; overwriting a
  landed one is not.
- `check_provenance.sh` (PostToolUse) — flags any data file written under
  `data/` without its `.provenance.md` sidecar.

`.claude/settings.json` adds deny rules for `data/raw/` and `.env`, sets
plan mode as the default, and **denies the TradingView MCP tools that LD-5
puts out of bounds** — `replay_trade`, `alert_create`/`alert_delete`, the
Pine and watchlist/layout mutators, and the raw `ui_*` automation tools
(which could otherwise drive the UI to do any of the above). Project deny
beats the global allow, so the boundary holds by configuration rather than
by good intentions. The deny is project-scoped: other sessions are
unaffected.

## TradingView MCP

Already configured — **no clone or install needed**. The server is
registered globally in `~/.claude/.mcp.json` pointing at a single shared
checkout of [tradesdontlie/tradingview-mcp](https://github.com/tradesdontlie/tradingview-mcp),
and every project on this machine inherits it. This repo also ships a
project-level [.mcp.json](.mcp.json) so the dependency is declared rather
than assumed.

Requires TradingView Desktop running with `--remote-debugging-port=9222`.
Verify with `tv_health_check`; if it fails, launch via
`scripts\launch_tv_debug.bat` in the server checkout, or the `tv_launch`
tool.

---

## Resuming a session

Fill [docs/CONTINUATION_TEMPLATE.md](docs/CONTINUATION_TEMPLATE.md) from
STATE.md's header and the latest handover, then paste it as the first
message. The session begins by verifying `git status`, the STATE.md
header, and `git log` against each other — aligned in one line, or a full
stop on mismatch. Disk and git are truth; conversation memory never
overrides them.
