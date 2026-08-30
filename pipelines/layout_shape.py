# -*- coding: utf-8 -*-
"""R-27 - lock the SHAPE of every section (LD-82).

Jeff, 2026-08-30: "again don't change the report format wihtout my approval.
if there's a need to change then let me know."

R-24 locks four table headers by name. This locks the WHOLE EDITION's shape:
for every section, how many tables it carries and what each one's columns are.
A table that APPEARS is caught the same as a column that changes.

    python pipelines/layout_shape.py <edition.md>           # check
    python pipelines/layout_shape.py <edition.md> --bless   # re-baseline

--bless is deliberate and separate so a baseline can never be silently
rewritten by a render. Blessing is Jeff's call, not a build step.
"""
import io, os, re, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
BASELINE = os.path.join(os.path.dirname(HERE), 'docs', 'LAYOUT_LOCK.json')

# Sections whose table count legitimately varies with the data.
# 2.1-2.5 hold the 71 whitelist rows; 4.0 varies with the week's events.
# Their COLUMNS are still locked - by R-24 and by the header check here.
VARIABLE_ROWS = ()


def shape(md):
    """{section: [header, ...]} - one entry per table, in document order."""
    out, cur = {}, 'PRE'
    in_table = False
    for line in md.split(chr(10)):
        m = re.match(r'^#{2,4}\s*\u00a7?\s*([\d.]+[a-z]?|\u00a7\d+)', line)
        if line.startswith('#') and m:
            cur = m.group(1).rstrip('.')
            in_table = False
            continue
        if line.startswith('#'):
            in_table = False
            continue
        t = line.strip()
        if not t.startswith('|'):
            in_table = False
            continue
        if re.match(r'^[|\s:-]+$', t):
            continue
        if in_table:
            continue
        in_table = True
        hdr = [c.strip().replace('*', '') for c in t.strip('|').split('|')]
        out.setdefault(cur, []).append(' | '.join(hdr))
    return out


def load():
    if not os.path.exists(BASELINE):
        return None
    return json.load(io.open(BASELINE, encoding='utf-8'))


def check(md):
    """Compare an edition's shape to the blessed baseline. Returns a summary."""
    base = load()
    got = shape(md)
    if base is None:
        return 'no baseline - run with --bless once Jeff approves the layout'
    problems = []
    for sec in sorted(set(base) | set(got)):
        b, g = base.get(sec, []), got.get(sec, [])
        if sec in VARIABLE_ROWS:
            b, g = b[:1], g[:1]
        if len(g) > len(b):
            for h in g[len(b):]:
                problems.append('\u00a7%s GAINED a table: %s' % (sec, h))
        elif len(g) < len(b):
            problems.append('\u00a7%s LOST %d table(s)' % (sec, len(b) - len(g)))
        for k, (bh, gh) in enumerate(zip(b, g)):
            if bh != gh:
                problems.append('\u00a7%s table %d header changed:'
                                '%s    was: %s%s    now: %s'
                                % (sec, k + 1, chr(10), bh, chr(10), gh))
    if problems:
        raise SystemExit(
            'FATAL (R-27/LD-82): the report SHAPE changed.' + chr(10)
            + chr(10).join('  ' + p for p in problems) + chr(10)
            + 'Jeff, 2026-08-30: "don\'t change the report format wihtout my'
            + ' approval. if there\'s a need to change then let me know."'
            + chr(10)
            + 'CONTENT changes freely - rows, values, highlighting, prose.'
            + chr(10)
            + 'STRUCTURE does not. A new table is a format change even when'
            + chr(10)
            + 'the content in it was asked for. Ask, then re-bless:'
            + chr(10)
            + '    python pipelines/layout_shape.py <edition.md> --bless')
    return '%d section(s) match the blessed shape' % len(base)


def bless(md, path):
    json.dump(shape(md), io.open(BASELINE, 'w', encoding='utf-8'),
              indent=1, ensure_ascii=False, sort_keys=True)
    print('blessed the shape of %s' % os.path.basename(path))
    print('  -> %s' % BASELINE)
    print('  This is now the shape every edition must match.')


if __name__ == '__main__':
    src = sys.argv[1]
    md = io.open(src, encoding='utf-8').read()
    if '--bless' in sys.argv:
        bless(md, src)
    else:
        print(check(md))
