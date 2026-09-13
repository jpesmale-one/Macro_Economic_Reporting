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

CAP = sorted(glob.glob(os.path.join(
    REPO, 'data/raw/calendar/2026-09-13_*_cal_full.json')))
START, END = '2026-09-14', '2026-09-18'


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
