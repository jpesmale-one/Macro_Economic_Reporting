# -*- coding: utf-8 -*-
"""LD-85 - FORWARD ADJUSTMENT: price the week in, do not wait for it.

Jeff, 2026-08-31:

    "the market is forward looking. if we react after the data has released
     then we are already late. that's the whole point of this market
     Sentiment. To be able to foresee where the price is going. not following
     the price. ... isn't it better to price in early than to react after?
     That's why I'm giving weight to the forecast. The only question is how
     much weight? Because not all indicators do have the same weight so we
     need to consider balancing the scores in that sense"

I had argued against this by citing LD-3 - "the release is truth, the forecast
is a prediction". THAT WAS A MISUSE OF THE RULE. LD-3 is a SOURCING rule: never
dress a forecast as a print, always name the issuing agency for a released
value. It says nothing about how much a forecast should move a FORWARD-LOOKING
BIAS. Being early is the product.

THE FORMULA

    adjusted(ccy) = base(ccy) + k * SUM( verdict * category_weight )

  verdict          +1 GOOD, -1 BAD, 0 NEUTRAL, from market_pricing()
  category_weight  THE TALLY'S OWN weights - Infl 3, Rate 3, Empl 2,
                   Production/Spending/Trade 1
  k                0.50, Jeff's call 2026-08-31

WHY WEIGHTED AND NOT FLAT. The first costing was flat: every priced row moved
the tally the same amount, so a Mfg PMI (w1) counted as much as an Inflation
print (w3). Jeff named that imbalance directly. Running the adjustment through
the SAME weights as the base keeps one taxonomy for both.

WHY k=0.50, AND WHAT WOULD CHANGE IT. It is the largest value at which NO
CURRENCY'S RANK IS DECIDED BY A SINGLE FORECAST. At k=0.75 CHF's lone inflation
print (w3) moves it 2.25 points and drops it past USD on its own; at k=1.00 it
moves 3.00 and a forecast counts as much as a release. At k=0.50 the largest
possible single-row move is 1.50 on an 11-point scale.

That is a TESTABLE claim, not a preference. 4.0 records the projections in
advance, so the Saturday retrospective can grade k against what actually
printed. Revisit after 2026-09-04 close - Jeff: "we can revisit it later after
this week's market close."

WHAT THIS DOES NOT DO
  - It does not touch the BASE tally. Both numbers are published side by side
    so the forecast's contribution is always visible, never baked in.
  - It does not re-grade a released row. Once a print lands it belongs to the
    base tally through score_model, and its forward adjustment is dropped.
  - It does not model the CYCLE view (2.0b). That gap is still open.
"""
import os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_model as sm

K = 0.50            # Jeff's call, 2026-08-31. Revisit after 2026-09-04.
VERDICT = {'GOOD': 1, 'BAD': -1, 'NEUTRAL': 0}


def weights():
    """The tally's own category weights, Rate included."""
    w = dict(sm.W)
    w['Rate'] = 3
    return w


def category_of(ccy, indicator):
    """The whitelist's own category for a row - never guessed."""
    for cat, iso, name, a, p, r, thr, v in sm.ROWS:
        if sm.LABEL[iso] == ccy and name == indicator:
            return cat
    return None


def adjust(priced, base=None, k=K):
    """priced: [(ccy, indicator, verdict), ...] for UNRELEASED rows only.

    Returns {ccy: {'base', 'adj', 'delta', 'parts'}}.
    """
    if base is None:
        _, tot = sm.compute()
        base = dict((sm.LABEL[i], v) for i, v in tot.items())
    w = weights()
    delta = collections.Counter()
    parts = collections.defaultdict(list)
    for ccy, ind, verd in priced:
        v = VERDICT.get(verd)
        if not v:
            continue
        cat = category_of(ccy, ind)
        if cat is None:
            continue
        contrib = v * w[cat]
        delta[ccy] += contrib
        parts[ccy].append((ind, cat, w[cat], contrib))
    out = {}
    for c, b in base.items():
        out[c] = {'base': b, 'adj': b + k * delta[c], 'delta': delta[c],
                  'parts': parts[c]}
    return out


def table(res, k=K):
    """The 2.0c markdown table. Base and adjusted BOTH visible."""
    nl = chr(10)
    rows = ['| CCY | Base | **Forward** | Change | What the week prices |',
            '|---|---|---|---|---|']
    for c in sorted(res, key=lambda x: -res[x]['adj']):
        d = res[c]
        mv = d['adj'] - d['base']
        why = ' \u00b7 '.join('%s %s w%d %+d' % (i[:22], ct[:4], w, p)
                             for i, ct, w, p in d['parts']) or '\u2014'
        rows.append('| **%s** | %+.2f | **%+.2f** | %s | %s |'
                    % (c, d['base'], d['adj'],
                       '**%+.2f**' % mv if abs(mv) >= 1 else '%+.2f' % mv,
                       why))
    return nl.join(rows)


if __name__ == '__main__':
    demo = [
        ('JPY', 'Retail Sales YoY', 'GOOD'),
        ('JPY', 'Consumer Confidence', 'GOOD'),
    ]
    r = adjust(demo)
    for c in sorted(r, key=lambda x: -r[x]['adj']):
        print('%-4s base %+6.2f -> %+6.2f  (delta %+d, k=%.2f)'
              % (c, r[c]['base'], r[c]['adj'], r[c]['delta'], K))
