# Handover — 2026-08-24 — the fine-tuning session

> ## ⚠ READ THIS BEFORE BUILDING TUESDAY'S EDITION
>
> Thirteen decisions and six findings landed today, all of them changing how an
> edition is built. **STATE.md is 4,250 lines; this file is the part that
> changes what you do tomorrow.**
>
> Then run, in order:
> ```
> python pipelines/audit_te.py --fetch     # LD-50 — reconcile the whitelist
> python pipelines/freshness.py            # LD-54 — revisions + stalled series
> python pipelines/test_guards.py          # 7 regressions must all block
> python pipelines/week_ahead.py           # §4.0 events, DATE→TIME→CCY
> ```

---

## 1. Where the repo is

**Edition `2026-08-24` (r3, UNSEALED). The week is LOCKED — four pairs.**

| Pair | Dir | Conf | Falsifier | Clear by |
|---|---|---|---|---|
| CADJPY | LONG | LOW (+1) | close < **114.472** | 58 pips |
| EURCHF | LONG | LOW (+1) | close < **0.92796** | 80 pips |
| GBPUSD | LONG | LOW (+1) | close < **1.35197** | 107 pips |
| AUDNZD | **SHORT** | LOW (+1) | close > **1.20724** | 65 pips |

**All four score +1. The set has no rank this week** — that is the finding, not
a defect. **All eight currencies used once** (the LD-35 ceiling).

**Tuesday is a TRACKING day.** §4 stays locked (LD-29); a pair leaves only when
its falsifier fires, and is **not replaced**. §0 tracks; §4.0 monitors.

Everything is pushed. `git log --oneline origin/main..HEAD` should return zero.

---

## 2. What changed today, by where it bites

### Scoring rules — these change numbers

| ID | Rule |
|---|---|
| **LD-57** | **Full Time Employment**: `>0 & ≥prev` GOOD · `>0 & <prev` NEUTRAL · `<0 & ≤prev` BAD · `<0 & >prev` NEUTRAL · `=0` NEUTRAL. Full time still weighted heaviest. `score_model.full_time_grade()` |
| **LD-58** | **Claimant Count Change** scored against **ZERO**, not the prior month. `>0` BAD · `<0` GOOD · `=0` NEUTRAL. `score_model.claimant_grade()` |
| **LD-63** | **§4.0 reads MARKET POSITIONING**, not a forecast score. Range `[Consensus, Forecast]` vs the **current actual** (the last released **Final**): above → GOOD, below → BAD, inside → NEUTRAL. **Category-independent.** `week_ahead.market_pricing()` |
| **LD-51** | GBP Spending uses **Retail Sales Ex Fuel**, not the headline |
| **LD-53** | **USD Manufacturing Production YoY** added — whitelist is now **71 rows** |
| **LD-55** | All Balance-of-Trade rows in **billions** |

### Report structure — these change what ships

| ID | Rule |
|---|---|
| **LD-61** | **§2.0 is GENERATED and sorted by score.** `section2.tally_table()`. Never patch a cell |
| **LD-62** | **§4.1 is DELETED.** Bands live in §2.0 only. Numbering gap kept: 4.0 → 4.3 → 4.4 → 4.5 |
| **LD-60** | **§4.5 is a POSITIONING list** — live price, range position, distance to resistance and support, **for every carried pair**. Run candidates through `select_pairs.exposure()` first |
| **LD-64** | §4.0's market pricing **feeds the pair read** |
| **LD-65** | **§1 must cover every currency §0 says moved** |
| **LD-52** | §4.0 sorted **date → time → CCY** |

### Working rules — these change how you behave

| ID | Rule |
|---|---|
| **LD-59** | **STICK TO THE THRESHOLDS.** They are Jeff's specification. Do **not** propose a rule change because a *different* indicator's rule changed — "similar" is his judgement, not yours. Report a threshold that is **internally broken** or a figure that **does not match its source**; otherwise the default is no change |
| **LD-49** | Sort the whitelist by reference period every edition and explain the outliers |
| **LD-54** | Revisions are **advisory** (triage by hand); **stalled series are FATAL** |

---

## 3. The failure modes that produced today's findings

**Read these before writing anything. Each cost a published error.**

### A wrong series is invisible to a value check

**F-38** (Westpac index vs change), **F-40** (permits level vs MoM), **F-41**
(TE's `/consumer-confidence` is *Michigan*, not CB). **Three times today**, one
TE page served a different series than the whitelist named.

**Both numbers are real TE values, so comparing values cannot see it.** Check
the **unit** and the **series name**, not just the figure.

### A provisional wearing a Final's name

**F-27** (StatCan advance estimate), **F-29** (EUR flash), **F-36/F-40**
(permits prel). **The current actual is the last released FINAL.** The phantom
guard checks whether a figure was *released*, never whether it was *provisional*.

### An absence asserted from one attempt

**F-41** and **F-42**, three hours apart. F-42 is the worse one: the CAD
catalyst — a 50% tariff regime going live — was on the front page of a mandated
source, and the morning sweep asked for "Canada" headlines while the story ran
under *trade war*.

**Search by the MOVE, not by the country.** And **check the artifact you already
have** — the calendar capture had the CB Consumer Confidence row all along.

### A derived block drifts silently

**F-24** (§2 summarised), **F-23** (F&G hand-written), **LD-61** (§2.0
mis-sorted). **If a block is derived from data, GENERATE IT.** A mis-sorted
tally contains every correct number — no content check can see it.

---

## 4. What the guards do and do not catch

**Eleven guards run before any edition renders.** All refuse to publish:

R-7 sections · LD-38 generated-block markers · LD-39 71 rows no blanks ·
LD-41 no off-list scoring · LD-46 levels drawn · LD-50 TE reconciled ·
LD-54 no stalled series · LD-61 tally sorted · LD-65 news coverage ·
F-17 §1 cites a source · LD-27 prose ratio *(advisory only)*

### They check SHAPE, never JUDGEMENT

**These shipped past every guard and Jeff caught them by reading:**

- **F-33** — a falsifier at 114.992 that **no bar ever printed** (it was the
  mean of two others)
- **F-32** — every published level sat **at or below price**; "resistance" was
  Friday's own high
- **F-42** — the CAD catalyst, missing from §1 while §0 diagnosed the CAD leg

**A green guard run is not a clean edition.**

---

## 5. Carry into Tuesday

### The reads that need watching

**CAD carries four negatives and the score sees none of them** — superseded
Spending row, GDP −0.1% Friday, the weekend gap, and **50% US tariffs live on
~$20bn**. A trade war is not one of the 71 indicators. **CAD stays +8.38 while
its currency is repriced on a policy shock.** CADJPY's falsifier is the tightest
of the four.

**Three of four pairs are long a currency whose strength is really dollar
weakness** (EUR, GBP, and CHF via the carry channel). **Less independent than
leg-disjointness implies** — EF-3's risk through a channel the rule does not
measure.

**The intervention supports short-JPY, it does not threaten it** (F-39). The
threat is episodic; the flow runs the other way.

### Tuesday's two releases — both on GBPUSD's short leg

| When (PHT) | Event | Why |
|---|---|---|
| **Tue 25 20:00** | USD Building Permits **Final** | Resolves F-36. Break-even **1.3809M** |
| **Tue 25 22:00** | USD CB Consumer Confidence | Current **90.8**, range **90.8–91.2** |

### Open queue

| ID | Item |
|---|---|
| **R-14** | **The calendar capture contains NO CHF rows.** `week_ahead.py` structurally cannot see Swiss events; any CHF row in §4.0 is hand-sourced. **The most consequential open item** |
| **R-10** | BTCUSD still publishes its own Friday high as resistance — needs an LD-47 forward map |
| **R-12** | Cadence-staleness (LD-49) is still a procedure |
| **R-15** | CAD's June FT/PT split unsourced, so LD-57 cannot run on it |

**R-1, R-3, R-5, R-7, R-13, R-16 closed.** R-8 superseded by LD-27.

---

## 6. The working agreement that matters most

**Jeff catches what the method hides.** Today: the mis-sorted tally, the wrong
Westpac series, the conflated permits row, the missing CB event, the thin §1,
the duplicated §4.1, and the CAD catalyst.

**Every one was a real defect and none was caught by tooling.** When he asks
"can you check X" — **check it against the source, not against your memory of
it.** Twice today the answer was in a file already on disk.
