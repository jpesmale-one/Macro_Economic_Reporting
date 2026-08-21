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
        buf = [lines[i].strip()]; i += 1
        while i < n and lines[i].strip() and not lines[i].strip().startswith(('|', '#', '>', '---')) \
                and not re.match(r'^([-*]|\d+\.)\s+', lines[i].strip()):
            buf.append(lines[i].strip()); i += 1
        emit('<p>%s</p>' % inline(' '.join(buf)))
    flush()
    return '\n'.join(out)


EXEC = """
<div class="exec">
  <div class="exec-hd">The week in one screen &middot; Mon 17 &ndash; Fri 21 Aug</div>
  <div class="exec-b">
    <p><b>Carried three leg-disjoint reads, ranked by confidence:</b>
       <b>CADJPY LONG (HIGH)</b> &middot; <b>EURCHF LONG (MEDIUM)</b> &middot;
       <b>GBPUSD LONG (LOW)</b>. All three are intact at 16:40 and none is near
       its falsifier. Six currencies, each used once &mdash; three independent
       tests, not one bet counted three times.</p>
    <p><b>Yesterday's four positions all worked</b> (+82 / +108 / +163 pips and
       &minus;29), <b>but that was two bets, not four</b> &mdash; three shared the
       JPY leg. The scorecard is corrected in &sect;0 rather than quietly fixed.</p>
    <p><b>Interest Rate is now scored</b> (&sect;2.6, weight 3) &mdash; it was
       defined as category 6 from the start and had never fed the tally.
       <b>NZD jumps two ranks</b> as the only active hiker; USD and AUD each drop
       one on inflation that is above target but <em>falling</em>.</p>
    <p><b>The week's projections graded 10 of 13.</b> All three misses were
       BAD-projected <em>survey</em> indicators that printed GOOD &mdash; a
       one-directional error, recorded as a finding about the method rather than
       patched.</p>
    <p><b>Tally:</b> CAD +8.38 &middot; EUR +6.25 &middot; GBP +5.75 &middot;
       NZD +3.75 &middot; USD +2.25 &middot; AUD +2.08 &middot; JPY +0.00 &middot;
       CHF &minus;3.38 &nbsp;<span class="note">(scale &plusmn;11.00)</span></p>
  </div>
</div>
"""

if __name__ == '__main__':
    md = io.open(SRC, encoding='utf-8').read()
    style = io.open(STYLE_FROM, encoding='utf-8').read()
    head = style[:style.find('</style>') + len('</style>')]
    head = head.replace('<title>Market Sentiment 19 Aug</title>',
                        '<title>Market Sentiment 21 Aug</title>') + EXTRA_CSS
    mast = """
<div class="tzbar">ALL TIMES PHILIPPINE STANDARD TIME (UTC+8) &middot; TE CALENDAR IS UTC &rarr; PHT = UTC + 8h &middot; RE-VERIFIED THIS RUN</div>
<div class="masthead"><div class="wrap mh">
  <div>
    <div class="eyebrow">Macro Economic Reporting &middot; Daily Market Sentiment</div>
    <div class="mdate">Friday, 21 August 2026 &middot; 16:40 PHT</div>
    <div class="draft">REVISION 7 &middot; FULL SEAL CANDIDATE &middot; WEEK GRADED 10/13</div>
  </div>
  <div class="chips">
    <span>CARRIED <b class="up">CADJPY HIGH</b> &middot; EURCHF MED &middot; GBPUSD LOW</span>
    <span>WEEK <b class="up">10 of 13</b> <span class="dn">3 misses all surveys</span></span>
    <span>SCALE <b>&plusmn;11.00</b> <span class="dn">rate = cat 6</span></span>
  </div>
</div></div>
<div class="wrap">
""" + EXEC
    io.open(DST, 'w', encoding='utf-8').write(head + mast + render(md) + '\n</div>\n')
    h = io.open(DST, encoding='utf-8').read()
    print('rendered %d bytes' % len(h))
    for t in ['table', 'div', 'tr', 'td', 'th', 'details', 'summary', 'p', 'ul', 'ol', 'li']:
        o = len(re.findall(r'<%s[ >]' % t, h)); c = len(re.findall(r'</%s>' % t, h))
        print('  %-8s %d/%d %s' % (t, o, c, 'OK' if o == c else '*** MISMATCH ***'))
