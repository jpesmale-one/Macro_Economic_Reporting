---
paths:
  - "reports/**"
  - "docs/**"
  - "data/**"
---

# Analysis evidence rules (loads when working in reports/, docs/, data/)

These are the audit rules from CLAUDE.md section 5. The PUBLISH GATE
(section 3), the full-track DEFINITION OF DONE (section 4), and the
"never publish an unrecomputed figure" prohibition stay in CLAUDE.md and
always apply — this file is the detail, not the authority.

## Truth order
- The official RELEASE is truth. It outranks your model, your prior, the
  consensus, and any secondary reporting of it.
- Where two official sources disagree (e.g. a headline print vs the
  detail table it should sum to), that disagreement is a FINDING. Name
  both, show the arithmetic, do not silently pick one.
- When Jeff pastes data, read it before theorizing. If his premise and
  the data disagree, say so with the numbers — the data wins, kindly.

## Recompute before publishing
- RECOMPUTE every derived figure and state the arithmetic: YoY and MoM
  from index levels, annualized rates from the period rate, contribution
  decompositions, real from nominal minus breakeven, spreads, z-scores,
  diffusion counts. A figure you carried over from a source without
  recomputing is unverified — say so or drop it.
- Show the inputs, not just the result. "Core CPI 3.1% YoY" is not
  auditable; "324.812 / 315.036 - 1 = 3.10%" is.
- Rounding is declared, not assumed: state the decimals used and round
  once at presentation, never mid-chain.
- Unit and scale discipline: percent vs percentage point vs basis point,
  SA vs NSA, index vs level vs rate, monthly vs annualized. Most macro
  arithmetic errors are unit errors. Name the unit in the label.

## Vintage discipline
- Every series carries: source, series ID, release date, and the as-of
  date of the print used. A number without a vintage cannot be audited
  later, because the underlying will be revised.
- Revisions are first-class events. When a series is revised, record the
  old value, the new value, and the release that changed it. Never
  silently overwrite a stored number.
- A revision touching a SEALED edition's conclusion fires T4 — the
  sealed edition stands as history and a new edition names the change.
- Real-time vs current-vintage matters for any backtest or historical
  claim: if the analysis asks "what was knowable then", it must use the
  vintage available then, and say which it used.

## Absence and must-NOT claims
- A claim that something did NOT happen (no acceleration, no breadth
  deterioration, no divergence) requires checking for what is not there
  and saying so explicitly with the range checked. An unexamined absence
  is an assumption, not a finding.

## Inference hygiene
- Separate SIGNAL from NARRATIVE in the artifact, not just in chat. What
  the data shows gets its own statement; what you infer is labelled as
  inference.
- Correlation is not mechanism. If you assert a transmission channel,
  name it and say what would break it.
- Regime dependence: a relationship established in one regime is not
  portable. Say which regime the evidence came from.
- Every macro read states its CONFIDENCE and its FALSIFIER — the
  specific observation that would change the conclusion. A read with no
  falsifier does not get published.
- Base rates before stories. When a move is within normal variation, say
  so before explaining it.

## Carry-forward
- Conclusions from a sealed edition survive into later work only if the
  new data provably cannot affect them; say which and why. A conclusion
  built on a series that has since been revised is NOT carry-forward
  until re-checked against the revision.

## FAIL protocol
- Root cause FIRST (trace the exact figures and sources), then the
  correction, then a STATE.md entry so it can never silently regress,
  then hardening (a matrix row on the full track). RETAIN the original
  error and its evidence in STATE.md — a correction that erases its own
  history teaches nothing.
