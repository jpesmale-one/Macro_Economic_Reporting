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
    # LD-69: §7 IS the build-notes section - guards run, sourcing
    # this run, what was not done. It already folds. An extra §11
    # would have made THREE folded build sections with fuzzy borders.
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

  /* LD-77 - impact tiers in §4.0. A left rule + tinted ground so the
     rows that can reprice a currency separate at a glance. */
  tr.ev-critical > td:first-child{box-shadow:inset 3px 0 0 var(--bear)}
  tr.ev-critical > td{background:var(--bear-bg)}
  tr.ev-high > td:first-child{box-shadow:inset 3px 0 0 var(--warn)}
  tr.ev-high > td{background:var(--warn-bg)}
  tr.ev-critical:hover > td,tr.ev-high:hover > td{filter:brightness(1.06)}
  .imp{font-family:var(--mono);font-size:.56rem;font-weight:700;
    letter-spacing:.09em;padding:2px 6px;border-radius:3px;
    margin-right:7px;vertical-align:1px;white-space:nowrap}
  .imp-c{background:var(--bear);color:#fff}
  .imp-h{background:var(--warn);color:#fff}
  /* LD-78 - aesthetic lift. Jeff, 2026-08-30: make the report more
     lively aesthetically. Restrained: more air, clearer hierarchy,
     tables that read as data rather than as walls. NO NEW HUES - the
     palette that already exists just gets used properly. */
  .tblwrap{border-radius:6px;overflow:hidden;overflow-x:auto;
    border:1px solid var(--border);margin:16px 0 20px;
    box-shadow:0 1px 2px rgba(0,0,0,.05)}
  th{background:var(--surface2);font-family:var(--mono);font-size:.62rem;
    letter-spacing:.1em;text-transform:uppercase;color:var(--muted);
    font-weight:700;text-align:left;padding:10px 13px;
    border-bottom:1px solid var(--border);white-space:nowrap}
  td{padding:9px 13px;border-bottom:1px solid var(--border)}
  table tr:last-child td{border-bottom:none}
  /* zebra, very light - enough to track a row across a wide table */
  table tr:nth-child(even):not(.ev-critical):not(.ev-high) > td{
    background:rgba(128,128,128,.045)}
  table tr:hover:not(.ev-critical):not(.ev-high) > td{
    background:var(--surface2)}
  /* the exec block carries the read - give it presence */
  .exec{box-shadow:0 2px 12px rgba(0,0,0,.07)}
  .exec-b p:first-child{font-size:.95rem}
  h2.sec{margin-top:44px}
  blockquote{background:var(--surface);border-radius:0 5px 5px 0;
    padding:10px 16px;border-left:3px solid var(--info)}
  /* LD-77 legend for the impact tiers */
  .implegend{display:flex;flex-wrap:wrap;gap:16px;align-items:center;
    margin:14px 0 2px;font-family:var(--mono);font-size:.6rem;
    letter-spacing:.09em;color:var(--muted);font-weight:600}
  .implegend span{display:inline-flex;align-items:center;gap:7px}
  .swatch{width:22px;height:11px;border-radius:2px;display:inline-block}
  .sw-c{background:var(--bear-bg);box-shadow:inset 3px 0 0 var(--bear)}
  .sw-h{background:var(--warn-bg);box-shadow:inset 3px 0 0 var(--warn)}
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


CRITICAL_EVENT = re.compile(
    r'interest rate decision|rate statement|rate decision', re.I)
HIGH_EVENT = re.compile(
    r'non.?farm payrolls|inflation rate|unemployment rate|'
    r'employment change|gdp growth|cpi\b', re.I)


def impact_class(cells):
    """Impact tier for one §4.0 row (LD-77).

    Jeff, 2026-08-30: "can you highlight the High Impact news in 4.0?
    So that I can get a sense even if I just scan the report"

    Tiers match the weights selection_gates.py already uses, so the
    table and the event-risk score cannot disagree about what counts
    as high impact.
    """
    txt = ' '.join(cells)
    if CRITICAL_EVENT.search(txt):
        return 'ev-critical'
    if HIGH_EVENT.search(txt):
        return 'ev-high'
    return ''


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
_NAME = {'AUD': 'Australia', 'NZD': 'New Zealand', 'USD': 'US', 'EUR': 'Europe',
         'GBP': 'UK', 'JPY': 'Japan', 'CAD': 'Canada', 'CHF': 'Switzerland'}

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
    in_week_ahead = False   # LD-77 - impact tagging is scoped to 4.0
    pending_legend = False  # LD-77 - emit the key once, under 4.0

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
        # LD-77: 4.0 is the WEEK-AHEAD table; impact tagging applies there.
        _h = re.match(r'^#{3,4}\s+(.*)$', s)
        if _h:
            _t = _h.group(1)
            if _t.startswith('4.0'):
                in_week_ahead = True
                pending_legend = True
            elif re.match(r'^\d+\.\d', _t) or _t.startswith('§'):
                in_week_ahead = False
        # table
        if s.startswith('|') and i + 1 < n and re.match(r'^\|[\s:|-]+\|$', lines[i + 1].strip()):
            hdr = [c.strip() for c in s.strip('|').split('|')]
            i += 2
            if pending_legend:
                emit('<div class="implegend">'
                     '<span><i class="swatch sw-c"></i>CENTRAL BANK DECISION</span>'
                     '<span><i class="swatch sw-h"></i>HIGH IMPACT</span>'
                     '<span>&mdash; scan these first</span></div>')
                pending_legend = False
            t = ['<div class="tblwrap"><table>',
                 '<tr>' + ''.join('<th>%s</th>' % inline(c) for c in hdr) + '</tr>']
            while i < n and lines[i].strip().startswith('|'):
                cs = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                tds = []
                for c in cs:
                    k, b = cell(c)
                    tds.append('<td%s>%s</td>' % (k, b))
                # LD-77: tag high-impact rows so a SCAN surfaces them.
                # Scoped to the week-ahead table - elsewhere an "inflation
                # rate" row is a data row, not a scheduled event.
                klass = impact_class(cs) if in_week_ahead else ''
                t.append('<tr%s>%s</tr>'
                         % ((' class="%s"' % klass) if klass else '',
                            ''.join(tds)))
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
    'MONDAY':  ['2.0', '2.0c', '2.1', '2.2', '2.3', '2.4', '2.5', '2.6',
                'Fear', '4.0'],
    # LD-74: a WEEKEND edition SELECTS, so it must also carry the cycle
    # view (2.0b), the chosen set (4.3) and the bench (4.5). Sunday is
    # not a different template - it is this one with selection in it.
    'WEEKEND': ['2.0', '2.0b', '2.0c', '2.1', '2.2', '2.3', '2.4', '2.5',
                '2.6', 'Fear', '4.0', '4.3', '4.5'],
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
              'cnbc.com', 'wsj.com', 'marketwatch.com', 'forexlive.com',
              # STATISTICAL AGENCIES. Added 2026-08-28: the list carried
              # central banks and wires but not the issuing agencies, which
              # LD-3 ranks ABOVE both. An edition sourcing the ABS and the
              # Swiss FSO directly scored "1 source" while a day citing three
              # wires scored 3 - exactly backwards.
              'abs.gov.au', 'bls.gov', 'bea.gov', 'census.gov',
              'statcan.gc.ca', 'ons.gov.uk', 'bfs.admin.ch', 'stats.govt.nz',
              'destatis.de', 'insee.fr', 'stat.go.jp', 'conference-board.org',
              'roymorgan.com', 'lenews.ch', 'fxstreet.com')


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
    # Count only REAL indicator rows. A row is one if its first cell is a
    # known currency code - explanatory tables inside a section note are not
    # indicator rows. Before this, an LD-57 note containing three markdown
    # tables pushed the count to 82/71: the guard still passed on >=, but the
    # number was meaningless and an UNDER-count could equally have hidden a
    # dropped row.
    codes = set(score_model.LABEL.values())
    rows = []
    for l in sec.splitlines():
        if not l.startswith('| ') or l.startswith('|---'):
            continue
        first = l.strip('|').split('|')[0].strip().replace('*', '')
        if first in codes:
            rows.append(l)
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


# LD-80 - LOCKED TABLE HEADERS. Full context: docs/LAYOUT_LOCK.md
# Jeff, 2026-08-30: "once the report layout is approve we should lock it
# up and not just changing the report format every now and then. It's
# important for an analyst to consistently look at standard report."
#
# The §4.0 header changed in FOUR CONSECUTIVE EDITIONS and the fourth
# silently dropped three columns - the entire LD-63 pricing read - while
# nothing noticed. Content changes freely; STRUCTURE DOES NOT.
LOCKED_TABLES = {
    '2.0': ['Band', 'CCY', 'Score', 'Group'],
    # LD-87, approved 2026-08-31: the indicator tables gain NEXT DUE, read
    # from TE's published schedule. docs/LAYOUT_LOCK.md documented 2.1-2.5
    # from the start but R-24 never enforced them - they are locked now.
    '2.1': ['CCY', 'Indicator', 'Actual', 'Previous', 'Ref', 'Threshold',
            'Score', 'Next due'],
    '2.2': ['CCY', 'Indicator', 'Actual', 'Previous', 'Ref', 'Threshold',
            'Score', 'Next due'],
    '2.3': ['CCY', 'Indicator', 'Actual', 'Previous', 'Ref', 'Threshold',
            'Score', 'Next due'],
    '2.4': ['CCY', 'Indicator', 'Actual', 'Previous', 'Ref', 'Threshold',
            'Score', 'Next due'],
    '2.5': ['CCY', 'Indicator', 'Actual', 'Previous', 'Ref', 'Threshold',
            'Score', 'Next due'],
    '2.0b': ['CCY', 'Leading', 'Confirming', 'Gap', 'Score'],
    # v2, Jeff 2026-08-31: PREVIOUS is frozen and a release lands in
    # its own ACTUAL column; Cons/Fcst is a RANGE when both exist.
    '4.0': ['When (PHT)', 'CCY', 'Indicator', 'Previous',
            'Cons / Fcst range', 'Actual', 'Market priced', 'Status'],
    # LD-85, approved 2026-08-31. Base and Forward BOTH visible - the
    # base is never overwritten by the forecast.
    '2.0c': ['CCY', 'Base', 'Forward', 'Change',
             'What the week prices'],
    '4.3': ['#', 'Pair', 'Bias'],
}


def assert_layout_locked(md):
    """A locked table must keep its column set (R-24/LD-80).

    Checks the FIRST table under each locked heading. Compares stripped
    header cells against LOCKED_TABLES - a prefix match, so a table may
    carry EXTRA trailing columns but never fewer, reordered, or renamed.

    This is the guard that would have caught §4.0 going from seven
    columns to four on 2026-08-30, taking the pricing read with it.
    """
    checked = 0
    for key, want in LOCKED_TABLES.items():
        m = re.search(r'^#{3,4}\s+' + re.escape(key) + r'(?![\d])', md, re.M)
        if not m:
            continue
        seg = md[m.end():]
        nxt = re.search(r'^#{2,4}\s', seg, re.M)
        if nxt:
            seg = seg[:nxt.start()]
        hdr = None
        for line in seg.split(chr(10)):
            t = line.strip()
            if t.startswith('|') and not re.match(r'^[|\s:-]+$', t):
                hdr = [c.strip().replace('*', '')
                       for c in t.strip('|').split('|')]
                break
        if hdr is None:
            continue
        checked += 1
        got = hdr[:len(want)]
        if got != want:
            raise SystemExit(
                'FATAL (R-24/LD-80): §%s table header changed.%s'
                '  locked: %s%s'
                '  found : %s%s'
                'A locked table keeps its COLUMN SET - content changes freely,'
                ' structure does not. §4.0 changed shape in four consecutive'
                ' editions and the fourth dropped the pricing columns entirely.'
                " If the change is intended, ask Jeff and update"
                ' docs/LAYOUT_LOCK.md in the same commit.'
                % (key, chr(10), ' | '.join(want), chr(10),
                   ' | '.join(got), chr(10)))
    return '%d locked table(s) intact' % checked


DEAD_DATE_FWD = re.compile(
    'next signal|the next is|is the next|upcoming|next week|watch for'
    '|next meeting|still ahead|lands next|due next', re.I)
_MON = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}


def assert_every_section_moved(md, fm):
    """Every section must MOVE against the previous edition (R-35/LD-89).

    Jeff, 2026-09-02: "can we make sure we visit every section everytime we
    build a new report moving forward?"

    R-35 shipped as a REPORT and that was not enough - a report I have to
    remember to read is exactly what failed on 26 Aug, when he first asked
    for this. It now BLOCKS.

    A section that carried verbatim is not automatically wrong. 8 (findings
    ledger) and 9 (gate status) legitimately repeat, and they are exempt.
    Everything else must show movement, or the edition does not publish.

    THE ESCAPE HATCH IS DELIBERATE AND NARROW. A section that genuinely has
    nothing new says so IN THE SECTION - "unchanged since <date>: <why>" -
    which turns a silent carry into a published claim someone can check.
    That is the same principle as F-73: say what you know, and say that you
    know it.
    """
    import difflib
    import glob as _glob
    QUIET = ('8', '9')
    cur = os.path.join(REPO, 'reports/2026/Q3',
                       '%s_market-sentiment.md' % fm.get('date', ''))
    prior = [f for f in sorted(_glob.glob(
        os.path.join(REPO, 'reports/2026/Q3/*_market-sentiment.md')))
        if os.path.basename(f) < os.path.basename(cur)]
    if not prior:
        return 'no previous edition to compare'
    prev = io.open(prior[-1], encoding='utf-8').read()

    def _secs(t):
        out, k, buf = {}, None, []
        for line in t.split(chr(10)):
            m = re.match(r'^#{2}\s*\u00a7(\d+[a-z]?)', line)
            if m:
                if k:
                    out[k] = chr(10).join(buf)
                k, buf = m.group(1), [line]
            elif k is not None:
                buf.append(line)
        if k:
            out[k] = chr(10).join(buf)
        return out

    A, B = _secs(prev), _secs(md)
    stale = []
    for key in sorted(B):
        if key in QUIET or key not in A:
            continue
        r = difflib.SequenceMatcher(None, A[key], B[key]).ratio()
        if r >= 0.98:
            body = B[key].lower()
            if 'unchanged since' in body or 'no change since' in body:
                continue          # declared, not forgotten
            stale.append((key, r))
    if stale:
        raise SystemExit(
            'FATAL (R-35/LD-89): %d section(s) did not move against %s.%s'
            % (len(stale), os.path.basename(prior[-1]), chr(10))
            + chr(10).join('  \u00a7%-4s %.1f%% identical' % (k, r * 100)
                           for k, r in stale) + chr(10)
            + 'Jeff, 2026-08-26: "Everytime we build a new edition we should'
            + ' be looking' + chr(10)
            + 'if every parts of the report have moved."' + chr(10)
            + 'On 2026-09-02 \u00a74 was 99.2%% identical and published SUNDAY room'
            + ' figures that' + chr(10)
            + 'contradicted \u00a74.2 in the same edition; \u00a77 said the market was'
            + ' CLOSED on a' + chr(10)
            + 'Wednesday. EITHER refresh the section, OR write "unchanged'
            + ' since <date>: <why>"' + chr(10)
            + 'inside it - which turns a silent carry into a claim someone'
            + ' can check.')
    return '%d section(s) moved' % (len(B) - len(QUIET))


def assert_no_dead_signal(md, fm):
    """No line may call a PAST date the next signal (R-34/F-79).

    Jeff, 2026-09-02: "is this updated? I can see this note Jackson Hole
    27-29 Aug is the next signal. but this is already in the past"

    3 carried FOUR dead references at once - Jackson Hole as the next Fed
    signal, "AU inflation Wed 26 Aug", "No CHF release next week" while CHF
    had released twice, and "the next is NZD on 2 Sep" on 2 Sep itself.
    5 and 6 carried Jackson Hole as a live headwind in five more places.

    R-19 catches a RELEASED event still previewed in 4.0. This catches the
    other shape: prose naming a date that has passed as though it were
    ahead. A carried-forward section keeps its verbs, and the verbs are what
    go stale first.
    """
    import datetime as _dt
    try:
        today = _dt.datetime.strptime(fm.get('date', ''), '%Y-%m-%d').date()
    except ValueError:
        return 'no edition date'
    bad = []
    for line in md.split(chr(10)):
        t = line.strip()
        if not t:
            continue
        # F-79b. Scope the test to the CLAUSE, not the line. A 3 table row
        # is 300 characters wide and legitimately holds "HELD 29 Jul" in one
        # cell and "next meeting" in another - matching across the whole line
        # flags a row that is entirely correct. Split on sentence and cell
        # boundaries so a forward phrase is only tested against dates that
        # sit beside it.
        for t in re.split(r'\|| — |\. ', t):
            t = t.strip()
            if not t or not DEAD_DATE_FWD.search(t):
                continue
            for m in re.finditer(r'(\d{1,2})(?:–\d{1,2})?\s+'
                                 r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|'
                                 r'Nov|Dec)', t):
                try:
                    d = _dt.date(today.year, _MON[m.group(2)],
                                 int(m.group(1)))
                except ValueError:
                    continue
                if d < today:
                    bad.append((d.isoformat(), t[:110]))
                    break
    if bad:
        raise SystemExit(
            'FATAL (R-34/F-79): %d line(s) call a PAST date the next signal.%s'
            % (len(bad), chr(10))
            + chr(10).join('  [%s] %s' % b for b in bad) + chr(10)
            + 'A carried-forward section keeps its verbs, and the verbs go '
            'stale first.')
    return 'no dead forward references'


def assert_no_raw_generated_html(md):
    """A GENERATED block is emitted by its MARKER, never pasted (R-33/F-78).

    Jeff, 2026-09-02, with a screenshot: "Our Fear and Greed index is not
    rendering correctly."

    It rendered TWICE - once properly from <!--FNG--> and once as an escaped
    paragraph, because a previous build had pasted the generated HTML into
    the markdown right after the marker. The renderer BUILDS that block from
    the marker alone; anything else in the file is a duplicate, and markdown
    escapes it into visible tag soup.

    This is LD-38's other half. LD-38 catches a generated block REPLACED by
    hand-written markdown; this catches one DUPLICATED by hand-pasted HTML.
    Same root cause - treating a generated block as editable text.

    Also flags PRE-ESCAPED ENTITIES in the body. The renderer escapes on
    output, so a literal "&amp;" in the source becomes "&amp;amp;" and the
    reader sees the entity. Front-matter is exempt - it IS html by design.
    """
    body = md[md.index('-->') + 3:] if '-->' in md else md
    problems = []
    for cls in ('fng-head', 'fng-bars', 'fng-row'):
        n = body.count(cls)
        if n:
            problems.append('%d copy of generated FNG markup pasted into the '
                            'body (class="%s")' % (n, cls))
            break
    ents = re.findall(r'&(amp|lt|gt|quot);', body)
    if ents:
        problems.append('%d pre-escaped entit(y/ies) in the body - the '
                        'renderer escapes on output, so "&amp;" becomes '
                        '"&amp;amp;"' % len(ents))
    if problems:
        raise SystemExit(
            'FATAL (R-33/F-78): generated markup or escaped entities in the '
            'markdown body.%s  %s%s'
            'A generated block is emitted by its MARKER and built by its '
            'module. Pasting%sthe rendered HTML back into the .md renders it '
            'twice - once correctly and%sonce as escaped tag soup, which is '
            'what Jeff saw.'
            % (chr(10), (chr(10) + '  ').join(problems), chr(10), chr(10),
               chr(10)))
    return 'no pasted markup, no pre-escaped entities'


def assert_cycle_gate_live(md):
    """§4.2's Cycle column must carry a TILT, not prose (R-31/LD-86).

    §2.0b was computed and published for two days while feeding NOTHING.
    LD-74 required it to be PRESENT; no code consumed it. NZDJPY was selected
    on a 4.12 tally spread while §2.0b said NZD was IN THE PAST with nothing
    upstream - and the cycle view turned out to be right.

    A descriptive Cycle column is exactly what that looked like. This checks
    the column carries a signed NUMBER, which only the gate produces.
    """
    try:
        blk = md[md.index('### 4.2'):md.index('### 4.3')]
    except ValueError:
        return 'no §4.2'
    body = [l for l in blk.split(chr(10))
            if l.strip().startswith('|') and 'Pair' not in l
            and not re.match(r'^[|\s:-]+$', l.strip())]
    if not body:
        return '§4.2 has no rows'
    tilted = sum(1 for l in body
                 if re.search(r'[+−-]\d\.\d\d', l.split('|')[-2]))
    if tilted < len(body):
        raise SystemExit(
            'FATAL (R-31/LD-86): §4.2 Cycle column is not carrying a tilt on'
            ' %d of %d row(s).%s'
            'Criterion 7 of docs/SELECTION_CRITERIA.md re-ranks confluence by'
            ' the cycle%stilt. A DESCRIPTIVE cycle column is what §2.0b looked'
            ' like for two days%swhile feeding nothing - and NZDJPY was'
            ' selected against its own cycle read.'
            % (len(body) - tilted, len(body), chr(10), chr(10), chr(10)))
    return '%d row(s) carry a cycle tilt' % tilted


def assert_bench_room_gated(md):
    """§4.5's bench must be room-gated, like the primaries (R-29/F-69).

    Jeff, 2026-08-31: "did we look at the technicals of the benched pairs?"

    We had not. §4.5 ranked alternates on MACRO SPREAD and EVENT RISK only -
    criterion 4 of LD-84, room to move, was never applied to it. The two
    highest-ranked bench pairs turned out to be the two with the LEAST room:
    GBPCHF at 80% of range with a LONG bias and 63 pips of headroom, EURCHF
    at 82% with 41. GBPCHF carried the best macro spread on the bench, so the
    old ranking would have offered it first - which is the GBPUSD failure
    (F-32/LD-73) reproduced on the bench a week after it was fixed for the
    primaries.

    A bench pair is entered MID-WEEK with less time to work than a primary.
    It deserves more scrutiny, not less.

    Checks that §4.5's table carries a Room column. Does not grade the
    numbers - that is reading, not running (see "What the guards CANNOT
    catch").
    """
    try:
        blk = md[md.index('### 4.5'):md.index('### 4.6')]
    except ValueError:
        return 'no §4.5'
    hdr = None
    for line in blk.split(chr(10)):
        t = line.strip()
        if t.startswith('|') and not re.match(r'^[|\s:-]+$', t):
            hdr = [c.strip().replace('*', '').lower()
                   for c in t.strip('|').split('|')]
            break
    if hdr is None:
        return '§4.5 has no table'
    if 'room' not in hdr:
        raise SystemExit(
            'FATAL (R-29/F-69): §4.5 ranks the bench without ROOM TO MOVE.%s'
            '  header: %s%s'
            'Criterion 4 of docs/SELECTION_CRITERIA.md applies to EVERY pair'
            ' we might enter,%sprimary and bench alike. Jeff, 2026-08-29:'
            ' "we may want to look for other%spairs with the same or a little'
            ' bit lesser conviction ... but with room to move%sin the favor of'
            ' our bias."%sRanking a bench on spread alone is how GBPCHF - best'
            ' spread, 63 pips of room -%swould have been offered as the first'
            ' replacement.'
            % (chr(10), ' | '.join(hdr), chr(10), chr(10), chr(10), chr(10),
               chr(10), chr(10)))
    return '§4.5 room-gated'


def assert_pairs_charted(md, etype):
    """A SELECTED pair must be on a chart, with entity IDs (R-23).

    Jeff, 2026-08-30: "I think you forgot to chart the pairs."

    LD-46 checked §5 and §6 only. The 2026-08-30 WEEKEND edition
    selected three pairs, published a falsifier for each, and drew NOT ONE
    LINE - and LD-46 still reported success, because it was looking at
    gold and BTC.

    A selected pair is the MOST important thing in the report to have on a
    chart: it is what gets tracked all week against a level. Only a
    SELECTING edition is checked - a mid-week edition carries the set
    forward and the lines are already there.
    """
    if etype != 'WEEKEND':
        return 'n/a (not a selecting edition)'
    try:
        blk = md[md.index('### 4.3'):md.index('### 4.4')]
    except ValueError:
        return 'no §4.3'
    ids = re.findall(r'`([A-Za-z0-9]{6})`', blk)
    if len(ids) < 3:
        raise SystemExit(
            'FATAL (R-23/LD-46): §4.3 selects pairs but records only %d drawn'
            ' level(s).%sEvery selected pair needs its entry reference, its'
            ' falsifier and the structure it is aiming into ON THE CHART, with'
            ' entity IDs recorded.%sOn 2026-08-30 three pairs were selected and'
            ' NOTHING was drawn, while LD-46 passed on §5/§6.'
            % (len(ids), chr(10), chr(10)))
    return '%d entity ids in §4.3' % len(ids)


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
    bad, unmatched = audit_te.stale_rows()
    if unmatched:
        # F-38: an unmatched row is NOT a passing row - the audit cannot see
        # it at all. 11 of 71 were silently unaudited while the tool printed
        # "all rows agree with TE".
        lines = chr(10).join('  %-4s %-34s ours %s (%s)' % (r[0], r[1], r[2], r[3])
                             for r in unmatched)
        raise SystemExit(
            'FATAL (LD-50/F-38): %d whitelist row(s) match NO TE series, so '
            'they are unverified:%s%s%sAdd a TE_ALIAS entry in audit_te.py '
            'mapping each to its TE series key.'
            % (len(unmatched), chr(10), lines, chr(10)))
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


def assert_tally_sorted(md):
    """Section 2.0 must be sorted by score, descending (LD-61).

    Jeff found USD +2.25 listed above AUD +2.75 on 2026-08-24. LD-57 had moved
    AUD from +2.08 and the cell was patched in place without re-sorting.

    A MIS-SORTED TALLY DRIFTS SILENTLY because every number in it is still
    correct - no content check can see it, only an ordering check. And this is
    the table that sets the BANDS every other section reads.
    """
    try:
        # 2.0b (LD-72) sits between 2.0 and 2.1 and is NOT a tally -
        # its columns are normalised stage scores. End the slice there.
        _end = md.index('### 2.0b') if '### 2.0b' in md else md.index('### 2.1')
        blk = md[md.index('### 2.0'):_end]
    except ValueError:
        return 0
    scores = []
    for line in blk.splitlines():
        if not line.startswith('| ') or line.startswith('|---'):
            continue
        cells = [c.strip().replace('*', '') for c in line.strip('|').split('|')]
        if len(cells) < 3 or cells[0] == 'Band':
            continue
        m = re.match(r'([+−-]?[\d.]+)$', cells[2].replace('−', '-'))
        if m:
            scores.append((cells[1], float(m.group(1))))
    if len(scores) < 2:
        return len(scores)
    for a, b in zip(scores, scores[1:]):
        if b[1] > a[1]:
            raise SystemExit(
                'FATAL (LD-61): section 2.0 is not sorted by score - %s %+.2f '
                'is listed above %s %+.2f.%sRegenerate it with '
                'section2.tally_table(); never patch a cell in place.'
                % (a[0], a[1], b[0], b[1], chr(10)))
    return len(scores)


# R-22 v2. The FIRST version counted every F-/LD-/R- number in §0-§6 and
# reported 26 lines on 2026-08-29. Reading them showed only ~6 were build
# narrative; the other 20 were RULE CITATIONS EXPLAINING A MARKET FACT -
# "LD-48 saved it: a falsifier fires on a CLOSE" explains why a pair survived,
# and belongs in the read. A guard that overstates by 3x gets ignored, which
# is precisely how LD-27 died. So this looks for BUILD VOCABULARY, not for
# rule numbers.
PROCESS_RE = re.compile(
    r'(\b(?:score_model|section2|week_ahead|audit_te|whole_edition|render_edition|'
    r'directional|freshness|rate_model|select_pairs)\.py\b'
    r'|\bregression fixture|\bthe sweep|\bguard(?:s)? (?:fired|pass|run)'
    r'|\bre-?tallied|\bnot re-?charted|\brefreshed (?:to|this run)'
    r'|\bbefore the next run\b|\bthis run\b'
    r'|\bgenerated from|\bhand-?sourced|\bcarried version|\bRESOLVED \u2014)',
    re.I)

ANALYSIS_SECTIONS = ('§0', '§1', '§2', '§3', '§4', '§5', '§6')


def assert_process_placement(md):
    """§0-§6 are the MARKET READ, not the build log (R-22/LD-69).

    Jeff, 2026-08-29: "I asked for the report to be clean and less
    process narrative. But I got tired of complaining so I just accepted
    it."

    LD-27 measured prose VOLUME and its own docstring recorded that it
    FAILED - the edition he called too noisy scored BETTER than the one
    he liked. His objection was PLACEMENT: build talk where the market
    read should be. This measures that.

    It does NOT flag a rule citation that explains a market fact. Those
    belong in the read. It flags BUILD VOCABULARY - pipeline filenames,
    "not re-charted", "this run", "before the next run".

    Advisory. The border is editorial, so this reports a count and a
    location rather than refusing to publish. Build detail goes to
    §7 Method notes, which already folds.
    """
    cur, hits = 'PRE', []
    for line in md.split(chr(10)):
        if line.startswith('## '):
            m = re.match(r'##\s*(§\d+)', line)
            cur = m.group(1) if m else 'PRE'
        t = line.strip()
        if not t or t.startswith(('|', '#', '<!--')):
            continue
        if cur in ANALYSIS_SECTIONS and PROCESS_RE.search(t):
            hits.append((cur, t))
    if not hits:
        return 'analysis sections clean'
    by = {}
    for sec, _t in hits:
        by[sec] = by.get(sec, 0) + 1
    worst = sorted(by.items(), key=lambda kv: -kv[1])[0]
    return ('%d build line(s) in §0-6, worst %s with %d — move to §7'
            % (len(hits), worst[0], worst[1]))


def assert_no_stale_preview(md, fm):
    """No section may preview an event 4.0 marks RELEASED (R-19).

    Jeff, 2026-08-26, on 2.7: "This is also stale is this still
    relevant?" It was not - 2.7 said "three Friday prints were fed in
    THIS SESSION" three sessions after the fact, and its premise ("the
    tally did not move") had since been falsified by USD +1.75 -> +2.25.

    The same read found 1 still saying "CPI lands in three hours" for a
    release that had landed, and 7 reporting "ZERO whitelist releases so
    far today" after one had printed.

    R-18 compares sections to each other on PRICES and STATUS. This
    catches the TENSE mismatch: 4.0 says RELEASED while prose still
    counts down to it.
    """
    released = set()
    try:
        blk = md[md.index('### 4.0'):md.index('### 4.3')]
    except ValueError:
        return 'no 4.0'
    for line in blk.split(chr(10)):
        up = line.upper()
        # A settled edition reports OUTCOMES, not the word RELEASED
        # (2026-08-29). Anchoring on one literal made the guard a
        # no-op that whole edition.
        if not line.startswith('|') or not any(
                k in up for k in ('RELEASED', 'BEAT', 'MISS',
                                  'IN LINE', 'AS PRICED', 'DID NOT')):
            continue
        cells = [c.strip().replace('*', '')
                 for c in line.strip().strip('|').split('|')]
        for c in cells:
            if re.fullmatch(r'[A-Z]{3}', c):
                released.add(c)
                break
    if not released:
        return 'nothing released yet'

    body = md[:md.index('### 4.0')]
    AHEAD = re.compile(
        r'(lands? in [a-z0-9 ]{1,12}(hours?|hrs)|is due |hours? out|hrs out|ahead of this edition|after this edition|awaiting|not yet released)',
        re.I)
    hits = []
    for para in body.split(chr(10) + chr(10)):
        m = AHEAD.search(para)
        if not m:
            continue
        for ccy in released:
            if ccy in para or _NAME.get(ccy, ccy) in para:
                hits.append((ccy, m.group(0).strip(), para[:90]))
                break
    if hits:
        ccy, phrase, ctx = hits[0]
        raise SystemExit(
            'FATAL (R-19): §4.0 marks a %s event RELEASED, but earlier prose '
            'still previews it as upcoming ("%s").%s  %s...%s'
            'A released event must be reported, never counted down to. On '
            '2026-08-26 §1 said "CPI lands in three hours" after it had landed.'
            % (ccy, phrase, chr(10), ctx.replace(chr(10), ' '), chr(10)))
    return '%d released, no stale preview' % len(released)


def assert_whole_edition(md):
    """Every section must agree with every other (R-18/LD-67).

    Jeff, 2026-08-26: "Everytime we build a new edition we should be
    looking if every parts of the report have moved. we should be looking
    at it wholistically and not just look at the moving parts"

    Four defects that day lived in sections nobody re-read: a carried
    score contradicting the tally (F-46), a 5-day-stale sentiment block
    that blamed its source (F-51), 4.4 calling a LOCKED pair REJECTED for
    three editions (F-52), and 4.5 using a 5-day high as a 45-bar high,
    which INVERTED a family ranking (F-53).

    Every other guard checks a section against ITSELF or against source.
    This checks sections against EACH OTHER, which is the only way a
    carried-forward contradiction becomes visible.
    """
    sys.path.insert(0, os.path.join(REPO, 'pipelines'))
    from whole_edition import sweep
    probs = sweep(md)
    if probs:
        lines = ['  %-16s %s' % (k, m) for k, m in probs]
        raise SystemExit(
            'FATAL (R-18/LD-67): %d cross-section contradiction(s):%s%s%s'
            'A section carried forward must still AGREE with the sections '
            'that were re-derived. Refresh the prices in every carried '
            'table (Jeff: refresh prices, keep analysis) and re-check any '
            'status that changed since it was written.'
            % (len(probs), chr(10), chr(10).join(lines), chr(10)))
    return 'no cross-section contradictions'


def assert_fng_fresh(fm):
    """The F&G capture must be current for the edition date (R-17/F-51).

    2026-08-26. Three editions ran on a 21 Aug reading while telling the
    reader 'the CNN endpoint posts once daily and HAS NOT UPDATED SINCE'.
    The historical series inside our own payload showed the endpoint had
    published every business day - Fri 21 54.51, Mon 24 56.09, Tue 25
    58.80. THE SOURCE WAS FINE; WE STOPPED FETCHING, and the carry-forward
    note asserted an outage that never happened.

    Cost: headline 3.6 points low, 'four of seven components in Fear' when
    two were, and 'Junk Bond Demand alone carries the headline' when that
    component had FALLEN 7.4 while the index rose.

    LD-54 catches this for score_model rows. The F&G block is not a
    score_model row, so nothing looked at it.
    """
    import glob, json, datetime as _dt
    caps = sorted(glob.glob(os.path.join(REPO, 'data/raw/fng/*.json')))
    if not caps:
        return 'no capture'
    d = json.load(io.open(caps[-1], encoding='utf-8'))
    fg = d.get('fear_and_greed', {})
    ts = str(fg.get('timestamp', ''))[:10]
    ed = fm.get('date', '')
    if not ts or not ed:
        return 'undated'
    try:
        gap = (_dt.date.fromisoformat(ed)
               - _dt.date.fromisoformat(ts)).days
    except ValueError:
        return 'unparseable'
    # The reading is stamped the prior close, so 1 day is normal;
    # 3 spans a weekend. Beyond that the block is stale.
    if gap > 3:
        raise SystemExit(
            'FATAL (R-17/F-51): the Fear & Greed capture is stamped %s but '
            'this edition is dated %s - %d days.%sRe-fetch before publishing:%s'
            '  curl -sL -A "Mozilla/5.0" -H "Referer: https://edition.cnn.com/markets/fear-and-greed" %s'
            '    "https://production.dataviz.cnn.io/index/fearandgreed/graphdata" %s'
            '    -o data/raw/fng/$(date +%%Y-%%m-%%d)_capture.json%s'
            'On 2026-08-26 three editions ran on a 21 Aug reading while claiming'
            ' the endpoint had not updated. It had - every business day.'
            % (ts, ed, gap, chr(10), chr(10), chr(92) + chr(10),
               chr(92) + chr(10), chr(10)))
    return '%s, %dd old' % (ts, gap)


def assert_scores_consistent(md):
    """Any currency score quoted OUTSIDE 2.0 must equal the 2.0 tally (R-16).

    F-46, 2026-08-26. The 25 Aug edition published USD +1.75 in 2.0 and
    USD +2.25 in BOTH 5 and 6 - each citing "2.0 tally" as its source.
    Sections 5/6 were carried from Sunday and flagged "not re-charted", but
    the carry included a SCORE, not just levels and prose.

    A STALE LEVEL IS DISCLOSED; A STALE SCORE CONTRADICTS 2 SILENTLY. No
    existing guard compared a number quoted elsewhere against the tally that
    produced it, so one edition shipped two different values for one currency.
    """
    try:
        # 2.0b (LD-72) sits between 2.0 and 2.1 and is NOT a tally -
        # its columns are normalised stage scores. End the slice there.
        _end = md.index('### 2.0b') if '### 2.0b' in md else md.index('### 2.1')
        blk = md[md.index('### 2.0'):_end]
    except ValueError:
        return 0
    tally = {}
    for line in blk.splitlines():
        if not line.startswith('| ') or line.startswith('|---'):
            continue
        cells = [c.strip().replace('*', '') for c in line.strip('|').split('|')]
        if len(cells) < 3 or cells[0] == 'Band':
            continue
        m = re.match(r'([+−-]?[\d.]+)$', cells[2].replace('−', '-'))
        if m and re.match(r'^[A-Z]{3}$', cells[1]):
            tally[cells[1]] = float(m.group(1))
    if not tally:
        return 0

    body = md[md.index('### 2.1'):]
    pat = re.compile(r'\b(USD|EUR|GBP|JPY|CHF|CAD|AUD|NZD)\b'
                     r'[^|\n]{0,40}?score[^|\n]{0,20}?'
                     r'([+−-]\s?\d+\.\d\d)')
    bad = []
    for m in pat.finditer(body):
        ccy = m.group(1)
        val = float(m.group(2).replace('−', '-').replace(' ', ''))
        if ccy in tally and abs(val - tally[ccy]) > 0.005:
            bad.append((ccy, val, tally[ccy], m.group(0).strip()))
    if bad:
        ccy, val, want, ctx = bad[0]
        # LD-85: 2.0c publishes a FORWARD-ADJUSTED score that legitimately
        # differs from the base. R-16 only knows base values, so a forward
        # number quoted bare in prose lands here. That is the RIGHT default -
        # it forces the label - but the message must say so, or the next
        # session "fixes" a correct number to silence a guard.
        raise SystemExit(
            'FATAL (R-16/F-46): %s is quoted as %+.2f outside section 2.0, but '
            'the 2.0 tally says %+.2f.%s  "%s"%sOn 2026-08-25 sections 5 and 6 '
            'carried a STALE USD score from Sunday while citing 2.0 as the '
            'source. Re-derive the score wherever it is quoted; carrying a '
            'section forward must never carry its numbers.%s'
            'IF THIS IS A FORWARD-ADJUSTED SCORE (LD-85, published in 2.0c) '
            'it legitimately differs from the base - LABEL it as forward '
            'rather than changing the number to silence this guard.'
            % (ccy, val, want, chr(10), ctx, chr(10), chr(10)))
    return len(tally)


def assert_news_coverage(md):
    """Section 1 must carry news for every currency section 0 says MOVED.

    F-43, 2026-08-24. Jeff: "This kind of news should be in our section 1.
    Earlier this morning we only have 1 for Japan but the CAD is already
    pricing the move and we have no Idea why."

    THE FAILURE WAS NOT A BAD SEARCH - it was that section 1 HAD NO REQUIRED
    SCOPE. r1's section 0 diagnosed the gap to the CAD leg explicitly, ruled
    OUT a JPY event, and named USDCAD's 48.7-pip move. Section 1 then covered
    JAPAN - the leg just ruled out - and said nothing about Canada, the leg
    just ruled in. One news item shipped while the market priced a trade war,
    and every guard passed, because nothing required section 1 to cover
    anything at all.

    LD-30 says HOW to write a news item. It never said WHICH currencies need
    one. This is that rule.

    TRIGGER: a currency named in section 0's tracking table with a non-trivial
    gap, or flagged as NO / unexplained, must appear in section 1. Requiring
    all eight every edition would force six empty headings on a quiet day and
    LD-27 bans filler - so the trigger is what the edition ITSELF says moved.
    """
    try:
        s0 = md[md.index('## \u00a70 '):md.index('## \u00a71 ')]
        s1 = md[md.index('## \u00a71 '):md.index('## \u00a72 ')]
    except ValueError:
        return 0
    codes = ('USD', 'EUR', 'GBP', 'JPY', 'AUD', 'NZD', 'CAD', 'CHF')
    need = set()
    for line in s0.splitlines():
        if not line.startswith('| ') or line.startswith('|---'):
            continue
        cells = [c.strip().replace('*', '') for c in line.strip('|').split('|')]
        if len(cells) < 3:
            continue
        pair = cells[0]
        if not any(pair.startswith(c) for c in codes):
            continue
        # a row that moved: flagged NO/unexplained, or carrying a pip gap
        row = line.upper()
        moved = ('| NO |' in row or 'UNEXPLAINED' in row
                 or re.search(r'[-\u2212+]\d+\.\d+ PIPS', row))
        if moved:
            for c in codes:
                if c in pair:
                    need.add(c)
    if not need:
        return 0
    missing = sorted(c for c in need if c not in s1)
    if missing:
        raise SystemExit(
            'FATAL (LD-65/F-43): \u00a70 says %s moved, but \u00a71 carries no '
            'news for %s.%sA currency the edition itself flags as moving needs '
            'its catalyst looked for. On 2026-08-24 \u00a70 diagnosed a CAD gap '
            'and \u00a71 covered Japan - the leg just ruled OUT - while 50%% '
            'tariffs were live.' % (', '.join(sorted(need)),
                                    ', '.join(missing), chr(10)))
    return len(need)


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


FOLDED_SECTIONS = ('§7', '§8')


def prose_ratio(md):
    """LD-27 v2 - prose share of the READ, excluding folded sections.

    Jeff, 2026-08-29: "it's ok if we overshoot a little as long as it is
    concentrated on section 7 so the noise is not impacting the other
    sections."

    v1 counted the WHOLE body and was red on every edition of the 2026-08-24
    week while the report measurably improved. Worse, its own docstring
    already recorded that it FAILED to detect what Jeff objected to: the
    edition he called too noisy scored 13.0%, the one he liked 15.1%.

    Two changes fix that. R-22 (LD-69) now measures PLACEMENT - build
    narrative sitting in §0-§6 - which is the real complaint. And this
    counts prose only where noise HURTS: the read. §7 and §8 FOLD, so
    verbosity there costs the reader nothing.

    Measured on 2026-08-29 after LD-69 was applied: whole body 15.7%,
    READ 14.5%, folded sections 25.7%. The overshoot was entirely in the
    part designed to absorb it.

    Still ADVISORY, and KNOWN TO BE INSENSITIVE. units = blocks + table
    rows + headings, and a data-heavy edition carries ~260 table rows, so
    injecting 30 padding paragraphs moved the ratio only 14.8% -> 15.0%.
    It separates a CLEANED edition (14.8% OK) from uncleaned ones (15.8%,
    17.7%) and that is the signal it is good for. It is NOT a sensitive
    bloat detector - do not read it as one. R-22 is the guard that
    measures the actual complaint.

    Front-matter and the exec block are metadata, not prose subject to
    LD-27.
    """
    md = EXEC_RE.sub('', FM_RE.sub('', md))
    cur, kept = 'PRE', []
    for line in md.split(chr(10)):
        if line.startswith('## '):
            m = re.match(r'##\s*(§\d+)', line)
            cur = m.group(1) if m else 'PRE'
        if cur not in FOLDED_SECTIONS:
            kept.append(line)
    body = [l.rstrip() for l in kept if l.strip()]

    def is_prose(l):
        return (not l.lstrip().startswith(
                    ('|', '#', '>', '<!--', '<', '- ', '* ',
                     '```', '---'))
                and not re.match(r'^\d+\.\s', l.lstrip()))

    # Count BLOCKS, not lines: prose hard-wraps at ~78 chars so one
    # paragraph spans ~4.5 lines while a table row spans 1.
    blocks, run = 0, False
    for l in body:
        if is_prose(l):
            if not run:
                blocks += 1
                run = True
        else:
            run = False
    # v1's arithmetic, unchanged - only the INPUT LINES differ. My first
    # v2 rewrote this too and collapsed a 20-row table to ONE unit,
    # reporting 38.7% where the true read figure is 14.5%.
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
    ntal = assert_tally_sorted(md)
    assert_levels_drawn(md)
    # R-27/LD-82 - the SHAPE of every section, not just four headers.
    # 4.0's columns held under R-24 while 4.6 quietly GAINED TWO TABLES.
    import layout_shape
    shape_state = layout_shape.check(md)
    # R-32/F-77 - every 4.0 time must equal pht(capture). The hand-typed
    # labels had both central banks EIGHT HOURS EARLY and produced a whole
    # section about an RBNZ decision that had not happened yet.
    import audit_times
    moved = assert_every_section_moved(md, fm)
    dead = assert_no_dead_signal(md, fm)
    rawhtml = assert_no_raw_generated_html(md)
    times = audit_times.check(md)
    cyc = assert_cycle_gate_live(md)
    bench = assert_bench_room_gated(md)
    layout = assert_layout_locked(md)
    charted = assert_pairs_charted(md, fm['type'])
    assert_no_offlist_scores(md)
    place_state = assert_process_placement(md)
    preview_state = assert_no_stale_preview(md, fm)
    whole_state = assert_whole_edition(md)
    fng_state = assert_fng_fresh(fm)
    nsc = assert_scores_consistent(md)
    ncov = assert_news_coverage(md)
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
    print('  R-23 pairs      %s' % charted)
    print('  R-24 layout     %s' % layout)
    print('  R-29 bench      %s' % bench)
    print('  R-31 cycle      %s' % cyc)
    print('  R-32 times      %s' % times)
    print('  R-33 markup     %s' % rawhtml)
    print('  R-34 dead refs  %s' % dead)
    print('  R-35 drift      %s' % moved)
    print('  R-27 shape      %s' % shape_state)
    print('  LD-61 tally     %d rows, sorted by score' % ntal)
    if nexp:
        print('  LD-41 4.0 scores  whitelist indicators only')
        print('  LD-39 whitelist %d/%d indicator rows, no blanks'
              % (nrow, nexp))
    print('  R-18 whole ed   %s' % whole_state)
    print('  R-19 tense      %s' % preview_state)
    print('  R-22 placement  %s' % place_state)
    print('  R-17 F&G fresh  %s' % fng_state)
    print('  R-16 scores     %d currency scores agree with §2.0' % nsc)
    print('  LD-65 news cov  %d moved currency(ies) covered' % ncov)
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
