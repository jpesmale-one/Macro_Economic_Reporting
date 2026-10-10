# -*- coding: utf-8 -*-
"""THE DAILY REPORT - WHAT MOVED THE MARKET YESTERDAY, AND DID IT CONFIRM US?

Jeff, 2026-10-10:

    "it's primary objective is to give explanation as to what moves the
     prices. Tuesday -- Show the Currency Rank based on Monday price movement.
     Is it confirming to our Bias or not. And then look for explanation or the
     catalyst for each of the Currencies movements whether market reacted on a
     certain news we're tracking or not, Central Bank press releases, etc."

    "For Monday we should not create a daily report since the Weekly report is
     our baseline for Monday"

*** THE PROBLEM IT EXISTS FOR, MEASURED. On 5-9 Oct the model learned on
SATURDAY that AUD had beaten the entire board. MONDAY ALONE did most of the
damage - three of four pairs BEATEN on day one, EURAUD at 1.74x ATR adverse,
before any scheduled release. A daily would have said so on Monday evening.
And EUR's 17-month low came at the end of FIVE CONSECUTIVE DOWN WEEKS; the
weekly cadence reported each leg of that as a fresh surprise.

WHAT IT IS NOT. This reports what happened and whether the bias is confirming.
It does NOT re-rank the board, re-select pairs, or tell anyone to act. The
weekly is the decision (LD-97) and Monday's baseline is the weekly itself -
which is exactly why Monday has no daily.

*** SCOPE (LD-4). Observation only: ranks, moves, and the releases that landed.
No entries, no stops, no targets, no sizing. "The bias is not confirming" is an
observation; "so exit" is the money path, and the distinction is the whole
reason this is safe to run daily.

HONESTY RULE, AND IT IS THE HARD PART. The report must say WHEN IT CANNOT
EXPLAIN A MOVE. A currency that moved 0.6% on a day with no scheduled release
and no decision gets "NO SCHEDULED CATALYST" - not a story. Financial
commentary always has an explanation; that is what makes it unreliable. On
5-9 Oct the true cause was a positioning shift no calendar could show, and a
report that invented a reason would have been worse than one that admitted it.

    python pipelines/daily_report.py              # yesterday's session
    python pipelines/daily_report.py 2026-10-06   # a named session
"""
import io
import os
import sys
import glob
import json
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import pair_atr as pa
import atr_grade as ag
import daily_review as dr

TXT = ('C:/Users/jpesm/AppData/Local/Temp/claude/'
       'c--Users-jpesm-OneDrive-Documents-GitHub/'
       '16c8f514-dc2c-4587-b6a0-4fa0ff0b7ba8/scratchpad')

MAJ = ['EURUSD', 'GBPUSD', 'AUDUSD', 'NZDUSD', 'USDJPY', 'USDCAD', 'USDCHF']
CCYS = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'NZD', 'CAD', 'CHF']


def bars(pair):
    """[(session, o, h, l, c)] from a pull_bars .txt, or None."""
    p = os.path.join(TXT, '%s.txt' % pair)
    if not os.path.exists(p):
        return None
    out = []
    for ln in io.open(p, encoding='utf-8'):
        x = ln.split()
        if len(x) >= 5:
            out.append((pa.session(int(x[0])),)
                       + tuple(float(v) for v in x[1:5]))
    return sorted(out)


def session_strength(day):
    """{ccy: % change} for one session, open to close, or None.

    Open-to-close rather than close-to-close: the question is what THAT
    SESSION did, and an overnight gap belongs to the session that opened it.
    """
    chg = {}
    for p in MAJ:
        b = bars(p)
        if not b:
            return None
        row = [x for x in b if x[0] == day]
        if not row:
            return None
        _, o, h, l, c = row[0]
        chg[p] = (c - o) / o * 100.0
    usd = sum((chg[p] if p.startswith('USD') else -chg[p])
              for p in MAJ) / len(MAJ)
    out = {'USD': usd}
    for ccy in CCYS:
        if ccy == 'USD':
            continue
        for p in MAJ:
            if p[:3] == ccy:
                out[ccy] = chg[p] + usd
            elif p[3:] == ccy:
                out[ccy] = -chg[p] + usd
    return out


def catalysts(day):
    """{ccy: [(hh:mm, event, actual, forecast)]} for releases ON that day.

    *** ACCEPTS A STRING OR A date, AND THAT IS NOT A CONVENIENCE. The first
    version compared `day` to a datetime.date while report() passed an ISO
    STRING, so every lookup silently returned NOTHING and the catalyst column
    read "quiet, nothing scheduled" on a Friday that carried SIXTEEN releases
    including the CAD employment collapse (-68.3K vs +65K forecast).
    A silent empty is the one failure this report cannot afford: it does not
    look broken, it looks like calm.
    """
    if not isinstance(day, dt.date):
        day = dt.datetime.strptime(str(day), '%Y-%m-%d').date()
    rel = dr.releases_by_day()
    out = {}
    for (ccy, d), evs in rel.items():
        if d != day:
            continue
        for name, (hhmm, act, fc) in evs.items():
            out.setdefault(ccy, []).append((hhmm, name, act, fc))
    for c in out:
        out[c].sort()
    return out


def beat(actual, forecast):
    """'BEAT' / 'MISS' / 'INLINE' / None - did the print clear expectation?"""
    import score_model as sm
    a, f = sm._num(actual), sm._num(forecast)
    if a is None or f is None:
        return None
    if a > f:
        return 'BEAT'
    if a < f:
        return 'MISS'
    return 'INLINE'


def explain(ccy, move, evs):
    """A one-line read of why a currency moved, or an honest refusal.

    *** THE REFUSAL IS THE POINT. If nothing we track landed, the report says
    NO SCHEDULED CATALYST rather than reaching for a narrative.
    """
    big = abs(move) >= 0.25
    if not evs:
        return ('NO SCHEDULED CATALYST - nothing we track released'
                if big else 'quiet, nothing scheduled')
    hits = []
    for hhmm, name, act, fc in evs:
        b = beat(act, fc)
        if b in ('BEAT', 'MISS'):
            hits.append('%s %s (%s vs %s)' % (name[:26], b, act, fc))
    if not hits:
        return ('%d release(s), all in line - move is NOT explained by them'
                % len(evs)) if big else '%d release(s), all in line' % len(evs)
    agree = [h for h in hits
             if (('BEAT' in h) == (move > 0))]
    tag = 'CONSISTENT' if agree else 'AGAINST the move'
    return '%s | %s' % ('; '.join(hits[:2]), tag)


def report(day, board=None, picks=None):
    """Print the daily. `board` is {ccy: score}; `picks` is [(pair, side)]."""
    # *** A DAILY NEEDS A CAPTURE FROM THAT MORNING, OR THE CATALYST COLUMN
    # LIES BY OMISSION. releases_by_day() reads ACTUALS, and TE only carries
    # an actual once the row has released - so a Tuesday report built on
    # Sunday's capture shows "nothing scheduled" for five rows that printed.
    # The first run did exactly that and it is the worst possible failure for
    # this report: a confident "no catalyst" on a day that had five.
    caps = sorted(glob.glob(os.path.join(
        REPO, 'data/raw/calendar/*_cal_full.json')))
    newest = None
    if caps:
        import re as _re
        m = _re.search(r'(\d{4}-\d{2}-\d{2})_', os.path.basename(caps[-1]))
        newest = m.group(1) if m else None
    if newest and newest < day:
        print('*** CAPTURE IS OLDER THAN THE SESSION (%s < %s).' % (newest, day))
        print('    Run capture_calendar.py --write first, or every release')
        print('    that day will read as NO CATALYST when it simply is not')
        print('    in the data yet.')
        print()

    s = session_strength(day)
    if not s:
        print('no bars for %s - pull them from TradingView first' % day)
        return 1
    ev = catalysts(day)
    order = sorted(s, key=lambda c: -s[c])

    print('DAILY REPORT   session %s (PHT)' % day)
    print('what moved, and whether it confirms the weekly bias')
    print()
    print('  %-4s %9s  %-5s %-7s %s'
          % ('CCY', 'MOVE', 'RANK', 'BOARD', 'CATALYST'))
    brank = (sorted(board, key=lambda c: -board[c]) if board else [])
    for i, c in enumerate(order, 1):
        br = ('#%d' % (brank.index(c) + 1)) if board and c in brank else '-'
        print('  %-4s %+8.3f%%  #%-4d %-7s %s'
              % (c, s[c], i, br, explain(c, s[c], ev.get(c, []))[:68]))

    if board:
        print()
        gap = [(c, abs((brank.index(c) + 1) - (order.index(c) + 1)))
               for c in order if c in brank]
        worst = sorted(gap, key=lambda x: -x[1])[:3]
        print('  BIGGEST RANK GAPS vs the weekly board:')
        for c, g in worst:
            print('    %-4s board #%d, session #%d  (%d places)'
                  % (c, brank.index(c) + 1, order.index(c) + 1, g))

    if picks:
        print()
        print('  THE SET, this session:')
        for pair, side in picks:
            b = bars(pair)
            if not b:
                continue
            row = [x for x in b if x[0] == day]
            if not row:
                continue
            _, o, h, l, c = row[0]
            f = ag.pip_factor(pair)
            prior = [x for x in b if x[0] < day]
            atr = ag.atr([(hh, ll, cc) for _, oo, hh, ll, cc in prior], 14, f) \
                if len(prior) > 15 else None
            fav, adv, frac, hit = ag.grade_day(side, o, h, l, f, atr or 1)
            k = ag.classify(fav, adv, atr) if atr else '-'
            print('    %-8s %-6s fav %6.1f  adv %6.1f  %s'
                  % (pair, side, fav, adv, k))
    return 0


# *** THE BOARD IS READ FROM THE PUBLISHED EDITION, NEVER RECOMPUTED.
#
# The first version called ps.final_scores() live, which re-scored the board
# on today's fact tables and produced a DIFFERENT SET from the one actually
# published - GBPCHF and NZDCHF appeared, neither of which Jeff is holding.
# A daily that silently re-ranks is not reporting on the bias, it is quietly
# replacing it, and the reader would be grading pairs they never took.
#
# THE WEEKLY IS THE DECISION (LD-97) and Monday's baseline is the weekly
# itself - which is why Monday has no daily. So the daily reads the SEALED
# numbers off the edition's own markdown and treats them as fixed for the
# week. If the file is missing it says so and reports ranks alone rather than
# inventing a baseline.
EDITION_BOARD = {}
EDITION_SET = []


def load_edition(path=None):
    """Read the board and set from the published weekly .md.

    *** ANCHOR ON THE SECTION, NOT ON A ROW SHAPE. Two earlier attempts bound
    to the wrong table: a positional "| CCY | ... | number |" regex picked up
    the CALIBRATOR table and put CHF at board #1 when it is #6, and a
    rank-marker regex matched only the five rows that happen to carry "(#n)".
    A document with several similar tables will defeat any row-level pattern
    sooner or later. This finds the "### §1 — The board" heading first and
    reads only the rows under it, so the FINAL column is unambiguous.
    """
    import re
    if path is None:
        c = sorted(glob.glob(os.path.join(REPO, 'reports/2026/Q*/*_weekly.md')))
        if not c:
            return None, None
        path = c[-1]
    txt = io.open(path, encoding='utf-8').read()

    board = {}
    k = txt.find('The board')
    if k > 0:
        blk = txt[k:k + 2000]
        for ln in blk.split(chr(10)):
            cells = [c.strip() for c in ln.split('|')]
            if len(cells) < 8:
                continue
            m = re.match(r'\*?\*?([A-Z]{3})\*?\*?$', cells[2])
            if not m:
                continue
            v = re.search(r'[+-]?\d+\.\d+', cells[6] or '')
            if v:
                board[m.group(1)] = float(v.group(0).replace(chr(8722), '-'))

    # THE SET is the numbered list under "THE SET:" - one line per pair, with
    # the direction on the same line. Read that rather than scanning the whole
    # document for any six letters followed by LONG/SHORT.
    picks = []
    t = txt.find('THE SET')
    if t > 0:
        for ln in txt[t:t + 900].split(chr(10)):
            m = re.search(r'\*\*\d+\.\s*([A-Z]{6})\s+(LONG|SHORT)\*\*', ln)
            if m:
                picks.append((m.group(1), m.group(2)))
    return (board or None), (picks[:4] or None)


def live_board():
    """(board, picks) as PUBLISHED - the weekly is the baseline, not a rerun."""
    b, p = load_edition()
    if not b:
        print('  (no published edition found - reporting ranks only)')
    return b, p


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    if a:
        day = a[0]
    else:
        d = dt.date.today() - dt.timedelta(days=1)
        day = d.isoformat()
    wd = dt.datetime.strptime(day, '%Y-%m-%d').date().weekday()
    if wd >= 5:
        print('%s is a weekend session - nothing to report' % day)
        sys.exit(0)
    _b, _p = live_board()
    sys.exit(report(day, _b, _p))
