# -*- coding: utf-8 -*-
"""
Regression suite: every fixture reproduces a REAL error from a real edition.

WHY THIS EXISTS - Jeff, 2026-08-23: "If we closed this session would the next
session going to create the exact report without the errors we addressed this
session?"

The honest answer needed evidence, not confidence. This is the evidence.

Each fixture takes the current sealed-quality edition and reintroduces one
error that actually shipped, then asserts the renderer REFUSES to publish it.
A guard that has never been seen to fail is not a verified guard (F-13).

RUN:  python pipelines/test_guards.py
It exits non-zero if any regression renders successfully.

WHAT THIS DOES NOT COVER, stated plainly so nobody mistakes a green run for
safety: these guards check the SHAPE of an edition - sections present, blocks
generated, rows counted, sources cited, levels drawn, whitelist reconciled.
They cannot check JUDGEMENT. A fabricated level that names a real bar (F-33),
a projection built from the wrong window, a falsifier inside 1 ATR - those are
caught by reading, not by running this.
"""
import io, os, re, sys, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
EDITION = os.path.join(REPO, 'reports', '2026', 'Q3',
                       '2026-08-23_market-sentiment.md')
RENDER = os.path.join(HERE, 'render_edition.py')


def _sec2(md):
    return md[md.index('### 2.1'):md.index('### 2.6')]


def fixtures(md):
    """(name, what real error this reproduces, mutated markdown)."""
    out = []

    # F-23: the F&G block hand-written as markdown instead of the LD-25 chart.
    out.append(('fng_downgrade', 'F-23 F&G hand-written, not generated',
                md.replace('<!--FNG-->',
                           '| | Score |\n|---|---|\n| Index | 55.2 |')))

    # F-24: section 2 summarised instead of publishing all 70 rows.
    sec = _sec2(md)
    rows = [l for l in sec.splitlines()
            if l.startswith('| ') and not l.startswith('|---')
            and 'CCY | Indicator' not in l]
    keep = set(rows[::2])
    out.append(('s2_summarised', 'F-24 section 2 summarised, rows dropped',
                md.replace(sec, '\n'.join(
                    l for l in sec.splitlines()
                    if not l.startswith('| ') or l.startswith('|---')
                    or 'CCY | Indicator' in l or l in keep))))

    # F-24b: full row count but blanked cells.
    out.append(('s2_blank_cells', 'F-24 blank cells instead of NOT FOUND',
                md.replace(rows[0], re.sub(r'\| [^|]+ \|', '| — |',
                                           rows[0], count=4))))

    # F-25: the week-ahead projection table omitted.
    out.append(('no_section_40', 'F-25 section 4.0 omitted',
                md.replace('### 4.0 — Week ahead', '### Week ahead notes')))

    # F-31: levels published in tables but never drawn on the chart.
    i, j = md.index('## §5 '), md.index('## §7 ')
    out.append(('levels_not_drawn', 'F-31 levels published but not drawn',
                md[:i] + re.sub(r'`[A-Za-z0-9]{6}`', '(none)', md[i:j]) + md[j:]))

    # F-17: section 1 citing no news source.
    m = re.search(r'^##\s*§1\b.*?$(.*?)(?=^##\s*§)', md, re.S | re.M)
    s1 = m.group(1)
    for h in ('investinglive.com', 'investing.com', 'treasury.gov', 'cnbc.com'):
        s1 = s1.replace(h, 'REDACTED')
    out.append(('no_news_sources', 'F-17 section 1 cites no source',
                md[:m.start(1)] + s1 + md[m.end(1):]))

    # F-28: an off-list indicator carrying a SCORED projection.
    out.append(('offlist_scored', 'F-28 off-list indicator scored in 4.0',
                md.replace(
                    '| **Wed 26 09:30** | **AUD** | **Inflation Rate YoY**',
                    '| **Fri 28 20:30** | **CAD** | **GDP Growth Annualized** '
                    '| **3.4%** | **-0.1%** | **BAD** | contraction |\n'
                    '| **Wed 26 09:30** | **AUD** | **Inflation Rate YoY**', 1)))
    return out


def main():
    md = io.open(EDITION, encoding='utf-8').read()
    tmp = tempfile.mkdtemp(prefix='guardtest_')
    failed = []
    print('REGRESSION SUITE - each fixture is a real error that shipped')
    print('=' * 70)
    for name, why, content in fixtures(md):
        path = os.path.join(tmp, name + '.md')
        io.open(path, 'w', encoding='utf-8').write(content)
        r = subprocess.run([sys.executable, RENDER, path],
                           capture_output=True, text=True)
        blocked = 'FATAL' in (r.stdout + r.stderr)
        tag = re.search(r'FATAL \(([^)]*)\)', r.stdout + r.stderr)
        print('%-22s %-42s %s' % (
            name, why,
            'BLOCKED by ' + tag.group(1) if blocked else '*** NOT CAUGHT ***'))
        if not blocked:
            failed.append(name)
    print('=' * 70)
    if failed:
        print('%d REGRESSION(S) NOT CAUGHT: %s' % (len(failed), ', '.join(failed)))
        return 1
    print('All %d regressions blocked.' % len(fixtures(md)))
    print()
    print('NOTE: these check an edition\'s SHAPE, never its JUDGEMENT.')
    print('A fabricated level naming a real bar, a falsifier inside 1 ATR, a')
    print('projection from the wrong window - those need reading, not running.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
