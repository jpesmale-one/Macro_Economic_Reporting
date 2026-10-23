# -*- coding: utf-8 -*-
"""Build the 19-23 Oct retrospective on the sealed house style."""
import io

REPO = 'c:/Users/jpesm/OneDrive/Documents/GitHub/Macro_Economic_Reporting/'
SP = ('C:/Users/jpesm/AppData/Local/Temp/claude/'
      'c--Users-jpesm-OneDrive-Documents-GitHub/'
      '16c8f514-dc2c-4587-b6a0-4fa0ff0b7ba8/scratchpad/')

prev = io.open(REPO + 'reports/2026/Q4/2026-10-17_retro.html',
               encoding='utf-8').read()
head = prev[:prev.index('</style>') + len('</style>')]
head = head.replace('<title>The Week The Board Was Right</title>',
                    '<title>The Week The Hedge Paid</title>', 1)

BODY = u'''

<div class="wrap">

<header>
  <p class="eyebrow">Macro Economic Reporting &middot; Retrospective &middot; Saturday 24 Oct 2026</p>
  <h1>The Week The Hedge Paid</h1>
  <p class="dek"><strong>2 WIN, 2 CONTESTED, set ratio 1.14</strong> &mdash; a
  clear step down from last week&#39;s clean sweep. But the headline result is
  the opposite of what the week felt like: <strong>the &times;3 CHF
  concentration I warned about twice returned 1.45, a WIN</strong>, while the
  one diversified pair returned <strong>0.84</strong>. And rho fell to
  <strong>+0.17</strong> &mdash; destroyed almost single-handedly by one
  currency.</p>
  <div class="chips">
    <span class="chip">2 WIN / 2 CONTESTED / 0 LOSS</span>
    <span class="chip">rho +0.17</span>
    <span class="chip q">ratio 1.14</span>
    <span class="chip q">8-week mean +0.02</span>
  </div>
</header>

<section>
<h2>&sect;1 &mdash; The verdict</h2>

<div class="scroll">
<table>
<thead><tr><th>PAIR</th><th class="num">ATR</th><th class="num">&Sigma; fav</th>
<th class="num">&Sigma; adv</th><th class="num">ratio</th><th>VERDICT</th>
<th>Mon&ndash;Fri</th></tr></thead>
<tbody>
<tr><td class="ccy">CADCHF</td><td class="num">33</td><td class="num pos">98.7</td><td class="num">63.6</td><td class="num pos">1.55</td><td class="pos"><strong>WIN</strong></td><td class="mono s">CLEAN DRIFT DRIFT <span class="neg">BEATEN</span> CLEAN</td></tr>
<tr><td class="ccy">NZDCHF</td><td class="num">28</td><td class="num pos">105.6</td><td class="num">69.9</td><td class="num pos">1.51</td><td class="pos"><strong>WIN</strong></td><td class="mono s">CLEAN CLEAN DRIFT <span class="neg">BEATEN</span> CLEAN</td></tr>
<tr><td class="ccy">GBPCHF</td><td class="num">60</td><td class="num">158.8</td><td class="num">116.4</td><td class="num">1.36</td><td><strong>CONTESTED</strong></td><td class="mono s">DRIFT CLEAN DRIFT <span class="neg">BEATEN</span> DRIFT</td></tr>
<tr><td class="ccy">GBPAUD</td><td class="num">109</td><td class="num">220.2</td><td class="num neg">262.2</td><td class="num neg">0.84</td><td><strong>CONTESTED</strong></td><td class="mono s">DRIFT DRIFT <span class="neg">BEATEN</span> DRIFT <span class="neg">BEATEN</span></td></tr>
<tr><td colspan="2"><strong>SET TOTAL</strong></td><td class="num"><strong>583.3</strong></td><td class="num"><strong>512.1</strong></td><td class="num"><strong>1.14</strong></td><td><strong>CONTESTED</strong></td><td class="s">no pair lost; none cleared 1.40 but two</td></tr>
</tbody>
</table>
</div>

<div class="note">
  <strong>Nothing lost, and nothing ran away.</strong> Last week every pair
  cleared the band with room (1.57&ndash;1.70). This week the spread is
  0.84&ndash;1.55 and the set total sits in the middle of the CONTESTED zone.
  <strong>GBPCHF at 1.36 missed WIN by 0.04</strong> &mdash; a single
  mid-sized session either way would have flipped it.
</div>
</section>

<section>
<h2>&sect;2 &mdash; Where the week turned</h2>

<div class="scroll">
<table>
<thead><tr><th>SESSION</th><th class="num">fav</th><th class="num">adv</th>
<th class="num">ratio</th><th>the set, that day</th></tr></thead>
<tbody>
<tr><td class="mono">Mon 19</td><td class="num">124.9</td><td class="num">79.5</td><td class="num pos">1.57</td><td class="s">two CLEAN</td></tr>
<tr><td class="mono">Tue 20</td><td class="num pos">183.9</td><td class="num">23.5</td><td class="num pos">7.83</td><td class="s"><strong>the best session on record</strong></td></tr>
<tr><td class="mono">Wed 21</td><td class="num">58.2</td><td class="num neg">101.5</td><td class="num neg">0.57</td><td class="s">one BEATEN</td></tr>
<tr><td class="mono">Thu 22</td><td class="num">82.4</td><td class="num neg">161.4</td><td class="num neg">0.51</td><td class="s"><span class="neg">three BEATEN</span></td></tr>
<tr><td class="mono">Fri 23</td><td class="num">133.9</td><td class="num">146.2</td><td class="num">0.92</td><td class="s">two CLEAN, one BEATEN</td></tr>
</tbody>
</table>
</div>

<div class="note">
  <strong>Two days made the week and three days gave it back.</strong> Monday
  and Tuesday banked a 2.0 ratio between them; the last three sessions ran
  0.57, 0.51 and 0.92. <strong>Remove Thursday alone and the week reads
  1.43 &mdash; a WIN.</strong> That is the second consecutive retro where a
  single session decides the verdict, which says more about a four-pair set
  than about the method.
</div>
</section>

<section>
<h2>&sect;3 &mdash; The concentration paid, and I was wrong about it</h2>

<div class="note fail">
  <strong>&#9888; I WARNED ABOUT THE &times;3 CHF CONCENTRATION TWICE AND IT
  OUTPERFORMED.</strong>
  <br><br>
  <table style="margin:10px 0">
  <tr><td>the <strong>three</strong> CHF shorts</td><td class="num">363.1</td><td class="num">249.9</td><td class="num pos"><strong>1.45</strong></td><td class="s">WIN band</td></tr>
  <tr><td>the <strong>one</strong> non-CHF pair</td><td class="num">220.2</td><td class="num neg">262.2</td><td class="num neg"><strong>0.84</strong></td><td class="s">below 1.00</td></tr>
  </table>
  <strong>The diversified leg was the worst performer in the set.</strong>
  GBPAUD took two BEATEN &mdash; more than any CHF pair &mdash; and finished
  the only pair with more adverse than favourable movement.
  <br><br>
  <strong>This does not make the warning wrong.</strong> Thursday was exactly
  the predicted failure: CHF rose against all four counterparts and took three
  BEATEN in one session, 32&#37; of the week&#39;s adverse in a single day. The
  risk was real and it fired. <strong>It was simply outweighed by four
  sessions where the same concentration paid three times over</strong> &mdash;
  the CHF leg ran 4.02, 9.19, 3.01 and 1.85 on the other four days.
  <br><br>
  <strong>What this actually argues</strong> is that &times;3 is a
  <em>variance</em> decision, not a <em>quality</em> one. It makes good weeks
  better and bad days worse. Two weeks of evidence now point in opposite
  directions &mdash; 14 Oct cost three BEATEN inside a winning week, 22 Oct
  cost three BEATEN inside a CONTESTED one &mdash; and neither settles it.
</div>
</section>

<section>
<h2>&sect;4 &mdash; One currency destroyed rho</h2>

<div class="scroll">
<table>
<thead><tr><th>CCY</th><th class="num">board</th><th class="num">Mon</th>
<th class="num">Tue</th><th class="num">Wed</th><th class="num">Thu</th>
<th class="num">Fri</th><th class="num">mean</th><th class="num">drift</th></tr></thead>
<tbody>
<tr><td class="ccy">GBP</td><td class="num">1</td><td class="num">6</td><td class="num pos">1</td><td class="num">3</td><td class="num">4</td><td class="num neg">7</td><td class="num">4.2</td><td class="num neg">+3.2</td></tr>
<tr><td class="ccy">CAD</td><td class="num">2</td><td class="num">4</td><td class="num">4</td><td class="num">4</td><td class="num">3</td><td class="num">3</td><td class="num">3.6</td><td class="num">+1.6</td></tr>
<tr><td class="ccy">NZD</td><td class="num">3</td><td class="num">3</td><td class="num">2</td><td class="num">2</td><td class="num neg">8</td><td class="num pos">1</td><td class="num">3.2</td><td class="num pos">+0.2</td></tr>
<tr><td class="ccy">JPY</td><td class="num">4</td><td class="num">8</td><td class="num">6</td><td class="num">6</td><td class="num pos">1</td><td class="num">5</td><td class="num">5.2</td><td class="num">+1.2</td></tr>
<tr><td class="ccy">USD</td><td class="num">5</td><td class="num">5</td><td class="num">8</td><td class="num">7</td><td class="num">5</td><td class="num">4</td><td class="num">5.8</td><td class="num">+0.8</td></tr>
<tr><td class="ccy">EUR</td><td class="num">6</td><td class="num">2</td><td class="num">5</td><td class="num">8</td><td class="num">7</td><td class="num">6</td><td class="num">5.6</td><td class="num pos">&minus;0.4</td></tr>
<tr><td class="ccy">CHF</td><td class="num">7</td><td class="num">7</td><td class="num">7</td><td class="num">5</td><td class="num">2</td><td class="num">8</td><td class="num">5.8</td><td class="num pos">&minus;1.2</td></tr>
<tr><td class="ccy"><strong>AUD</strong></td><td class="num">8</td><td class="num neg">1</td><td class="num">3</td><td class="num neg">1</td><td class="num">6</td><td class="num neg">2</td><td class="num"><strong>2.6</strong></td><td class="num neg"><strong>&minus;5.4</strong></td></tr>
</tbody>
</table>
</div>

<div class="note fail">
  <strong>&#9888; rho = +0.17 with AUD. WITHOUT AUD IT IS +0.81.</strong>
  <br><br>
  Drop-one testing: GBP +0.15, CAD +0.06, NZD +0.08, JPY +0.20, USD +0.15,
  EUR +0.10, CHF +0.00 &mdash; and <strong>AUD +0.81</strong>. Every other
  currency moves rho by at most 0.17. <strong>AUD moves it by 0.63.</strong>
  <br><br>
  <strong>AUD was board #8 and traded like #2.6.</strong> It ranked #1 or #2
  on <strong>three sessions where it had zero scheduled releases</strong>, and
  ranked #6 on the one day it did have data &mdash; a flash PMI miss at 47.8
  against 51.1.
</div>

<div class="note">
  <strong>And the board is not wrong about AUD&#39;s fundamentals.</strong> I
  checked whether the negative rows were stale: they are not. Production
  (&minus;2) rests on a Sep PMI of 49.6, and <strong>the October flash printed
  49.7 on Thursday</strong> &mdash; still contractionary, still confirming.
  Trade (&minus;2) rests on an Aug balance that does not re-print until 5 Nov.
  <strong>The data says AUD is weak. Price disagreed for four of five
  sessions.</strong>
  <br><br>
  That gap is the single most useful thing this week produced. It is not a
  data-freshness problem, so it cannot be fixed by refreshing; it is either
  flow the board cannot see, or a genuine limit on what fundamentals predict
  over five days.
</div>
</section>

<section>
<h2>&sect;5 &mdash; Eight weeks of rho</h2>

<div class="scroll">
<table>
<thead><tr><th>WEEK</th><th class="num">rho</th><th>reading</th></tr></thead>
<tbody>
<tr><td class="mono">28 Sep</td><td class="num neg">&minus;0.40</td><td class="s">inverted</td></tr>
<tr><td class="mono">5 Oct</td><td class="num zero">+0.00</td><td class="s">nothing</td></tr>
<tr><td class="mono">&middot;&middot;</td><td class="num zero">+0.02</td><td class="s">nothing</td></tr>
<tr><td class="mono">&middot;&middot;</td><td class="num">+0.17</td><td class="s">weak</td></tr>
<tr><td class="mono">&middot;&middot;</td><td class="num">+0.26</td><td class="s">weak</td></tr>
<tr><td class="mono">&middot;&middot;</td><td class="num neg">&minus;0.62</td><td class="s">strongly inverted</td></tr>
<tr><td class="mono">12&ndash;16 Oct</td><td class="num pos">+0.52</td><td class="s">the best reading</td></tr>
<tr><td class="mono">19&ndash;23 Oct</td><td class="num">+0.17</td><td class="s">weak &mdash; +0.81 without AUD</td></tr>
<tr><td colspan="1"><strong>mean</strong></td><td class="num"><strong>+0.02</strong></td><td class="s">stdev 0.34 &mdash; indistinguishable from zero</td></tr>
</tbody>
</table>
</div>

<div class="note">
  <strong>Eight weeks in, the mean is +0.02 with a standard deviation of
  0.34.</strong> Last week&#39;s +0.52 looked like a turn; this week pulls the
  mean back to nothing. <strong>The board still has no demonstrated ranking
  skill</strong>, and the honest summary has not changed in two months.
  <br><br>
  <strong>But the AUD result points somewhere specific for the first time.</strong>
  If one currency can take rho from +0.81 to +0.17, the interesting question is
  no longer &ldquo;does the board rank?&rdquo; but <strong>&ldquo;which
  currencies does it rank, and which does it systematically misread?&rdquo;</strong>
  That is a question eight weeks of per-currency drift data can actually answer,
  and it is worth the 31 Oct review.
</div>
</section>

<section>
<h2>&sect;6 &mdash; What the dailies caught</h2>

<div class="note">
  <strong>The CHF warning was dated and specific one session before it
  fired.</strong> Wednesday&#39;s daily carried: EUR/CHF at a three-month low,
  <em>&ldquo;the Swiss franc draws renewed support from its traditional
  safe-haven appeal&rdquo;</em>, French 10-year yields above 5&#37;, the
  France&ndash;Germany spread near 170bp, and the explicit line <strong>&ldquo;three
  of our four pairs are short CHF&rdquo;</strong>. Thursday it happened.
  <br><br>
  <strong>The franc&#39;s strength is euro weakness, not a Swiss story</strong>
  &mdash; and our board scores CHF on Swiss fundamentals at &minus;1.20, so it
  structurally cannot see it. That is a named, reproducible blind spot rather
  than bad luck.
</div>

<div class="note">
  <strong>Two prints read against their own move, both on our main long.</strong>
  Tuesday&#39;s UK jobs report beat on every stock measure (unemployment 4.7&#37;
  vs 4.9&#37;, employment +102K vs +20K, payrolls +13K vs &minus;15K) and
  missed badly on the one flow measure (claimant count 30.3K vs 19.4K).
  Wednesday&#39;s UK CPI beat on headline, core and MoM &mdash; hawkish under
  LD-155 &mdash; and GBP fell anyway. <strong>GBP finished the week at board
  #1 and session-mean #4.2.</strong>
  <br><br>
  Of the catalyst rows I can recount from the surviving dailies,
  <strong>4 read consistent and 4 read AGAINST</strong> &mdash; 50&#37; when
  the data said anything at all. That is in line with last week&#39;s 56&#37;
  over a larger sample.
</div>

<div class="note fail">
  <strong>&#9888; AND TWO OF THE FOUR DAILIES NO LONGER EXIST ON DISK.</strong>
  Monday and Tuesday&#39;s files were overwritten in the scratchpad; only
  Wednesday and Thursday survive. <strong>The published artifacts hold all
  four</strong>, so nothing is lost to you &mdash; but this retro&#39;s
  catalyst tally covers two sessions rather than four, and says so rather than
  quoting a week-total it cannot recount.
  <br><br>
  Session data was re-derived from bars instead, which is the authority
  anyway. <strong>The fix is to write dailies into
  <code>reports/2026/Q4/daily/</code> rather than the scratchpad</strong>,
  where the weekly and the retro already live.
</div>
</section>

<section>
<h2>&sect;7 &mdash; The machinery, and a page that lied</h2>

<div class="scroll">
<table>
<thead><tr><th>ID</th><th>what was wrong</th><th class="num">cost</th></tr></thead>
<tbody>
<tr><td class="mono">F-160</td><td>the weekly <code>.md</code> header carried <strong>five</strong> values pinned to 28 Sep &mdash; url, retro url, date, title (with its typo) and eyebrow</td><td class="s">Jeff followed a link to a four-week-old report</td></tr>
<tr><td class="mono">F-161</td><td>the published page&#39;s <strong>board disagreed with its own evidence table</strong>: NAB scoring &minus;1 in &sect;4 against AUD &minus;0.67 in &sect;2</td><td class="s"><strong>GBPAUD&#39;s gap understated by a full point</strong></td></tr>
<tr><td class="mono">R-49</td><td>nothing compared the board to the rows printed beside it</td><td class="s">now check 9b of 15</td></tr>
<tr><td class="mono">F-157b</td><td>a stale TradingView instance holds the app with no CDP; the launcher still reports OK</td><td class="s">recurred twice, now caught in one step</td></tr>
</tbody>
</table>
</div>

<div class="note">
  <strong>F-161 is the one worth remembering.</strong> Every existing guard
  passed on a self-contradicting page: F-134 compares the page to the fact
  tables (right), R-44 checks the rules (right), R-48 checks <code>prev</code>
  (right). <strong>Nothing compared the board to the rows printed beside
  it.</strong> The board had been rendered before the final sync pass corrected
  three verdicts.
  <br><br>
  <strong>And R-49 took four wrong cuts to get right</strong>, each a repeat
  hazard: it anchored on a phrase that matched its own note; it returned
  <em>true</em> on &ldquo;not parseable&rdquo; (a silent pass &mdash; the exact
  shape of F-150, F-152 and F-158); it anchored on a section number that is not
  stable across editions; and it re-derived against the newest capture, which
  made a correct page look broken because the calibrator legitimately moves
  daily.
</div>
</section>

<section>
<h2>&sect;8 &mdash; What this says for next week</h2>

<div class="qa">
  <p><span class="k">Is &times;3 concentration acceptable?</span>
  <span class="v">The evidence now cuts both ways and should be stated that way.
  This week it returned <strong>1.45 against the diversified pair&#39;s
  0.84</strong>; it also delivered the single worst session of the month. It is
  a variance choice, not a quality one. A &times;2 cap would have smoothed
  Thursday and cost most of Monday through Wednesday.</span></p>

  <p><span class="k">Does the board rank?</span>
  <span class="v">Still unproven at eight weeks &mdash; mean +0.02, stdev 0.34.
  But the question has sharpened: <strong>without AUD this week scores
  +0.81</strong>. Ask which currencies the board reads well rather than whether
  it reads at all.</span></p>

  <p><span class="k">What about AUD specifically?</span>
  <span class="v">Board #8, traded #2.6, and the fundamentals are
  <em>current</em> &mdash; October&#39;s flash PMI confirmed the weakness on
  Thursday. This is not staleness. Either flow the board cannot see, or a real
  limit on five-day prediction from fundamentals.</span></p>

  <p><span class="k">What should be fixed first?</span>
  <span class="v">Two things, both cheap. <strong>Write dailies into the repo</strong>
  so a retro can always recount its own week. And <strong>pull the full 28-pair
  grid</strong> &mdash; still the highest-value item, now five weeks old on the
  list.</span></p>
</div>

<div class="note">
  <strong>The honest summary.</strong> A CONTESTED week with no losing pair, in
  which the thing I warned about twice outperformed and the thing I did not
  flag &mdash; a single currency the board reads backwards &mdash; cost more
  than either. <strong>Last week I wrote that a good week with a known failure
  mechanism is not yet evidence of skill. The same applies in reverse:
  a mediocre week whose risk fired on schedule is not evidence of failure
  either.</strong>
</div>
</section>

<p class="sub" style="margin-top:28px">
  <strong>Macro Economic Reporting</strong> &middot; retrospective for
  19&ndash;23 Oct 2026 &middot; built Saturday 24 Oct. Friday&#39;s session is
  complete by calendar &mdash; the FX week closed 21:00 UTC, so no later bar can
  exist. Prices and ATR: <span class="mono">OANDA</span> daily bars read from
  TradingView (LD-5 as amended). Verdict: LD-149, bands 0.70 / 1.40, target
  0.75&times;ATR(14) from sessions ending before the week (LD-129).
  Catalyst tally covers the <strong>two</strong> dailies still on disk, not all
  four. <strong>Observations only &mdash; no entries, stops, targets or sizing
  (LD-4).</strong>
</p>

</div>
'''

html = head + BODY
io.open(SP + 'retro_1923.html', 'w', encoding='utf-8', newline='\n').write(html)
print('wrote %d bytes' % len(html))
for t in ('section', 'table', 'div', 'tr', 'td', 'p', 'thead', 'tbody'):
    a, b = html.count('<%s' % t), html.count('</%s' % t)
    print('  %-8s %3d/%3d %s' % (t, a, b, 'OK' if a == b else '*** BAD'))
print('  wrap closed :', html.rstrip().endswith('</div>'))
