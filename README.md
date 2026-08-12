# Macro_Economic_Reporting

Repository for macro market analysis: the written reads, the data behind
them, the pipelines that pull that data, and the record of what was
decided and why.

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
- **T2** — an artifact feeding a trading decision (a money path)
- **T3** — anything scheduled, automated, or re-run unattended
- **T4** — a revision to an already-sealed edition's conclusions

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

`.claude/settings.json` adds deny rules for `data/raw/` and `.env`, and
sets plan mode as the default.

---

## Resuming a session

Fill [docs/CONTINUATION_TEMPLATE.md](docs/CONTINUATION_TEMPLATE.md) from
STATE.md's header and the latest handover, then paste it as the first
message. The session begins by verifying `git status`, the STATE.md
header, and `git log` against each other — aligned in one line, or a full
stop on mismatch. Disk and git are truth; conversation memory never
overrides them.
