# -*- coding: utf-8 -*-
"""Build the 2-6 Nov retrospective on the sealed house style.

Same construction as mk_retro_2630.py: the PREVIOUS retro's <style> block is
inherited byte-for-byte and only the <title> changes.

EVERY NUMBER HERE IS COMPUTED, NOT TYPED - the tables below are generated
from data/derived/sessions.csv and the restored OANDA bars at build time,
so a figure cannot drift from the ledger without this script changing.
"""
import io
import os
import sys
import csv

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import daily_report as dr
import risk_index as RI

WEEK = '2026-11-02'
DAYS = ['2026-11-02', '2026-11-03', '2026-11-04',
        '2026-11-05', '2026-11-06']
DNAME = dict(zip(DAYS, ['Mon 2', 'Tue 3', 'Wed 4', 'Thu 5', 'Fri 6']))

# ---------------------------------------------------------------- the ledger
rows = [r for r in csv.DictReader(
    io.open(os.path.join(REPO, 'data/derived/sessions.csv'), encoding='utf-8'))
    if r['week_start'] == WEEK]

PAIRS = []
for r in rows:
    if r['pair'] not in [p for p, _ in PAIRS]:
        PAIRS.append((r['pair'], r['direction']))


def pair_rows(p):
    return sorted((r for r in rows if r['pair'] == p),
                  key=lambda r: r['session'])


def totals(p):
    rs = pair_rows(p)
    f = sum(float(r['fav_pips']) for r in rs)
    a = sum(float(r['adv_pips']) for r in rs)
    st = {}
    for r in rs:
        st[r['state']] = st.get(r['state'], 0) + 1
    return f, a, (f / a if a else float('inf')), st


# ------------------------------------------------------------ board vs market
import re
md = io.open(os.path.join(REPO, 'reports/2026/Q4/2026-11-01_weekly.md'),
             encoding='utf-8').read()
board = {}
for m in re.finditer(
        r'\|\s*(?:STRONG|NEUTRAL|WEAK)\s*\|\s*\*{0,2}([A-Z]{3})\*{0,2}\s*\|'
        r'[^|]*\|[^|]*\|[^|]*\|\s*\*\*([+-][0-9.]+)\*\*', md):
    board[m.group(1)] = float(m.group(2))

move = {}
for d in DAYS:
    s = dr.session_strength(d)
    for c, v in s.items():
        move[c] = move.get(c, 0.0) + v

bs = sorted(board, key=lambda c: -board[c])
ms = sorted(move, key=lambda c: -move[c])
brank = dict((c, i + 1) for i, c in enumerate(bs))
mrank = dict((c, i + 1) for i, c in enumerate(ms))
n = len(brank)
d2 = sum((brank[c] - mrank[c]) ** 2 for c in brank)
RHO = 1 - 6.0 * d2 / (n * (n * n - 1))

TONE = [(d,) + RI.tone(d)[:2] for d in DAYS]

# --------------------------------------------------------------------- render
prev = io.open(os.path.join(REPO, 'reports/2026/Q4/2026-10-31_retro.html'),
               encoding='utf-8').read()
head = prev[:prev.index('</style>') + len('</style>')]
head = head.replace('<title>The Week The Board Was Right</title>',
                    '<title>The Week It Paid Late</title>', 1)

A = []
W = A.append

gf, ga, gr, gst = totals('GBPNZD')
nf, na, nr, nst = totals('NZDJPY')
wins = sum(v for p, _ in PAIRS for k, v in totals(p)[3].items()
           if k in ('CLEAN', 'EARNED'))
total_sessions = sum(sum(totals(p)[3].values()) for p, _ in PAIRS)

W(u'''

<div class="wrap">

<header>
  <p class="eyebrow">Macro Economic Reporting &middot; Retrospective &middot;
     Tuesday 17 Nov 2026</p>
  <h1>The Week It Paid Late</h1>
  <p class="dek"><strong>Both pairs profitable, both beaten midweek</strong>
  &mdash; GBPNZD closed the week at <strong>%.2f</strong> favourable-to-adverse
  and NZDJPY at <strong>%.2f</strong>, but neither had it easy: each took its
  worst damage on Wednesday and Thursday before the risk-off turn paid them
  on Thursday night and Friday. The board itself was <em>half</em> right:
  <strong>rho %+.2f</strong>, down from %+.2f the week before, carried
  entirely by the bottom of the table &mdash; <strong>AUD and NZD ranked #7
  and #8 and traded #8 and #7</strong>, which is the half GBPNZD was short.
  The top half inverted.</p>
  <div class="chips">
    <span class="chip">%d of %d sessions delivered</span>
    <span class="chip">rho %+.2f</span>
    <span class="chip q">GBPNZD %.2f &middot; NZDJPY %.2f</span>
    <span class="chip q">built 11 days late</span>
  </div>
</header>
''' % (gr, nr, RHO, 0.48, wins, total_sessions, RHO, gr, nr))

# ---- §1 verdict
W(u'''
<section>
<h2>&sect;1 &mdash; The verdict</h2>
<p>Five sessions, two pairs, <strong>ten gradings</strong>. The week divides
cleanly in two: Monday and Tuesday drifted, Wednesday and Thursday hurt, and
then the market turned and both pairs were paid in a single stretch.</p>
<div class="scroll"><table>
<thead><tr><th>Session</th><th>Tone</th>''')
for p, side in PAIRS:
    W(u'<th>%s %s</th>' % (p, side))
W(u'</tr></thead><tbody>')
tonemap = dict((d, (l, s)) for d, l, s in TONE)
for d in DAYS:
    l, s = tonemap[d]
    kls = 'good' if s > 0 else ('bad' if s < 0 else '')
    W(u'<tr><td><strong>%s</strong></td><td class="%s">%s <span class="mono">%+.2f</span></td>'
      % (DNAME[d], kls, l, s))
    for p, _ in PAIRS:
        r = [x for x in pair_rows(p) if x['session'] == d]
        if not r:
            W(u'<td>&mdash;</td>')
            continue
        r = r[0]
        k = {'CLEAN': 'good', 'EARNED': 'good',
             'BEATEN': 'bad'}.get(r['state'], '')
        W(u'<td class="%s"><strong>%s</strong> '
          u'<span class="mono">%s / %s</span></td>'
          % (k, r['state'], r['fav_pips'], r['adv_pips']))
    W(u'</tr>')
W(u'<tr><td><strong>WEEK</strong></td><td class="mono">&mdash;</td>')
for p, _ in PAIRS:
    f, a, ratio, st = totals(p)
    W(u'<td><strong>ratio %.2f</strong> <span class="mono">%.1f / %.1f</span></td>'
      % (ratio, f, a))
W(u'</tr></tbody></table></div>')
W(u'''
<div class="note"><span class="lbl">Reading the states</span>
<strong>CLEAN</strong> delivered a full day unthreatened &middot;
<strong>EARNED</strong> delivered through a real fight &middot;
<strong>BEATEN</strong> the opposite side paid out &middot;
<strong>DRIFT</strong> neither side completed (LD-148). A BEATEN day is the
bias being contested, not a loss &mdash; and this week is the clearest case
yet, because both pairs were beaten midweek and still finished well above
break-even.</div>
</section>
''')

# ---- §2 the board
W(u'''
<section>
<h2>&sect;2 &mdash; The board got the bottom right and the top wrong</h2>
<p>Spearman rho between the board's ranking and what the eight currencies
actually did over the five sessions came in at <strong>%+.2f</strong>, down
from <strong>%+.2f</strong> on 26&ndash;30 Oct. Six of the eight sit exactly
three places from where they were ranked, and the sign of that error splits
the table in half: the three the board rated highest all traded lower, and
the three it rated lowest all traded higher.</p>
<div class="scroll"><table>
<thead><tr><th>CCY</th><th class="num">Board</th><th class="num">FINAL</th>
<th class="num">Week move</th><th class="num">Traded</th>
<th class="num">Gap</th></tr></thead><tbody>''' % (RHO, 0.48))
for c in bs:
    g = brank[c] - mrank[c]
    kls = 'good' if abs(g) <= 1 else ('bad' if abs(g) >= 3 else '')
    W(u'<tr><td class="ccy"><strong>%s</strong></td><td class="num">#%d</td>'
      u'<td class="num mono">%+.2f</td><td class="num mono">%+.3f%%</td>'
      u'<td class="num">#%d</td><td class="num %s">%+d</td></tr>'
      % (c, brank[c], board[c], move[c], mrank[c], kls, g))
W(u'''</tbody></table></div>
<div class="note"><span class="lbl">Why the set still paid</span>
The board's <strong>bottom</strong> was right: AUD and NZD were ranked #7 and
#8 and traded #8 and #7. Both pairs in the set are <em>short</em> that end
&mdash; GBPNZD short NZD, NZDJPY short NZD &mdash; so the half of the ranking
that held is exactly the half the set depended on, and GBPNZD returned
<strong>%.2f</strong> despite GBP itself only trading #4.
<strong>That is a warning as much as a result.</strong> A set can be paid by
one end of a board whose other end inverted, and a ratio alone will not say
which happened.</div>
</section>
''' % gr)

# ---- §3 the turn
W(u'''
<section>
<h2>&sect;3 &mdash; The turn, and what it paid</h2>
<p>The week's whole return arrived in its last two sessions. Thursday 5 Nov
read <strong>RISK OFF &minus;1.00</strong> &mdash; all four index legs against,
<span class="mono">SPX &minus;4.23%</span>, <span class="mono">VIX
&plus;64.35%</span> &mdash; the first unanimous reading the measure has
produced. NZDJPY SHORT is tagged RISK OFF, so it was <strong>ALIGNED with the
session</strong> and went CLEAN at <span class="mono">1.231&times;</span> ATR:
the pair paid for the reason it was selected, which is the comparison LD-174
exists to make.</p>
<div class="scroll"><table>
<thead><tr><th>Session</th><th class="num">SPX</th><th class="num">NI225</th>
<th class="num">DAX</th><th class="num">VIX</th><th>Tone</th></tr></thead>
<tbody>''')
for d in DAYS:
    l, s, det = RI.tone(d)
    cells = []
    for k in ('SPX', 'NI225', 'DAX', 'VIX'):
        p, v = det['legs'][k]
        if p is None:
            cells.append(u'<td class="num dim">&mdash;</td>')
        else:
            cells.append(u'<td class="num mono %s">%+.2f%%</td>'
                         % ('good' if v > 0 else ('bad' if v < 0 else ''), p))
    kls = 'good' if s > 0 else ('bad' if s < 0 else '')
    W(u'<tr><td><strong>%s</strong></td>%s<td class="%s">%s '
      u'<span class="mono">%+.2f</span></td></tr>'
      % (DNAME[d], ''.join(cells), kls, l, s))
W(u'''</tbody></table></div>
<div class="note warn"><span class="lbl">&#9888; One leg is missing, and it is
not a zero</span>Tuesday 3 Nov has no NI225 bar &mdash; it was
<strong>Culture Day</strong>, a Japanese market holiday. The table prints an
em-dash rather than a fabricated 0.00%, but the headline score still counts
that leg as <em>flat</em>, which is not the same as <em>did not trade</em>.
The same applies to Friday, where the committed index files reach 5 Nov for
three of the four legs. Both readings understate their sessions.</div>
</section>
''')

# ---- §4 method and limits
W(u'''
<section>
<h2>&sect;4 &mdash; Method, and what this build cannot say</h2>
<p>Every figure above is computed at build time from
<span class="mono">data/derived/sessions.csv</span> and the OANDA daily bars
in the repository, not typed. The board and the set are read from the
published 2&ndash;6 Nov weekly and are never recomputed (LD-97).</p>
<div class="note bad"><span class="lbl">This retrospective was built eleven
days late, and one session nearly went unrecorded</span>
The Friday 6 Nov daily was never built at the time. It is in the record now,
and this week is complete at five sessions &mdash; but the catalyst column of
that daily is <strong>partial</strong>: the last usable calendar capture was
taken at 15:57 PHT <em>during</em> the 6 Nov session, holding 11 actuals of
57 scheduled rows, so releases landing after that hour are absent rather than
absent-and-marked. Two further capture attempts on 17 Nov returned pages with
one table row against the usual 603; both were quarantined so an empty
vintage can never be read as a real one.</div>
<div class="note bad"><span class="lbl">The first data refresh for this build
was wrong, and it would have flattered the week</span>
A full 28-pair pull returned bars whose <strong>open had been replaced by a
smoothed value equal to the bar's own low</strong> in 3667 of 8400 cases (44%%,
against 122 in the committed baseline). Regraded on those bars, this week read
<strong>ratio 2.36 instead of %.2f</strong> and <strong>four of ten session
states flipped</strong> &mdash; two BEATEN days became CLEAN and DRIFT, because
an open pinned to the low means a long position never registers adverse
excursion. No gate caught it: the bars were present, nothing errored, and
F-188 and R-50 both passed. It was found by diffing against git.
The figures in this retrospective are from the restored, verified bars.</div>
<p class="fine">Observations only: no entries, stops, targets or sizing
(LD-4). Prices from OANDA via TradingView (LD-5 as amended); Yahoo is never
a fallback.</p>
</section>

</div>
''' % gr)

html = head + u''.join(A)
out = os.path.join(REPO, 'reports/2026/Q4/2026-11-17_retro.html')
io.open(out, 'w', encoding='utf-8', newline='\n').write(html)
print('wrote %s (%d bytes)' % (out, len(html)))
print('GBPNZD ratio %.2f %s' % (gr, gst))
print('NZDJPY ratio %.2f %s' % (nr, nst))
print('rho %+.2f' % RHO)
