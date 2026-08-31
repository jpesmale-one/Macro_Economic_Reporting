# -*- coding: utf-8 -*-
"""
Emit section 2 (Macro Economic Indicators) as markdown, straight from
score_model.ROWS.

WHY THIS EXISTS - F-24, 2026-08-23. Jeff: "the format on section 2 has
changed. I mentioned before that I want to see the whole data. why do we have
blanks on this section?"

The 2026-08-23 weekend edition published ~40 SUMMARY rows carrying em-dashes
where Actual/Previous/Ref/Threshold should be. The data was never missing -
all 70 rows sit in score_model.ROWS and the tally was regenerated from them in
the same session. I hand-wrote a condensed version instead of publishing the
model.

The spec is explicit (REPORT_SPEC section 3): ALL 70 NAMED INDICATORS ARE
PUBLISHED EVERY EDITION; an indicator that cannot be sourced is published with
score NOT FOUND so it can be verified, never dropped. A blank cell is not a
NOT FOUND - it is an unverifiable silent omission.

Same lesson as LD-13 (tally generated so tables cannot drift) and LD-25 (F&G
generated so the format cannot degrade): if a block is derived from data,
GENERATE IT. Hand-copying is how a format silently changes.

DATA + ARITHMETIC ONLY - this module does not fetch.
"""
import score_model as sm

CATS = [
    ('Production', '2.1', 1),
    ('Spending',   '2.2', 1),
    ('Trade',      '2.3', 1),
    ('Employment', '2.4', 2),
    ('Inflation',  '2.5', 3),
]

# Currency display order - matches the tally ordering used in section 2.0.
ORDER = ['US', 'EA', 'GB', 'JP', 'AU', 'NZ', 'CA', 'CH']

BOLD = {'GOOD', 'BAD'}


def _score_cell(v):
    """NOT FOUND is published, never blanked (spec section 3)."""
    if not v or v.upper() in ('', 'NONE'):
        return '**NOT FOUND**'
    return '**%s**' % v if v in BOLD else v


# LD-61 - SECTION 2.0, THE CATEGORY TALLY, IS GENERATED AND SORTED BY SCORE.
#
# It was hand-maintained until 2026-08-24 - the ONE table in section 2 that
# section2.py did not build, and the one that sets the BANDS every other
# section reads. Jeff found USD +2.25 listed above AUD +2.75: LD-57 moved AUD
# from +2.08 and I patched the cell in place without re-sorting.
#
# That is F-24's lesson still open in the highest-consequence table. A hand-
# maintained derived block drifts, and this one drifts SILENTLY because a
# mis-sorted table still contains every correct number.
GROUPS = {'US': 'Safe haven', 'JP': 'Safe haven', 'CH': 'Safe haven',
          'CA': 'Commodity', 'AU': 'Commodity', 'NZ': 'Commodity',
          'EA': 'Risk-corr', 'GB': 'Risk-corr'}

# Bands cut on the SCALE (+/-11.00 since LD-23), never on rank - a rank split
# would force three "weak" currencies in a week when all eight are positive.
# LD-76 - BANDS, confirmed by Jeff 2026-08-30: "The 5.5 is our benchmark
# for a strong currency then."
#
# 5.50 is EXACTLY HALF the +-11.00 scale (weights 1+1+1+2+3 = 8, plus
# Rate 3). It is a GEOMETRIC split, not an empirical or outcome-derived
# one: top half STRONG, anything positive NEUTRAL, zero or below WEAK.
#
# KEPT DELIBERATELY through the LD-71 regrade. Grading made full marks
# much harder to earn, so STRONG went from 3 currencies to 1 on the same
# line - GBP 5.75 -> 5.31 and EUR 6.25 -> 5.05 both crossed out without
# any judgement being made about them. Jeff's call is that a HIGHER BAR
# for STRONG is the correct outcome, not a mis-calibration.
#
# Nothing downstream SELECTS on a band - section 4 selects on the SPREAD
# between two currencies. The band is a published label.
#
# Full context: docs/SCORING_BASELINE.md section 5.
BAND_STRONG, BAND_WEAK = 5.50, 0.00


def band(score):
    if score >= BAND_STRONG:
        return 'STRONG'
    return 'WEAK' if score <= BAND_WEAK else 'NEUTRAL'


def tally_table():
    """Section 2.0, sorted by score descending. Returns (markdown, totals)."""
    cs, tot = sm.compute(include_rate=True)
    order = ['Production', 'Spending', 'Trade', 'Employment', 'Inflation', 'Rate']
    out = ['| Band | CCY | **Score** | Group | Prod · Spend · Trade · Empl · Infl · **Rate** |',
           '|---|---|---|---|---|']
    for iso, total in sorted(tot.items(), key=lambda kv: -kv[1]):
        ccy = sm.LABEL[iso]
        b = band(total)
        cells = []
        for cat in order:
            v = cs.get((cat, iso), (0.0,))[0]
            t = ('**%+.2f**' % v) if cat == 'Rate' else ('%+.2f' % v)
            cells.append(t.replace('-', '−'))
        em = '**' if b in ('STRONG', 'WEAK') else ''
        out.append('| %s%s%s | %s%s%s | **%s** | %s | %s |'
                   % (em, b, em, em, ccy, em,
                      ('%+.2f' % total).replace('-', '−'),
                      GROUPS[iso], ' · '.join(cells)))
    return '\n'.join(out), tot


LEADING = ('Production', 'Spending', 'Trade')
CONFIRMING = ('Employment', 'Inflation')


def cycle_table():
    """Section 2.0b - where each currency sits in Jeff's causal chain (LD-72).

    Jeff, 2026-08-29: "Production, Spending and Trade tends to predict the
    result of Employment and Inflation. And Employment and Inflation tends to
    predict what would be the Interest rate decision. Because the Interest Rate
    dictates if the Currency is Strong or Weak."

    The flat total sums six categories side by side and cannot express WHERE IN
    THE CHAIN a currency sits. Two currencies with the same score can be at
    opposite ends of it. Normalising each stage to its own maximum makes the
    gap comparable:

      GAP > 0   leading ahead of confirming - upstream improving, rate case
                BUILDING, the strength is still ARRIVING
      GAP < 0   confirming ahead of leading - nothing upstream feeding it,
                the strength has ALREADY HAPPENED

    On 2026-08-29 this read GBP at leading 0.00 / confirming 1.00 - maximum
    negative gap. GBPUSD lost 110.9 pips that week. One observation, not
    evidence, but it is the read the flat score could not produce.
    """
    cs, tot = sm.compute(include_rate=True)
    lead_max = float(sum(sm.W[c] for c in LEADING))
    conf_max = float(sum(sm.W[c] for c in CONFIRMING))
    rows = []
    for iso in tot:
        lead = sum(cs.get((c, iso), (0.0,))[0] for c in LEADING) / lead_max
        conf = sum(cs.get((c, iso), (0.0,))[0] for c in CONFIRMING) / conf_max
        rows.append((sm.LABEL[iso], lead, conf, lead - conf, tot[iso]))

    out = ['| CCY | Leading | Confirming | **Gap** | Score | Cycle position |',
           '|---|---|---|---|---|---|']
    for ccy, lead, conf, gap, total in sorted(rows, key=lambda r: -r[3]):
        if gap > 0.40:
            read = '**BUILDING** — upstream ahead, rate case forming'
        elif gap < -0.40:
            read = '**IN THE PAST** — nothing upstream feeding it'
        else:
            read = 'aligned'
        f = lambda x: ('%+.2f' % x).replace('-', '−')
        out.append('| **%s** | %s | %s | **%s** | %s | %s |'
                   % (ccy, f(lead), f(conf), f(gap), f(total), read))
    return chr(10).join(out)


def standings():
    """Group standings line, each group sorted by score."""
    cs, tot = sm.compute(include_rate=True)
    by = {}
    for iso, v in tot.items():
        by.setdefault(GROUPS[iso], []).append((v, sm.LABEL[iso]))
    parts = []
    for g in ('Safe haven', 'Commodity', 'Risk-corr'):
        rows = sorted(by[g], reverse=True)
        parts.append('%s: %s' % (g, ' › '.join(
            '%s %s' % (c, ('%+.2f' % v).replace('-', '−')) for v, c in rows)))
    return ' · '.join(parts)


def category_table(cat, due=None):
    """One markdown table for a category: every row, no blanks.

    LD-87 adds NEXT DUE. Jeff, 2026-08-31: "For each indicators in §2 we put
    which week these news will come out. in TE the whole schedule for
    September is already out."

    A GOOD score with a print due Thursday is a different thing from a GOOD
    score with nothing until the 24th - the first is about to be tested, the
    second is being carried. That distinction was invisible in this table,
    and it is the same blind spot that let NZD sit at +4.29 on Jun/26
    quarterly data while every fresh print ran the other way.
    """
    if due is None:
        try:
            import next_due as _nd
            due = _nd.next_due()
        except Exception:
            due = {}
    try:
        import next_due as _nd
        fmt = _nd.label
    except Exception:
        fmt = lambda e: '—'
    rows = [r for r in sm.ROWS if r[0] == cat]
    rows.sort(key=lambda r: (ORDER.index(r[1]) if r[1] in ORDER else 99, r[2]))
    out = ['| CCY | Indicator | Actual | Previous | Ref | Threshold | Score '
           '| **Next due** |',
           '|---|---|---|---|---|---|---|---|']
    for _c, ccy, name, actual, prev, ref, thr, score in rows:
        lbl = sm.LABEL.get(ccy, ccy)
        out.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (
            lbl, name,
            actual or '**NOT FOUND**', prev or '—',
            ref or '—', thr or '—', _score_cell(score),
            fmt(due.get((lbl, name)))))
    return '\n'.join(out), len(rows)


def counts_line(cat):
    """GOOD/BAD/NEUTRAL tally for the category, so the table can be checked."""
    rows = [r for r in sm.ROWS if r[0] == cat]
    g = len([r for r in rows if r[7] == 'GOOD'])
    b = len([r for r in rows if r[7] == 'BAD'])
    n = len(rows) - g - b
    return '**%d indicators — %d GOOD · %d BAD · %d NEUTRAL**' % (len(rows), g, b, n)


def build(notes=None):
    """Full section 2.1-2.5 markdown. notes: {'2.1': 'analysis line', ...}."""
    notes = notes or {}
    parts, total = [], 0
    for cat, num, weight in CATS:
        tbl, n = category_table(cat)
        total += n
        parts.append('### %s %s (weight %d)\n' % (num, cat, weight))
        parts.append(counts_line(cat) + '\n')
        parts.append(tbl + '\n')
        if notes.get(num):
            parts.append(notes[num] + '\n')
    return '\n'.join(parts), total


if __name__ == '__main__':
    md, total = build()
    print(md)
    print('\n<!-- %d indicator rows emitted -->' % total)
