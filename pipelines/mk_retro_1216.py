# -*- coding: utf-8 -*-
"""Build the 12-16 Oct retrospective, reusing the sealed house style.

Jeff, 2026-10-17: "It's time for our Retrospective review. use the 4 reports we
produced from Tuesday to Friday to have a more intelligent analysis"

THE STYLE IS LIFTED VERBATIM from 2026-10-10_retro.html rather than rewritten -
it is already theme-correct (bare :root light palette, prefers-color-scheme dark
guarded with :not([data-theme="light"]), explicit [data-theme="dark"]), and a
retro is a recurring artefact that should look like its predecessors.
"""
import io
import os

REPO = 'c:/Users/jpesm/OneDrive/Documents/GitHub/Macro_Economic_Reporting/'
SP = ('C:/Users/jpesm/AppData/Local/Temp/claude/'
      'c--Users-jpesm-OneDrive-Documents-GitHub/'
      '16c8f514-dc2c-4587-b6a0-4fa0ff0b7ba8/scratchpad/')

prev = io.open(REPO + 'reports/2026/Q4/2026-10-10_retro.html',
               encoding='utf-8').read()
head = prev[:prev.index('</style>') + len('</style>')]
# swap the title only; the palette and layout are the sealed house style
# The retro stylesheet has no .chips/.chip - those live in the WEEKLY's style.
# Caught by checking every class against the inherited block before publishing
# rather than after. Defined here in the SAME token vocabulary (var(--...)), so
# they theme correctly in light, dark and the un-stamped system default.
CHIPS = u"""
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}
.chip{font:500 12px/1 "IBM Plex Mono",ui-monospace,monospace;
      letter-spacing:.02em;padding:6px 10px;border-radius:999px;
      background:var(--accent-soft);color:var(--accent);
      border:1px solid var(--rule-2);white-space:nowrap}
.chip.q{background:transparent;color:var(--ink-3)}
</style>"""
head = head.replace('</style>', CHIPS, 1)

head = head.replace('<title>The Week It Was Wrong</title>',
                    '<title>The Week The Board Was Right</title>', 1)

BODY = u'''

<div class="wrap">

<header>
  <p class="eyebrow">Macro Economic Reporting &middot; Retrospective &middot; Saturday 17 Oct 2026</p>
  <h1>The Week The Board Was Right</h1>
  <p class="dek"><strong>4 WIN of 4, set ratio 1.65</strong> &mdash; the first clean
  sweep. And for the first time the <strong>ranking itself carried signal</strong>:
  rho <strong>+0.52</strong> against a six-week mean of &minus;0.10. But
  <strong>43&#37; of the week&#39;s favourable movement came from one session</strong>,
  and <strong>51&#37; of the adverse came from another</strong>. This is the first
  retro built on daily evidence, and the dailies change what can be concluded.</p>
  <div class="chips">
    <span class="chip">4 WIN / 0 CONTESTED / 0 LOSS</span>
    <span class="chip">rho +0.52</span>
    <span class="chip q">4 dailies</span>
    <span class="chip q">40 currency-sessions</span>
  </div>
</header>

<section>
<h2>&sect;1 &mdash; The verdict</h2>

<p>LD-149: a pair wins when summed favourable excursion divided by summed
adverse exceeds <span class="mono">1.40</span>; below <span class="mono">0.70</span>
it loses. Excursions are measured from each day&#39;s own open against a
<span class="mono">0.75&times;ATR(14)</span> target, with ATR drawn from sessions
ending <em>before</em> the week (LD-129).</p>

<div class="scroll">
<table>
<thead><tr><th>PAIR</th><th class="num">ATR</th><th class="num">&Sigma; fav</th>
<th class="num">&Sigma; adv</th><th class="num">ratio</th><th>VERDICT</th>
<th>Tue&ndash;Fri, by session</th></tr></thead>
<tbody>
<tr><td class="ccy">GBPJPY</td><td class="num">142</td><td class="num pos">393.8</td><td class="num">245.5</td><td class="num pos">1.60</td><td class="pos"><strong>WIN</strong></td><td class="mono s">DRIFT DRIFT <span class="neg">BEATEN</span> CLEAN CLEAN</td></tr>
<tr><td class="ccy">GBPAUD</td><td class="num">93</td><td class="num pos">388.7</td><td class="num">228.1</td><td class="num pos">1.70</td><td class="pos"><strong>WIN</strong></td><td class="mono s">DRIFT DRIFT <span class="neg">BEATEN</span> CLEAN DRIFT</td></tr>
<tr><td class="ccy">CADJPY</td><td class="num">77</td><td class="num pos">187.9</td><td class="num">119.4</td><td class="num pos">1.57</td><td class="pos"><strong>WIN</strong></td><td class="mono s">DRIFT DRIFT DRIFT DRIFT DRIFT</td></tr>
<tr><td class="ccy">EURJPY</td><td class="num">135</td><td class="num pos">286.7</td><td class="num">169.3</td><td class="num pos">1.69</td><td class="pos"><strong>WIN</strong></td><td class="mono s">DRIFT DRIFT <span class="neg">BEATEN</span> DRIFT DRIFT</td></tr>
<tr><td colspan="2"><strong>SET TOTAL</strong></td><td class="num pos"><strong>1257.1</strong></td><td class="num"><strong>762.3</strong></td><td class="num pos"><strong>1.65</strong></td><td class="pos"><strong>WIN</strong></td><td class="s">every pair above the band</td></tr>
</tbody>
</table>
</div>

<div class="note">
  <strong>Four of four, and the margin is not marginal.</strong> The tightest
  pair (CADJPY, 1.57) still clears the 1.40 band by 12&#37;. Compare the two
  prior editions: 5&ndash;9 Oct returned <strong>0 WIN, 2 CONTESTED, 2 LOSS,
  &minus;245 pips</strong>, and 28 Sep&ndash;2 Oct was no better. This is the
  first week where the measured verdict and the intended bias agree on every
  pair.
</div>

<div class="note">
  <strong>&#9888; CADJPY never produced a single CLEAN or BEATEN session.</strong>
  Five DRIFTs in a row &mdash; it won on accumulation, not on any day reaching
  target. Its ATR is the smallest in the set (77 pips) and its daily excursions
  the smallest. <strong>A 1.57 ratio built entirely from drift is a weaker claim
  than the same number built from two CLEAN days</strong>, and LD-149 cannot
  distinguish the two. Worth knowing before trusting the ratio alone.
</div>
</section>

<section>
<h2>&sect;2 &mdash; Where the week was actually won</h2>

<p>This is what the dailies made visible, and no previous retro could see it.</p>

<div class="scroll">
<table>
<thead><tr><th>SESSION</th><th class="num">fav</th><th class="num">adv</th>
<th class="num">ratio</th><th>the set, that day</th></tr></thead>
<tbody>
<tr><td class="mono">Mon 12</td><td class="num">163.8</td><td class="num">68.4</td><td class="num pos">2.39</td><td class="s">four DRIFT</td></tr>
<tr><td class="mono">Tue 13</td><td class="num">165.7</td><td class="num">165.0</td><td class="num zero">1.00</td><td class="s">four DRIFT &mdash; dead level</td></tr>
<tr><td class="mono">Wed 14</td><td class="num">101.3</td><td class="num neg">391.4</td><td class="num neg">0.26</td><td class="s"><span class="neg">three BEATEN</span></td></tr>
<tr><td class="mono">Thu 15</td><td class="num pos">541.4</td><td class="num">57.1</td><td class="num pos">9.48</td><td class="s"><strong>two CLEAN</strong></td></tr>
<tr><td class="mono">Fri 16</td><td class="num">284.9</td><td class="num">80.4</td><td class="num pos">3.54</td><td class="s">one CLEAN</td></tr>
</tbody>
</table>
</div>

<div class="note">
  <strong>Thursday alone supplied 43&#37; of the week&#39;s favourable movement</strong>
  (541.4 of 1257.1 pips). <strong>Wednesday alone supplied 51&#37; of the
  adverse</strong> (391.4 of 762.3). Remove those two sessions and the remaining
  three read <span class="mono">614.4 / 313.8 = 1.96</span> &mdash; still a WIN,
  but a different kind of week.
  <br><br>
  <strong>The honest reading: this was not four steady days of the bias working.
  It was one very good day, one bad day, and three that drifted.</strong> A single
  AUD employment print on Thursday is doing most of the work.
</div>
</section>

<section>
<h2>&sect;3 &mdash; Did the ranking predict anything?</h2>

<p>The open question for six weeks. rho compares each currency&#39;s board rank
against its <em>mean session rank</em> across the five sessions.</p>

<div class="scroll">
<table>
<thead><tr><th>CCY</th><th class="num">board</th><th class="num">Mon</th>
<th class="num">Tue</th><th class="num">Wed</th><th class="num">Thu</th>
<th class="num">Fri</th><th class="num">mean</th><th class="num">drift</th></tr></thead>
<tbody>
<tr><td class="ccy">GBP</td><td class="num">1</td><td class="num">4</td><td class="num">5</td><td class="num neg">8</td><td class="num">2</td><td class="num">2</td><td class="num">4.2</td><td class="num neg">+3.2</td></tr>
<tr><td class="ccy">CAD</td><td class="num">2</td><td class="num">2</td><td class="num">2</td><td class="num">3</td><td class="num">5</td><td class="num">4</td><td class="num">3.2</td><td class="num">+1.2</td></tr>
<tr><td class="ccy">EUR</td><td class="num">3</td><td class="num">6</td><td class="num">3</td><td class="num">7</td><td class="num">3</td><td class="num">6</td><td class="num">5.0</td><td class="num">+2.0</td></tr>
<tr><td class="ccy">USD</td><td class="num">4</td><td class="num">1</td><td class="num neg">8</td><td class="num">2</td><td class="num">7</td><td class="num">7</td><td class="num">5.0</td><td class="num">+1.0</td></tr>
<tr><td class="ccy">NZD</td><td class="num">5</td><td class="num">7</td><td class="num">1</td><td class="num">6</td><td class="num">4</td><td class="num">1</td><td class="num">3.8</td><td class="num pos">&minus;1.2</td></tr>
<tr><td class="ccy">CHF</td><td class="num">6</td><td class="num">8</td><td class="num">6</td><td class="num">5</td><td class="num pos">1</td><td class="num">5</td><td class="num">5.0</td><td class="num pos">&minus;1.0</td></tr>
<tr><td class="ccy">AUD</td><td class="num">7</td><td class="num">3</td><td class="num">4</td><td class="num">4</td><td class="num">8</td><td class="num">3</td><td class="num">4.4</td><td class="num pos">&minus;2.6</td></tr>
<tr><td class="ccy">JPY</td><td class="num">8</td><td class="num">5</td><td class="num">7</td><td class="num pos">1</td><td class="num">6</td><td class="num">8</td><td class="num">5.4</td><td class="num pos">&minus;2.6</td></tr>
</tbody>
</table>
</div>

<div class="note">
  <strong>rho = +0.52.</strong> The six-week record was
  <span class="mono">&minus;0.40, +0.00, +0.02, +0.17, +0.26, &minus;0.62</span>
  &mdash; mean &asymp;&nbsp;&minus;0.10, confidence interval spanning zero. This
  is the strongest reading by a wide margin.
  <br><br>
  <strong>And I tested whether one currency carried it.</strong> Dropping each in
  turn: GBP +0.53, CAD +0.35, EUR +0.63, USD +0.57, NZD +0.60, CHF +0.49, AUD
  +0.60, <strong>JPY +0.33</strong>. The range is +0.33 to +0.63 &mdash;
  <strong>positive however you cut it</strong>, so it is not one leg.
</div>

<div class="note fail">
  <strong>&#9888; BUT FOUR SESSIONS ARE POSITIVE AND ONE IS STRONGLY NEGATIVE.</strong>
  Per-session rho: <span class="mono">Mon +0.29, Tue +0.31,
  <strong>Wed &minus;0.55</strong>, Thu +0.40, Fri +0.33</span>.
  <br><br>
  Wednesday is the day GBP ranked <strong>#8</strong> from a board rank of #1 and
  JPY ranked <strong>#1</strong> from #8 &mdash; both extremes exactly inverted,
  seven places each. <strong>That is also the day the set took three BEATEN.</strong>
  The relationship is not weak-but-steady; it is strong on four days and sharply
  wrong on the fifth. <strong>One week does not retire a six-week null result</strong>,
  and the right conclusion is that the sample now has one strong positive in it,
  not that the board has been shown to rank.
</div>
</section>

<section>
<h2>&sect;4 &mdash; What the dailies proved about the catalysts</h2>

<p>Each daily graded all eight currencies against the scheduled releases that
landed that session. Across four dailies that is <strong>32 currency-sessions</strong>
&mdash; the first time this has been countable.</p>

<div class="scroll">
<table>
<thead><tr><th>VERDICT</th><th class="num">count</th><th>what it means</th></tr></thead>
<tbody>
<tr><td class="pos"><strong>consistent</strong></td><td class="num">10</td><td class="s">a release surprised, and the currency moved the way it implies</td></tr>
<tr><td class="neg"><strong>AGAINST</strong></td><td class="num">8</td><td class="s">a release surprised, and the currency moved the <em>other</em> way</td></tr>
<tr><td><strong>quiet</strong></td><td class="num">8</td><td class="s">nothing scheduled for that currency at all</td></tr>
<tr><td><strong>tone unread</strong></td><td class="num">4</td><td class="s">a speech &mdash; LD-107, we record that someone spoke, never what they said</td></tr>
<tr><td><strong>UNEXPLAINED</strong></td><td class="num">1</td><td class="s">rows landed that day, none for this currency</td></tr>
<tr><td><strong>none surprised</strong></td><td class="num">1</td><td class="s">released exactly on consensus</td></tr>
</tbody>
</table>
</div>

<div class="note fail">
  <strong>&#9888; THE SCHEDULED DATA EXPLAINED THE MOVE 10 TIMES AND CONTRADICTED
  IT 8 TIMES.</strong> That is <strong>56&#37;</strong> &mdash; barely better than
  a coin toss, on the very inputs the entire base score is built from.
  <br><br>
  <strong>Thursday is the sharpest case: four consistent and four AGAINST, an
  exact split</strong> on the week&#39;s best session. USD retail sales <em>beat</em>
  0.8&#37; vs 0.1&#37; and the dollar <em>fell</em>. EUR industrial production
  <em>missed</em> and the euro <em>rose</em>. CAD manufacturing sales <em>beat</em>
  and CAD was flat-to-lower.
  <br><br>
  This does not invalidate the board &mdash; the board scores a <em>stock</em> of
  conditions, not a day&#39;s flow. But it is direct evidence that
  <strong>a single session&#39;s releases are close to uninformative about that
  session&#39;s direction</strong>, and the daily report is now the thing that
  demonstrates it.
</div>
</section>

<section>
<h2>&sect;5 &mdash; The AUD print that did the work, and the rule that disagrees</h2>

<p>Thursday supplied 43&#37; of the week&#39;s favourable movement, and GBPAUD
was its widest pair (+1.36&#37; in one session). Nearly all of that is one
release.</p>

<div class="scroll">
<table>
<thead><tr><th>LEG</th><th class="num">actual</th><th class="num">expected</th><th>reads</th></tr></thead>
<tbody>
<tr><td>Employment Change, headline</td><td class="num neg">&minus;39.3K</td><td class="num">+20.0K</td><td class="neg">a 59K miss &mdash; NEGATIVE</td></tr>
<tr><td>Full&nbsp;time</td><td class="num pos">+34.4K</td><td class="num">&mdash;</td><td class="pos">POSITIVE</td></tr>
<tr><td>Part&nbsp;time</td><td class="num neg">&minus;73.7K</td><td class="num">&mdash;</td><td class="neg">NEGATIVE</td></tr>
<tr><td>Unemployment rate</td><td class="num neg">4.7&#37;</td><td class="num">4.6&#37;</td><td class="neg">worse than expected</td></tr>
<tr><td>Participation rate</td><td class="num">66.8&#37;</td><td class="num">67.0&#37;</td><td class="s">FELL &mdash; which <em>flatters</em> the jobless rate</td></tr>
</tbody>
</table>
</div>

<div class="note">
  <strong>The market sold AUD 1.083&#37;. Our rule says NEUTRAL.</strong>
  LD-57/LD-151 grades AUD on the <strong>full-time</strong> leg, and because
  headline and full time <em>disagree</em>, <span class="mono">employment_grade()</span>
  returns NEUTRAL. I called the function rather than assuming it.
  <br><br>
  So the daily&#39;s &ldquo;consistent&rdquo; label on that row is the
  <strong>headline&#39;s</strong> verdict, not <strong>the rule&#39;s</strong>.
  <strong>We were long GBPAUD and were paid by a print our own scoring rule
  would have called neutral.</strong> That is worth more than a win: it is the
  first live instance of the case LD-151 was written for, and it says the rule
  and the market can read the same release in opposite directions.
  <br><br>
  <strong>Which is right is genuinely open.</strong> The full-time preference
  exists because full-time jobs carry the income that drives consumption, and
  that reasoning has not been falsified by one session. But a rule that says
  NEUTRAL on a 59K headline miss will keep diverging from price, and the
  divergence should be tracked rather than resolved by argument.
</div>
</section>

<section>
<h2>&sect;6 &mdash; A metric that cannot fail is not a metric</h2>

<div class="note fail">
  <strong>&#9888; LD-162 RETURNED &ldquo;BROAD&rdquo; OR &ldquo;MOSTLY BROAD&rdquo;
  IN 40 OF 40 CURRENCY-SESSIONS. NARROW NEVER ONCE FIRED.</strong>
  <br><br>
  The cause is not the market. Breadth is measured only against counterparts we
  hold bars for: <strong>USD gets 7, JPY 4, GBP 3, CAD/EUR/AUD 2, and CHF and
  NZD get 1</strong>. With one counterpart the question
  &ldquo;did it move against most of them?&rdquo; has no content &mdash;
  &ldquo;BROAD, stronger against all 1&rdquo; is arithmetically true and says
  nothing.
  <br><br>
  LD-162 was added for a real reason, and it <em>did</em> work where the data was
  thick: on Tuesday it correctly showed the whole board was one USD move seen from
  seven sides, and every other currency&#39;s best gain was against USD. <strong>The
  metric is sound; its input is too thin for five of eight currencies.</strong>
  The fix is the full 28-pair grid rather than 11 pairs, and until then a BROAD
  reading on <span class="mono">n=1</span> should be treated as no reading at all.
</div>
</section>

<section>
<h2>&sect;7 &mdash; What changed in the machinery this week</h2>

<p>Five findings landed mid-week, three of them from Jeff reading the output
rather than from any guard.</p>

<div class="scroll">
<table>
<thead><tr><th>ID</th><th>what was wrong</th><th class="num">cost</th></tr></thead>
<tbody>
<tr><td class="mono">LD-165</td><td>the base never read a forward inflation consensus &mdash; LD-155&#39;s before-the-news half ran only in the calibrator</td><td class="s">0 this week; JPY was one rounding from flipping</td></tr>
<tr><td class="mono">F-154</td><td><span class="mono">score_model.ROWS</span> is a hand-written second copy and <span class="mono">prev</span> had drifted on 26 of 41 rows</td><td class="s"><strong>the set changed</strong></td></tr>
<tr><td class="mono">LD-166</td><td>the 1.5&ndash;2.5 corridor was never an Interest Rate rule &mdash; it was CPI&#39;s, applied to the policy rate 38 minutes later because one band for both was tidier</td><td class="s"><strong>the set rotated CHF&rarr;JPY</strong></td></tr>
<tr><td class="mono">F-155</td><td>R-48 matched only <em>released</em> rows, so a row it could not match passed as UNVERIFIED</td><td class="s">cosmetic, but the printed working was wrong</td></tr>
<tr><td class="mono">F-156/157</td><td>the daily runbook&#39;s two commands did not connect, and the Monday guard tested the wrong day</td><td class="s">the first daily could not build</td></tr>
</tbody>
</table>
</div>

<div class="note">
  <strong>LD-166 is the one that matters most, and it rotated the set
  mid-week.</strong> Retiring the corridor moved CHF from &minus;1.50 to
  &minus;1.00 and made JPY the weakest currency, which swapped three CHF shorts
  for three JPY shorts. <strong>That concentration then cost three BEATEN on
  Wednesday</strong> &mdash; and the 12&ndash;16 Oct edition still carried a note
  saying the overlap was &ldquo;balanced for the first time in a month&rdquo;,
  written before the rotation and never revisited.
  <br><br>
  <strong>The set changed; the diversification claim did not.</strong> That is
  the same family as F-149/F-151 &mdash; a description outliving the rule it
  described &mdash; except in prose rather than a table column, where no guard
  looks at all.
</div>

<div class="note fail">
  <strong>&#9888; AND THE CONCENTRATION IS NOW A MEASURED LOSS, NOT A
  HYPOTHETICAL.</strong> Three of four pairs were short JPY. On Wednesday JPY
  ranked #1 of eight and the set took three BEATEN in one session &mdash; 51&#37;
  of the week&#39;s entire adverse movement. The week still won, because Thursday
  was large enough to absorb it. <strong>That is luck about magnitude, not a
  defence of the concentration.</strong>
</div>
</section>

<section>
<h2>&sect;8 &mdash; What this says for next week</h2>

<div class="qa">
  <p><span class="k">Does the board rank?</span>
  <span class="v">Unresolved, but better evidenced than it has ever been. rho
  +0.52 is one strong positive in a seven-week sample whose mean is still near
  zero. The useful next step is not another week of rho &mdash; it is asking why
  Wednesday was &minus;0.55 when four other sessions were positive.</span></p>

  <p><span class="k">Is the set too concentrated?</span>
  <span class="v">Yes, on evidence. &times;3 on one leg cost three BEATEN in a
  single session. A cap of &times;2 per leg would have excluded one pair this
  week &mdash; and would also have excluded GBPAUD, the best performer. The
  trade-off is real and it is Jeff&#39;s call, not a derivation.</span></p>

  <p><span class="k">Are the scheduled releases informative?</span>
  <span class="v">Less than assumed. 10 consistent against 8 AGAINST over 32
  currency-sessions. They may still be informative about the <em>stock</em> of
  conditions while being near-useless about a single day&#39;s direction &mdash;
  which is exactly what the base/calibrator split already assumes, now with a
  number attached.</span></p>

  <p><span class="k">What should be fixed first?</span>
  <span class="v">The 28-pair bar grid. It costs nothing in logic, it makes
  LD-162 able to return NARROW, and without it five of eight currencies have a
  breadth reading that cannot be wrong and therefore cannot be right.</span></p>
</div>

<div class="note">
  <strong>The one thing I would not conclude from this week.</strong> Four of
  four won, rho turned positive, and the bias was paid on the session it
  mattered. It is tempting to read that as the method working. <strong>But 43&#37;
  of the gain came from one print that our own rule grades NEUTRAL</strong>, and
  the week&#39;s worst session was the one where the board&#39;s two extreme
  ranks both inverted. A good week with a known mechanism of failure inside it is
  still a good week &mdash; it is just not yet evidence of skill.
</div>
</section>

<p class="sub" style="margin-top:28px">
  <strong>Macro Economic Reporting</strong> &middot; retrospective for
  12&ndash;16 Oct 2026 &middot; built Saturday 17 Oct on the
  <span class="mono">2026-10-16_1208PHT</span> capture and the four dailies
  (<span class="mono">12, 13, 14, 15 Oct</span>).
  Prices and ATR: <span class="mono">OANDA</span> daily bars read from
  TradingView (LD-5 as amended). Friday&#39;s session is complete by calendar
  &mdash; the FX week closed 21:00 UTC, so no later bar can exist.
  Verdict: LD-149, bands 0.70 / 1.40, measured on 3,192 pair-weeks.
  <strong>Observations only &mdash; no entries, stops, targets or sizing
  (LD-4).</strong>
</p>

</div>
'''

html = head + BODY
io.open(SP + 'retro_1216.html', 'w', encoding='utf-8',
        newline='\n').write(html)
print('wrote %d bytes' % len(html))
for t in ('section', 'table', 'div', 'tr', 'td', 'p', 'thead', 'tbody'):
    a, b = html.count('<%s' % t), html.count('</%s' % t)
    print('  %-8s %3d/%3d %s' % (t, a, b, 'OK' if a == b else '*** BAD'))
print('  wrap closed :', html.rstrip().endswith('</div>'))
print('  title       :', html[html.find('<title>') + 7:html.find('</title>')])
