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


def edition_type(md):
    """The `type:` field from the edition frontmatter (F-19 validates it)."""
    m = re.search(r'^type:\s*(\w+)', md, re.M)
    return m.group(1).strip().upper() if m else 'UNKNOWN'


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
    """Compare an edition's shape to the baseline blessed FOR ITS TYPE.

    Per-type baselines (Jeff, 2026-08-31). 0 grades the expired week on a
    WEEKEND edition and tracks the live set on a MONDAY one - same section
    number, two purposes. A single baseline would force a live price under a
    column headed "Fri close".
    """
    allb = load()
    got = shape(md)
    etype = edition_type(md)
    if allb is None:
        return 'no baseline - run with --bless once Jeff approves the layout'
    base = allb.get(etype)
    if base is None:
        return ('no blessed shape for %s yet - bless this edition to set it'
                % etype)
    problems = []
    for sec in sorted(set(base) | set(got)):
        b, g = base.get(sec, []), got.get(sec, [])
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
            'FATAL (R-27/LD-82): the %s edition SHAPE changed.' % etype
            + chr(10)
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
    return '%d section(s) match the blessed %s shape' % (len(base), etype)


def bless(md, path):
    """Bless this edition's shape FOR ITS TYPE, leaving other types alone."""
    allb = load() or {}
    etype = edition_type(md)
    allb[etype] = shape(md)
    json.dump(allb, io.open(BASELINE, 'w', encoding='utf-8'),
              indent=1, ensure_ascii=False, sort_keys=True)
    print('blessed the %s shape from %s' % (etype, os.path.basename(path)))
    print('  -> %s' % BASELINE)
    print('  Types now blessed: %s' % ', '.join(sorted(allb)))
    print('  Every %s edition must match this shape.' % etype)


if __name__ == '__main__':
    src = sys.argv[1]
    md = io.open(src, encoding='utf-8').read()
    if '--bless' in sys.argv:
        bless(md, src)
    else:
        print(check(md))
