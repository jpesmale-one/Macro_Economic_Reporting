# -*- coding: utf-8 -*-
"""R-46 - THE WEEKLY BUILD FLOW, AS A RUNNABLE CHECKLIST.

Jeff, 2026-09-21: "Should we create a report build process flow so that when
the next refresh comes we can prevent this mismatches? It's something that you
can follow every weekly report build so that it is more systematic and
standard"

WHY A SCRIPT AND NOT A DOCUMENT. CLAUDE.md already lists ~20 guards to run
before an edition. That list is a DOCUMENT, and in the three weeks it has
existed it failed three times in the same way:

    F-132  R-45 run WITHOUT --refresh, so it validated today's fact table
           against a week-old cached page and reported OK
    F-130  gen_page's DAYS left pinned to last week while START/END moved
    F-127  build_weekly on ps.select() while gen_page used ps.the_set()

Every one of those was "the step was listed and I ran it slightly wrong".
A checklist that cannot check itself is a wish. This runs the steps, in
order, and stops at the first one that fails.

    python pipelines/build_check.py            # before building
    python pipelines/build_check.py --page X   # also check an assembled page

WHAT IT DELIBERATELY DOES NOT DO. It does not BUILD anything and it does not
WRITE to the fact tables. It reports, and a human decides. R-45's own
docstring explains why: a slug that resolves to the wrong series would
rewrite good data with a plausible number, and that failure is invisible
from inside the repo.
"""
import io
import os
import re
import sys
import glob
import subprocess
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import phtime as pt


def _py(*args):
    """Run a pipeline module, return (exit_code, output)."""
    r = subprocess.run([sys.executable] + list(args), cwd=REPO,
                       capture_output=True, text=True,
                       env=dict(os.environ, PYTHONIOENCODING='utf-8'))
    return r.returncode, (r.stdout or '') + (r.stderr or '')


def window():
    """The Mon-Fri window this build is for.

    *** F-136 - THE CHECKER MUST FOLLOW THE EDITION, NOT THE CALENDAR.
    The first version derived the window from today alone: any non-Sunday
    build was assumed to target NEXT week. Run on Wednesday 23 Sep it
    demanded 28 Sep-02 Oct and failed the renderers for being on the CURRENT
    edition's 21-25 Sep - blaming correct code, which is the same shape as
    R-43's own F-130 fix.

    STATE.md's header is the authority on edition identity (CLAUDE.md
    section 0), so read the live edition's window from the renderer and only
    fall back to the calendar when there is nothing to read.
    """
    src = io.open(os.path.join(HERE, 'gen_page.py'), encoding='utf-8').read()
    m = re.search(r"START, END = '(\d{4}-\d{2}-\d{2})', '(\d{4}-\d{2}-\d{2})'",
                  src)
    if m:
        return m.group(1), m.group(2)
    d = dt.datetime.now(pt.PHT).date()
    mon = d + dt.timedelta(days=(7 - d.weekday()) % 7 or 7)
    if d.weekday() == 6:                      # Sunday build -> tomorrow
        mon = d + dt.timedelta(days=1)
    return mon.isoformat(), (mon + dt.timedelta(days=4)).isoformat()


# ---------------------------------------------------------------- steps ---
# Each step: (id, label, callable -> (ok, detail)). Order matters: data is
# refreshed and verified BEFORE anything is built from it.

def s1_capture():
    """The capture must be fresh, or the week's own releases are missing."""
    caps = sorted(glob.glob(os.path.join(
        REPO, 'data/raw/calendar/*_cal_full.json')))
    if not caps:
        return False, 'no capture at all'
    m = re.search(r'(\d{4}-\d{2}-\d{2})_', os.path.basename(caps[-1]))
    taken = dt.datetime.strptime(m.group(1), '%Y-%m-%d').date()
    age = (dt.datetime.now(pt.PHT).date() - taken).days
    if age > 3:
        return False, ('newest capture is %s, %d days old - the TE window '
                       'has rotated (F-121). Run capture_calendar.py --write'
                       % (taken, age))
    return True, 'newest capture %s (%d days old)' % (taken, age)


def s2_gaps():
    """R-42: did a release print while no capture could see it?"""
    code, out = _py(os.path.join(HERE, 'capture_gap.py'), '--raise')
    lost = re.search(r'\*\*\* (\d+) ROW\(S\) CANNOT BE RECOVERED', out)
    if lost:
        return False, ('%s row(s) lost to a capture gap - recover from the '
                       'indicator page and record in RECOVERED.md'
                       % lost.group(1))
    return True, 'no release fell through a gap'


def s3_indicator_pages():
    """R-45 WITH --refresh. F-132: without it this reads a stale cache."""
    code, out = _py(os.path.join(HERE, 'indicator_pages.py'), '--refresh')
    bad = re.search(r'\*\*\* (\d+) ROW\(S\) DISAGREE WITH TE', out)
    cov = re.search(r'TRUE COVERAGE: (\d+) of (\d+)', out)
    detail = cov.group(0) if cov else 'coverage unknown'
    if bad:
        return False, '%s row(s) disagree with TE. %s' % (bad.group(1), detail)
    return True, detail


def s4_vintage():
    """R-37/R-40: held values vs what we have captured, value AND month."""
    for mod, name in ((('audit_evidence.py',), 'R-37'),
                      (('vintage_check.py',), 'R-40')):
        code, out = _py(os.path.join(HERE, mod[0]))
        if code != 0 or re.search(r'\*\*\*', out):
            n = re.search(r'(\d+) problem', out)
            return False, '%s reports %s' % (name, n.group(0) if n else 'a problem')
    return True, 'R-37 and R-40 clean'


def s5_rules():
    """R-44: every scoring rule, and both scorers agreeing."""
    code, out = _py(os.path.join(HERE, 'test_inflation.py'))
    if code != 0:
        n = re.search(r'\*\*\* (\d+) FAILURE', out)
        return False, 'R-44 %s' % (n.group(0) if n else 'failed')
    n = re.search(r'(\d+) cases pass', out)
    return True, n.group(0) if n else 'passed'


def s6_rates():
    """LD-142: the fact table's rate cells must equal rate_model's.

    A central bank decision changes the policy rate, and on 2026-09-21 the
    fact table still held USD at 3.50-3.75% and JPY at 1.00% - both pre-hike,
    days after the decisions. Nothing was watching the rate itself.
    """
    import rate_model as rm
    import fact_tables as ft
    import csv
    L = {'US': 'USD', 'EA': 'EUR', 'GB': 'GBP', 'JP': 'JPY',
         'AU': 'AUD', 'NZ': 'NZD', 'CA': 'CAD', 'CH': 'CHF'}
    want = dict((L[i], r[0]) for i, r in rm.ROWS.items())
    fp = os.path.join(REPO, 'data/macro_indicators/'
                            'Interest_Rate_Macro_Indicators.csv')
    rows = list(csv.reader(io.open(fp, encoding='utf-8')))
    ci = rows[0].index(ft.latest_month())
    bad = [(r[0].strip(), r[ci], want[r[0].strip()])
           for r in rows[1:]
           if r[0].strip() in want and r[ci] != want[r[0].strip()]]
    if bad:
        return False, ', '.join('%s cell=%s model=%s' % b for b in bad)
    return True, 'all 8 rate cells match rate_model'


def s7_selectors():
    """F-127: build_weekly and gen_page must use the SAME selector."""
    src = io.open(os.path.join(HERE, 'build_weekly.py'),
                  encoding='utf-8').read()
    if re.search(r'^PICKED = ps\.select\(', src, re.M):
        return False, ('build_weekly uses ps.select() - the LEG-DISJOINT rule '
                       'LD-126 repealed - while gen_page uses the_set()')
    return True, 'both on ps.the_set() (LD-126)'


def s8_dates():
    """F-130: no renderer may pin a date the window has moved past."""
    start, end = window()
    bad = []
    # Every renderer must agree with gen_page (the window authority above)
    # and none may carry a hardcoded dt.date literal.
    for f in ('gen_page.py', 'gen_audit.py', 'build_weekly.py'):
        src = io.open(os.path.join(HERE, f), encoding='utf-8').read()
        for m in re.finditer(r"'(\d{4}-\d{2}-\d{2})'\s*,\s*'(\d{4}-\d{2}-\d{2})'", src):
            if m.group(1) != start or m.group(2) != end:
                bad.append('%s: %s..%s' % (f, m.group(1), m.group(2)))
        for m in re.finditer(r'dt\.date\(\d{4},\s*\d+,\s*\d+\)', src):
            bad.append('%s: literal %s' % (f, m.group(0)))
    if bad:
        return False, ('window is %s..%s but: %s' % (start, end, '; '.join(bad)))
    return True, 'no pinned dates; window %s..%s' % (start, end)


def _edition_stamp():
    """The Sunday this edition was BUILT, which names its page file.

    The window starts Monday, so the page is stamped the day before it.
    Derived, never written down (F-130, F-136, F-140).
    """
    start, _ = window()
    d = dt.datetime.strptime(start, '%Y-%m-%d').date()
    return (d - dt.timedelta(days=1)).isoformat()


def s9_page_fresh():
    """F-134: is the PUBLISHED page built from the CURRENT fact tables?

    Jeff, 2026-09-21: "have we reflected all changes now to the report?" -
    and the answer was no. USD Retail Sales had been corrected AFTER the last
    publish, so the live page carried 5% while the repo held 6%.

    Nothing could answer that question without re-reading the HTML by hand,
    which I did badly twice before diffing the generated section instead. So
    this compares every HELD value against the repo's published .html. A
    value the page does not contain means the page is behind the data.

    It is a CONTAINMENT test, not a cell-by-cell parse - the table markup has
    grouped rows that a naive parser mis-reads (I produced 64 false "stale"
    rows trying). Containment cannot say WHERE a value is, only that it is
    absent, which is the question being asked.
    """
    import score_model as sm
    # *** F-140 - THIS WAS PINNED TO 2026-09-20_weekly.html, LAST WEEK'S PAGE.
    #
    # The same shape as F-130 and F-136: a date written into a checker
    # instead of derived. It passed on the 28 Sep-2 Oct V1 build only because
    # the 21-25 Sep page happened to contain the same four values, and it
    # FAILED against a correct page the moment those values were refreshed -
    # reporting "the published page is behind" about a page it never read.
    #
    # A guard that names the wrong file does not weaken to a no-op; it
    # accuses correct work. Derive from the window this build is FOR.
    page = os.path.join(REPO, 'reports/2026/Q3/%s_weekly.html'
                        % _edition_stamp())
    if not os.path.exists(page):
        return True, '(no published page yet)'
    live = io.open(page, encoding='utf-8').read()
    miss = []
    for cat, iso, name, act, prev, ref, thr, v in sm.ROWS:
        if name == 'GDP Growth Rate QoQ' or not (act or '').strip():
            continue
        esc = (act.replace('&', '&amp;').replace('<', '&lt;')
                  .replace('$', '$'))
        if act not in live and esc not in live:
            miss.append('%s %s=%s' % (sm.LABEL[iso], name[:22], act))
    if miss:
        return False, ('published page is BEHIND the fact tables - %d value(s) '
                       'absent: %s' % (len(miss), '; '.join(miss[:4])))
    return True, 'every held value appears on the published page'


def s10_high_impact():
    """F-135: every HIGH_IMPACT category must actually be flaggable.

    Jeff, 2026-09-23: "This should be highlighted as well as High Impact
    news" - the SNB decision was rendering as an ordinary row.

    LD-134 names Employment, Inflation, Interest Rate and GDP. The flag
    resolved a row's category through score_model, but LD-140 gives a rate
    decision a SYNTHETIC name that lives in rate_model - so the ONE CATEGORY
    THE RULE NAMES EXPLICITLY was the only one that could never light up.
    Three central bank decisions passed through 14-18 Sep unmarked.

    This asserts a real row from each listed category is flagged, so a
    category that becomes unreachable fails here rather than in print.
    """
    import gen_page as gp
    import score_model as sm
    probes = {}
    for cat, iso, name, a, p_, ref, thr, v in sm.ROWS:
        probes.setdefault(cat, (sm.LABEL[iso], name))
    probes['Interest_Rate'] = ('CHF', gp.wa.RATE_NAME)
    dark = [c for c in gp.HIGH_IMPACT
            if c in probes and not gp.hot(*probes[c])]
    if dark:
        return False, ('high-impact but never flagged: %s' % ', '.join(dark))
    return True, 'all %d high-impact categories flag (LD-134)' % len(gp.HIGH_IMPACT)


def s11_pair_bars():
    """LD-145: every SELECTED pair needs OANDA bars for its ATR and target.

    Jeff asked for ATR and Target beside the Gap. Gap comes from the board
    and always exists; ATR needs PRICE, and price must come from TradingView
    (LD-5 as amended, F-137 - two retrospectives were graded on Yahoo bars
    whose sessions are offset a day from OANDA's).

    A pair with no bars renders "no bars - pull OANDA:<PAIR>". This fails
    the build instead, so the prompt arrives BEFORE publishing rather than
    on the page.
    """
    import glob as _g
    import pair_atr as pa
    import pair_select as ps
    import fact_tables as ft
    caps = sorted(_g.glob(os.path.join(
        REPO, 'data/raw/calendar/*_cal_full.json')))
    if not caps:
        return True, '(no capture - skipped)'
    start, end = window()
    f = ps.final_scores(caps[-1], start, end)
    sc = dict((c, f[c]['total']) for c in f)
    band, _ = ft.bands(sc)
    sel = ps.the_set(ps.candidates(sc, band), band, sc)
    miss = [p['pair'] for p, _w in sel if not pa.atr_for(p['pair'], start)]
    if miss:
        return False, ('no OANDA bars for %s - pull from TradingView '
                       '(chart_set_symbol OANDA:<PAIR>, timeframe D, '
                       'data_get_ohlcv) and save to data/raw/bars/'
                       % ', '.join(miss))
    return True, 'all %d selected pairs have bars' % len(sel)


STEPS = [
    ('1', 'capture is fresh (<=3 days)', s1_capture),
    ('2', 'no release lost to a gap (R-42)', s2_gaps),
    ('3', 'every row vs TE, refreshed (R-45)', s3_indicator_pages),
    ('4', 'held values vs capture (R-37/R-40)', s4_vintage),
    ('5', 'scoring rules (R-44)', s5_rules),
    ('6', 'policy rates match rate_model (LD-142)', s6_rates),
    ('7', 'one selector everywhere (F-127)', s7_selectors),
    ('8', 'no renderer pins a stale date (F-130)', s8_dates),
    ('9', 'published page matches the data (F-134)', s9_page_fresh),
    ('10', 'high-impact rows can flag (F-135)', s10_high_impact),
    ('11', 'selected pairs have OANDA bars (LD-145)', s11_pair_bars),
]

PAGE_STEPS = """
AFTER ASSEMBLING THE PAGE, run these by hand - they need the file:

    python pipelines/shell_check.py <page.html>    R-43: header chip, pair
                                                   count, calibrator day
                                                   columns vs the window

THEN, BEFORE PUBLISHING:
    - the .wrap div is closed (F-129 - the splice drops last week's closer)
    - the header eyebrow, h1 and dek name THIS week (F-122)
    - section count is 6 and every table tag balances
"""


def main():
    start, end = window()
    print('R-46 BUILD CHECK   for the %s .. %s edition' % (start, end))
    print()
    failed = None
    for sid, label, fn in STEPS:
        try:
            ok, detail = fn()
        except Exception as e:
            ok, detail = False, 'raised %s: %s' % (type(e).__name__, e)
        print('  %s  %-40s %s' % ('PASS' if ok else 'FAIL', label, detail))
        if not ok and failed is None:
            failed = (sid, label)
    print()
    if failed:
        print('*** STOP AT STEP %s - %s' % failed)
        print('    Fix it before building. A later step built on bad data')
        print('    produces a page where every number is internally')
        print('    consistent and wrong (F-130, F-127).')
        return 1
    print('  all %d checks pass - safe to build' % len(STEPS))
    print(PAGE_STEPS)
    return 0


if __name__ == '__main__':
    sys.exit(main())
