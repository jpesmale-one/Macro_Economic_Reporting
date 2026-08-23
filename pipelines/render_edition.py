# -*- coding: utf-8 -*-
"""
Render the edition .md -> .html with collapsible sections.

LD-10: the .md is the sealed source of truth; the .html is re-rendered from it.
LD-24: reference-weight blocks collapse; the read stays open.

Collapse is opt-in per heading via COLLAPSE below. A collapsed block is a
<details> element - it is IN THE DOM and searchable/printable, not removed.
"""
import io, os, re, sys, html as H

REPO = r'c:/Users/jpesm/OneDrive/Documents/GitHub/Macro_Economic_Reporting'
DATE = '2026-08-21'
SRC = os.path.join(REPO, 'reports/2026/Q3/%s_market-sentiment.md' % DATE)
DST = os.path.join(REPO, 'reports/2026/Q3/%s_market-sentiment.html' % DATE)
STYLE_FROM = os.path.join(REPO, 'reports/2026/Q3/2026-08-19_market-sentiment.html')

# h3 headings whose bodies collapse (reference detail, not the read)
COLLAPSE = (
    '2.1 Production', '2.2 Spending', '2.3 Trade', '2.4 Employment',
    '2.5 Inflation', '2.6 Interest Rate', '4.2 All candidate pairings',
)

# h2 sections whose bodies collapse. Section 9 is deliberately NOT here: it is
# the publish gate, and its open-items list is what a seal is judged against.
COLLAPSE_H2 = (
    '§7 — Method notes', '§8 — Findings',
)

EXTRA_CSS = """
<style>
  details.fold{background:var(--surface);border:1px solid var(--border);
    border-radius:4px;margin:14px 0;overflow:hidden}
  details.fold>summary{cursor:pointer;list-style:none;padding:10px 15px;
    background:var(--surface2);font-family:var(--mono);font-size:.68rem;
    letter-spacing:.11em;text-transform:uppercase;font-weight:700;
    color:var(--strong);display:flex;align-items:center;gap:10px;
    user-select:none;transition:background .12s}
  details.fold>summary:hover{background:var(--border)}
  details.fold>summary::-webkit-details-marker{display:none}
  details.fold>summary::before{content:'▸';color:var(--info);font-size:.85rem;
    transition:transform .15s;display:inline-block}
  details.fold[open]>summary::before{transform:rotate(90deg)}
  details.fold>summary .cnt{margin-left:auto;font-size:.6rem;letter-spacing:.08em;
    color:var(--muted);font-weight:600;text-transform:none}
  details.fold>summary:focus-visible{outline:2px solid var(--info);outline-offset:-2px}
  .foldbody{padding:4px 15px 14px}
  .foldbody .tblwrap{border:none;border-radius:0}
  @media print{details.fold[open],details.fold{display:block}
    details.fold>summary::before{display:none}
    details.fold:not([open])>.foldbody{display:block}}
  @media (prefers-reduced-motion:reduce){
    details.fold>summary::before{transition:none}}

  /* LD-28 TYPOGRAPHY - headers outrank body.
     Before this block h2.sec/h3.sub inherited .68-.7rem uppercase mono
     while body prose ran ~1rem: body text 40% LARGER than the header
     above it, inverted at every level. Explicit scale, largest first. */
  h2.sec{font-size:1.6rem;font-weight:800;line-height:1.25;
    letter-spacing:-.01em;text-transform:none;font-family:inherit;
    margin:34px 0 12px;padding-bottom:7px;
    border-bottom:2px solid var(--border);color:var(--strong)}
  h3.sub{font-size:1.15rem;font-weight:700;line-height:1.3;
    text-transform:none;font-family:inherit;letter-spacing:0;
    margin:22px 0 8px;color:var(--strong)}
  h4{font-size:1rem;font-weight:700;margin:16px 0 6px;color:var(--strong)}
  /* body sits BELOW the headers, and analysis notes sit below body */
  p,li,td,th{font-size:.92rem;line-height:1.6}
  blockquote{font-size:.85rem;line-height:1.55;opacity:.9;
    border-left:3px solid var(--border);margin:12px 0;padding:2px 0 2px 14px}
  blockquote p{font-size:inherit}
  .note,em.note{font-size:.82rem;opacity:.85}

  del{opacity:.62;text-decoration-color:var(--bear)}
  .exec{background:var(--surface);border:1px solid var(--info);
    border-left:4px solid var(--info);border-radius:4px;margin:20px 0;overflow:hidden}
  .exec-hd{background:var(--info-bg);padding:11px 18px;font-family:var(--mono);
    font-size:.7rem;font-weight:700;letter-spacing:.11em;text-transform:uppercase;
    color:var(--info)}
  .exec-b{padding:14px 18px}
  .exec-b p{margin-bottom:9px;max-width:78ch;font-size:.88rem}
  .exec-b p:last-child{margin-bottom:0}
</style>
"""


def esc(t):
    t = H.escape(t, quote=False)
    # strikethrough FIRST: retained-original text (FAIL protocol) often contains
    # bold and quotes, and ~~ must not be eaten by the emphasis passes.
    t = re.sub(r'~~(.+?)~~', r'<del>\1</del>', t, flags=re.S)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    return t


def inline(t):
    """Protect code spans behind a sentinel, run emphasis over the WHOLE
    string, then restore. Splitting first breaks *emphasis spanning a code
    span* - the opening and closing markers land in different fragments."""
    codes = []

    def stash(m):
        codes.append(H.escape(m.group(1)))
        return '␟%d␟' % (len(codes) - 1)

    t = re.sub(r'`([^`]+)`', stash, t)
    t = esc(t)
    return re.sub(r'␟(\d+)␟',
                  lambda m: '<code>%s</code>' % codes[int(m.group(1))], t)


def cell(c):
    v = re.sub(r'[*`]', '', c).strip()
    for w, k in (('GOOD', 'p-good'), ('BAD', 'p-bad'), ('NEUTRAL', 'p-neut'),
                 ('SPLIT', 'p-warn'), ('UNSCORED', 'p-info'), ('MISSING', 'p-warn'),
                 ('HIGH', 'p-good'), ('MEDIUM', 'p-warn'), ('LOW', 'p-info')):
        if v == w:
            return ' class="num"', '<span class="pill %s">%s</span>' % (k, w)
    if re.match(r'^[−+\-]?[\d.,]+[%KMB]?$', v) or re.match(r'^[A-Z]{3}$', v):
        return ' class="num"', inline(c)
    return '', inline(c)


FNG_MARKER = '<!--FNG-->'

# Front-matter of the edition being rendered; set in __main__ before render().
FM = {}


def fng_html(fm=None):
    """Build the Fear & Greed bar chart from the persisted capture (LD-25).

    F-19/F-23: the cross-check and spread-history commentary is EDITION
    CONTENT and comes from front-matter (fng_note / fng_spread), not from
    this file. It was hardcoded to r13's narrative ("Safe Haven Demand fell
    68.0 -> 62.80", "today" meaning 21 Aug), so any later edition would have
    silently published 21 Aug's commentary under its own date.

    Returns '' if no capture exists, so the renderer degrades to whatever
    the markdown says rather than failing.
    """
    import glob, json
    caps = sorted(glob.glob(os.path.join(REPO, 'data/raw/fng/*.json')))
    if not caps:
        return ''
    sys.path.insert(0, os.path.join(REPO, 'pipelines'))
    from fng_block import build
    d = json.load(io.open(caps[-1], encoding='utf-8'))
    fm = fm or {}
    return build(d,
                 cross_check=fm.get('fng_note', ''),
                 spread_history=fm.get('fng_spread', ''))

def render(md):
    out, i = [], 0
    lines = md.split('\n')
    if lines and lines[0].strip() == '---':
        end = next(k for k in range(1, len(lines)) if lines[k].strip() == '---')
        lines = lines[end + 1:]
    n = len(lines)
    fold = None          # (title, buffer) while inside a collapsed h3

    def flush():
        nonlocal fold
        if fold:
            title, buf = fold
            rows = sum(x.count('<tr>') for x in buf) - sum(1 for x in buf if '<th>' in x)
            cnt = '%d rows' % rows if rows > 0 else ''
            out.append('<details class="fold"><summary>%s<span class="cnt">%s</span></summary>'
                       '<div class="foldbody">%s</div></details>'
                       % (inline(title), cnt, '\n'.join(buf)))
            fold = None

    def emit(x):
        (fold[1] if fold else out).append(x)

    while i < n:
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        # table
        if s.startswith('|') and i + 1 < n and re.match(r'^\|[\s:|-]+\|$', lines[i + 1].strip()):
            hdr = [c.strip() for c in s.strip('|').split('|')]
            i += 2
            t = ['<div class="tblwrap"><table>',
                 '<tr>' + ''.join('<th>%s</th>' % inline(c) for c in hdr) + '</tr>']
            while i < n and lines[i].strip().startswith('|'):
                cs = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                tds = []
                for c in cs:
                    k, b = cell(c)
                    tds.append('<td%s>%s</td>' % (k, b))
                t.append('<tr>' + ''.join(tds) + '</tr>')
                i += 1
            t.append('</table></div>')
            emit('\n'.join(t))
            continue
        m = re.match(r'^(#{1,4})\s+(.*)$', s)
        if m:
            lvl, txt = len(m.group(1)), m.group(2)
            if lvl <= 2:
                flush()
                if lvl == 2:
                    if any(txt.startswith(c) for c in COLLAPSE_H2):
                        fold = (txt, [])
                    else:
                        out.append('<h2 class="sec">%s</h2>' % inline(txt))
            elif lvl == 3:
                flush()
                if any(txt.startswith(c) for c in COLLAPSE):
                    fold = (txt, [])
                else:
                    out.append('<h3 class="sub">%s</h3>' % inline(txt))
            else:
                emit('<h3 class="sub" style="opacity:.85">%s</h3>' % inline(txt))
            i += 1
            continue
        if s.startswith('---'):
            i += 1
            continue
        if s.startswith('>'):
            buf = []
            while i < n and lines[i].strip().startswith('>'):
                buf.append(lines[i].strip().lstrip('>').strip())
                i += 1
            emit('<div class="warnbox">%s</div>' % inline(' '.join(buf)))
            continue
        if re.match(r'^(-\s+|\*\s+(?!\*)|\d+\.\s+)', s) and not re.match(r'^\*[^*\s]', s):
            ordered = bool(re.match(r'^\d+\.\s+', s))
            items = []
            while i < n:
                t = lines[i].strip()
                if re.match(r'^(-\s+|\*\s+(?!\*)|\d+\.\s+)', t) and not re.match(r'^\*[^*\s]', t):
                    items.append(re.sub(r'^([-*]|\d+\.)\s+', '', t)); i += 1
                elif t and items and not t.startswith(('|', '#', '>', '---')):
                    items[-1] += ' ' + t; i += 1
                else:
                    break
            tag = 'ol' if ordered else 'ul'
            emit('<%s>%s</%s>' % (tag, ''.join('<li>%s</li>' % inline(x) for x in items), tag))
            continue
        if s == FNG_MARKER:
            emit(fng_html(FM))
            i += 1
            continue
        buf = [lines[i].strip()]; i += 1
        while i < n and lines[i].strip() and not lines[i].strip().startswith(('|', '#', '>', '---')) \
                and not re.match(r'^([-*]|\d+\.)\s+', lines[i].strip()):
            buf.append(lines[i].strip()); i += 1
        emit('<p>%s</p>' % inline(' '.join(buf)))
    flush()
    return '\n'.join(out)


# The executive summary is EDITION CONTENT, not renderer content (F-19).
# It came hardcoded in this script until 2026-08-23, which meant every new
# edition inherited the previous one's summary unless someone remembered to
# edit it. It now comes from an optional <!--exec ... --> block in the .md;
# blank-line-separated paragraphs become <p>. No block = no panel.
EXEC_RE = re.compile(r'<!--exec\s*(.*?)-->', re.S)


def exec_panel(md):
    m = EXEC_RE.search(md)
    if not m:
        return ''
    paras = [p.strip() for p in re.split(r'\n\s*\n', m.group(1)) if p.strip()]
    if not paras:
        return ''
    inner = '\n'.join('  <p>%s</p>' % inline(' '.join(p.split()))
                      for p in paras)
    return ('\n<div class="exec"><div class="exec-hd">The read</div>'
            '<div class="exec-b">\n' + inner + '\n</div></div>\n')



# ---------------------------------------------------------------------------
# F-19 - EDITION IDENTITY COMES FROM THE .md, NEVER FROM THIS SCRIPT.
# Until 2026-08-23 the date, revision, seal state and chips were hardcoded in
# __main__. Rendering a new edition meant EDITING THE RENDERER, and the failure
# mode was silent: a fresh edition wearing a stale "SEALED FULL" badge looks
# correct. Identity now comes from an HTML-comment front-matter block at the
# top of the .md, so the source of truth (LD-10) carries its own identity.
#
#   <!--edition
#   date: 2026-08-24
#   title: Monday, 24 August 2026 - 07:10 PHT
#   revision: r1
#   seal: UNSEALED
#   type: DAILY            # DAILY | MONDAY | WEEKEND
#   chip: CARRIED <b class="up">CADJPY HIGH</b>
#   chip: SCALE <b>&plusmn;11.00</b>
#   -->
# ---------------------------------------------------------------------------

FM_RE = re.compile(r'<!--edition\s*(.*?)-->', re.S)


def front_matter(md):
    """Parse the edition front-matter block. Absence is a hard failure."""
    m = FM_RE.search(md)
    if not m:
        raise SystemExit(
            'FATAL (F-19): no <!--edition ... --> front-matter block in the .md.\n'
            'The renderer will not guess the date, revision or seal state.\n'
            'Add the block at the top of the .md - see render_edition.py header.')
    fm, chips = {}, []
    for line in m.group(1).splitlines():
        line = line.split('#')[0].strip() if not line.strip().startswith('#') else ''
        if not line or ':' not in line:
            continue
        k, v = line.split(':', 1)
        k, v = k.strip().lower(), v.strip()
        if k == 'chip':
            chips.append(v)
        else:
            fm[k] = v
    for req in ('date', 'title', 'revision', 'seal', 'type'):
        if req not in fm:
            raise SystemExit('FATAL (F-19): front-matter missing "%s".' % req)
    if fm['type'] not in ('DAILY', 'MONDAY', 'WEEKEND'):
        raise SystemExit('FATAL (F-19): type must be DAILY, MONDAY or WEEKEND, '
                         'got "%s".' % fm['type'])
    # A WEEKEND edition is never sealed (LD-32).
    if fm['type'] == 'WEEKEND' and fm['seal'].upper() not in ('UNSEALED', 'NONE', 'PREP'):
        raise SystemExit('FATAL (LD-32): a WEEKEND edition is never sealed, '
                         'got seal="%s".' % fm['seal'])
    fm['chips'] = chips
    return fm


# ---------------------------------------------------------------------------
# R-7 / F-15 - SECTION-PRESENCE MANIFEST.
# Every other check in this repo is a CONTENT check - "is this figure right?"
# A section that is ABSENT has no figures to verify, so absence is invisible to
# all of them. F-15: the Fear & Greed block vanished across three editions and
# was sealed without. Only a manifest catches that.
#
# F-17 / LD-30 - SOURCE-PRESENCE. Section 1 mandates real news sources; three
# editions shipped with none, costing three sealed conclusions.
# ---------------------------------------------------------------------------

REQUIRED = {
    'DAILY':   ['§0', '§1', '§2', '§3', '§4', '§5', '§6', '§7', '§8', '§9'],
    'MONDAY':  ['§0', '§1', '§2', '§3', '§4', '§5', '§6', '§7', '§8', '§9'],
    'WEEKEND': ['§0', '§0L', '§1', '§2', '§3', '§4', '§5', '§6'],
}
# Sub-blocks that must appear within section 2 (spec 2.3) plus the F&G block.
# 4.0 is the WEEK-AHEAD PROJECTION table and it is mandatory (F-25). It is the
# only forward-looking record the method keeps: next week's edition grades the
# method against it, and F-21 exists ONLY because the projections were written
# down in advance. It went missing from the 2026-08-23 edition and no guard saw
# it, because the manifest checked h2 sections and 2.x sub-blocks but not 4.x.
REQUIRED_SUB = {
    'DAILY':   ['2.0', '2.1', '2.2', '2.3', '2.4', '2.5', '2.6', 'Fear', '4.0'],
    'MONDAY':  ['2.0', '2.1', '2.2', '2.3', '2.4', '2.5', '2.6', 'Fear', '4.0'],
    'WEEKEND': ['2.0', '2.1', '2.2', '2.3', '2.4', '2.5', '2.6', 'Fear', '4.0'],
}
# LD-38 / F-23 - MANDATORY GENERATED BLOCKS, asserted by MARKER not heading.
# A heading proves a section EXISTS; it does not prove it was BUILT the way
# the spec requires. On 2026-08-23 the F&G section had its heading and
# plausible content but was hand-written markdown tables instead of the
# LD-25 bar chart - a DOWNGRADE, invisible to a presence check.
REQUIRED_MARKERS = {
    '<!--FNG-->': 'the Fear & Greed bar chart (LD-25) - do not hand-write it '
                  'as markdown tables; emit the marker and fng_block.py '
                  'builds it from the persisted capture',
}

NEWS_HOSTS = ('investinglive.com', 'investing.com', 'reuters.com', 'bloomberg.com',
              'treasury.gov', 'federalreserve.gov', 'ecb.europa.eu',
              'bankofengland.co.uk', 'rba.gov.au', 'boj.or.jp', 'snb.ch',
              'bankofcanada.ca', 'rbnz.govt.nz', 'apnews.com', 'ft.com',
              'cnbc.com', 'wsj.com', 'marketwatch.com', 'forexlive.com')


def assert_sections(md, etype):
    """Refuse to render an edition missing a mandated section (R-7)."""
    heads = re.findall(r'^#{1,4}\s+(.+)$', md, re.M)
    blob = '\n'.join(heads)
    missing = [s for s in REQUIRED[etype]
               if not re.search(r'%s\s*[—\-–]' % re.escape(s), blob)]
    if missing:
        raise SystemExit(
            'FATAL (R-7/F-15): %s edition is missing mandated section(s): %s\n'
            'A missing section has no figures to verify - no content check can '
            'see it. Add the section or change the edition type.'
            % (etype, ', '.join(missing)))
    sub_missing = [s for s in REQUIRED_SUB[etype] if s not in blob]
    if sub_missing:
        raise SystemExit(
            'FATAL (R-7/F-15): missing mandated sub-block(s): %s\n'
            '(F-15: the Fear & Greed block vanished from three editions this way.)'
            % ', '.join(sub_missing))
    return len(heads)


def assert_markers(md):
    """Refuse to render if a mandatory generated block was hand-written."""
    missing = [(k, why) for k, why in REQUIRED_MARKERS.items() if k not in md]
    if missing:
        detail = chr(10).join('  %s  -> %s' % (k, why) for k, why in missing)
        raise SystemExit(
            'FATAL (LD-38/F-23): mandatory generated block(s) not emitted:'
            + chr(10) + detail + chr(10) +
            'A heading is not enough - the FORMAT is locked to the generator.')
    return len(REQUIRED_MARKERS)


def assert_whitelist(md):
    """All 70 whitelist indicators published, none blanked (LD-39 / F-24).

    The spec is explicit: ALL 70 NAMED INDICATORS ARE PUBLISHED EVERY EDITION,
    and one that cannot be sourced is published as NOT FOUND so it can be
    verified. A blank cell is not a NOT FOUND - it is an unverifiable silent
    omission. On 2026-08-23 section 2 shipped ~40 summary rows carrying
    em-dashes while all 70 rows sat in score_model.ROWS.
    """
    try:
        sys.path.insert(0, os.path.join(REPO, 'pipelines'))
        import score_model
        expected = len(score_model.ROWS)
    except Exception:
        return 0, 0
    try:
        sec = md[md.index('### 2.1'):md.index('### 2.6')]
    except ValueError:
        raise SystemExit('FATAL (LD-39): cannot locate section 2.1-2.5.')
    rows = [l for l in sec.splitlines()
            if l.startswith('| ') and not l.startswith('|---')
            and 'CCY | Indicator' not in l]
    if len(rows) < expected:
        raise SystemExit(
            'FATAL (LD-39/F-24): section 2 publishes %d indicator rows, '
            'expected %d.%sAll %d whitelist indicators are published EVERY '
            'edition; an unsourced one is published as NOT FOUND, never '
            'dropped. Generate the section with pipelines/section2.py rather '
            'than hand-writing it.' % (len(rows), expected, chr(10), expected))
    blank = [l for l in rows if '|  |' in l or '| \u2014 |' in l]
    if blank:
        raise SystemExit(
            'FATAL (LD-39/F-24): %d indicator row(s) carry a BLANK cell.%s'
            'A blank is not a NOT FOUND - it cannot be verified. First: %s'
            % (len(blank), chr(10), blank[0][:110]))
    return len(rows), expected


def assert_no_offlist_scores(md):
    """Section 4.0 may only SCORE whitelist indicators (F-3 / F-28 / LD-41).

    F-3, 2026-08-19: section 2 was built from the TE calendar instead of the
    named list, and 24 of 34 rows were off-list. It CHANGED THE RANKING.
    F-28, 2026-08-23: the same error in section 4.0 - 9 of 14 projection rows
    off-list, two of them SCORED, and those two fed the LD-40 confidence tally
    and changed the published ranking of the proposals.

    The rule is settled: off-list data informs the READ, never a SCORE. This
    checks the scored column of 4.0 only - the off-list NARRATIVE block below
    it is allowed and expected, because it carries no score.
    """
    import sys as _s
    try:
        _s.path.insert(0, os.path.join(REPO, 'pipelines'))
        import score_model
    except Exception:
        return 0
    names = {}
    for r in score_model.ROWS:
        names.setdefault(score_model.LABEL[r[1]], set()).add(r[2].lower())
    try:
        blk = md[md.index('### 4.0'):]
        blk = blk[:blk.index('#### Off the whitelist')] if '#### Off the whitelist' in blk \
            else blk[:blk.index('#### ')] if '#### ' in blk else blk
    except ValueError:
        return 0
    SCORED = ('GOOD', 'BAD', 'NEUTRAL')
    bad = []
    for line in blk.splitlines():
        if not line.startswith('| ') or line.startswith('|---'):
            continue
        cells = [c.strip().replace('*', '') for c in line.strip('|').split('|')]
        if len(cells) < 6 or 'When' in cells[0]:
            continue
        ccy, ind, proj = cells[1], cells[2], cells[5].upper()
        if not any(proj == v for v in SCORED):
            continue          # UNSCORED / UNSCORABLE rows are fine
        key = ind.lower()
        if not any(key == n or key in n or n in key for n in names.get(ccy, ())):
            bad.append('%s %s (projected %s)' % (ccy, ind, proj))
    if bad:
        raise SystemExit(
            'FATAL (F-3/F-28/LD-41): section 4.0 SCORES off-list indicator(s):'
            + chr(10) + chr(10).join('  ' + b for b in bad) + chr(10) +
            'Off-list data informs the READ, never a SCORE. Move these to the '
            '"Off the whitelist" narrative block, or publish them UNSCORED.')
    return len([l for l in blk.splitlines() if l.startswith('| ')])


def assert_levels_drawn(md):
    """Sections 5 and 6 must record drawn levels with their TV entity IDs.

    Project_Plan.txt line 10, the ORIGINAL request: "plot Key levels ...
    Update these levels as we refresh the report." The spec carried the
    clearing half of that instruction but never the plotting half, so
    drawing happened ad hoc instead of every refresh (F-31).

    A level published in a table and not on the chart is half-delivered -
    the reader re-plots by hand what the report already computed. This
    checks that each of section 5 and section 6 names at least one TV
    entity id, which is only present when levels were actually drawn and
    recorded for the next run to clear.
    """
    import re as _re
    missing = []
    for sec, nxt in (('## \u00a75 ', '## \u00a76 '), ('## \u00a76 ', '## \u00a77 ')):
        try:
            blk = md[md.index(sec):md.index(nxt)]
        except ValueError:
            continue
        # entity ids are 6 alphanumeric chars in backticks, e.g. `vHuuCj`
        if not _re.search(r'`[A-Za-z0-9]{6}`', blk):
            missing.append(sec.strip())
    if missing:
        raise SystemExit(
            'FATAL (LD-46/F-31): no drawn levels recorded in: %s%s'
            'Every refresh DRAWS the levels it publishes and records the TV '
            'entity ids, so the next run can clear exactly what it owns. '
            'A level in a table but not on the chart is half-delivered.'
            % (', '.join(missing), chr(10)))
    return len(missing) == 0


def assert_te_reconciled(etype):
    """The whitelist must be reconciled against TE before an edition publishes.

    F-35: seven of 70 rows were wrong, two of them from the day the model was
    built. The 20 and 21 Aug editions re-scored the same wrong numbers and
    EVERY CHECK PASSED - because every other check in this repo verifies
    ARITHMETIC ON THE ROWS and never the rows themselves. This is the only
    gate that compares a row to the world.

    Fails on a stale capture (nobody ran the audit) or on an unresolved
    difference (somebody ran it and ignored the output).
    """
    try:
        sys.path.insert(0, os.path.join(REPO, 'pipelines'))
        import audit_te
    except Exception:
        return 'audit unavailable'
    age = audit_te.capture_age_days()
    MAX_AGE = 4.0 if etype == 'WEEKEND' else 1.5
    if age is None:
        raise SystemExit(
            'FATAL (LD-50/F-35): the whitelist has never been reconciled '
            'against TradingEconomics.' + chr(10) +
            'Run: python pipelines/audit_te.py --fetch')
    if age > MAX_AGE:
        raise SystemExit(
            'FATAL (LD-50/F-35): TE capture is %.1f days old (max %.1f for a '
            '%s edition).%sSeven of 70 rows were wrong on 2026-08-23 because '
            'nothing re-read the source for four days.%sRun: python '
            'pipelines/audit_te.py --fetch' % (age, MAX_AGE, etype, chr(10), chr(10)))
    bad = audit_te.stale_rows()
    if bad:
        lines = chr(10).join(
            '  %-4s %-32s ours %-11s (%s)  TE %-11s (%s)' % r for r in bad)
        raise SystemExit(
            'FATAL (LD-50/F-35): %d whitelist row(s) disagree with TE:%s%s%s'
            'Triage each: a newer print means UPDATE score_model.py; a '
            'different presentation means add it to audit_te.KNOWN_DIFFERENT '
            'WITH A REASON. Never edit a row just to clear this gate.'
            % (len(bad), chr(10), lines, chr(10)))
    return '%.1fd capture, all rows agree' % age


def assert_freshness():
    """Revisions and stalled series (LD-54).

    TWO THINGS LD-50 CANNOT SEE. LD-50 checks whether we RE-READ the source;
    these check what the source SAID.

    A revised PREVIOUS silently flips a DIRECTION claim - "2.9% from 2.8%,
    rising" becomes "2.9% from 3.0%, falling" on the same Actual. That is F-4,
    which cost a withdrawn conclusion. LD-3 flagged TE's in-place revision on
    the repo's first day and nothing was ever built to catch it.

    A STALLED series sits at an old reference period with a perfectly fresh
    capture, because the capture faithfully reports that nothing arrived.

    Revisions are ADVISORY - they must be read and triaged, not auto-applied.
    Stalled series are FATAL: a series that stopped printing is either a
    sourcing failure or a discontinued indicator, and both need a decision.
    """
    try:
        sys.path.insert(0, os.path.join(REPO, 'pipelines'))
        import freshness
    except Exception:
        return 'freshness unavailable'
    rev, snap = freshness.revisions()
    st = freshness.stalled()
    if st:
        lines = chr(10).join(
            '  %-4s %-32s %-8s %s %d months behind (limit %d)' % r for r in st)
        raise SystemExit(
            'FATAL (LD-54): %d series have stopped producing prints:%s%s%s'
            'A monthly series more than 2 reference months behind is missing '
            'releases; a quarterly more than 5. Either the pull is failing or '
            'the indicator is discontinued - both need a decision, not a '
            'silent carry-forward.' % (len(st), chr(10), lines, chr(10)))
    if rev:
        print('  LD-54 REVISIONS  %d row(s) changed since %s - TRIAGE THESE:'
              % (len(rev), snap))
        for ccy, name, field, was, now in rev[:8]:
            print('        %-4s %-30s %-9s %s -> %s'
                  % (ccy, name[:30], field, was, now))
        if len(rev) > 8:
            print('        ... and %d more (python pipelines/freshness.py)'
                  % (len(rev) - 8))
        return '%d revision(s) flagged, no stalled series' % len(rev)
    return 'no revisions%s, no stalled series' % (
        '' if snap else ' (baseline not yet set)')


def assert_news_sources(md):
    """Section 1 must cite a real news source (F-17 / LD-30)."""
    m = re.search(r'^##\s*§1\b.*?$(.*?)(?=^##\s*§)', md, re.S | re.M)
    if not m:
        raise SystemExit('FATAL (R-7): cannot locate §1 to check its sources.')
    body = m.group(1).lower()
    hits = sorted({h for h in NEWS_HOSTS if h in body})
    if not hits:
        raise SystemExit(
            'FATAL (F-17/LD-30): §1 cites NO news source.\n'
            'Three editions shipped this way and it cost three sealed '
            'conclusions (the 19 Aug Treasury buyback). §1 must name where its '
            'news came from. Known hosts: %s ...' % ', '.join(NEWS_HOSTS[:4]))
    return hits


def prose_ratio(md):
    """LD-27 advisory check - prose blocks as a share of content units.

    ADVISORY ONLY, AND A WEAK SIGNAL. Measured 2026-08-23: r13 - the edition
    Jeff called too noisy - scores 13.0%, while the leaner weekend edition
    scores 15.1%. The ratio does NOT detect what he objected to, which was
    225 lines of PROCESS narrative in sections 0/0b/0c before any macro
    figure. That is a placement problem, not a volume one. Read this as a
    smell, never as a gate; LD-29 and LD-27's content rule are the real fix.

    Measures the REPORT BODY only. Front-matter and the exec block are
    metadata, not prose subject to LD-27, and counting them inflated the
    first measurement by ~6pp.
    """
    md = EXEC_RE.sub('', FM_RE.sub('', md))
    lines = [l.rstrip() for l in md.splitlines()]
    body = [l for l in lines if l.strip()]
    def is_prose(l):
        return (not l.lstrip().startswith(('|', '#', '>', '<!--', '<', '- ', '* ',
                                           '```', '---'))
                and not re.match(r'^\d+\.\s', l.lstrip()))

    # Count BLOCKS, not lines. Prose is hard-wrapped at ~78 chars so one
    # paragraph spans ~4.5 lines while one table row spans 1 - counting lines
    # measured wrapping style, not verbosity, and put a well-sourced edition at
    # 42% against a 15% target that no edition could ever meet.
    blocks, run = 0, False
    for l in body:
        if is_prose(l):
            if not run:
                blocks += 1; run = True
        else:
            run = False
    rows = len([l for l in body if l.lstrip().startswith(('|', '- ', '* '))])
    units = blocks + rows + len([l for l in body if l.lstrip().startswith('#')])
    return blocks, units, (100.0 * blocks / max(1, units))


if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else SRC
    md = io.open(src, encoding='utf-8').read()
    fm = front_matter(md)
    globals()['FM'] = fm
    dst = os.path.join(REPO, 'reports/2026/Q3/%s_market-sentiment.html' % fm['date'])

    # --- guards run BEFORE a single byte is written ---
    nheads = assert_sections(md, fm['type'])
    te_state = assert_te_reconciled(fm['type'])
    fresh_state = assert_freshness()
    nmark = assert_markers(md)
    nrow, nexp = assert_whitelist(md)
    assert_levels_drawn(md)
    assert_no_offlist_scores(md)
    sources = assert_news_sources(md)
    pn, bn, pct = prose_ratio(md)
    print('guards:')
    print('  R-7  sections   %d headings, all mandated present (%s)'
          % (nheads, fm['type']))
    print('  LD-38 markers   %d/%d generated blocks emitted'
          % (nmark, len(REQUIRED_MARKERS)))
    print('  LD-50 TE recon  %s' % te_state)
    print('  LD-54 freshness %s' % fresh_state)
    print('  LD-46 levels    drawn and entity ids recorded')
    if nexp:
        print('  LD-41 4.0 scores  whitelist indicators only')
        print('  LD-39 whitelist %d/%d indicator rows, no blanks'
              % (nrow, nexp))
    print('  F-17 sources    §1 cites %d: %s' % (len(sources), ', '.join(sources)))
    print('  LD-27 prose     %d prose blocks of %d units = %.1f%% %s'
          % (pn, bn, pct, 'OK' if pct < 15 else '*** OVER 15% TARGET ***'))

    style = io.open(STYLE_FROM, encoding='utf-8').read()
    head = style[:style.find('</style>') + len('</style>')]
    head = re.sub(r'<title>[^<]*</title>',
                  '<title>Market Sentiment %s</title>' % fm['date'], head) + EXTRA_CSS

    chips = '\n'.join('    <span>%s</span>' % c for c in fm['chips'])
    mast = """
<div class="tzbar">ALL TIMES PHILIPPINE STANDARD TIME (UTC+8) &middot; TE CALENDAR IS UTC &rarr; PHT = UTC + 8h &middot; RE-VERIFIED THIS RUN</div>
<div class="masthead"><div class="wrap mh">
  <div>
    <div class="eyebrow">Macro Economic Reporting &middot; %s</div>
    <div class="mdate">%s</div>
    <div class="draft">%s &middot; %s</div>
  </div>
  <div class="chips">
%s
  </div>
</div></div>
<div class="wrap">
""" % (fm.get('eyebrow', 'Daily Market Sentiment'), fm['title'],
       fm['revision'].upper(), fm['seal'].upper(), chips)

    body = EXEC_RE.sub('', md[FM_RE.search(md).end():])
    io.open(dst, 'w', encoding='utf-8').write(
        head + mast + exec_panel(md) + render(body) + '\n</div>\n')
    h = io.open(dst, encoding='utf-8').read()
    print('rendered %d bytes -> %s' % (len(h), os.path.basename(dst)))
    for t in ['table', 'div', 'tr', 'td', 'th', 'details', 'summary', 'p', 'ul', 'ol', 'li']:
        o = len(re.findall(r'<%s[ >]' % t, h)); c = len(re.findall(r'</%s>' % t, h))
        print('  %-8s %d/%d %s' % (t, o, c, 'OK' if o == c else '*** MISMATCH ***'))
