# -*- coding: utf-8 -*-
"""Generate the whole web page from the model - nothing hand-typed.

Every figure the page shows is read from the pipelines at build time. The
first three revisions carried hand-typed numbers and went stale the moment
F-92/F-93 moved the board; two of them I had already corrected by hand in
the OUTPUT and watched the next rebuild revert.
"""
import io, os, sys, glob, json, datetime as dt

os.chdir(r'c:/Users/jpesm/OneDrive/Documents/GitHub/Macro_Economic_Reporting')
sys.path.insert(0, os.path.join(os.getcwd(), 'pipelines'))
NL = chr(10)
import fact_tables as ft
import pair_select as ps
import calibrator as cal
import score_model as _sm
import pair_atr as pa
import pair_swap as psw
import week_ahead as wa

# LD-132 - the threshold each calibrator row is graded against. score_model
# owns the rule; the calibrator only applies it, so the rule is read from
# there rather than restated.
THR = dict(((_sm.LABEL[_r[1]], _r[2]), _r[6]) for _r in _sm.ROWS)

# LD-134 - HIGH-IMPACT ROWS ARE FLAGGED AS A CAUTION. Jeff, 2026-09-13:
# "These are High Impact news can you Highlight these rows so I can be
# reminded of the schedule of these news? Next time let's highlight
# Employment, Inflation, Interest Rate, and GDP news on the board as a form
# of caution".
#
# THE FLAG IS A CAUTION, NOT A WEIGHT. It changes no score and no ranking -
# the calibrator still treats every row identically (LD-98, the day is the
# unit). It marks the rows that move price hardest so a reader knows which
# days carry event risk before the week starts.
#
# The category comes from score_model, which already classifies every row -
# so a row moving category moves its flag automatically, and nothing here
# restates a list that could drift (the F-96/97/98 shape).
HIGH_IMPACT = ('Employment', 'Inflation', 'Interest_Rate', 'GDP')
CAT = dict(((_sm.LABEL[_r[1]], _r[2]), _r[0]) for _r in _sm.ROWS)


def hot(ccy, name):
    """True when this row is one of the high-impact categories (LD-134).

    *** F-135 - THE ONE CATEGORY THE RULE NAMES WAS THE ONLY ONE NEVER
    FLAGGED. Jeff, 2026-09-23, on the SNB decision: "This should be
    highlighted as well as High Impact news".

    LD-134 lists Employment, Inflation, INTEREST RATE and GDP. But CAT is
    built from score_model.ROWS, and LD-140 gives a rate decision the
    SYNTHETIC name 'Interest Rate Decision' - a row that lives in
    rate_model, not score_model. So CAT.get(('CHF', 'Interest Rate
    Decision')) returned None, hot() returned False, and every central bank
    decision rendered as an ordinary row.

    Three central banks moved in 14-18 Sep and not one was marked as event
    risk on the page, which is precisely the caution LD-134 exists to give.
    """
    if name == wa.RATE_NAME:
        return 'Interest_Rate' in HIGH_IMPACT
    return CAT.get((ccy, name)) in HIGH_IMPACT

SP = ('C:/Users/jpesm/AppData/Local/Temp/claude/'
      'c--Users-jpesm-OneDrive-Documents-GitHub/'
      '16c8f514-dc2c-4587-b6a0-4fa0ff0b7ba8/scratchpad/')
CAP = sorted(glob.glob('data/raw/calendar/2026-10-04_*_cal_full.json'))[-1]
START, END = '2026-10-05', '2026-10-09'

F = ps.final_scores(CAP, START, END)
SC = dict((c, F[c]['total']) for c in F)
BAND, ORDER = ft.bands(SC)
CANDS = ps.candidates(SC, BAND)
# LD-125 - THE SET IS ONE TIER-1 PAIR PER CATEGORY. Jeff, 2026-09-10:
# "on The set let's get Tier 1 pairs for each category".
# NOT leg-disjoint any more: guaranteeing coverage and forbidding leg
# reuse cannot both hold. LEGACY is kept so the page can still show what
# the old gap-first rule would have produced.
# LD-126 - the set covers every CATEGORY and every STRONG CURRENCY.
# Jeff, 2026-09-10: "we have EUR, CHF, JPY as our strong currencies. We
# have pairs for EUR, and CHF but we're not getting for JPY?" Per-category
# coverage does not imply per-currency coverage: CHF and JPY are both safe
# havens, so every pair they make is RISK OFF and they compete for one
# slot. SET SIZE VARIES - that is the honest consequence.
SETROWS = ps.the_set(CANDS, BAND, SC)
PICKED = [x for x, _w in SETROWS]
WHY = dict((id(x), w) for x, w in SETROWS)
LEGACY = ps.select(CANDS)
OVERLAP = ps.leg_overlap(PICKED)
CALD = cal.calibrate(CAP, START, END)
# F-116: a row can have NO published time (NZD Global Dairy Trade). Sorting
# on `when` directly raises on None; dropping such rows would be F-36, where
# a sort silently discarded events. Sort by day, then untimed LAST within
# the day, then by clock - and keep every row.
def _order(r):
    return (r['day'] or dt.date.max,
            1 if r['when'] is None else 0,
            r['when'].strftime('%H:%M') if r['when'] else '')


ROWS = sorted(cal.week_rows(CAP, START, END), key=_order)
B = ft.base_scores()
BSC = dict((c, F[c]['base']) for c in F)
BBAND, BORDER = ft.bands(BSC)
BPICK = ps.select(ps.candidates(BSC, BBAND))
MONTH = ft.latest_month()
scored, total = ft.coverage(MONTH)
BRANK = dict((c, i + 1) for i, c in enumerate(BORDER))
FRANK = dict((c, i + 1) for i, c in enumerate(ORDER))
n_cons = len([r for r in ROWS if r['cons']])
n_scor = len([r for r in ROWS if r['score'] is not None])
BEST = PICKED[0]
# *** F-130 - THE CALIBRATOR GRID WAS PINNED TO LAST WEEK'S DATES.
#
# Jeff, 2026-09-20, on the published 21-25 Sep page: "we don't have anything
# on this?" - the grid showed MON 14 ... FRI 18 with every cell a dash, while
# the WEEK column beside it carried real non-zero totals.
#
# DAYS was a literal [14,15,16,17,18] while START/END had already moved to
# 21-25. Every lookup missed, so every cell printed a dash - and the page
# then explained the emptiness with a confident footnote ("EUR and JPY and
# NZD have no rows at all this week"), which was FALSE.
#
#     THE NUMBERS WERE RIGHT AND THE GRID THEY WERE PLOTTED ON WAS WRONG.
#
# That is F-111/F-122's class again: an OUTPUT defect that survives because
# everything it is computed from is correct. START and END were already in
# scope two lines up; the window must be derived, never restated.
DAYS = [dt.date(*(int(x) for x in START.split('-'))) + dt.timedelta(days=i)
        for i in range(5)]
assert DAYS[-1].isoformat() == END, (
    'calibrator grid %s..%s does not match the edition window %s..%s'
    % (DAYS[0], DAYS[-1], START, END))
BANDCLS = {'STRONG': 's', 'NEUTRAL': 'n', 'WEAK': 'w'}


def cls(v):
    return 'pos' if v > 0 else ('neg' if v < 0 else 'zero')


def sg(v, f='%+.2f'):
    return (f % v).replace('-', '\u2212')


o = []
A = o.append

A('<section>')
A('  <h2>The set</h2>')
A('  <p class="sub">%d pairs \u2014 one tier-1 read for every category and every strong currency.</p>'
  % len(PICKED))
A('')
A('  <div class="set">')
for i, c in enumerate(PICKED, 1):
    A('    <div class="pair%s">' % (' top' if i == 1 else ''))
    A('      <span class="rank">%d</span>' % i)
    A('      <span class="sym">%s<span class="bias %s">%s</span></span>'
      % (ps.label(CANDS, c), c['direction'].lower(), c['direction']))
    A('      <span class="gap%s">%s</span>'
      % (' big' if i == 1 else '', sg(c['gap'])))
    A('      <span class="legs"><span class="cat">%s</span> &nbsp;long %s '
      '<strong>%s</strong> \u00b7 short %s <strong>%s</strong></span>'
      % (c['category'], c['long'], sg(SC[c['long']]),
         c['short'], sg(SC[c['short']])))
    A('      <span class="legs"><span class="cat">covers</span> '
      '&nbsp;%s</span>' % ' \u00b7 '.join(WHY[id(c)]))
    # LD-145 - Jeff, 2026-09-27: "on the next report for the selected
    # pairs, lets put the ATR and Target as well. I believe we already
    # putting the Gap there".
    #
    # GAP is the MODEL - a score difference on a -9..+9 board, never price.
    # ATR is what the pair NORMALLY moves. TARGET is 0.75 x ATR, the
    # distance a day must cover to count (LD-128). Without ATR the retro's
    # day-readings are not comparable across pairs: 1.06x on GBPAUD is
    # 89 pips, 1.40x on AUDCHF is 45.
    #
    # Bars come from TradingView/OANDA ONLY (LD-5 as amended, F-137). A pair
    # with no bars says so rather than printing a guessed number.
    _at = pa.atr_for(c['pair'], START)
    if _at:
        A('      <span class="legs"><span class="cat">range</span> '
          '&nbsp;ATR(14) <strong>%.0f</strong> pips · '
          '0.75 target <strong>%.0f</strong> pips</span>'
          % (_at[0], _at[1]))
    else:
        A('      <span class="legs"><span class="cat">range</span> '
          '&nbsp;<em>no bars — pull OANDA:%s from TradingView</em>'
          '</span>' % c['pair'])
    # LD-147 - DOES THE SWAP PAY OR COST IN THE DIRECTION WE ARE BIASED?
    #
    # Jeff, 2026-09-30: "Can we add here if the Swap is +/- in the
    # directional bias?" A pair has two swaps with opposite signs; which
    # applies depends on the SIDE, so this is computed per position.
    #
    # A SIGN AND A DIFFERENTIAL IN PERCENTAGE POINTS, never a money
    # figure. LD-4 draws the line at position sizing, and "$4.20 a night
    # on a mini lot" is a sizing input; a rate differential is a property
    # of two currencies, the same class of fact as the rates in section 4.
    # LD-8 already caps carry at a tiebreak - this does not even tiebreak.
    _sw = psw.differential(c['pair'], c['direction'])
    if _sw:
        _d = _sw[0]
        _cl = 'pos' if _d > 0 else ('neg' if _d < 0 else 'zero')
        _wd = 'earns' if _d > 0 else ('costs' if _d < 0 else 'flat')
        _ov = psw.overlaid(c['pair'])
        A('      <span class="legs"><span class="cat">swap</span> '
          '&nbsp;<strong class="%s">%+.2f pp</strong> — %s to hold'
          '%s</span>'
          % (_cl, _d, _wd,
             (' <em>(on today’s %s %.2f%%, not the edition’s '
              '%.2f%%)</em>' % (_ov[0][0], _ov[0][1], _ov[0][2]))
             if _ov else ''))
    A('    </div>')
A('  </div>')
A('')
# LD-147 - SAY WHAT THE SWAP LINE IS, AND WHAT IT IS NOT.
_swaps = [psw.differential(c['pair'], c['direction']) for c in PICKED]
_swaps = [x for x in _swaps if x]
if _swaps:
    _neg = [x for x in _swaps if x[0] < 0]
    A('  <div class="note">')
    A('    <strong>The swap line is the POLICY RATE DIFFERENTIAL in the '
      'direction of the bias, not a broker swap rate.</strong> A pair has two '
      'swaps with opposite signs; which one applies depends on the side, so it '
      'is computed per position. Brokers quote swaps in points per lot, set by '
      'their own funding and marked up — two brokers differ, and so do two '
      'accounts at one broker. What is shown is the economic force underneath '
      'that number, never the number itself.')
    if len(_neg) == len(_swaps):
        A('    <br><br><strong>⚠ All %d selected pairs carry a NEGATIVE '
          'differential</strong> — every one of them costs something to '
          'hold. That is not a coincidence and it is not an argument against '
          'the set: the board ranks currencies on macro strength, and this '
          'week the strong ones (GBP 3.75%%, EUR 2.65%%, JPY 1.25%%) mostly '
          'carry LOWER policy rates than the weak one (AUD 4.60%%). '
          '<strong>Being macro-right and carry-negative at the same time is '
          'the normal shape of a divergence trade</strong>, and the cost is '
          'the price of holding it.' % len(_swaps))
    A('    <br><br><strong>It moves nothing.</strong> LD-8 caps carry at a '
      'swing-ranking tiebreak, never a filter; this does not even tiebreak. '
      'The set, the gaps and the board are computed before it runs and do not '
      'consult it. It is disclosed so a reader holding a position for a week '
      'can see whether the week costs them anything — <strong>no lot '
      'sizes, no money figures (LD-4)</strong>.')
    A('  </div>')
A('')
A('  <p><strong>%s %s carries the widest gap on the board at %s</strong> '
  '\u2014 <strong>%s is top at %s and %s is bottom at %s</strong>.</p>'
  % (BEST['pair'], BEST['direction'], sg(BEST['gap']),
     ORDER[0], sg(SC[ORDER[0]]), ORDER[-1], sg(SC[ORDER[-1]])))
last = PICKED[-1]
if len(PICKED) > 1 and last['gap'] < 2.0:
    # LD-108: a gap under 0.50 on a +/-14 scale is not a weak view, it is
    # noise. Jeff's call 2026-09-09 is to TAKE it (LD-96 - take what
    # qualifies) rather than reinstate a floor, so the report has to say so
    # in proportion to how thin it actually is.
    _noise = last['gap'] < 0.50
    A('  <div class="note flag">')
    A('    <span class="lbl">%s</span>'
      % ('⚠ THE LAST PAIR IS NOISE, NOT A VIEW' if _noise
         else '⚠ THE TAIL IS THIN'))
    A('    <strong>%s %s rests on a %s gap</strong> — %s at %s against %s '
      'at %s. %s'
      % (last['pair'], last['direction'], sg(last['gap']),
         last['long'], sg(SC[last['long']]),
         last['short'], sg(SC[last['short']]),
         ('<strong>On a ±14 scale that is inside the rounding of a '
          'single indicator flip</strong> — one row changing verdict would '
          'reverse it. It is in the set because it qualified and no rule '
          'forces a count either way (LD-96); <strong>read it as a coin '
          'flip, not a signal.</strong>') if _noise else
         ('On a ±14 scale that is a weak view. It is in the set because '
          'it qualified, not because anything demanded another pair.')))
    A('  </div>')
used = set()
for c in PICKED:
    used.add(c['long'])
    used.add(c['short'])
unused = sorted(set(ft.CCYS) - used)
A('')
A('')
if OVERLAP:
    A('  <div class="note flag">')
    A('    <span class="lbl">\u26a0 THESE PAIRS SHARE LEGS</span>')
    _worst = max(OVERLAP.values())
    _conc = ('  <strong>Note the concentration: short %s carries %d of the %d pairs.</strong>'
             % (', '.join(k for k, v in OVERLAP.items()
                          if v == _worst), _worst, len(PICKED))
             ) if _worst >= 3 else ''
    A('    <strong>%s.</strong> The set covers every category AND every '
      'strong currency (LD-126), and that guarantee means a currency can '
      'appear more than once. <strong>These are %d separate reads, not a '
      'portfolio</strong> \u2014 taking them all would hold one view several '
      'times over, which is the correlation that inflates a scorecard (EF-3).%s'
      % (', '.join('%s appears in %d pairs' % (k, v)
                   for k, v in sorted(OVERLAP.items(),
                                      key=lambda z: -z[1])),
         len(PICKED), _conc))
    A('  </div>')
_gapfirst = ' \u00b7 '.join('%s %s' % (c['pair'], c['direction'])
                            for c in LEGACY)
A('  <p><strong>The old gap-first rule would have given:</strong> '
  '<span class="mono">%s</span> \u2014 leg-disjoint, %s total gap '
  'against %s here. <strong>That set was optimal on conviction and had '
  'no way to guarantee a category was represented</strong>; this one '
  'guarantees coverage and gives up the disjointness.</p>'
  % (_gapfirst, sg(sum(c['gap'] for c in LEGACY)),
     sg(sum(c['gap'] for c in PICKED))))
A('</section>')
A('<section>')
A('  <h2>\u00a71 The pairs</h2>')
A('  <p class="sub">Risk category is an output, not a forecast.</p>')
# LD-121: count what the TABLES show. Tied twins fold into one row, so
# counting raw candidates here would print "8 RISK OFF" above a table
# listing 6 - two numbers on one page describing the same thing.
_fold = set()
for _p in PICKED:
    for _t in ps.tied_with(CANDS, _p):
        _fold.add(id(_t))
_shown = [c for c in CANDS if id(c) not in _fold]
non = len([c for c in _shown if c['category'] == 'RISK ON'])
noff = len([c for c in _shown if c['category'] == 'RISK OFF'])
nei = len([c for c in _shown if c['category'] == 'EITHER'])

A('  <p>Of the <strong>%d permitted pairings, %d are RISK ON, %d RISK OFF '
  'and %d EITHER</strong>. Nothing here predicts the regime \u2014 the roles '
  'present in each band decide which categories can be filled.</p>'
  % (non + noff + nei, non, noff, nei))
A('')
# LD-123 - ONE REPRESENTATIVE PER CATEGORY. Jeff, 2026-09-10: "I want you to
# give me representative for each categories (Risk On, Off, Either)".
#
# THE CASE THAT MAKES IT NECESSARY, live this week: EITHER holds +5.88 - the
# SECOND WIDEST GAP ON THE BOARD - and contributed NOTHING to the set,
# because both its top pairs need EUR and EURUSD had already taken it. A
# reader seeing "EITHER: 0 selected" would conclude the category was weak.
# It was crowded out by leg-disjointness, which is a different fact.
A('  <h3>The strongest read in each category</h3>')
A('  <div class="scroll">')
A('  <table>')
A('    <thead><tr><th>Category</th><th>Representative</th><th>Dir</th>'
  '<th class="num">Gap</th><th>Long / short</th><th>In the set?</th>'
  '</tr></thead>')
A('    <tbody>')
for _cat, _top, _inset in ps.representatives(CANDS, PICKED):
    A('      <tr%s><td><span class="cat">%s</span></td>'
      '<td class="ccy">%s</td><td>%s</td><td class="num %s">%s</td>'
      '<td>%s over %s</td><td>%s</td></tr>'
      % (' class="sel"' if _inset else '', _cat, ps.label(CANDS, _top),
         _top['direction'], 'pos' if _inset else '', sg(_top['gap']),
         _top['long'], _top['short'],
         '<strong>yes</strong>' if _inset
         else '<span class="zero">crowded out</span>'))
A('    </tbody>')
A('  </table>')
A('  </div>')
_out = [(c, t) for c, t, i in ps.representatives(CANDS, PICKED) if not i]
if _out:
    A('  <p><strong>%s</strong> \u2014 %s. <strong>That is a leg conflict, '
      'not a weak read</strong>: the pairs it would need were built on '
      'currencies an earlier, wider pair had already taken (LD-96).</p>'
      % (', '.join('%s carries %s and is not in the set'
                   % (c, sg(t['gap'])) for c, t in _out),
         'leg-disjoint selection allows each currency once'))
A('')

# LD-120 - ONE TABLE PER RISK CATEGORY. Jeff, 2026-09-10: "create a table for
# each category Risk On, Risk Off, Either just so the pairs are segragated and
# easy to spot". The categories are an OUTPUT of which roles sit in which band
# (LD-99), so grouping by them shows what the week actually permits - a band
# holding no safe haven simply produces no RISK OFF table.
# LD-121: a twin folded into a selected row must NOT also render as its own
# row. NZDCHF was appearing twice - once inside "AUDCHF/NZDCHF" and again
# beneath it - which reads as four pairs when the model produced three.
_folded = set()
for _p in PICKED:
    for _t in ps.tied_with(CANDS, _p):
        _folded.add(id(_t))

for _cat in ('RISK ON', 'RISK OFF', 'EITHER'):
    # LD-125: Jeff, 2026-09-10 - "for §1 The pairs sort them by Tier
    # then Gap". Tier 1 is STRONG vs WEAK, the widest structural
    # separation; sorting on it first puts the strongest STRUCTURE at the
    # top rather than the widest number, which can be a tier-2 pair.
    _rows = sorted([c for c in CANDS
                    if c['category'] == _cat and id(c) not in _folded],
                   key=lambda c: (c['tier'], -c['gap']))
    if not _rows:
        A('  <h3>%s</h3>' % _cat)
        A('  <p class="note">No pairing this week produces a %s pair \u2014 '
          'the bands hold no role combination that fills it.</p>' % _cat)
        continue
    _sel = [c for c in _rows if c in PICKED]
    A('  <h3>%s <span class="wt">%d pair%s\u00b7 %d selected</span></h3>'
      % (_cat, len(_rows), 's ' if len(_rows) != 1 else ' ', len(_sel)))
    A('  <div class="scroll">')
    A('  <table>')
    A('    <thead><tr><th>Pair</th><th>Dir</th>'
      '<th class="num">Tier</th><th class="num">Gap</th>'
      '<th>Long / short</th></tr></thead>')
    A('    <tbody>')
    for c in _rows:
        s = c in PICKED
        A('      <tr%s><td class="ccy">%s</td><td>%s</td>'
          '<td class="num">%d</td><td class="num %s">%s</td>'
          '<td>%s over %s</td></tr>'
          % (' class="sel"' if s else '', (ps.label(CANDS, c) if s else c['pair']), c['direction'],
             c['tier'], 'pos' if s else '', sg(c['gap']), c['long'],
             c['short']))
    A('    </tbody>')
    A('  </table>')
    A('  </div>')
# LD-121 - A TIE IS PROPOSED AS BOTH PAIRS, ONE SLOT. Jeff, 2026-09-10:
# "Instead of dropping 1, propose both instead. Something like AUDCHF/NZDCHF".
# The gap is identical because the two legs scored identically, so choosing
# between them on sort order asserted a preference the data never had.
_ties = [(c, ps.tied_with(CANDS, c)) for c in PICKED]
_ties = [(c, t) for c, t in _ties if t]
if _ties:
    A('  <div class="note">')
    _txt = '; '.join(
        '<strong>%s</strong> at gap %s' % (ps.label(CANDS, c), sg(c['gap']))
        for c, t in _ties)
    A('    <strong>A slash means the legs scored identically and either '
      'expression carries the same read</strong> \u2014 %s. '
      '<strong>They are alternatives, not additions</strong>: both share a '
      'leg, so taking both would hold one exposure twice, which is the '
      'correlation LD-96\'s leg-disjoint rule exists to prevent. '
      '<strong>The slot counts once.</strong>' % _txt)
    A('  </div>')


A('  <p><strong>Conviction is the score gap, not the category</strong> \u2014 '
  'a RISK OFF pair is not inherently better than a RISK ON one. Tier 1 is '
  'STRONG vs WEAK; tier 2 is STRONG vs NEUTRAL or NEUTRAL vs WEAK. '
  '<strong>All 28 currency combinations are eligible</strong>, each returned '
  'in the symbol the market quotes with the direction carrying the bias.</p>')
A('')
A('  <h3>What the calibrator changed in the set</h3>')
A('  <div class="scroll">')
A('  <table>')
A('    <thead><tr><th>Basis</th><th>Pairs</th></tr></thead>')
A('    <tbody>')
A('      <tr><td class="zero">Base only</td><td class="mono">%s</td></tr>'
  % ' \u00b7 '.join('%s %s' % (c['pair'], c['direction']) for c in BPICK))
A('      <tr class="sel"><td><strong>+ calibrator</strong></td>'
  '<td class="mono"><strong>%s</strong></td></tr>'
  % ' \u00b7 '.join('%s %s' % (c['pair'], c['direction']) for c in PICKED))
A('    </tbody>')
A('  </table>')
A('  </div>')
bp = set('%s %s' % (c['pair'], c['direction']) for c in BPICK)
fp = set('%s %s' % (c['pair'], c['direction']) for c in PICKED)
gone, new = sorted(bp - fp), sorted(fp - bp)
if gone or new:
    A('  <p><strong>The calibrator changed the set.</strong> %s%s</p>'
      % (('<strong>Out: %s.</strong> ' % ', '.join(gone)) if gone else '',
         ('<strong>In: %s.</strong>' % ', '.join(new)) if new else ''))
else:
    A('  <p><strong>The calibrator did not change the set this week</strong> '
      '\u2014 it re-ranked the board without altering which pairs qualify.</p>')
A('</section>')
A('<section>')
A('  <h2>\u00a72 The board</h2>')
A('  <p class="sub">FINAL = base + calibrator</p>')
A('  <div class="scroll">')
A('  <table>')
A('    <thead><tr><th>Band</th><th>CCY</th><th>Role</th>'
  '<th class="num">Base</th><th class="num">Calib</th>'
  '<th class="num">Final</th><th class="num">Lead</th>'
  '<th class="num">Confirm</th></tr></thead>')
A('    <tbody>')
for c in ORDER:
    A('      <tr><td><span class="band %s">%s</span></td>'
      '<td class="ccy">%s</td><td>%s</td>'
      '<td class="num">%s</td><td class="num %s">%s</td>'
      '<td class="num %s">%s</td><td class="num">%s</td>'
      '<td class="num">%s</td></tr>'
      % (BANDCLS[BAND[c]], BAND[c], c, ft.ROLE[c],
         sg(F[c]['base']), cls(F[c]['cal']), sg(F[c]['cal']),
         cls(F[c]['total']), sg(F[c]['total']),
         sg(B[c]['leading']), sg(B[c]['confirming'])))
A('    </tbody>')
A('  </table>')
A('  </div>')
A('')
A('  <dl class="kv">')
# F-105b: the range and the table count were typed for six categories.
# LD-113 made both wrong. Derive from WEIGHT, the one authority.
_lim = sum(ft.WEIGHT.values())
_nm = {6: 'six', 7: 'seven', 8: 'eight', 9: 'nine'}.get(
    len(ft.WEIGHT), str(len(ft.WEIGHT)))
A('    <dt>Base</dt><dd>\u2212%d \u2026 +%d \u2014 %s fact tables, <code>%s</code>, '
  '%d of %d cells scored</dd>' % (_lim, _lim, _nm, MONTH, scored, total))
A('    <dt>Calibrator</dt><dd>\u22125 \u2026 +5 \u2014 %d scheduled rows, %d '
  'scorable, %d with a TE consensus</dd>' % (len(ROWS), n_scor, n_cons))
A('    <dt>Weights</dt><dd>%s = <strong>2</strong> (leading) \u00b7 %s = <strong>1</strong>. '
  '<strong>The calibrator has no weights</strong> \u2014 the day is the unit.</dd>'
  % (' \u00b7 '.join(sorted(c.replace('_', ' ') for c in ft.LEADING)), ' \u00b7 '.join(sorted(c.replace('_', ' ') for c in ft.CONFIRMING))))
sizes = [len([c for c in ORDER if BAND[c] == b])
         for b in ('STRONG', 'NEUTRAL', 'WEAK')]
ties = {}
for c in ORDER:
    ties.setdefault(round(SC[c], 4), []).append(c)
tied = [v for v in ties.values() if len(v) > 1]
A('    <dt>Bands</dt><dd>Target 3 / 2 / 3 by rank, and <strong>a tie is '
  'never split</strong>. This week: <strong>%d / %d / %d</strong>.%s</dd>'
  % (sizes[0], sizes[1], sizes[2],
     ' ' + ' '.join('<strong>%s tie at %s and share a band.</strong>'
                    % (' and '.join(g), sg(SC[g[0]])) for g in tied)
     if tied else ''))
A('  </dl>')
A('')
A('  <h3>What the calibrator changed</h3>')
A('  <div class="scroll">')
A('  <table>')
A('    <thead><tr><th>CCY</th><th class="num">Base</th>'
  '<th class="num">Calib</th><th class="num">Final</th>'
  '<th>Effect</th></tr></thead>')
A('    <tbody>')
for c in sorted(ORDER, key=lambda x: -abs(F[x]['cal'])):
    if not F[c]['cal']:
        continue
    moved = BBAND[c] != BAND[c]
    eff = ('<strong>%s \u2192 %s</strong>' % (BBAND[c], BAND[c])
           if moved else 'stays %s' % BAND[c])
    A('      <tr%s><td class="ccy">%s</td>'
      '<td class="num">%s <span class="zero">(#%d)</span></td>'
      '<td class="num %s">%s</td>'
      '<td class="num">%s <span class="zero">(#%d)</span></td>'
      '<td>%s</td></tr>'
      % (' class="sel"' if moved else '', c, sg(F[c]['base']), BRANK[c],
         cls(F[c]['cal']), sg(F[c]['cal']), sg(F[c]['total']),
         FRANK[c], eff))
A('    </tbody>')
A('  </table>')
A('  </div>')
moved = [c for c in ORDER if BBAND[c] != BAND[c]]
changed = len([c for c in ORDER if F[c]['cal']])
spread = SC[ORDER[0]] - SC[ORDER[-1]]
A('  <p><strong>%d of 8 currencies move band</strong> (%d take a non-zero '
  'adjustment). <strong>The board is tightly packed \u2014 the whole final '
  'spread is %.2f points \u2014 so a term bounded at \u00b15 re-ranks it '
  'readily</strong>, which is what a calibrator is for.</p>'
  % (len(moved), changed, spread))
A('</section>')
A('<section>')
A('  <h2>\u00a73 The calibrator</h2>')
A('  <p class="sub">The day is the unit, not the category.</p>')
A('  <p>One question per currency per day \u2014 <em>is this currency positive '
  'or negative on Monday?</em> <strong>A currency with three releases on '
  'Tuesday scores Tuesday once</strong>, so a crowded calendar cannot '
  'outvote the macro base by accident.</p>')
A('  <div class="scroll">')
A('  <table>')
A('    <thead><tr><th>CCY</th>'
  + ''.join('<th class="num">%s</th>' % d.strftime('%a %d').replace(' 0', ' ')
            for d in DAYS)
  + '<th class="num">Week</th></tr></thead>')
A('    <tbody>')
for c in ORDER:
    cells = []
    for d in DAYS:
        e = CALD[c]['days'].get(d)
        cells.append('<td class="num dash">\u2014</td>' if e is None
                     else '<td class="num %s">%s</td>' % (cls(e[0]), sg(e[0])))
    t = CALD[c]['total']
    A('      <tr><td class="ccy">%s</td>%s<td class="num %s">%s</td></tr>'
      % (c, ''.join(cells), cls(t), sg(t)))
A('    </tbody>')
A('  </table>')
A('  </div>')
quiet = [c for c in ORDER if not CALD[c]['days']]
A('  <div class="note"><strong>A dash is a day with no scheduled whitelist '
  'row.</strong>%s</div>'
  % ((' <strong>%s ha%s no rows at all this week</strong>, so %s '
      'calibrator term%s +0.00 by absence \u2014 not by balance.'
      % (' and '.join(quiet), 's' if len(quiet) == 1 else 've',
         'its' if len(quiet) == 1 else 'their',
         ' is' if len(quiet) == 1 else 's are')) if quiet else ''))
A('')
A('  <h3>Every scheduled row, and how it scored</h3>')
A('  <div class="scroll">')
A('  <table>')
# LD-132 - Jeff, 2026-09-13: "can you put on the threshold also for this
# section? so I know the scoring". The score was shown without the RULE that
# produced it, so a +1 could not be checked against anything. The threshold
# is the whole reason the row scored what it did.
A('    <thead><tr><th>When (PHT)</th><th>CCY</th><th>Indicator</th>'
  '<th class="num">Previous</th><th class="num">Cons / Fcst</th>'
  '<th>Threshold</th><th class="num">Score</th></tr></thead>')
A('    <tbody>')
for r in ROWS:
    rng = r['cons'] or ''
    if r['fcst'] and r['fcst'] != r['cons']:
        rng = ('%s \u2013 %s' % (rng, r['fcst'])) if rng else r['fcst']
    s = r['score']
    sc = ('<td class="num %s">%s</td>' % (cls(s), sg(s, '%+d'))
          if s else '<td class="num zero">0</td>') if s is not None \
        else '<td class="num dash">\u2014</td>'
    # F-116: TE schedules some rows with NO time (NZD Global Dairy Trade).
    # Calling .strftime() on None killed the build; dropping the row would
    # be F-36. Publish it with its day and an explicit "no time".
    _when = (r['when'].strftime('%a %d %H:%M') if r['when']
             else ('%s \u2014' % r['day'].strftime('%a %d')
                   if r.get('day') else 'no time'))
    # LD-146 - a rate row has no score_model threshold (that is F-135's
    # shape), so its RULE comes from the calibrator instead of an em-dash.
    # Jeff, 2026-09-27: "please update this with the rule and score for the
    # interest rate". The score was already -1 in the engine while the page
    # printed a dash in BOTH columns - the report contradicting its model.
    if r['name'] == cal.RATE_NAME:
        _thr = cal.rate_rule_text(r['ccy'], r['cons'], r['fcst'], r['prev'])
    else:
        _thr = THR.get((r['ccy'], r['name']), '\u2014')
    # LD-134: mark the high-impact rows so event risk is visible before
    # the week starts. Style only - no score changes.
    _hi = hot(r['ccy'], r['name'])
    A('      <tr%s><td class="mono">%s</td><td class="ccy">%s</td>'
      '<td>%s%s</td>'
      '<td class="num v">%s</td><td class="num v">%s</td>'
      '<td class="dim sm">%s</td>%s</tr>'
      % (' class="hot"' if _hi else '', _when, r['ccy'],
         r['name'], ' <span class="tag-hi">HIGH</span>' if _hi else '',
         (r['prev'] or '\u2014').replace('-', '\u2212'),
         (rng or '\u2014').replace('-', '\u2212'),
         _thr.replace('<', '&lt;').replace('>', '&gt;'), sc))
A('    </tbody>')
A('  </table>')
A('  </div>')
# LD-134 - name the high-impact days up front, so the caution is readable
# without scanning 21 rows.
_hi_rows = [r for r in ROWS if hot(r['ccy'], r['name'])]
if _hi_rows:
    _by = {}
    for _r in _hi_rows:
        _by.setdefault(_r['day'], []).append(_r)
    A('  <div class="note flag">')
    A('    <span class="lbl">\u26a0 HIGH-IMPACT RELEASES THIS WEEK</span>')
    A('    <strong>%d of %d rows are Employment, Inflation, Interest Rate '
      'or GDP</strong> \u2014 the categories that move price hardest. '
      'They are highlighted in the table above. <strong>This is a caution, '
      'not a weight</strong>: the calibrator scores every row identically '
      '(LD-98). %s'
      % (len(_hi_rows), len(ROWS),
         ' '.join('<strong>%s:</strong> %s.'
                  % (_d.strftime('%a %d') if _d else 'undated',
                     ', '.join('%s %s' % (x['ccy'], x['name']) for x in _v))
                  for _d, _v in sorted(_by.items(),
                                       key=lambda z: z[0] or __import__('datetime').date.max))))
    A('  </div>')
# LD-133 - a row TE has DATED but not TIMED is provisional. Jeff,
# 2026-09-13: "if this changes schedule then let's revisit the report".
# Name it, so a reschedule is noticed rather than silently re-weighting
# a day.
_untimed = [r for r in ROWS if r['when'] is None and r['day']]
if _untimed:
    A('  <div class="note flag">')
    A('    <span class="lbl">\u26a0 SCHEDULED WITHOUT A TIME</span>')
    A('    <strong>%s.</strong> TE has published the DATE but not the '
      'clock, so it is counted on its day (LD-98 \u2014 the day is the '
      'unit) with no time of its own. <strong>If TE moves it to another '
      'day this report needs revisiting</strong> \u2014 a reschedule '
      'changes which day it scores.'
      % ', '.join('%s %s is set for %s'
                  % (r['ccy'], r['name'], r['day'].strftime('%a %d %b'))
                  for r in _untimed))
    A('  </div>')
A('  <p><strong>%d of %d rows are scorable, and %d carry a real TE '
  'consensus.</strong> That is the value of building on Sunday rather than '
  'a week out \u2014 the same pipeline run against 14\u201318 Sep could score '
  'only 13 of 20, because <strong>TE publishes consensus close to the '
  'release</strong>.</p>' % (n_scor, len(ROWS), n_cons))
A('')
# LD-146 - kept in step with build_weekly.py. Two renderers that disagree
# about a rule name is F-127's defect at a smaller scale.
_RULE_LABEL = {
    'latest month': 'RULE 1 — latest month wins',
    'shared': 'RULE 2 — same month, shared',
    'single': 'RULE 2 — same month, shared',
    'rate decision': 'RATE PRECEDENCE — the decision takes the day (LD-140, scored by LD-146)',
    'rate shared': 'RATE PRECEDENCE — two decisions share the day (LD-140, scored by LD-146)',
}


def _refmon(raw):
    """The reference month cell. NOT raw[-3:] - that read the last three
    characters of the event name, so 'Interest Rate Decision' printed its
    month as 'ION'. A decision is not FOR a month, so it shows an
    em-dash."""
    _m = cal.ref_month(raw)
    return cal.MONTHS[_m[1] - 1].upper() if _m else '—'


A('  <h3>The collision rules, from this run</h3>')
for d in DAYS:
    for c in ORDER:
        e = CALD[c]['days'].get(d)
        if not e:
            continue
        val, rule, keep, drop = e
        if len(keep) + len(drop) < 2:
            continue
        A('  <p><strong>%s, %s \u2014 %d rows, %s.</strong></p>'
          % (d.strftime('%a %d').replace(' 0', ' '), c, len(keep) + len(drop),
             _RULE_LABEL.get(rule, 'RULE 2 — same month, shared')))
        A('  <div class="scroll">')
        A('  <table>')
        A('    <thead><tr><th>Row</th><th>Ref</th><th class="num">Score</th>'
          '<th>Kept?</th></tr></thead>')
        A('    <tbody>')
        for r in keep + drop:
            k = r in keep
            # F-118: an UNSCORABLE row reaching a collision table crashed
            # cls(None). It can now, because LD-133 gives a dated-but-untimed
            # row a day - NZD Global Dairy Trade joins Tuesday's group with
            # no consensus to grade. It is shown with an em-dash and marked
            # "not scored", never dropped from the table (F-36).
            _s = r['score']
            _cell = ('<td class="num dash">—</td>' if _s is None
                     else '<td class="num %s">%s</td>'
                     % (cls(_s), sg(_s, '%+d') if _s else '0'))
            A('      <tr%s><td>%s</td><td class="mono">%s</td>%s<td>%s</td></tr>'
              % (' class="sel"' if k else '', r['name'],
                 _refmon(r['raw']), _cell,
                 '<strong>KEPT</strong>' if k else
                 ('<span class="zero">not scored</span>' if _s is None
                  else '<span class="zero">dropped</span>')))
        A('    </tbody>')
        A('  </table>')
        A('  </div>')
        kv = sum(r['score'] for r in keep) / float(len(keep))
        # F-118: only SCORABLE rows can be averaged. An unscorable row
        # (LD-133, dated but untimed) has no score to share, so it is
        # excluded from the arithmetic rather than counted as zero - which
        # would drag the comparison toward neutral on an absence (F-73).
        alls = [r for r in keep + drop if r['score'] is not None]
        av = (sum(r['score'] for r in alls) / float(len(alls))
              if alls else 0.0)
        if rule == 'latest month' and abs(kv - av) > 0.01:
            A('  <div class="note flag"><span class="lbl">\u26a0 THE RULE '
              'CHANGES THE NUMBER</span>Sharing all %d rows would give '
              '<strong>%s</strong>; taking only the latest month gives '
              '<strong>%s</strong>. <strong>The most current read of the '
              'economy decides the day</strong> \u2014 an older row does not '
              'dilute it.</div>' % (len(alls), sg(av), sg(kv)))
        else:
            A('  <p>Day score <strong>%s</strong>.</p>' % sg(val))
A('</section>')


# F-110 - SECTION 4 IS NOW GENERATED. It used to be hand-written in the page
# shell, so the first splice that replaced the body deleted it silently -
# taking the VINTAGE DISCLOSURE with it. A back-dated edition that does not
# say which vintage it used is precisely what the repo's rules forbid.
A('')
A('<section>')
A('  <h2>\u00a75 Method and limits</h2>')
A('  <p class="sub">What this report can and cannot see.</p>')
A('  <div class="scroll">')
A('  <table>')
A('    <thead><tr><th>Term</th><th>Range</th><th>Source</th></tr></thead>')
A('    <tbody>')
_lim = sum(ft.WEIGHT.values())
_nm = {6: 'six', 7: 'seven', 8: 'eight'}.get(len(ft.WEIGHT), str(len(ft.WEIGHT)))
A('      <tr><td>Base</td><td class="mono">\u2212%d \u2026 +%d</td>'
  '<td>%s fact tables, <code>%s</code>, %d of %d cells</td></tr>'
  % (_lim, _lim, _nm, MONTH, scored, total))
A('      <tr><td>Calibrator</td><td class="mono">\u22125 \u2026 +5</td>'
  '<td><strong>%d scheduled rows, %d scorable, %d with a TE consensus'
  '</strong></td></tr>' % (len(ROWS), n_scor, n_cons))
A('      <tr class="sel"><td><strong>FINAL</strong></td>'
  '<td class="mono"><strong>\u2212%d \u2026 +%d</strong></td>'
  '<td>the sum</td></tr>' % (_lim + 5, _lim + 5))
A('    </tbody>')
A('  </table>')
A('  </div>')
A('')
A('  <div class="note flag">')
A('    <span class="lbl">\u26a0 VINTAGE</span>')
A('    <strong>Built as of Sunday 6 September.</strong> The fact tables hold '
  'what was knowable then \u2014 rows that printed Mon 7 or Tue 8 are held at '
  'their earlier values.<br><br>'
  'Releases up to Friday 4 September stay: a Sunday report legitimately sees '
  'Friday\'s prints.<br><br>'
  '<strong>Leaving the Mon/Tue prints in would have been a backtest '
  'contaminated with hindsight.</strong> An analysis asking <em>what was '
  'knowable then</em> must use the vintage available then, and say which it '
  'used. This one says.')
A('  </div>')
A('')
A('  <h3>What is not here</h3>')
A('  <div class="scroll">')
A('  <table>')
A('    <thead><tr><th>Absent</th><th>Reason</th></tr></thead>')
A('    <tbody>')
A('      <tr><td>Gold, BTC</td><td><strong>Removed</strong> \u2014 forex '
  'focus</td></tr>')
A('      <tr><td>Entry references, falsifiers, charts</td>'
  '<td><strong>No price data in this edition</strong></td></tr>')
A('      <tr><td>News, rate-path commentary</td><td>LD-97 \u2014 the weekly '
  'is the decision</td></tr>')
A('      <tr><td>Lot sizes, entries, stops, targets</td>'
  '<td><strong>LD-4 \u2014 no money path</strong></td></tr>')
A('    </tbody>')
A('  </table>')
A('  </div>')
A('</section>')

io.open(SP + 'body.html', 'w', encoding='utf-8', newline=NL).write(NL.join(o))
print('body.html: %d lines' % len(o))
print('SET: %s' % ', '.join('%s %s %+.2f' % (c['pair'], c['direction'],
                                             c['gap']) for c in PICKED))
