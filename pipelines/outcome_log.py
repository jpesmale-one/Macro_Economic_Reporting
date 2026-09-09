# -*- coding: utf-8 -*-
"""The OUTCOME LEDGER - what was selected, and what price did (LD-111).

Jeff, 2026-09-09:

    "how many weeks do you actually consider before you can say that this is
     not noise? do we need to wait a Month or a Year before we adjust
     anything? If something is not looking right then we need to analyze why
     and the soonest. I don't have that much of time and capital for
     prolonged trial and error"

THE HONEST ANSWER IS THAT "WAIT FOR MORE WEEKS" WAS A DODGE, because nothing
was accumulating. There was no record. Every review reasoned from memory of
the last one, so the sample never grew and the wait never ended.

THREE QUESTIONS, THREE DIFFERENT SAMPLE SIZES. Conflating them is what made
the answer sound like "wait forever":

  A  DOES IT MAKE MONEY?        ~85-190 trades to separate a 60-65% hit rate
                                from a coin flip. Months. Not a usable loop,
                                and not the question to run the model on.

  B  DOES CONVICTION RANK?      Measurable EVERY WEEK as a rank correlation
                                between gap and outcome across the selected
                                pairs. THREE consecutive inverted weeks is a
                                signal, not noise - roughly a 1-in-8 fluke if
                                the gap were truly uninformative.

  C  IS A COMPONENT WRONG?      n = 1. A defect is a defect. F-92 was found
                                on a single row and fixed the same day.

WHAT THIS FILE MEASURES IS B, weekly, because that is the question that
broke on 2026-09-09: the gap ranked the four pairs almost exactly backwards
(rho -0.80) and nothing in the repo would have remembered it next week.

PEAK, NOT FRIDAY (Jeff's point, same day): "if the pair already moved 174.8
pips why would I wait ti'll Friday just to see it reversed? I would have
already taken profit." So the ledger records MFE - the best favourable
excursion during the week - alongside the close. A move that happened is a
move that happened, whatever Friday says. MAE is recorded too: a pair that
paid 170 after first going 80 against is not the same trade.

LD-4 STILL HOLDS. This records what PRICE did. It does not set an exit, a
target or a stop, and MFE is an observation about the week, not an
instruction about when to close.
"""
import io, os, sys, csv, json
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
LEDGER = os.path.join(REPO, 'data', 'derived', 'outcomes.csv')

FIELDS = ('week_start', 'built', 'pair', 'direction', 'gap', 'tier',
          'category', 'ref_close', 'mfe_pips', 'mae_pips', 'close_pips',
          'graded_to', 'note')


def load():
    if not os.path.exists(LEDGER):
        return []
    with io.open(LEDGER, encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def save(rows):
    d = os.path.dirname(LEDGER)
    if not os.path.isdir(d):
        os.makedirs(d)
    out = io.open(LEDGER, 'w', encoding='utf-8', newline=chr(10))
    w = csv.DictWriter(out, fieldnames=FIELDS, lineterminator=chr(10))
    w.writeheader()
    for r in rows:
        w.writerow(dict((k, r.get(k, '')) for k in FIELDS))
    out.close()


def add(rows_in):
    """Append rows, replacing any (week_start, pair) already present."""
    rows = load()
    keys = set((r['week_start'], r['pair']) for r in rows_in)
    rows = [r for r in rows if (r['week_start'], r['pair']) not in keys]
    rows.extend(rows_in)
    rows.sort(key=lambda r: (r['week_start'], -abs(float(r['gap'] or 0))))
    save(rows)
    return len(rows)


def spearman(pairs):
    """Rank correlation between gap and realised move. None if n < 3."""
    n = len(pairs)
    if n < 3:
        return None
    by_gap = sorted(pairs, key=lambda p: -p[1])
    by_out = sorted(pairs, key=lambda p: -p[2])
    d2 = sum((by_gap.index(p) - by_out.index(p)) ** 2 for p in pairs)
    return 1 - 6.0 * d2 / (n * (n * n - 1))


def weekly_ranking(metric='mfe_pips'):
    """{week: (rho, n)} - did conviction rank the outcomes?"""
    rows = load()
    weeks = {}
    for r in rows:
        weeks.setdefault(r['week_start'], []).append(r)
    out = {}
    for wk, rs in sorted(weeks.items()):
        pts = [(r['pair'], float(r['gap']), float(r[metric] or 0))
               for r in rs if r.get(metric)]
        out[wk] = (spearman(pts), len(pts))
    return out


def verdict(metric='mfe_pips'):
    """Three consecutive inverted weeks is a signal, not noise."""
    wk = weekly_ranking(metric)
    seq = [(k, v[0]) for k, v in sorted(wk.items()) if v[0] is not None]
    if not seq:
        return 'NO GRADED WEEKS YET', seq
    tail = [r for _, r in seq[-3:]]
    if len(tail) >= 3 and all(r < 0 for r in tail):
        return ('*** THREE CONSECUTIVE INVERTED WEEKS - the gap is ranking '
                'backwards. INVESTIGATE, do not wait.', seq)
    if len(tail) >= 3 and all(r > 0.5 for r in tail):
        return 'three consecutive well-ranked weeks - the gap is working', seq
    return ('%d week(s) logged - need 3 consecutive in one direction to call '
            'it' % len(seq), seq)


if __name__ == '__main__':
    rows = load()
    print('OUTCOME LEDGER  %s' % LEDGER)
    print('  %d row(s)' % len(rows))
    if not rows:
        print('  empty - nothing has been graded yet')
        sys.exit(0)
    print()
    print('%-11s %-8s %-6s %6s %9s %9s %9s' % (
        'WEEK', 'PAIR', 'BIAS', 'GAP', 'MFE', 'MAE', 'CLOSE'))
    for r in rows:
        print('%-11s %-8s %-6s %6s %9s %9s %9s' % (
            r['week_start'], r['pair'], r['direction'], r['gap'],
            r['mfe_pips'], r['mae_pips'], r['close_pips']))
    print()
    for metric, label in (('mfe_pips', 'PEAK (MFE)'),
                          ('close_pips', 'CLOSE')):
        wk = weekly_ranking(metric)
        print('CONVICTION RANKING on %s' % label)
        for k, (rho, n) in sorted(wk.items()):
            print('   %s  rho %s  (n=%d)'
                  % (k, ('%+.2f' % rho) if rho is not None else ' n/a', n))
        v, _ = verdict(metric)
        print('   -> %s' % v)
        print()
