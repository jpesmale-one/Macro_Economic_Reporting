# -*- coding: utf-8 -*-
"""Assemble the 19-23 Oct edition.

Jeff, 2026-10-18: "Lets build our weekly report for October 19-23. Make sure to
update our macro economic indicator on the last week's news result. Scan all
indicators and see if there are stalled data and update them accordingly."

LOGIC FROZEN (LD-167): no scoring rule, band, weight or report rule changed in
this edition. Everything below is DATA and the two DEFECT fixes the freeze
explicitly allows (F-159, and the CB Consumer Confidence read).
"""
import io

REPO = 'c:/Users/jpesm/OneDrive/Documents/GitHub/Macro_Economic_Reporting/'
SP = ('C:/Users/jpesm/AppData/Local/Temp/claude/'
      'c--Users-jpesm-OneDrive-Documents-GitHub/'
      '16c8f514-dc2c-4587-b6a0-4fa0ff0b7ba8/scratchpad/')

prev = io.open(REPO + 'reports/2026/Q4/2026-10-11_weekly.html',
               encoding='utf-8').read()
body = io.open(SP + 'body.html', encoding='utf-8').read()
sec4 = io.open(SP + 'indicators.html', encoding='utf-8').read().strip()
head = prev[:prev.find('<div class="wrap">')]

HEADER = u'''<div class="wrap">

<header>
  <p class="eyebrow">Macro Economic Reporting &middot; Weekly &middot; Sunday 18 Oct 2026</p>
  <h1>Week of 19&ndash;23 Oct</h1>
  <p class="dek">Selection for the 19&ndash;23 Oct cycle, built on the biggest
  data refresh this project has run: <strong>R-45 found FIFTEEN stale rows</strong>
  and three more were caught only by the capture. <strong>EUR collapses
  +4.00 &rarr; &minus;1.00</strong> on a trade surplus turning to deficit, and
  <strong>GBP strengthens to +7.50</strong> on a rate-hike consensus. Thirteen
  scheduled rows, <strong>five of them GBP</strong>.</p>
  <div class="chips">
    <span class="chip">4 pairs</span>
    <span class="chip">GBPAUD LONG +9.17</span>
    <span class="chip">18 rows refreshed</span>
    <span class="chip q">12 of 13 rows scorable</span>
    <span class="chip q">logic frozen (LD-167)</span>
  </div>
</header>

<div class="note rev">
  <strong>&#9888; r2 &mdash; THIS PAGE WAS REBUILT: ITS BOARD HAD DISAGREED WITH
  ITS OWN EVIDENCE TABLE (F-161).</strong> Jeff asked why the link in the repo
  markdown pointed at a four-week-old report (F-160, fixed), and checking that
  surfaced this. The r1 page showed <strong>NAB Business Confidence scoring
  &minus;1 in &sect;4</strong> and <strong>AUD &minus;0.67 in &sect;1</strong>
  &mdash; and those cannot both be true. The board had been rendered BEFORE the
  final <code>sync_score_model</code> pass corrected three verdicts, so the
  document contradicted itself.
  <br><br>
  <strong>Corrected: AUD &minus;0.67 &rarr; &minus;1.67, CAD +6.40 &rarr;
  +7.40, NZD +1.40 &rarr; +1.20.</strong> <strong>The SET IS THE SAME FOUR
  PAIRS</strong> &mdash; only the gaps and their order move, with GBPAUD now
  top at <strong>+9.17</strong> instead of GBPCHF at +8.70.
  <br><br>
  <strong>Every existing guard passed on the broken page</strong>, which is the
  real finding: F-134 compares the page to the FACT TABLES (which were right),
  R-44 checks the RULES (right), R-48 checks <code>prev</code> (right).
  <strong>Nothing compared the board to the rows printed beside it.</strong>
  <code>R-49</code> is now build check 9b and does exactly that.
</div>

<div class="note">
  <strong>LOGIC IS FROZEN THIS EDITION (LD-167).</strong> Jeff, after the
  retro: <em>&ldquo;we stick with our current logic on the report
  building.&rdquo;</em> Five scoring changes landed in 36 hours during
  12&ndash;16 Oct and the graded set shared only <strong>one</strong> pair with
  the one first published. <strong>Nothing in this edition changes a rule, a
  band or a weight</strong> &mdash; everything below is DATA, plus the two
  defect fixes the freeze explicitly allows.
</div>

<div class="note rev">
  <strong>&#9888; EIGHTEEN STALE ROWS, AND THE TWO CHECKS FOUND DIFFERENT
  ONES.</strong> R-45 sweeps the TE indicator page; R-37/R-40 compare against
  our own capture. <strong>Neither alone was sufficient.</strong>
  <br><br>
  <strong>R-45 found 15</strong>: USD industrial production, manufacturing
  production, retail sales and CPI; EUR industrial production, trade and CPI
  Final; GBP industrial production, manufacturing production and trade; JPY
  industrial production Final and machinery orders; AUD NAB confidence,
  employment and unemployment.
  <br><br>
  <strong>R-37 found three more that R-45 structurally CANNOT see</strong>
  &mdash; NZD Business NZ PMI (53.1&rarr;56.5), NZD card spending
  (0.2&rarr;0.9&#37;) and CAD building permits (&minus;17.3&rarr;8.8&#37;).
  All three sit in R-45&#39;s <em>NO PAGE</em> list: the slug does not resolve,
  so only the capture could find them. <strong>True coverage rose 42 &rarr; 60
  of 70 rows.</strong>
  <br><br>
  <strong>And every ref month was stale too.</strong> All 15 carried Jul/26 or
  Aug/26 against TE&#39;s Aug/26 or Sep/26 &mdash; and <code>ref_drift()</code>
  reported <strong>ZERO</strong> until watchers were added, because it only
  checks rows it is handed. That is F-152&#39;s blind spot on a new set of
  rows. A value-only sync would have left every one of them internally
  inconsistent: the September number wearing August&#39;s label.
</div>

<div class="note rev">
  <strong>&#9888; THE &ldquo;NEVER VERIFIED&rdquo; ROW HAS FINALLY BEEN
  READ.</strong> <strong>USD CB Consumer Confidence</strong> has carried
  <em>UNVERIFIED</em> in the dark-row ledger since it was created, because its
  TE slug resolves to <strong>University of Michigan sentiment &mdash; a
  different survey</strong>. We held <strong>89.4</strong>.
  <br><br>
  Read from the Conference Board release and <strong>confirmed by three
  independent sources before changing a scoring row</strong>: <strong>81.9 for
  September</strong>, down 6.7 from 88.6, against an 89.2 consensus &mdash; the
  lowest since 2014. The score is <strong>&minus;1 either way</strong>, so the
  board does not move, but <strong>the printed value was wrong by 7.5 points
  and two vintages</strong>.
  <br><br>
  <strong>F-143 now reads 10 dark rows current, ZERO unverifiable &mdash; the
  first time ever.</strong>
</div>

<div class="note">
  <strong>EUR IS THE WEEK&#39;S MOVER, AND IT IS THE TRADE ROW.</strong>
  +4.00 &rarr; <strong>&minus;1.00</strong>, a five-point swing that takes it
  from third to seventh. The cause is one cell: <strong>Balance of Trade
  &euro;14.2B &rarr; &euro;&minus;16.1B</strong>, a surplus becoming a deficit,
  on a category carrying <strong>weight 2</strong>. Industrial production also
  turned (&minus;1.1&#37; against a &minus;0.1&#37; forecast).
  <br><br>
  <strong>Inflation still pays EUR +1</strong> &mdash; 3.8&#37; is far above the
  2.2&#37; ceiling, which under LD-155 is hawkish and therefore currency-
  positive. <strong>So the euro is being marked down on activity while its
  inflation argues the other way</strong>, and that tension is worth watching
  rather than resolving.
</div>

<div class="note">
  <strong>GBP STRENGTHENS ON A RATE-HIKE CONSENSUS.</strong> +6.57 &rarr;
  <strong>+7.50</strong>. The capture now carries a BoE consensus of
  <strong>4&#37;</strong> against the standing 3.75&#37; &mdash; a hike expected
  &mdash; where last Sunday there was no consensus and the row read HOLD. Under
  LD-154 before-the-news that is <strong>+1</strong>, and it is the first time
  LD-166&#39;s path-only rate row has moved a currency between editions.
  <br><br>
  <strong>&#9888; AND GBP HAS FIVE OF THIRTEEN SCHEDULED ROWS</strong> &mdash;
  unemployment and claimant count Tuesday, <strong>CPI Wednesday</strong>, GfK
  and retail sales Friday. Two of four pairs are long GBP. <strong>A single
  currency carries nearly half the week&#39;s event risk on the leg we are most
  exposed to.</strong>
</div>

<div class="note rev">
  <strong>&#9888; CHF IS &times;3, WHICH IS EXACTLY WHAT COST THREE BEATEN LAST
  WEEK.</strong> <code>GBPCHF</code>, <code>CADCHF</code> and
  <code>NZDCHF</code> are all short CHF. Last week JPY was &times;3; on
  Wednesday 14 Oct JPY ranked <strong>#1 of eight</strong> and the set took
  <strong>three BEATEN in one session &mdash; 51&#37; of the week&#39;s entire
  adverse movement</strong>.
  <br><br>
  <strong>The selector is unchanged and will not be changed this edition</strong>
  (LD-167 defers the &times;2 cap to the 31 Oct review). But the risk is now a
  <em>measured</em> one, not a hypothetical: <strong>one currency moving against
  us can take three of the four pairs with it</strong>. CHF has no scheduled
  row at all this week except Tuesday&#39;s trade balance, so the move that
  would do it is one we cannot see coming from the calendar.
</div>

<div class="note">
  <strong>TWO DEFECT FIXES, BOTH ALLOWED UNDER THE FREEZE.</strong>
  <strong>F-159</strong>: R-40 reported EUR and GBP trade as <em>&ldquo;data
  the world has superseded&rdquo;</em> on the very build that had just
  refreshed them &mdash; because we store <code>EUR-16.1B</code> and TE renders
  <code>&euro;-16.1B</code>. The numbers were identical; the guard compares
  strings. It now treats an ISO code and its glyph as the same value, which is
  F-139&#39;s rule one axis over. <strong>Negative-tested</strong>: planting a
  wrong EUR value still fails it.
  <br><br>
  <strong>And one scoring correction</strong>: AUD unemployment held a previous
  of 4.5&#37; where the ABS revised August up to 4.7&#37;, so September reads
  <strong>FLAT rather than a rise</strong> &mdash; BAD became NEUTRAL. Verified
  on the TE page <em>and</em> in our capture, which carries TE&#39;s revision
  marker.
</div>
'''

full = head + HEADER + '\n' + body
k = full.find(u'<h2>\u00a75 Method and limits')
if k > 0:
    k = full.rfind('<section', 0, k)
    full = full[:k] + sec4 + '\n\n' + full[k:]
else:
    full += '\n' + sec4

full = full.rstrip() + u'''

<p class="sub" style="margin-top:28px">
  <strong>Macro Economic Reporting</strong> &middot; weekly selection for
  19&ndash;23 Oct 2026 &middot; built Sunday 18 Oct on the
  <span class="mono">2026-10-18_2238PHT</span> capture.
  Whitelist: <strong>78 rows</strong>, <strong>18 refreshed this build</strong>
  (15 by R-45 against the TE indicator page, 3 by R-37 against the capture).
  True coverage <strong>60 of 70</strong>, up from 42. Dark-row ledger:
  <strong>10 current, 0 unverifiable</strong>. Prices and ATR:
  <span class="mono">OANDA</span> daily bars read from TradingView (LD-5 as
  amended). All eight policy rates verified against Trading Economics (R-47).
  <strong>Logic frozen this edition (LD-167)</strong> &mdash; no rule, band or
  weight changed.
  <strong>Observations only &mdash; no entries, stops, targets or sizing
  (LD-4).</strong>
</p>

</div>
'''

io.open(SP + 'weekly_1923.html', 'w', encoding='utf-8',
        newline='\n').write(full)
print('wrote %d bytes' % len(full))
for t in ('section', 'table', 'div', 'tr', 'td', 'p'):
    a, b = full.count('<%s' % t), full.count('</%s' % t)
    print('  %-8s %3d/%3d %s' % (t, a, b, 'OK' if a == b else '*** BAD'))
print('  wrap closed :', full.rstrip().endswith('</div>'))
