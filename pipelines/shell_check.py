# -*- coding: utf-8 -*-
"""R-43 - DOES THE HAND-WRITTEN SHELL STILL AGREE WITH THE GENERATED BODY?

F-122, 2026-09-13. The 14-18 Sep edition was rebuilt after F-121 recovered
three GBP releases. The body regenerated correctly - the set, the board and
every table showed GBPAUD on top. THE HEADER CHIP STILL READ "EURAUD LONG
+5.00", the previous top pair.

    THE SHELL DOES NOT PARTICIPATE IN THE REBUILD.

gen_page.py writes the BODY. The page shell - <header>, the chips, the dek -
is hand-written once and preserved verbatim by every subsequent splice. So a
rebuild silently leaves the shell describing the PREVIOUS edition, and the
page contradicts itself: header says one pair, section 1 says another.

This is F-110's shape exactly (the splice dropped a hand-written section, and
the page published twice before anyone noticed) and F-104/F-111's class: an
OUTPUT defect that survives because every number it is computed from is right.
The repo's other guards all check data. None of them read the rendered page.

WHAT THIS CHECKS. The few facts the shell restates about the edition, against
the live pipelines:

    top pair + gap     the chip must name the set's rank-1 pair
    pair count         "N pairs" must equal len(the_set)
    seal              the chip must match the edition's manifest

It deliberately does NOT check prose. The dek argues a point ("no RISK ON pair
qualifies") and arguments are Jeff's to make. Only restated FACTS are checked -
those are the ones that go stale silently.

    python pipelines/shell_check.py <page.html>
"""
import io
import os
import re
import sys
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import fact_tables as ft
import pair_select as ps

# *** THE GUARD MUST FOLLOW THE EDITION, NOT A PINNED DATE. On 2026-09-20
# this compared the new 21-25 Sep page against the 13 Sep capture and the
# 14-18 window, then reported the PAGE as wrong. A guard that hard-codes the
# edition it was written for starts lying the moment the next one is built -
# and it lies in the most damaging direction, by blaming correct output.
#
# The newest capture and the window it covers are both derivable; nothing
# here needs a literal date.
_caps = sorted(glob.glob(os.path.join(
    REPO, 'data/raw/calendar/*_cal_full.json')))
CAP = _caps


def _window():
    """The Mon-Fri window the newest capture is the Sunday build for."""
    import datetime as _dt
    import re as _re
    m = _re.search(r'(\d{4})-(\d{2})-(\d{2})_', os.path.basename(_caps[-1]))
    d = _dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    mon = d + _dt.timedelta(days=(7 - d.weekday()) % 7 or 7)
    if d.weekday() == 6:                 # Sunday build -> tomorrow
        mon = d + _dt.timedelta(days=1)
    return mon.isoformat(), (mon + _dt.timedelta(days=4)).isoformat()


START, END = _window()


def expected():
    """(top_pair, top_gap, n_pairs) from the live pipelines."""
    f = ps.final_scores(CAP[-1] if CAP else None, START, END)
    sc = dict((c, f[c]['total']) for c in f)
    band, _ = ft.bands(sc)
    cands = ps.candidates(sc, band)
    sel = ps.the_set(cands, band, sc)
    top = sel[0][0]
    return top['pair'], top['gap'], len(sel)


def check(path):
    html = io.open(path, encoding='utf-8').read()
    head = html[:html.find('<section>')] if '<section>' in html else html
    pair, gap, n = expected()
    bad = []

    # The chip that names the top pair.
    chips = re.findall(r'<span class="chip[^"]*">([^<]+)</span>', head)
    named = [c for c in chips if re.search(r'[A-Z]{6}\s+(LONG|SHORT)', c)]
    if not named:
        bad.append(('top pair chip', 'absent', '%s +%.2f' % (pair, gap)))
    else:
        want = '%s' % pair
        if want not in named[0]:
            bad.append(('top pair chip', named[0], '%s +%.2f' % (pair, gap)))
        else:
            m = re.search(r'([+-]?\d+\.\d+)', named[0])
            if m and abs(float(m.group(1)) - gap) > 0.005:
                bad.append(('top pair gap', named[0], '+%.2f' % gap))

    # "N pairs"
    m = re.search(r'(\d+)\s+pairs', head)
    if m and int(m.group(1)) != n:
        bad.append(('pair count', m.group(0), '%d pairs' % n))

    # F-130 - THE CALIBRATOR GRID'S DAY COLUMNS MUST BE THIS WEEK'S.
    # gen_page pinned DAYS to a literal [14..18] while START/END had moved to
    # 21-25, so every cell missed its lookup and printed a dash - under
    # correct non-zero week totals. Jeff caught it by reading the page.
    # The header row is cheap to check and the failure is silent otherwise.
    import datetime as _dt
    want = [(_dt.date(*(int(x) for x in START.split('-')))
             + _dt.timedelta(days=i)).strftime('%a %d').replace(' 0', ' ')
            for i in range(5)]
    grid = re.search(r'The day is the unit.{0,3000}', html, re.S)
    if grid:
        got = re.findall(r'<th[^>]*>([A-Z][a-z]{2} \d{1,2})</th>', grid.group(0))
        if got and got[:5] != want:
            bad.append(('calibrator days', ' '.join(got[:5]), ' '.join(want)))

    # *** F-171 - THE <title> WAS STALE FOR FOUR EDITIONS AND NOTHING READ
    # <head>. Every page from 28 Sep on shipped titled "Week of 28 Sep to 2
    # Oct", including the one published an hour ago, because the shell is
    # reused verbatim and <title> lives in it. R-43 checked the header chip,
    # F-122 the eyebrow/h1/dek, R-49 the board - none looked at <head>.
    # AND IT IS NOT COSMETIC: the Artifact platform names the published page
    # from this tag, so the artifact carried a four-week-old window.
    _t = re.search(r'<title>(.*?)</title>', html, re.S)
    if not _t:
        bad.append((chr(60) + 'title' + chr(62), '(absent)', 'the window'))
    else:
        _sd = _dt.date(*(int(x) for x in START.split('-')))
        _ed = _sd + _dt.timedelta(days=4)
        _txt = _t.group(1)
        # *** THE FIRST VERSION OF THIS CHECK DID NOT FIRE, and the reason
        # matters: it asked whether the month name appeared ANYWHERE in the
        # title, and the stale title "Week of 28 Sep to 2 Oct" contains
        # "Oct". A substring test on a date range is not a date test.
        # Require the START DAY NUMBER beside its own month, which is what
        # actually distinguishes one edition from another.
        _d1 = str(_sd.day)
        _m1 = _sd.strftime('%b')
        _ok = (_d1 in _txt and _m1 in _txt) or (
            str(_ed.day) in _txt and _ed.strftime('%b') in _txt)
        if not _ok:
            bad.append((chr(60) + 'title' + chr(62), _txt.strip(),
                        'a title naming %s %s' % (_d1, _m1)))

    return bad, (pair, gap, n)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: shell_check.py <page.html>')
        sys.exit(2)
    bad, (pair, gap, n) = check(sys.argv[1])
    print('R-43 SHELL CHECK   %s' % os.path.basename(sys.argv[1]))
    print('  pipelines say: %s +%.2f, %d pairs' % (pair, gap, n))
    print()
    if bad:
        print('*** THE SHELL CONTRADICTS THE BODY')
        for what, got, want in bad:
            print('  %-16s shell says %-24s should be %s' % (what, got, want))
        print()
        print('  The shell is hand-written and does NOT regenerate. Fix it in')
        print('  the page, not in gen_page.py.')
        sys.exit(1)
    print('  the shell agrees with the generated body')
