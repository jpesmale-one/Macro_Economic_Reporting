# -*- coding: utf-8 -*-
"""The WEEK-AHEAD CALIBRATOR - the second half of pair selection (LD-98).

Jeff, 2026-09-04: "In here we are scoring the day not the category. It can
perceive as 'Does USD (for example) is positive or negative on Monday?' We
don't look at it as the usual category separation."

THE DAY IS THE UNIT. One score per currency per day, summed across the week.
There is NO CATEGORY WEIGHT anywhere in this file - weights live only in the
base scoring (fact_tables.py). Two separate scales that meet at the tally:

    FINAL = base (-9 .. +9)  +  calibrator (-5 .. +5)

That bound is deliberate. The week ahead RE-RANKS the board but cannot
overturn it, and a busy day is worth no more than a quiet one - a currency
with four releases on Thursday scores that Thursday ONCE, not four times.
The alternative lets a crowded calendar outvote the macro base by accident.

THE TWO COLLISION RULES (Jeff's own examples):

  RULE 1  same day, DIFFERENT reference months -> the LATEST month wins.
          "EUR have Unemployment Rate JUL and S&P Global Manufacturing PMI
          Final AUG ... we give focus on the PMI for that day."

  RULE 2  same day, SAME reference month -> they SHARE the day, averaged.
          "JPY have S&P Global Manufacturing PMI Final AUG and Consumer
          Confidence AUG since both of them is for AUG month only then the
          score would be (+1+1)/2"

GRADING each row: subject the Cons-Fcst range to that indicator's own macro
criterion, through the SAME channel logic as the base scoring (LD-94) -
unemployment lower-is-better, inflation through the rate channel, everything
else against consensus where TE publishes one and forecast where it does not
(F-85). Direction of goodness is never re-derived here; week_ahead owns it.
"""
import io, os, sys, csv, glob, json, re
import collections
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import week_ahead as wa
from test_pricing import num
import fact_tables as ft

MONTHS = ('jan', 'feb', 'mar', 'apr', 'may', 'jun',
          'jul', 'aug', 'sep', 'oct', 'nov', 'dec')

# The whitelist threshold for each row, so direction survives (F-66/F-68).
def _thresholds():
    import score_model as sm
    out = {}
    for cat, iso, name, a, p, ref, thr, v in sm.ROWS:
        out[(sm.LABEL[iso], name)] = thr
    return out


THR = _thresholds()


def ref_month(raw_event):
    """The reference month a TE row is FOR, as a sortable key.

    'balance of trade aug' -> (0, 8). 'machinery orders yoy jul' -> (0, 7).
    A quarter ('q2') sorts by its last month. None when nothing is named -
    such a row cannot be compared and never wins RULE 1.
    """
    e = (raw_event or '').lower()
    q = re.search(r'\bq([1-4])\b', e)
    if q:
        return (0, int(q.group(1)) * 3)
    for i, m in enumerate(MONTHS, 1):
        if re.search(r'\b%s\b' % m, e):
            return (0, i)
    return None


def score_row(ccy, name, rec):
    """+1 / 0 / -1 for one scheduled row, or None if unscorable.

    Grades the EXPECTATION - previous against the consensus/forecast range -
    which is what "what the market is pricing" means before a release.
    """
    prev = num(rec.get('previous'))
    cons = num(rec.get('consensus'))
    fcst = num(rec.get('forecast'))
    if cons is None:
        cons = fcst            # F-85: forecast is the documented fallback
    if prev is None or cons is None:
        return None
    v = wa.market_pricing(prev, cons, fcst, name=name,
                          threshold=THR.get((ccy, name)), ccy=ccy)
    return {'GOOD': 1, 'NEUTRAL': 0, 'BAD': -1}.get(v)


def week_rows(capture, start, end):
    """Every whitelist row in the window, with its score and reference month."""
    raw = json.load(io.open(capture, encoding='utf-8'))
    ISO = {'US': 'USD', 'GB': 'GBP', 'EA': 'EUR', 'JP': 'JPY',
           'CH': 'CHF', 'CA': 'CAD', 'AU': 'AUD', 'NZ': 'NZD'}
    idx = {}
    for r in raw:
        if r['iso'] in ISO:
            idx[(r['date'], ISO[r['iso']], r['event'])] = r

    timed, untimed = wa.whitelist_events(capture, start, end)
    out = []
    for when, ccy, name, rawev, d in list(timed) + list(untimed):
        rec = idx.get((d, ccy, rawev), {})
        out.append(dict(when=when, ccy=ccy, name=name, raw=rawev,
                        day=when.date() if when else None,
                        month=ref_month(rawev), score=score_row(ccy, name, rec),
                        cons=(rec.get('consensus') or '').strip(),
                        fcst=(rec.get('forecast') or '').strip(),
                        prev=(rec.get('previous') or '').strip()))
    return out


def day_score(rows):
    """One score for one currency on one day (LD-98 rules 1 and 2).

    Returns (score, rule, kept, dropped). Rows that cannot be scored drop
    out entirely - they are NOT counted as 0, which would dilute the day
    toward neutral on an absence (the F-73 shape).

    RULE 1a - A GAP IN LD-98, DECIDED HERE AND FLAGGED. Jeff's rule says the
    latest reference month wins the day. It does not say what happens when
    THE LATEST ROW IS UNSCORABLE and an earlier one is not - which is live
    on JPY, Wed 16 Sep: Balance of Trade AUG has no previous or consensus,
    while Machinery Orders YoY JUL scores -1.

    THE CHOICE MADE: precedence runs over SCORABLE rows only, so the JUL row
    carries the day. The alternative - the unscorable AUG row wins and
    blanks the day - throws away a real signal to honour a row that carries
    none. But it IS a choice, and Jeff has not ratified it.
    """
    scored = [r for r in rows if r['score'] is not None]
    if not scored:
        return None, 'unscorable', [], list(rows)
    dated = [r for r in scored if r['month'] is not None]
    if dated:
        top = max(r['month'] for r in dated)
        latest = [r for r in dated if r['month'] == top]
        undated = [r for r in scored if r['month'] is None]
        if len(latest) < len(dated) or undated:
            # RULE 1 - a later month supersedes; undated rows never win
            keep = latest
            rule = 'latest month'
        else:
            keep = latest
            rule = 'shared' if len(keep) > 1 else 'single'
    else:
        keep = scored
        rule = 'shared' if len(keep) > 1 else 'single'
    if len(keep) > 1:
        rule = 'shared'
    val = sum(r['score'] for r in keep) / float(len(keep))
    drop = [r for r in rows if r not in keep]
    return val, rule, keep, drop


def calibrate(capture, start, end):
    """{ccy: {'total', 'days': {date: (score, rule, kept, dropped)}}}."""
    rows = week_rows(capture, start, end)
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        if r['day'] is not None:
            by[r['ccy']][r['day']].append(r)
    out = {}
    for c in ft.CCYS:
        days = {}
        tot = 0.0
        for d, rs in sorted(by.get(c, {}).items()):
            val, rule, keep, drop = day_score(rs)
            if val is None:
                continue
            days[d] = (val, rule, keep, drop)
            tot += val
        out[c] = {'total': tot, 'days': days}
    return out


if __name__ == '__main__':
    cap = sorted(glob.glob(os.path.join(
        REPO, 'data/raw/calendar/*_cal_full.json')))[-1]
    start = sys.argv[1] if len(sys.argv) > 2 else '2026-09-14'
    end = sys.argv[2] if len(sys.argv) > 2 else '2026-09-18'
    print('CALIBRATOR (LD-98)  %s .. %s' % (start, end))
    print('capture: %s' % os.path.basename(cap))
    print()
    res = calibrate(cap, start, end)
    for c in sorted(res, key=lambda x: -res[x]['total']):
        d = res[c]
        if not d['days']:
            print('  %-4s  %+5.2f   (no scheduled rows)' % (c, d['total']))
            continue
        print('  %-4s  %+5.2f' % (c, d['total']))
        for day, (val, rule, keep, drop) in sorted(d['days'].items()):
            names = ', '.join('%s %+d' % (r['name'][:26], r['score'])
                              for r in keep)
            print('        %s  %+5.2f  [%s]  %s'
                  % (day.strftime('%a %d'), val, rule, names))
            for r in drop:
                why = ('unscorable' if r['score'] is None
                       else 'superseded by a later month')
                print('              dropped: %-28s (%s)'
                      % (r['name'][:28], why))
