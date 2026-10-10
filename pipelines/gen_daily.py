# -*- coding: utf-8 -*-
"""RENDER THE DAILY REPORT AS A PAGE (LD-156).

Jeff, 2026-10-11: "then where can I see it if not in the web report?"

The daily was built as console output, which is no use to the person it is
written for. This renders the same numbers as a page, styled like the weekly
and the retrospective so the three read as one publication.

WHAT IT DOES NOT DO, deliberately: it never recomputes the board or the set.
Both are read from the PUBLISHED weekly .md by daily_report.load_edition(),
because a daily that silently re-ranks is replacing the bias rather than
reporting on it - that bug is recorded in daily_report.py and this renderer
inherits the fix rather than repeating the mistake.

    python pipelines/gen_daily.py              # yesterday
    python pipelines/gen_daily.py 2026-10-09   # a named session
"""
import io
import os
import sys
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import daily_report as dr
import atr_grade as ag

SP = ('C:/Users/jpesm/AppData/Local/Temp/claude/'
      'c--Users-jpesm-OneDrive-Documents-GitHub/'
      '16c8f514-dc2c-4587-b6a0-4fa0ff0b7ba8/scratchpad/')

HEAD = u'''<title>%(title)s</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
:root{
  --paper:#0E1116; --card:#151A21; --ink:#E8EAED; --ink-2:#A8B0BA;
  --ink-3:#6B7480; --rule:#242B34; --accent:#5FB98A;
  --bull:#4ADE80; --bear:#F87171; --warn:#FBBF24;
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--paper); color:var(--ink);
  font:16px/1.65 "IBM Plex Sans",system-ui,sans-serif;
}
.wrap{max-width:860px; margin:0 auto; padding-block:40px; padding-left:16px; padding-right:16px}
h1{font:600 34px/1.2 Newsreader,Georgia,serif; margin:6px 0 10px; text-wrap:balance}
h2{font:600 21px/1.3 Newsreader,Georgia,serif; margin:34px 0 12px;
   padding-bottom:7px; border-bottom:1px solid var(--rule)}
.eyebrow{font:500 11px/1 "IBM Plex Mono",monospace; letter-spacing:.14em;
  text-transform:uppercase; color:var(--accent); margin:0}
.dek{color:var(--ink-2); max-width:62ch; margin:0 0 18px}
table{width:100%%; border-collapse:collapse; font-size:14px;
  font-variant-numeric:tabular-nums; margin:10px 0}
th{font:600 11px/1 "IBM Plex Mono",monospace; letter-spacing:.08em;
  text-transform:uppercase; color:var(--ink-3); text-align:left;
  padding:8px 10px; border-bottom:1px solid var(--rule)}
td{padding:9px 10px; border-bottom:1px solid var(--rule); vertical-align:top}
.num{text-align:right; font-family:"IBM Plex Mono",monospace}
.mono{font-family:"IBM Plex Mono",monospace; font-size:13px}
.pos{color:var(--bull)} .neg{color:var(--bear)} .zero{color:var(--ink-3)}
.ccy{font-weight:600; font-family:"IBM Plex Mono",monospace}
.note{background:var(--card); border-left:3px solid var(--accent);
  padding:15px 18px; margin:18px 0; border-radius:0 5px 5px 0; font-size:14.5px}
.note.warn{border-left-color:var(--warn)}
.note.bad{border-left-color:var(--bear)}
.lbl{display:block; font:600 10px/1 "IBM Plex Mono",monospace;
  letter-spacing:.12em; text-transform:uppercase; color:var(--ink-3);
  margin-bottom:7px}
.scroll{overflow-x:auto}
a.src{display:inline-block; margin-top:9px; color:var(--accent);
  font:400 12px/1.4 "IBM Plex Mono",monospace; word-break:break-all}
a.src:hover{text-decoration:underline}
footer{margin-top:36px; padding-top:18px; border-top:1px solid var(--rule);
  font-size:12.5px; color:var(--ink-3)}
@media(max-width:480px){ h1{font-size:27px} .wrap{padding-block:26px} }
</style>
'''


def cls(v):
    return 'pos' if v > 0.02 else ('neg' if v < -0.02 else 'zero')


def esc(t):
    return (str(t).replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;'))


def build(day):
    s = dr.session_strength(day)
    if not s:
        return None
    ev = dr.catalysts(day)
    board, picks = dr.load_edition()
    order = sorted(s, key=lambda c: -s[c])
    brank = sorted(board, key=lambda c: -board[c]) if board else []
    d = dt.datetime.strptime(day, '%Y-%m-%d').date()

    o = []
    A = o.append
    A(HEAD % {'title': 'Daily %s' % d.strftime('%-d %b') if os.name != 'nt'
              else 'Daily %s' % d.strftime('%d %b').lstrip('0')})
    A('<div class="wrap">')
    A('<p class="eyebrow">Macro Economic Reporting &middot; Daily &middot; '
      'session %s</p>' % d.strftime('%A %d %B %Y'))
    A('<h1>What moved, and did it confirm us</h1>')

    # the one-line verdict: how far the session ran from the board
    if board:
        gaps = [abs((brank.index(c) + 1) - (order.index(c) + 1))
                for c in order if c in brank]
        mean = sum(gaps) / float(len(gaps)) if gaps else 0
        worst = max(gaps) if gaps else 0
        A('<p class="dek">The session ranked the eight currencies an average '
          'of <strong>%.1f places</strong> from where the weekly board put '
          'them, the widest by <strong>%d</strong>. A reading near zero is a '
          'session that confirmed the bias; a wide one is the board and the '
          'market disagreeing.</p>' % (mean, worst))

    A('<h2>The session, ranked</h2>')
    A('<div class="scroll"><table>')
    A('<thead><tr><th>CCY</th><th class="num">Move</th><th class="num">Session</th>'
      '<th class="num">Board</th><th>Catalyst</th></tr></thead><tbody>')
    for i, c in enumerate(order, 1):
        br = (brank.index(c) + 1) if board and c in brank else None
        why = dr.explain(c, s[c], day=day)
        wc = ''
        if 'UNEXPLAINED' in why:
            wc = ' class="neg"'
        elif 'AGAINST' in why:
            wc = ' class="neg"'
        elif 'CONSISTENT' in why:
            wc = ' class="pos"'
        A('<tr><td class="ccy">%s</td>'
          '<td class="num %s">%+.3f%%</td>'
          '<td class="num">#%d</td><td class="num">%s</td>'
          '<td%s>%s</td></tr>'
          % (c, cls(s[c]), s[c], i, ('#%d' % br) if br else '&mdash;',
             wc, esc(why)))
    A('</tbody></table></div>')

    # unexplained movers - the honest half
    big = [c for c in order
           if abs(s[c]) >= 0.25 and 'UNEXPLAINED' in
           dr.explain(c, s[c], day=day)]
    if big:
        A('<div class="note bad"><span class="lbl">&#9888; MOVED WITH '
          'NOTHING ON THE CALENDAR</span>')
        A('<strong>%s</strong> moved materially and <strong>the whole '
          'captured calendar &mdash; not just our whitelist &mdash; carries '
          'nothing for it that day.</strong> '
          '<strong>This is reported, not explained.</strong> Financial '
          'commentary always finds a reason, and that is exactly what makes '
          'it unreliable. The honest reading is that the cause sits outside '
          'any calendar: positioning, yields, or cross-asset flow.</div>'
          % ', '.join('%s %+.3f%%' % (c, s[c]) for c in big))

    # TIER 5 - what the market said, for the currencies the calendar cannot
    # explain. ATTRIBUTED, never stated as our own finding (LD-158).
    import market_note as mn
    mnotes = mn.notes(day)

    # LD-161 - the risk regime, if recorded. A MEASURED INDEX, not commentary,
    # so it sits above the quoted notes rather than among them.
    reg = mn.regime(day)
    if reg:
        A('<div class="note warn"><span class="lbl">RISK REGIME &middot; %s'
          '</span><strong>%s</strong><br>'
          'Jeff, 3 Oct: <em>&ldquo;for the whole week we are at Fear Index. '
          'meaning Safe Haven are the ones people were looking at&rdquo;</em> '
          '&mdash; that week the three havens rose and all three commodity '
          'currencies fell.%s</div>'
          % (esc(reg['source']), esc(reg['note']),
             ('<br><a href="%s" target="_blank" rel="noopener" class="src">'
              '%s</a>' % (esc(reg.get('url')), esc(reg.get('url'))))
             if reg.get('url') else ''))

    mnotes = dict((k, v) for k, v in mnotes.items() if k != '_REGIME')
    if mnotes:
        A('<h2>What the market said</h2>')
        A('<div class="note warn"><span class="lbl">REPORTED, NOT MEASURED'
          '</span>'
          'Everything in this section is <strong>someone else&rsquo;s '
          'explanation of a price move</strong>, quoted with its source. '
          'Commentary is written after the fact to explain a chart: useful '
          'for naming what a calendar cannot see &mdash; yields, positioning, '
          'politics &mdash; and <strong>worthless as evidence of '
          'causation</strong>. It never reaches the board.</div>')
        # *** NOT `d` - that is the session date four lines below, and
        # shadowing it crashed the footer with 'NoneType has no strftime'.
        for c in order:
            # LD-160 - several sources per currency, each with its own link.
            # Disagreement between commentaries is SHOWN, never resolved: we
            # are not placed to arbitrate between two opinions about why a
            # price moved.
            for nd in mn.note_for(day, c):
                u = nd.get('url')
                A('<div class="note"><span class="lbl">%s &middot; %s</span>%s'
                  '%s</div>'
                  % (c, esc(nd['source']), esc(nd['note']),
                     ('<br><a href="%s" target="_blank" rel="noopener" '
                      'class="src">%s</a>' % (esc(u), esc(u))) if u else ''))

    if board:
        A('<h2>Against the weekly board</h2>')
        gaps = sorted(((abs((brank.index(c) + 1) - (order.index(c) + 1)), c)
                       for c in order if c in brank), reverse=True)[:3]
        A('<div class="scroll"><table>')
        A('<thead><tr><th>CCY</th><th class="num">Board</th>'
          '<th class="num">Session</th><th class="num">Gap</th>'
          '<th>Read</th></tr></thead><tbody>')
        for g, c in gaps:
            bi, si = brank.index(c) + 1, order.index(c) + 1
            read = ('ranked high, traded low' if si > bi
                    else 'ranked low, traded high')
            A('<tr><td class="ccy">%s</td><td class="num">#%d</td>'
              '<td class="num">#%d</td><td class="num %s">%d</td>'
              '<td>%s</td></tr>'
              % (c, bi, si, 'neg' if g >= 4 else '', g, read))
        A('</tbody></table></div>')

    if picks:
        A('<h2>The set, this session</h2>')
        A('<div class="scroll"><table>')
        A('<thead><tr><th>Pair</th><th>Side</th><th class="num">Favourable</th>'
          '<th class="num">Adverse</th><th>State</th></tr></thead><tbody>')
        for pair, side in picks:
            b = dr.bars(pair)
            if not b:
                continue
            row = [x for x in b if x[0] == day]
            if not row:
                continue
            _, op, hi, lo, cl = row[0]
            f = ag.pip_factor(pair)
            prior = [x for x in b if x[0] < day]
            atr = (ag.atr([(h2, l2, c2) for _, o2, h2, l2, c2 in prior], 14, f)
                   if len(prior) > 15 else None)
            fav, adv, _fr, _h = ag.grade_day(side, op, hi, lo, f, atr or 1)
            k = ag.classify(fav, adv, atr) if atr else '&mdash;'
            kc = {'CLEAN': 'pos', 'EARNED': 'pos',
                  'BEATEN': 'neg', 'DRIFT': ''}.get(k, '')
            A('<tr><td class="ccy">%s</td><td>%s</td>'
              '<td class="num">%.1f</td><td class="num">%.1f</td>'
              '<td class="%s"><strong>%s</strong></td></tr>'
              % (pair, side, fav, adv, kc, k))
        A('</tbody></table></div>')
        A('<div class="note"><span class="lbl">WHAT THESE STATES MEAN</span>'
          '<strong>CLEAN</strong> delivered a full day without being '
          'threatened &middot; <strong>EARNED</strong> delivered through a '
          'real fight &middot; <strong>BEATEN</strong> the opposite side '
          'paid out &middot; <strong>DRIFT</strong> neither side completed '
          '(LD-148). <strong>BEATEN is not a loss</strong> &mdash; it is a '
          'sign the bias is being contested.</div>')

    A('<footer><p><strong>Macro Economic Reporting</strong> &middot; daily '
      'for the %s session &middot; built %s. Currency strength is each '
      'currency against the other seven, open to close, on OANDA daily bars '
      'from TradingView (LD-5). The board and the set are read from the '
      'published weekly and are <strong>never recomputed here</strong> '
      '&mdash; the weekly is the decision (LD-97). '
      '<strong>Observations only: no entries, stops, targets or sizing '
      '(LD-4).</strong></p></footer>'
      % (d.strftime('%A %d %B'), dt.date.today().strftime('%d %B %Y')))
    A('</div>')
    return '\n'.join(o)


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    day = a[0] if a else (dt.date.today() - dt.timedelta(days=1)).isoformat()
    wd = dt.datetime.strptime(day, '%Y-%m-%d').date().weekday()
    if wd >= 5:
        print('%s is a weekend session - no daily' % day)
        sys.exit(0)
    if wd == 0:
        print('%s is a MONDAY - the weekly is the baseline, no daily '
              '(LD-156)' % day)
        sys.exit(0)
    html = build(day)
    if not html:
        print('no bars for %s' % day)
        sys.exit(1)
    out = SP + 'daily_%s.html' % day
    io.open(out, 'w', encoding='utf-8', newline='\n').write(html)
    print('wrote %s (%d bytes)' % (out, len(html)))
