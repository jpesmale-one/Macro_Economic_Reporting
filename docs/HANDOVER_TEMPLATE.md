# Handover template

Written at the END of every session that produced work. Save as
`docs/HANDOVER_YYYY-MM-DD_<topic>.md`. The next session reads this plus
STATE.md and nothing else — so anything not written here is lost.

STATE.md's header is the authority on edition identity. This file restates
it for convenience and goes stale the moment the next edition lands.

---

## 1. Resume protocol
Expect: edition `{{EDITION}}`, data_asof `{{DATA_ASOF}}`, track `{{TRACK}}`.
Run `git status` + STATE.md header + `git log --oneline -5`. Aligned = say
so in one line. Mismatch = STOP (CLAUDE.md section 0 step 2).

## 2. Where we are
One paragraph. What is sealed, what is in flight, what is blocked and on
what.

## 3. Delivered this session
Per item: what shipped, which track it ran (LEAN / FULL), which gate it
reached, and the seal status. Name the trigger by number if one fired.

## 4. Empirical facts established
Only what the DATA settled this session, each with source, series ID,
release date, and as-of. These are candidates for STATE.md's established-
facts ledger — say which were promoted there and which are still draft.

## 5. Decisions locked
Each with its LD-number in STATE.md, the rejected alternatives, and the
rationale. If nothing was locked, say "none" — do not leave it blank.

## 6. Checklist / publish-gate disposition
Full track: each S-item and its status with the evidence that closed it.
Lean track: P1/P2/P3 status per artifact.
Anything closed on INSPECTION rather than EVIDENCE is called out
explicitly here and carries a caveat — never quietly marked verified.

## 7. Remaining — WITH RECIPES
Not just "do X". Each remaining item states: the setup, the exact steps,
and what the expected output looks like, so a cold start can execute it
without reconstructing intent.

## 8. Queued / parked
New backlog items and any parked item that changed status. Each says what
would un-park it.

## 9. Open findings
Numbered. Each with: what was observed, why it matters, current status.

## 10. Working agreements confirmed or changed this session
Anything about HOW we work that shifted. If a CLAUDE.md rule proved wrong
or insufficient, say so here — the protocol file is maintained, not fixed.

## 11. Git state
Branch, last commit, whether anything is unpushed, whether the tree is
clean. Pushing is Jeff's call.
