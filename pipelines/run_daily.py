# -*- coding: utf-8 -*-
"""Run one daily build, in order, stopping at the first real failure.

*** WHY A RUNNER AND NOT A LIST, FOR THE SECOND TIME.

CLAUDE.md 0a-ii already answered this for the WEEKLY: "This file listed ~20
guards, and in three weeks that list failed three times the same way - the
step was there and I ran it slightly wrong. A checklist that cannot check
itself is a wish." build_check.py was the answer, and the weekly has not
mis-ordered a step since.

The DAILY never got the same treatment. It is ten commands in a documented
order, typed by hand, and every one of its ordering traps has now fired at
least once in a published report:

    F-188  the session had not CLOSED        -> a hit target published as DRIFT
    F-190  the bars were not raw PRICE       -> four of ten states flipped
    R-50   the 28-pair grid was incomplete   -> 40 of 40 read BROAD
    F-192  the ATR never reached the ledger  -> five builds filled by hand
    LD-162 the capture was from yesterday    -> real prints read NO CATALYST

Not one of those announced itself. Each produced a page that was internally
consistent, plausible, and wrong - which is precisely the failure a human
reading his own output cannot catch, and a gate run in a fixed order can.

*** WHAT THIS DOES NOT DO. It does not decide anything. It does not touch the
weekly board or the set (LD-97), it does not score, and it does not publish.
It runs the steps that are already the protocol, in the order the protocol
already specifies, and it REFUSES rather than proceeding on bad data. LD-4
holds absolutely: no lot size, entry, stop, target or order anywhere in it.

*** THE STEP THAT CANNOT BE AUTOMATED, AND IS NOT PRETENDED AWAY.
pull_bars.py drives a live TradingView window over CDP. If that window is
closed or its bridge is wedged, no amount of orchestration conjures price,
and LD-5 forbids a fallback source - Yahoo is NEVER one. So this runner
CHECKS the bars and tells you to pull them; it does not fake them, and it
does not continue without them.

    python pipelines/run_daily.py                  # today's session, dry run
    python pipelines/run_daily.py --session 2026-11-18
    python pipelines/run_daily.py --go             # actually build the page
"""
import os
import re
import sys
import glob
import subprocess
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

PY = sys.executable

# The 28-pair grid LD-168/R-50 requires. Not the majors - a thin grid makes
# every move read BROAD, because breadth is measured against the counterparts
# we actually hold bars for.
GRID = [
    'EURUSD', 'EURGBP', 'EURAUD', 'EURNZD', 'EURCAD', 'EURCHF', 'EURJPY',
    'GBPUSD', 'GBPAUD', 'GBPNZD', 'GBPCAD', 'GBPCHF', 'GBPJPY',
    'AUDUSD', 'AUDNZD', 'AUDCAD', 'AUDCHF', 'AUDJPY',
    'NZDUSD', 'NZDCAD', 'NZDCHF', 'NZDJPY',
    'USDCAD', 'USDCHF', 'USDJPY', 'CADCHF', 'CADJPY', 'CHFJPY',
]


def run(args, env=None, timeout=900):
    """A child step. Returns (returncode, combined output)."""
    e = dict(os.environ)
    if env:
        e.update(env)
    p = subprocess.run([PY] + args, cwd=REPO, env=e, timeout=timeout,
                       capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    return p.returncode, (p.stdout or '') + (p.stderr or '')


def newest_capture():
    """The date of the most recent calendar capture on disk, or None."""
    caps = sorted(glob.glob(os.path.join(
        REPO, 'data/raw/calendar/*_cal_full.json')))
    if not caps:
        return None
    m = re.search(r'(\d{4}-\d{2}-\d{2})_', os.path.basename(caps[-1]))
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# The gates. Each returns (ok, detail). None of them writes to a fact table.
# ---------------------------------------------------------------------------

def g_publication_day(ctx):
    """LD-156 / F-157: do not publish ON a Monday or a weekend.

    The test is on TODAY, the publication day, never on the session - the
    Tuesday edition REPORTS the Monday session, which is its whole content.
    F-157 got this backwards and refused a legitimate build.
    """
    today = dt.date.today()
    if today.weekday() == 0:
        return False, ('today is MONDAY - the weekly is the baseline '
                       '(LD-156). No daily is published today.')
    if today.weekday() >= 5:
        return False, 'today is the weekend - no daily is published'
    wd = dt.datetime.strptime(ctx['session'], '%Y-%m-%d').date().weekday()
    if wd >= 5:
        return False, ('session %s is a weekend - there are no bars for it'
                       % ctx['session'])
    return True, 'publishing %s, reporting the %s session' % (
        today.isoformat(), ctx['session'])


def g_capture_fresh(ctx):
    """LD-162: the capture must be from the session day or later.

    releases_by_day() reads ACTUALS, and TE only carries one once a row has
    released. Yesterday's capture therefore shows "nothing scheduled" for
    rows that printed - a confident "no catalyst" on a day that had five.
    """
    n = newest_capture()
    if not n:
        return False, 'no calendar capture on disk at all'
    if n < ctx['session']:
        return False, ('newest capture is %s, older than the %s session - '
                       'run capture_calendar.py --write, or every release '
                       'that day reads as NO CATALYST' % (n, ctx['session']))
    return True, 'newest capture %s covers the session' % n


def g_grid_complete(ctx):
    """R-50 / LD-168: all 28 crosses present, and none behind THE OTHERS.

    *** A STALE FILE DOES NOT ERROR, IT SILENTLY SHRINKS n. The 17 Oct retro
    measured 40 of 40 sessions BROAD-ish with NARROW never firing once,
    because CHF and NZD had ONE counterpart each on disk. The same week on
    the full grid reads 20 NARROW / 10 mostly / 10 BROAD. The breadth
    reading was not noisy - it was structurally unable to say NARROW.

    *** THIS GATE TESTS COMPLETENESS, NOT FRESHNESS, AND THE FIRST VERSION
    CONFLATED THEM. It compared every cross against the SESSION, so on a day
    when no pull had run yet it reported "28 crosses are behind the session"
    and stopped the run there - before F-188, the gate that actually owns
    that question, could say the clearer thing: the session is still open.
    All 28 files were present and uniformly at the same date; nothing was
    incomplete at all.

    A gate that fires for someone else's reason is worse than a missing
    gate, because the message sends you looking in the wrong place. So the
    comparison here is cross-vs-cross: the test is whether the grid is
    RAGGED, which is what silently shrinks n. Whether the newest bar is
    recent enough belongs to F-188 alone.
    """
    import daily_report as dr
    missing, newest = [], {}
    for p in GRID:
        b = dr.bars(p)
        if not b:
            missing.append(p)
        else:
            newest[p] = b[-1][0]
    if missing:
        return False, ('%d cross(es) have no bars: %s'
                       % (len(missing), ', '.join(missing[:6])))
    top = max(newest.values())
    behind = sorted('%s@%s' % (p, d) for p, d in newest.items() if d != top)
    if behind:
        return False, ('grid is RAGGED - %d cross(es) behind %s, so breadth '
                       'would be measured on a thinner set than it reports '
                       '(R-50): %s' % (len(behind), top, ', '.join(behind[:6])))
    return True, 'all %d crosses present and level at %s' % (len(GRID), top)


def g_session_closed(ctx):
    """F-188: the reported session must be FINISHED.

    Delegated to build_check step 11c, which is the authority for this test -
    duplicating the logic here would let the two drift apart, and a guard
    that disagrees with its own twin is worse than one guard.
    """
    import build_check as bc
    os.environ['SESSION'] = ctx['session']
    return bc.s11c_session_closed()


def g_bars_are_price(ctx):
    """F-190: refuse a pull that is not raw price.

    3,667 of 8,400 bars once had `open` overwritten by the low or the high -
    44% - and it flipped four of ten session states while every number on the
    page stayed internally consistent. The 20% threshold sits far above
    ordinary doji noise (real populations measure 0-13%) and far below the
    44% a corrupt pull produced.
    """
    import daily_report as dr
    bad = []
    for p in GRID:
        b = dr.bars(p)
        if not b:
            continue
        n = len(b)
        ext = sum(1 for x in b
                  if float(x[1]) == float(x[3]) or float(x[1]) == float(x[2]))
        if ext * 100 >= n * 20:
            bad.append('%s %d%%' % (p, ext * 100 // n))
    if bad:
        return False, ('opens equal an extreme too often - NOT RAW PRICE '
                       '(F-190): %s' % ', '.join(bad[:6]))
    return True, 'no cross shows the F-190 signature'


def g_ledger_writes_atr(ctx):
    """F-192 / R-51: the per-session ledger must carry atr_pips.

    A blank atr_pips is a legal CSV cell that silently drops the row from
    every ATR-normalised read (LD-176, F-73). It was filled by hand on five
    consecutive builds before anyone noticed the generator had stopped
    writing it.
    """
    rc, out = run([os.path.join(HERE, 'test_session_log.py')])
    if rc != 0:
        last = [l for l in out.splitlines() if 'FAIL' in l or 'FAILURE' in l]
        return False, (last[-1].strip() if last else 'test_session_log failed')
    return True, 'R-51 passes - every row carries an ATR'


GATES = [
    ('publication day (LD-156/F-157)', g_publication_day),
    ('capture covers the session (LD-162)', g_capture_fresh),
    ('28-cross grid complete (R-50/LD-168)', g_grid_complete),
    ('bars are raw price (F-190)', g_bars_are_price),
    ('reported session has CLOSED (F-188)', g_session_closed),
    ('ledger writes atr_pips (F-192/R-51)', g_ledger_writes_atr),
]


def default_session():
    """The session a build run today would report.

    Tuesday reports Monday; Wednesday reports Tuesday. On a Monday there is
    no publication at all, but return the preceding Friday so the gate can
    say so clearly rather than erroring on an empty value.
    """
    t = dt.date.today()
    back = 3 if t.weekday() == 0 else (2 if t.weekday() == 6 else 1)
    d = t - dt.timedelta(days=back)
    while d.weekday() >= 5:
        d -= dt.timedelta(days=1)
    return d.isoformat()


def main():
    a = sys.argv[1:]
    session = a[a.index('--session') + 1] if '--session' in a \
        else default_session()
    go = '--go' in a

    ctx = {'session': session}
    print('DAILY BUILD RUNNER   session %s' % session)
    print('  mode: %s' % ('BUILD' if go else 'DRY RUN - gates only'))
    print()

    failed = None
    for label, fn in GATES:
        try:
            ok, detail = fn(ctx)
        except Exception as e:
            ok, detail = False, 'raised %s: %s' % (type(e).__name__, e)
        print('  %-4s %-38s %s' % ('PASS' if ok else 'FAIL', label, detail))
        if not ok and failed is None:
            failed = label

    print()
    if failed:
        print('*** STOP - %s' % failed)
        print('    Nothing was built. A later step run on bad data produces')
        print('    a page where every number agrees with every other number')
        print('    and the session is still wrong (F-188, F-190).')
        return 1

    print('  all %d gates pass' % len(GATES))
    if not go:
        print()
        print('  DRY RUN - pass --go to build. It would then run:')
        print('    daily_report.py %s     (console read)' % session)
        print('    gen_daily.py %s        (the page)' % session)
        return 0

    print()
    for script in ('daily_report.py', 'gen_daily.py'):
        print('  running %s %s' % (script, session))
        rc, out = run([os.path.join(HERE, script), session])
        for line in out.splitlines():
            print('    | %s' % line)
        if rc != 0:
            print()
            print('*** %s exited %d - stopping.' % (script, rc))
            return rc

    print()
    print('  BUILT. Still to do by hand, because each needs the file:')
    print('    python pipelines/shell_check.py <page.html>     R-43')
    print('    then read the page before publishing (LD-167 publish gate)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
