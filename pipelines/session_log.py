# -*- coding: utf-8 -*-
"""LD-170 - THE PER-SESSION LEDGER, so a give-back day can be FOUND.

Jeff, 2026-10-24:

    "I think we need to observe this more. If we find a pattern then we can
     use this to somehow see what day the currencies usually gives back to
     the market. then I can avoid that day or close my trades before that
     day comes."

WHY THIS EXISTS. Two retros in a row were decided by ONE session. The
19-23 Oct week ran Mon 1.57, Tue 7.83, Wed 0.57, Thu 0.51, Fri 0.92 - remove
Thursday and a CONTESTED week reads 1.43, a WIN. The previous retro had the
same shape on a DIFFERENT day. So the question "is there a give-back day?"
is live, and TWO WEEKS CANNOT ANSWER IT: with 5 weekdays you need roughly
8-10 weeks before a weekday effect is distinguishable from one bad Thursday.

*** THE POINT OF THIS FILE IS THAT THE SAMPLE NOW ACCUMULATES. The same
failure outcome_log.py was built to fix (LD-111: "nothing was accumulating,
so the sample never grew and the wait never ended") applies here one level
down - we had weekly rows but no per-session rows, so every weekday claim
reasoned from the last retro's memory.

HONEST STATUS ON DAY ONE: n = 1 week on disk. This file promises NOTHING
about Thursdays. It makes the claim TESTABLE in about two months, and
weekday_table() refuses to call a winner until it has the sample.

LD-4 HOLDS ABSOLUTELY. This records what price DID, per session. It sets no
entry, no exit, no stop, no target. "Avoid Thursday" would be Jeff's call
on his own evidence, never an instruction from this repo.
"""
import io, os, csv
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
LEDGER = os.path.join(REPO, 'data', 'derived', 'sessions.csv')

FIELDS = ('week_start', 'session', 'weekday', 'pair', 'direction',
          'fav_pips', 'adv_pips', 'frac_atr', 'hit', 'state', 'note')

WEEKDAY = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')


def _rows():
    if not os.path.exists(LEDGER):
        return []
    with io.open(LEDGER, encoding='utf-8') as f:
        return list(csv.DictReader(f))


def append(week_start, session, pair, direction, fav, adv,
           frac=None, hit=None, state='', note=''):
    """Add one pair-session row. Idempotent on (week, session, pair).

    Re-running a daily build must not double-count the day, so an existing
    row for the same (week_start, session, pair) is REPLACED, not appended.
    """
    # *** F-164 - DIRECTION MUST BE UPPERCASE, AND A SILENT FALL-THROUGH
    # COST ME A WHOLE BACKFILL. atr_grade.grade_day tests `bias == 'LONG'`
    # and treats ANYTHING else as short, so passing 'long' graded every
    # long as a short and inverted fav/adv on all 20 rows. The numbers
    # matched the published retro EXACTLY but swapped, which is what
    # exposed it. A ledger that accepts a silently-wrong direction is
    # worse than no ledger, so this refuses rather than guesses.
    direction = (direction or '').strip().upper()
    if direction not in ('LONG', 'SHORT'):
        raise ValueError("direction must be 'LONG' or 'SHORT', got %r"
                         % direction)
    wd = WEEKDAY[dt.datetime.strptime(session, '%Y-%m-%d').date().weekday()]
    new = {'week_start': week_start, 'session': session, 'weekday': wd,
           'pair': pair, 'direction': direction,
           'fav_pips': '%.1f' % float(fav), 'adv_pips': '%.1f' % float(adv),
           'frac_atr': ('%.3f' % frac) if frac is not None else '',
           'hit': ('1' if hit else '0') if hit is not None else '',
           'state': state, 'note': note}
    keep = [r for r in _rows()
            if not (r['week_start'] == week_start
                    and r['session'] == session and r['pair'] == pair)]
    keep.append(new)
    keep.sort(key=lambda r: (r['session'], r['pair']))
    d = os.path.dirname(LEDGER)
    if not os.path.isdir(d):
        os.makedirs(d)
    with io.open(LEDGER, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, FIELDS, lineterminator='\n')
        w.writeheader()
        for r in keep:
            w.writerow(dict((k, r.get(k, '')) for k in FIELDS))
    return len(keep)


def session_ratio(session):
    """Sum(fav)/sum(adv) for one session across the set, or None."""
    rs = [r for r in _rows() if r['session'] == session]
    if not rs:
        return None
    f = sum(float(r['fav_pips']) for r in rs)
    a = sum(float(r['adv_pips']) for r in rs)
    return (f / a) if a > 0 else None


def weekday_table(min_weeks=8):
    """Per-weekday aggregate, and an EXPLICIT refusal while n is too small.

    min_weeks defaults to 8 because that is roughly where a one-weekday
    effect clears the noise of a single bad session. Below it the table is
    still printed - the numbers are real - but no pattern is asserted.
    """
    rs = _rows()
    weeks = sorted(set(r['week_start'] for r in rs))
    agg = {}
    for r in rs:
        d = agg.setdefault(r['weekday'], {'f': 0.0, 'a': 0.0, 'n': 0,
                                          'w': set()})
        d['f'] += float(r['fav_pips'])
        d['a'] += float(r['adv_pips'])
        d['n'] += 1
        d['w'].add(r['week_start'])
    out = []
    for wd in WEEKDAY[:5]:
        d = agg.get(wd)
        if not d:
            out.append((wd, None, 0, 0))
            continue
        out.append((wd, (d['f'] / d['a']) if d['a'] > 0 else None,
                    d['n'], len(d['w'])))
    return out, len(weeks), len(weeks) >= min_weeks


def report(min_weeks=8):
    tab, nweeks, ready = weekday_table(min_weeks)
    L = ['LD-170 PER-WEEKDAY LEDGER   weeks on disk: %d' % nweeks,
         '  %-5s %9s %7s %7s' % ('day', 'ratio', 'rows', 'weeks')]
    for wd, r, n, w in tab:
        L.append('  %-5s %9s %7d %7d'
                 % (wd, ('%.3f' % r) if r is not None else '-', n, w))
    if not ready:
        L.append('')
        L.append('  *** NOT ENOUGH DATA TO CLAIM A WEEKDAY EFFECT.')
        L.append('      %d of %d weeks. Numbers above are real but a '
                 'single bad' % (nweeks, min_weeks))
        L.append('      session still dominates. No day is called here.')
    return '\n'.join(L)


if __name__ == '__main__':
    print(report())
