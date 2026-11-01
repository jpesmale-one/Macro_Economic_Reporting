# -*- coding: utf-8 -*-
"""LD-175 - WEEK-BY-WEEK, ATR-NORMALISED, COMMON-SESSION PRODUCT COMPARISON.

Jeff, 2026-11-01: "lets do that week-by-week comparison on the ATR-normalised
common-session basis. was it going to be on our daily report?"

*** NO, AND THE REASON IS THE POINT. A daily grades ONE SESSION; this measures
a WEEK, so there is no number to print on a Tuesday. It also compares two
products, and a cross-product scoreboard does not belong inside either one's
own page. But the real reason is that a figure which moves every day gets
WATCHED every day, and this one needs roughly eight weeks before it means
anything. It belongs in the Saturday retrospective, one row per week.

WHY THIS MEASURE AND NOT THE SET RATIO
--------------------------------------
Three corrections, each of which changed the answer for 26-30 Oct:

1. COMMON SESSIONS ONLY. The macro set was graded on five sessions, the
   rates set on four - CAD's 2-year never settled a Friday bar. Comparing
   1.074 to 1.011 compared five days to four. On the same four days the
   macro set is 0.917, BELOW the rates set. The extra day was the entire gap.

2. ATR-NORMALISED. Raw pips are not comparable across instruments whose
   ATRs run 31 to 128. A 50-pip gain on GBPJPY is a shrug; 50 on CADCHF is a
   real move. Each pair's net excursion is divided by ITS OWN ATR, the same
   ATR the grade used (LD-128/129: sessions ending before the graded week).

3. PER PAIR-DAY. A set of four pairs is not twice as good as a set of two for
   holding twice as much. The headline divides by pairs x sessions.

WHAT THIS IS NOT
----------------
It is not a P&L. LD-4 stands: there are no positions, no sizing and no money
here - an ATR-multiple is an excursion measure, and "profitable" in this file
means "moved favourably relative to its own volatility", nothing more.

It is not significant yet either. MIN_WEEKS is the number of weeks below
which this module REFUSES to call a winner, for the same reason
session_log.weekday_table refuses below eight: with two weeks, the ranking
flips between four reasonable measures, and a reader shown a single bolded
winner will believe it.
"""
import csv
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

MACRO = os.path.join(REPO, 'data', 'derived', 'sessions.csv')
RATES = os.path.join(os.path.dirname(REPO), 'Rate_Differential_Reporting',
                     'data', 'derived', 'sessions.csv')

# Below this, no winner is declared. See the docstring.
MIN_WEEKS = 8


def rows(path):
    if not os.path.exists(path):
        return []
    with io.open(path, encoding='utf-8') as f:
        return list(csv.DictReader(f))


def _num(r, k):
    v = (r.get(k) or '').strip()
    return float(v) if v else None


def weeks(path):
    """{week_start: {session: [row, ...]}}"""
    out = {}
    for r in rows(path):
        out.setdefault(r['week_start'], {}) \
           .setdefault(r['session'], []).append(r)
    return out


def common_sessions(a, b, week):
    """Sessions BOTH products graded in that week."""
    return sorted(set(a.get(week, {})) & set(b.get(week, {})))


def score(wk_rows, sessions):
    """ATR-normalised net for one product over the given sessions.

    Returns (total_atr, per_pair_day, n_pairs, n_sessions, {pair: atr_net}),
    or None when a row lacks the ATR it must be divided by (F-73 - a missing
    divisor is NOT a 1, and it is not a zero either; the pair is dropped and
    the caller is told how many were dropped).
    """
    by_pair = {}
    dropped = 0
    for s in sessions:
        for r in wk_rows.get(s, []):
            atr = _num(r, 'atr_pips')
            fav = _num(r, 'fav_pips')
            adv = _num(r, 'adv_pips')
            if not atr or fav is None or adv is None:
                dropped += 1
                continue
            by_pair.setdefault(r['pair'], [0.0, atr])
            by_pair[r['pair']][0] += (fav - adv)
    if not by_pair:
        return None
    per = dict((p, net / atr) for p, (net, atr) in by_pair.items())
    total = sum(per.values())
    n = len(per) * len(sessions)
    return (total, (total / n) if n else None, len(per), len(sessions),
            per, dropped)


def table():
    """One row per week that BOTH products graded."""
    A, B = weeks(MACRO), weeks(RATES)
    out = []
    for wk in sorted(set(A) & set(B)):
        sess = common_sessions(A, B, wk)
        if not sess:
            continue
        a = score(A[wk], sess)
        b = score(B[wk], sess)
        if not a or not b:
            continue
        out.append({'week': wk, 'sessions': sess,
                    'macro': a, 'rates': b,
                    'lead': a[1] - b[1]})
    return out


def verdict(t=None):
    """The standing answer, or a refusal with the reason."""
    t = table() if t is None else t
    if len(t) < MIN_WEEKS:
        return (None, '%d of %d weeks - too few to call a winner. The 26-30 '
                'Oct ranking reversed across four reasonable measures, which '
                'is itself the evidence that the gap is not yet real.'
                % (len(t), MIN_WEEKS))
    m = sum(w['macro'][1] for w in t) / len(t)
    r = sum(w['rates'][1] for w in t) / len(t)
    lead = m - r
    return (('MACRO' if lead > 0 else 'RATES'),
            'mean per pair-day over %d weeks: macro %+.3f ATR, rates %+.3f '
            'ATR' % (len(t), m, r))


def report():
    t = table()
    print('WEEK-BY-WEEK, ATR-NORMALISED, COMMON SESSIONS ONLY')
    print('(an ATR-multiple is an excursion measure, not a P&L - LD-4)')
    print()
    print('%-12s %4s  %18s  %18s  %8s' %
          ('WEEK', 'SESS', 'MACRO (tot/pd)', 'RATES (tot/pd)', 'LEAD'))
    for w in t:
        a, b = w['macro'], w['rates']
        print('%-12s %4d  %+8.2f %+8.2f  %+8.2f %+8.2f  %+8.2f'
              % (w['week'], len(w['sessions']),
                 a[0], a[1], b[0], b[1], w['lead']))
        if a[5] or b[5]:
            print('%14s dropped rows - macro %d, rates %d (no ATR, F-73)'
                  % ('', a[5], b[5]))
    print()
    who, why = verdict(t)
    print('VERDICT: %s' % (who or 'NO CALL'))
    print('  %s' % why)
    return t


if __name__ == '__main__':
    report()
