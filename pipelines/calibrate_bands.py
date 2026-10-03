# -*- coding: utf-8 -*-
"""LD-149 calibration, 28 pairs x ~57 weeks x 2 directions.

The question: where do the fav/adv ratio bands belong? The first pass used
one pair and I picked 0.80/1.20 by eye. This measures it.

Grading every week in BOTH directions gives a symmetric null - a random week
is LONG-favourable or SHORT-favourable with equal prior, so the pooled median
should sit at 1.0 by construction. It does, which is the sanity check that
the statistic is built right.

OUT-OF-SAMPLE SPLIT: bands are fitted on the FIRST half of the history and
scored on the SECOND. Thresholds fitted and reported on the same data would
flatter themselves, which is exactly the trap a 97% hit rate invites.
"""
import io
import os
import sys
import glob
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
# the 28-pair sample LD-149's bands were measured on, committed so the
# calibration can be RE-RUN rather than taken on trust (R-48).
BARS = os.path.join(REPO, 'data/raw/bars/calibration')
import pair_atr as pa
import atr_grade as ag


def load(path):
    out = []
    for ln in io.open(path, encoding='utf-8'):
        x = ln.split()
        if len(x) >= 5:
            out.append((pa.session(int(x[0])),) + tuple(float(v) for v in x[1:5]))
    return sorted(out)


rows = []          # (pair, week_start, bias, ratio, close_pips, ld128_hit)
pairs = sorted(glob.glob(os.path.join(BARS, '*.txt')))
for path in pairs:
    pair = os.path.basename(path)[:-4]
    if len(pair) != 6 or not pair.isalpha():
        continue
    bars = load(path)
    if len(bars) < 40:
        continue
    F = ag.pip_factor(pair)
    weeks, cur = [], []
    for b in bars:
        cur.append(b)
        if len(cur) == 5:
            weeks.append(cur)
            cur = []
    for wk in weeks:
        prior = [b for b in bars if b[0] < wk[0][0]]
        if len(prior) < 15:
            continue
        a = ag.atr([(h, l, c) for _, o, h, l, c in prior], 14, F)
        if not a:
            continue
        for bias in ('LONG', 'SHORT'):
            sf = sa = 0.0
            hit = False
            for _, o, h, l, c in wk:
                fav, adv, _, hh = ag.grade_day(bias, o, h, l, F, a)
                sf += fav
                sa += adv
                hit = hit or hh
            if sa <= 0:
                continue
            wo, wc = wk[0][1], wk[-1][4]
            close = ((wc - wo) if bias == 'LONG' else (wo - wc)) * F
            rows.append((pair, wk[0][0], bias, sf / sa, close, hit))

rows.sort(key=lambda r: r[1])
n = len(rows)
print('%d pair-weeks from %d pairs, %s -> %s'
      % (n, len({r[0] for r in rows}), rows[0][1], rows[-1][1]))
print()

ratios = sorted(r[3] for r in rows)


def pct(p, xs=None):
    xs = xs or ratios
    return xs[min(len(xs) - 1, int(round(p / 100.0 * (len(xs) - 1))))]


print('RATIO DISTRIBUTION (pooled, both directions)')
for p in (1, 5, 10, 25, 50, 75, 90, 95, 99):
    print('  p%-3d %6.2f' % (p, pct(p)))
print('  median %.3f    mean %.3f' % (st.median(ratios), st.mean(ratios)))
print()

print('*** LD-128 fires on %d of %d = %.0f%% of RANDOM pair-weeks'
      % (sum(1 for r in rows if r[5]), n,
         100.0 * sum(1 for r in rows if r[5]) / n))
print()

BANDS = [(0, .60), (.60, .70), (.70, .80), (.80, .90), (.90, 1.0),
         (1.0, 1.1), (1.1, 1.2), (1.2, 1.3), (1.3, 1.4), (1.4, 1.6),
         (1.6, 9e9)]
print('%-13s %6s %8s %12s' % ('RATIO BAND', 'N', '% POS', 'MEDIAN CLOSE'))
for lo, hi in BANDS:
    sub = [r for r in rows if lo <= r[3] < hi]
    if len(sub) < 8:
        continue
    up = sum(1 for r in sub if r[4] > 0)
    print('%5.2f - %-6s %6d %7.0f%% %12.1f'
          % (lo, ('%.2f' % hi) if hi < 9e8 else 'inf', len(sub),
             100.0 * up / len(sub), st.median([r[4] for r in sub])))
print()

# ---------------------------------------------------------------- OOS test
half = n // 2
tr, te = rows[:half], rows[half:]
print('OUT-OF-SAMPLE  fit on %d weeks to %s, score on %d weeks from %s'
      % (len(tr), tr[-1][1], len(te), te[0][1]))
print()


def score(lo, hi, data, label):
    win = [r for r in data if r[3] >= hi]
    los = [r for r in data if r[3] < lo]
    mid = [r for r in data if lo <= r[3] < hi]
    def pos(x):
        return 100.0 * sum(1 for r in x if r[4] > 0) / len(x) if x else 0.0
    print('  %-10s WIN n=%-4d %5.1f%% pos | LOSS n=%-4d %5.1f%% pos '
          '| CONTESTED n=%-4d %5.1f%% pos'
          % (label, len(win), pos(win), len(los), pos(los), len(mid), pos(mid)))
    return pos(win), pos(los)


for lo, hi in ((.70, 1.20), (.80, 1.20), (.85, 1.15), (.70, 1.40), (.60, 1.40)):
    print('bands %.2f / %.2f' % (lo, hi))
    score(lo, hi, tr, 'in-sample')
    score(lo, hi, te, 'OUT-OF-S')
    print()
