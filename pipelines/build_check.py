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


def s4b_prev():
    """R-48 - no row scores off a wrong `previous`.

    Jeff, 2026-10-12: "Every week we are facing the same issue again and
    again". He is right, and the reason is that NOTHING OWNED prev.
    refresh_rows advances the actual, roll_month rolls the CSV columns,
    sync_score_model copies the actual and the ref month - and prev keeps
    whatever it held when the row was last hand-edited, one vintage behind.
    A recurring defect with no guard recurs by design.
    """
    import prev_check as pv
    bad, unv = pv.audit()
    scoring = [b for b in bad if b[4] != b[5]]
    if scoring:
        return False, '%d row(s) scoring off a wrong previous: %s' % (
            len(scoring), ', '.join('%s %s' % (b[0], b[1][:18])
                                    for b in scoring[:3]))
    if bad:
        return True, ('%d cosmetic prev mismatch(es), 0 scoring, %d unverified'
                      % (len(bad), len(unv)))
    return True, 'every matchable prev agrees with TE, %d unverified' % len(unv)


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


def s8b_rates_vs_te():
    """R-47/F-142: does rate_model match the WORLD, not just the page?

    Step 6 checks the page against rate_model. Nothing checked rate_model
    against TE, so the RBA's 29 Sep hike sat unrecorded for five days through
    a published edition and a published retrospective.
    """
    import rate_check as rc
    rows = rc.compare()
    stale = [r for r in rows if r[3] == 'STALE']
    unv = [r for r in rows if r[3] == 'UNVERIFIED']
    if stale:
        return False, ('%d rate(s) STALE vs TE: %s'
                       % (len(stale), ', '.join(
                           '%s %s->%s' % (rc.LABEL[i], h, t)
                           for i, h, t, _ in stale)))
    if unv:
        return False, ('%d rate(s) UNVERIFIED: %s'
                       % (len(unv), ', '.join(rc.LABEL[i]
                                              for i, _, _, _ in unv)))
    return True, 'all 8 policy rates match TE'


def s8c_dark_rows():
    """F-143: the rows no automated check reaches must still be READ.

    R-45 fetches with curl, and several TE pages render their release table
    client-side - so curl gets a shell with the right title and no data, and
    the row reports NO PAGE. Worse, the old report counted a match against ANY
    captured print as verified, including one five weeks old: AUD's PMI was
    listed as checked on its AUGUST value while September's 49.6 went unseen.

    dark_rows.READS is the hand-read ledger. This asserts two things: the
    ledger agrees with the fact table, and no read is older than its cadence.
    """
    import dark_rows as dr
    import fact_tables as ft
    m = ft.latest_month()
    held = {}
    for cat in ('Production', 'Spending', 'Trade', 'Employment', 'Inflation'):
        for r in ft.load(cat):
            held[((r.get('Currency') or '').strip(),
                  (r.get('Indicator') or '').strip())] = (r.get(m) or '').strip()
    bad = [(c, n) for (c, n), (v, _r, _d, _s) in dr.READS.items()
           if held.get((c, n)) is not None and held[(c, n)] != v]
    if bad:
        return False, ('%d ledger/table mismatch: %s'
                       % (len(bad), ', '.join('%s %s' % x for x in bad)))
    st = [x for x in dr.stale() if x[3] is not None]
    if st:
        return False, ('%d dark row(s) past their cadence: %s'
                       % (len(st), ', '.join('%s %s (%dd)' % (c, n[:22], a)
                                             for c, n, _d, a in st)))
    never = [x for x in dr.stale() if x[3] is None]
    return True, ('%d dark rows current, %d UNVERIFIABLE (bad slug): %s'
                  % (len(dr.READS) - len(never), len(never),
                     ', '.join('%s %s' % (c, n[:20]) for c, n, _d, _a in never)))


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
    # F-140b - THE QUARTER WAS HARDCODED TOO. F-140 derived the DATE and left
    # 'Q3' literal, so the first Q4 edition reported "no published page yet"
    # about a page that exists. A half-derived path is still a pinned path.
    _st = _edition_stamp()
    _q = (int(_st[5:7]) - 1) // 3 + 1
    page = os.path.join(REPO, 'reports/%s/Q%d/%s_weekly.html'
                        % (_st[:4], _q, _st))
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


def s9b_board_self_consistent():
    """R-49 (F-161): the page's BOARD must equal what the page's OWN ROWS give.

    *** THE DEFECT THIS CATCHES, OBSERVED ON A PUBLISHED PAGE. On 2026-10-23
    the 19-23 Oct edition showed, in the same document:
        section 4  NAB Business Confidence ... -1    (correct)
        section 1  AUD ... -0.67                     (the PRE-sync total)
    AUD's true total from those rows is -1.67. The board had been rendered
    BEFORE the final sync_score_model pass corrected that row's verdict, so the
    page contradicted ITSELF - every number internally consistent with the pass
    that produced it, and wrong against the page's own evidence table.
    GBPAUD's gap was understated by a full point as a result (+8.17 vs +9.17),
    which changed the ORDER of the set though not its membership.

    *** WHY THE EXISTING GUARDS ALL PASSED. F-134 compares the page against the
    FACT TABLES, and the fact tables were right. R-44 checks the RULES, and the
    rules were right. R-48 checks `prev`, which was right. NOTHING compared the
    board to the rows PRINTED BESIDE IT, so a renderer that ran mid-refresh
    produced a self-contradicting document that every check waved through.
    This is the F-127/F-134 family: one artefact regenerated, another left on an
    older pass.

    THE CHECK IS DELIBERATELY NOT "re-derive and compare to the page" - that is
    F-134's job. It asks the narrower question F-134 cannot: do the board and
    the evidence table in the SAME FILE agree? If they do not, one of them was
    written by a stale pass and the page must be rebuilt before publishing.
    """
    import re as _re
    page = os.path.join(REPO, 'reports', '2026', 'Q4')
    import glob as _g
    cands = sorted(_g.glob(os.path.join(page, '*_weekly.html')))
    if not cands:
        return True, 'no published page yet - nothing to compare'
    html = io.open(cands[-1], encoding='utf-8').read()
    name = os.path.basename(cands[-1])

    # the board: rows under the §1 HEADING carrying a band and a FINAL.
    #
    # *** ANCHOR ON THE HEADING, NOT ON THE PHRASE. The first cut searched for
    # the bare string "The board" and matched the first PROSE use of those two
    # words - which my own F-161 note then introduced three screens earlier, so
    # the parser read a note instead of a table and reported "0 of 8". The
    # F-141 lesson (anchor on the section, never on a row shape) applies to
    # headings too.
    # ANCHOR ON THE <h2> WHOSE TEXT IS THE BOARD, not on a section NUMBER.
    # Two wrong guesses are recorded because both are easy to repeat: first
    # "The board" as a bare phrase (matched my own prose note), then "§1"
    # (the board is §2 in this edition - the numbering is not stable across
    # editions, so it is not an anchor at all).
    board = {}
    k = -1
    for _m in _re.finditer(r'<h2[^>]*>(.*?)</h2>', html, _re.S):
        if 'board' in _re.sub('<[^>]+>', '', _m.group(1)).lower():
            k = _m.end()
            break
    if k < 0:
        return False, ('%s: no <h2> naming the board - it cannot be checked, '
                       'and that is a FAILURE, not a pass' % name)
    for m in _re.finditer(r'<tr[^>]*>(.*?)</tr>', html[k:k + 4000], _re.S):
        cells = [_re.sub('<[^>]+>', '', c).strip()
                 for c in _re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>',
                                      m.group(1), _re.S)]
        if len(cells) < 6:
            continue
        ccy = cells[1]
        if ccy not in ('USD', 'EUR', 'GBP', 'JPY', 'AUD', 'NZD', 'CAD', 'CHF'):
            continue
        try:
            board[ccy] = float(cells[5].replace('\u2212', '-')
                               .replace('+', '').strip())
        except ValueError:
            continue
    if len(board) != 8:
        # *** NEVER A SILENT PASS. A board this check cannot read is the exact
        # shape of every false green this project has found (F-150, F-152,
        # F-158): silence that looks like success. If the page cannot be
        # parsed, say so and fail.
        return False, ('%s: board not parseable (%d of 8 currencies found) - '
                       'an unreadable board is a FAILURE, not a skip' % (name, len(board)))

    # what the live fact tables say the FINAL should be, on the page's own window
    import pair_select as _ps
    import glob as _g2
    start, end = window()
    # *** RE-DERIVE ON THE PAGE'S OWN CAPTURE, NOT THE NEWEST ONE. My first cut
    # used caps[-1] and reported NZD +1.40 on the page against +1.20 "live" -
    # but the page was RIGHT: it was built on the Sunday capture whose
    # calibrator read +0.40, and by Thursday a later capture read +0.20. The
    # calibrator is a FORWARD-LOOKING term and it legitimately moves every day;
    # comparing a published page to a capture it never saw makes a correct page
    # look broken. The page names its capture in the footer, so read it there.
    _cap = None
    _fm = _re.search(r'(2026-\d{2}-\d{2}_\d{4}PHT)', html)
    if _fm:
        _hit = sorted(_g2.glob(os.path.join(
            REPO, 'data/raw/calendar/%s_cal_full.json' % _fm.group(1))))
        if _hit:
            _cap = _hit[0]
    if _cap is None:
        return False, ('%s does not name the capture it was built on - the '
                       'board cannot be re-derived against the right data' % name)
    live = _ps.final_scores(_cap, start, end)
    bad = []
    for c, v in sorted(board.items()):
        want = live[c]['total']
        if abs(want - v) > 0.005:
            bad.append('%s page %+.2f vs rows %+.2f' % (c, v, want))
    if bad:
        return False, ('%s board disagrees with its own rows: %s'
                       % (name, '; '.join(bad)))
    return True, '%s board matches its own evidence rows' % name


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


def s11b_pair_grid():
    """R-50 (LD-168): LD-162 needs all 28 crosses, or it cannot return NARROW.

    *** WHY THIS IS A GUARD AND NOT A ONE-OFF PULL. The 17 Oct retro measured
    that LD-162 returned BROAD or mostly-broad in 40 OF 40 currency-sessions
    and NARROW never once fired - not because markets were broad, but because
    breadth is measured only against counterparts we hold bars for, and CHF and
    NZD had exactly ONE. "BROAD, stronger against all 1" is arithmetically true
    and says nothing.
    With the full grid the SAME WEEK re-reads as 20 NARROW, 10 mostly, 10 BROAD
    - the metric went from unable-to-fail to informative. That is worth a guard,
    because the failure mode is SILENT: a missing file does not error, it just
    quietly shrinks n and makes every reading look broad.

    TWO THINGS ARE CHECKED, and the second is the one that bit:
      1. all 28 conventional crosses have a bar file at all;
      2. every file carries the SAME latest session. Five files sat at 16 Oct
         while the rest were current - left over from the previous week's set
         and never re-pulled when the set rotated - so legs() silently dropped
         three counterparts per currency and JPY still read n=4 on a grid that
         was nominally complete.
    """
    import itertools as _it
    import glob as _g
    ORDER = ['EUR', 'GBP', 'AUD', 'NZD', 'USD', 'CAD', 'CHF', 'JPY']
    _rank = dict((c, i) for i, c in enumerate(ORDER))
    want = set()
    for a, b in _it.combinations(ORDER, 2):
        want.add(a + b if _rank[a] < _rank[b] else b + a)

    import daily_report as _dr
    have = set(os.path.basename(f)[:-4]
               for f in _g.glob(os.path.join(_dr.TXT, '??????.txt')))
    missing = sorted(want - have)
    if missing:
        return False, ('%d of 28 crosses have no bar file: %s - LD-162 cannot '
                       'return NARROW without them (R-50)'
                       % (len(missing), ' '.join(missing[:6])))

    # 2. every file must reach the same latest session
    last = {}
    for p in sorted(want):
        b = _dr.bars(p)
        if not b:
            return False, '%s has a file but no readable bars (R-50)' % p
        last[p] = b[-1][0]
    newest = max(last.values())
    behind = sorted(p for p, d in last.items() if d != newest)
    if behind:
        return False, ('%d cross(es) are behind the others (newest %s): %s - a '
                       'stale file does not error, it SILENTLY shrinks breadth '
                       '(R-50)' % (len(behind), newest, ' '.join(behind[:6])))
    return True, 'all 28 crosses present and current to %s' % newest


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
    ('4b', 'prev vs TE, no wrong scoring (R-48)', s4b_prev),
    ('5', 'scoring rules (R-44)', s5_rules),
    ('6', 'policy rates match rate_model (LD-142)', s6_rates),
    ('7', 'one selector everywhere (F-127)', s7_selectors),
    ('8', 'no renderer pins a stale date (F-130)', s8_dates),
    ('8b', 'policy rates match TE (R-47/F-142)', s8b_rates_vs_te),
    ('8c', 'dark rows read and current (F-143)', s8c_dark_rows),
    ('9', 'published page matches the data (F-134)', s9_page_fresh),
    ('9b', 'board matches its own rows (R-49/F-161)', s9b_board_self_consistent),
    ('10', 'high-impact rows can flag (F-135)', s10_high_impact),
    ('11', 'selected pairs have OANDA bars (LD-145)', s11_pair_bars),
    ('11b', 'all 28 crosses for LD-162 (R-50)', s11b_pair_grid),
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
