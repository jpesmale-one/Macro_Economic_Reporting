# PROPOSAL — LD-141: the rate score reads how compelled the bank is

**Status: AWAITING JEFF'S APPROVAL. No scoring code has been changed.**

Jeff, 2026-09-20:

> *"the surprise won't matter here anymore. because by the time we capture the
> data its already past."*
>
> *"the Inflation will dictate the Interest Rate tone. Central Banks have a
> target inflation, which is 2%. Now if their inflation is way above 2% let's
> say 3.25% then they are compelled to increase the IR to reduce spending which
> will bring down the inflation. Now if the IR increased meaning businesses will
> hesitate to take loans hence the circulation of that currency will get
> tightened. If there is low circulation of that currencies the more it will
> become valuable because of less supply. That's the Supply and Demand idea in
> forex."*

**The chain, as the model needs it:**

```
CPI above 2%  →  bank compelled to hike  →  credit tightens
              →  currency supply falls   →  currency more valuable
```

The operative quantity is **how far above 2% the CPI sits.** That is what
compels the bank.

---

## 1. What the score does today, and why it does not say that

`rate_model.compute()` averages four weighted terms:

| Term | Weight | Looks |
|---|---:|---|
| realised | 0.2 | backward — what the bank already did |
| expected | 0.3 | **backward** — inflation vs its own mandate band |
| surprise | 0.2 | **backward** — last decision vs consensus |
| path | 0.3 | **forward** — is a move priced for the next meeting |

**Nominally 50/50. Measured, the forward share is 29–38%, never 50%:**

```
NZD 29%   EUR 29%   CAD 29%
USD 38%   GBP 38%   JPY 38%   CHF 38%   AUD 38%
```

Two causes: **`surprise` is 0.00 for every currency that has it** — every recent
decision landed exactly on consensus — and **`path` is None for CAD, EUR and
NZD**, which TE publishes no forecast for. Those three are scored *entirely on
backward terms*.

---

## 2. Three specific breaks against Jeff's mechanism

### 2a. It uses a country band, not the 2% point

`MANDATE` gives NZD and CAD a 1–3% band, CHF 0–2%. So **CAD at 3.0% reads as
"inside the band"** and scores +0.25 — when by the stated rule it is a full point
above target and the bank is compelled.

### 2b. It discards the size of the gap

Three states only: above ceiling / inside / below floor.

| | CPI | Gap vs 2% | Score |
|---|---:|---:|---:|
| NZD | 4.1% | **+2.1** | +0.50 |
| EUR | 2.9% | **+0.9** | +0.50 |

**Same score for a gap more than twice as large.** The magnitude that drives the
compulsion is thrown away.

### 2c. Direction overrides level — the worst one

| | CPI | Gap | Direction | Score |
|---|---:|---:|---|---:|
| **AUD** | 3.8% | **+1.8** | falling | **+0.00** |
| CAD | 3.0% | +1.0 | rising | +0.25 |

**AUD has higher inflation, further above target, and scores lower.** AUD holds
the highest policy rate in the group (4.35%) precisely because inflation is high.

> **THIS IS THE SAME INVERSION LD-136 ALREADY FIXED — IN THE OTHER CATEGORY.**
> For Inflation, Jeff ruled that *above 2% and not falling* is GOOD, because a
> bank that has not won yet stays hawkish. **The rate model never got that fix.**
> It still neutralises a high-but-falling print and rewards falling inflation
> inside a band.

---

## 3. The change

### 3a. Drop `surprise` entirely

It is backward by construction and currently contributes nothing but dilution —
0.00 for every currency that has it. Jeff: *"by the time we capture the data its
already past."*

### 3b. Score the gap from 2%, continuously

```python
TARGET = 2.0
FULL   = 1.5          # gap in points earning full marks

def expected(cpi):
    return clip((cpi - TARGET) / FULL, -1.0, +1.0)
```

The 2% target replaces the country band. **Direction is dropped** — level alone,
matching LD-136's treatment in the Inflation category.

### 3c. Reweight

| Term | Was | Now |
|---|---:|---:|
| realised | 0.2 | 0.2 |
| expected | 0.3 | **0.4** |
| surprise | 0.2 | **removed** |
| path | 0.3 | **0.4** |

---

## 4. Measured effect

### The category

| CCY | CPI | Gap | exp OLD | exp NEW | IR OLD | IR NEW |
|---|---:|---:|---:|---:|---:|---:|
| NZD | 4.1% | +2.1 | +0.50 | **+1.00** | +0.50 | **+1.00** |
| AUD | 3.8% | +1.8 | +0.00 | **+1.00** | +0.00 | **+0.40** |
| USD | 3.4% | +1.4 | +0.00 | **+0.93** | +0.19 | **+0.57** |
| CAD | 3.0% | +1.0 | +0.25 | +0.67 | +0.11 | +0.44 |
| EUR | 2.9% | +0.9 | +0.50 | +0.60 | +0.50 | +0.73 |
| GBP | 2.9% | +0.9 | +0.50 | +0.60 | +0.19 | +0.24 |
| JPY | 1.9% | −0.1 | +0.00 | −0.07 | +0.19 | +0.17 |
| **CHF** | 0.8% | **−1.2** | +0.25 | **−0.80** | +0.09 | **−0.32** |

### The base board

| CCY | BASE now | BASE new |
|---|---:|---:|
| GBP | +8.19 | +8.24 |
| EUR | +5.50 | **+5.73** |
| CHF | +6.09 | **+5.68** |
| CAD | +2.61 | +2.94 |
| USD | +1.69 | **+2.07** |
| JPY | +1.85 | +1.84 |
| AUD | 0.00 | **+0.40** |
| NZD | −0.50 | **0.00** |

```
now:  GBP > CHF > EUR > CAD > JPY > USD > AUD > NZD
new:  GBP > EUR > CHF > CAD > USD > JPY > AUD > NZD
```

**Two swaps: EUR above CHF, and USD above JPY.**

---

## 5. What is worth noticing about CHF

**CHF falls from +0.09 to −0.32** — the largest single move, and the only
negative score on the board.

CPI 0.8% is 1.2 points *below* target, so the SNB has no reason to tighten: it is
structurally dovish, which by Jeff's chain means loose supply and a weaker
currency. **That is the CHF anomaly he raised on 2026-09-19** — good economic
data, persistent weakness — and this rule produces it from the mechanism rather
than from a hand-coded carry penalty.

**It is not a carry rule and does not replace one.** The carry work stays a
measured column (13 weeks tested, no forward-looking regime signal found).

---

## 6. What this contradicts

**Nothing locked.** LD-90 is untouched — it governs how a *decision* is priced
and this proposal removes the `surprise` term rather than redefining it. The
MANDATE bands stay in the file as a printed note; they stop driving the score.

**LD-23 is satisfied**: CPI and the 2% target are published for all eight.

---

## 7. Withdrawal condition

**If this ranks nothing by the 12–16 Oct retrospective — four weeks — it comes
out.** LD-113 is the precedent: a change made for mechanism rather than measured
evidence lasted one day when it ranked nothing.

The specific thing to check: **does CHF's new negative score track its realised
weakness**, and does AUD's rise from 0.00 to +0.40 stop the model ranking it last
in weeks when it is not?

---

## 8. If approved, the build

1. `rate_model.py` — `expected()` on the 2% gap; drop `surprise`; reweight
2. `test_rate.py` (new, R-46) — the gap cases, the clip, the missing-path case
3. `docs/REPORT_SPEC.md` — LD-141 with section 4's board intact
4. Rebuild the 21–25 Sep edition on it

**Approval needed before any of that runs.**
