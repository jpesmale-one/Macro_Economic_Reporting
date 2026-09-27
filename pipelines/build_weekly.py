# -*- coding: utf-8 -*-
"""The weekly for 7-11 Sep, built as of SUNDAY 6 SEPTEMBER.

Jeff, 2026-09-09: "Make it as if it's September 6 Sunday. Our cycle is every
Sunday to Saturday. Since we don't have the report yet for this week, lets
build it first. Then let's look at Next week on the Weekend."

VINTAGE. The fact tables were rolled back to what was knowable on 6 Sep -
four rows that printed Mon 7 / Tue 8 reverted to their Aug-26 values. The
five that printed on or before Friday 4 Sep stay: a Sunday report sees
Friday's releases.
"""
import io, os, re, sys, glob, datetime as dt
os.chdir(r'c:/Users/jpesm/OneDrive/Documents/GitHub/Macro_Economic_Reporting')
sys.path.insert(0, os.path.join(os.getcwd(), 'pipelines'))
NL = chr(10)
import fact_tables as ft
import pair_select as ps
import calibrator as cal
import score_model as _sm

# LD-132 - the threshold each calibrator row is graded against.
THR = dict(((_sm.LABEL[_r[1]], _r[2]), _r[6]) for _r in _sm.ROWS)

# LD-134 - high-impact categories, flagged as a caution (never a weight).
HIGH_IMPACT = ('Employment', 'Inflation', 'Interest_Rate', 'GDP')
CAT = dict(((_sm.LABEL[_r[1]], _r[2]), _r[0]) for _r in _sm.ROWS)


def hot(ccy, name):
    return CAT.get((ccy, name)) in HIGH_IMPACT

CAP = sorted(glob.glob('data/raw/calendar/2026-09-27_*_cal_full.json'))[-1]
START, END = '2026-09-28', '2026-10-02'

F = ps.final_scores(CAP, START, END)
SC = dict((c, F[c]['total']) for c in F)
BAND, ORDER = ft.bands(SC)
CANDS = ps.candidates(SC, BAND)
# *** F-127 - TWO SELECTORS, TWO DIFFERENT SETS.
#
# build_weekly used ps.select() - the LEG-DISJOINT rule - while gen_page.py
# used ps.the_set(), which is LD-126. On 2026-09-20 they disagreed outright:
#
#     ps.select()  GBPAUD, EURUSD, CADJPY          (3 pairs, leg-disjoint)
#     the_set()    GBPAUD, GBPUSD, EURAUD, AUDJPY  (4 pairs, LD-126)
#
# The MD and the HTML would have published DIFFERENT SETS for the same
# edition, each internally consistent. LD-126 dropped leg-disjointness
# deliberately ("one tier-1 read per category AND per strong currency"), so
# the_set() is the authority and select() is the superseded rule.
#
# The same shape as F-122: one artefact regenerated, another left on an old
# path, and every number in both of them correct.
SEL = ps.the_set(CANDS, BAND, SC)
PICKED = [p for p, _ in SEL]
WHY = dict((p['pair'], why) for p, why in SEL)
CALD = cal.calibrate(CAP, START, END)
ROWS = cal.week_rows(CAP, START, END)
MONTH = ft.latest_month()
scored, total = ft.coverage(MONTH)
b = ft.base_scores(MONTH)

BSC = dict((c, F[c]['base']) for c in F)
BBAND, BORDER = ft.bands(BSC)
BPICK = [p for p, _ in ps.the_set(ps.candidates(BSC, BBAND), BBAND, BSC)]

TOP = ORDER[0]
BOT = ORDER[-1]
BEST = PICKED[0]
# currencies with no scheduled row at all this week
QUIET = [c for c in ORDER if not CALD[c]['days']]
# The interesting mover is one whose BAND changed, not merely the biggest
# absolute adjustment - CHF took +1.00 and stayed #1, which is not a story.
# Fall back to rank change, then to raw size.
# base-rank vs final-rank, for the "what changed" table
BRANK = {c: i + 1 for i, c in enumerate(BORDER)}
FRANK = {c: i + 1 for i, c in enumerate(ORDER)}
MOVED = [c for c in ORDER if BBAND[c] != BAND[c]]
MOVER = max(ORDER, key=lambda c: (
    BBAND[c] != BAND[c],
    abs(BRANK[c] - FRANK[c]),
    abs(F[c]['cal'])))

n_cons = len([r for r in ROWS if r['cons']])
n_scor = len([r for r in ROWS if r['score'] is not None])

# LD-130 - the published pages, so the repo copy carries its own pointers.
ARTIFACT = 'https://claude.ai/artifact/DU6Y3sC2T6eoPRu7Jkx82T'
RETRO = 'https://claude.ai/artifact/4PNbyCZETwNq19pTjepWP1'

out = []
A = out.append

A('<!--edition')
A('date: 2026-09-27')
A('title: Week of 28 Sep&ndash;2 Octtember 2026 &middot; WEEKLY &middot; '
  'Sunday 27 Sep')
# LD-131 - A NEW EDITION STARTS AT r1 AND UNSEALED. Reading STATE.md was
# right while rebuilding ONE edition (LD-130), but on a NEW week it
# inherits the PREVIOUS edition's identity - this build stamped r5/SEALED
# on a report Jeff had never seen. STATE.md is the authority on the
# CURRENT edition, and this is not it until the manifest is updated.
# LD-130 vs LD-131. r1 is right for a NEW edition. This edition already
# PUBLISHED at r1, and F-121 then changed its conclusions - GBP went
# +4.19 -> +8.19 and took the top slot - so the rebuild is a REVISION of
# a report Jeff has already read, not a new one. Reading the existing
# file's revision keeps the two rules from fighting: new editions still
# start at r1 (nothing on disk to read), a rebuild advances.
OUT = 'reports/2026/Q3/2026-09-27_weekly.md'
_rev = 1
if os.path.exists(OUT):
    for _l in io.open(OUT, encoding='utf-8').read()[:600].splitlines():
        if _l.startswith('revision: r'):
            # NOT split('r') - that splits on the 'r' in "revision" and
            # yields 'evision:', so every rebuild silently stayed at r1.
            try:
                _rev = int(_l.split(':', 1)[1].strip().lstrip('rR')) + 1
            except ValueError:
                pass
            break
A('revision: r%d' % _rev)
A('seal: UNSEALED')
A('type: WEEKLY')
A('eyebrow: Macro Economic Reporting &middot; the REVAMPED weekly &mdash; '
  'selection for the 28 Sep&ndash;2 Oct cycle')
A('chip: <b>%d pairs</b> &middot; base &plus; calibrator' % len(PICKED))
A('chip: <b>%s %s</b> &middot; gap <b>%+.2f</b>'
  % (BEST['pair'], BEST['direction'], BEST['gap']))
A('chip: <b class="dn">%d of %d rows scorable</b>' % (n_scor, len(ROWS)))
# LD-130 - Jeff, 2026-09-13: "can you put the URL of our report in the weekly
# MD file as well? so If I close it I know where I can open it again".
# THE MARKDOWN IS THE DURABLE COPY - it lives in the repo and survives every
# session, while the URL had only ever lived in conversation. Closing the tab
# lost the only pointer to the published page.
if ARTIFACT:
    A('url: %s' % ARTIFACT)
A('-->')
A('')
if ARTIFACT:
    A('> **Published page** &middot; %s' % ARTIFACT)
A("> **Last week&#39;s retrospective** &middot; %s" % RETRO)
A('')
A('<!--exec-->')
A('')
_nm = {6: 'six', 7: 'seven', 8: 'eight'}.get(len(ft.WEIGHT), str(len(ft.WEIGHT)))
A('**Selection for the 14\u201318 September cycle, built Sunday 27 September.** '
  'The second weekly on the revamped model \u2014 %s fact '
  'tables, leading indicators at weight 2, a day-scored week-ahead '
  'calibrator, and no room or event-risk gate anywhere in selection.' % _nm)
A('')
A('**THE SET:**')
A('')
for i, c in enumerate(PICKED, 1):
    A('**%d. %s %s** \u2014 %s, gap **%+.2f** (long %s / short %s)'
      % (i, c['pair'], c['direction'], c['category'], c['gap'],
         c['long'], c['short']))
A('')
A('**%s %s carries the widest gap on the board at %+.2f** \u2014 **%s is '
  'top at %+.2f and %s is bottom at %+.2f.**'
  % (BEST['pair'], BEST['direction'], BEST['gap'],
     TOP, SC[TOP], BOT, SC[BOT]))
A('')
A('**\u26a0 %s TAKES THE LARGEST CALIBRATOR ADJUSTMENT: %+.2f.** It ranks '
  '**#%d on base scores at %+.2f** and **#%d after the week ahead at '
  '%+.2f**%s'
  % (MOVER, F[MOVER]['cal'], BRANK[MOVER], F[MOVER]['base'],
     FRANK[MOVER], F[MOVER]['total'],
     ' \u2014 **moving it from %s to %s.**' % (BBAND[MOVER], BAND[MOVER])
     if BBAND[MOVER] != BAND[MOVER] else '.'))
A('')
_unused = sorted(set(ft.CCYS) - set(
    [c['long'] for c in PICKED] + [c['short'] for c in PICKED]))
A('**%d pairs, and nothing forced that number** (LD-96). **%s.**'
  % (len(PICKED),
     ('%s go unused' % ' and '.join(_unused)) if _unused
     else 'Every currency is used'))
A('')
A('---')
A('')

# ------------------------------------------------------------------ 1
A('## \u00a71 \u2014 The board')
A('')
A('| Band | CCY | Role | Base | Calib | **FINAL** | Leading | Confirming |')
A('|---|---|---|---|---|---|---|---|')
for c in ORDER:
    d = b[c]
    bold = '**%s**' % c if BAND[c] != 'NEUTRAL' else c
    cv = F[c]['cal']
    cs = '**%+.2f**' % cv if cv else '%+.2f' % cv
    A('| %s | %s | %s | %+.2f | %s | **%+.2f** | %+.2f | %+.2f |'
      % (BAND[c], bold, ft.ROLE[c], F[c]['base'], cs, F[c]['total'],
         d['leading'], d['confirming']))
A('')
_lim2 = sum(ft.WEIGHT.values())
A('**`FINAL = base + calibrator`.** **Base spans \u2212%d .. +%d** from the '
  '%s fact tables (`%s`, %d of %d cells scored); **the calibrator spans '
  '\u22125 .. +5** from the five trading days ahead.'
  % (_lim2, _lim2, _nm, MONTH, scored, total))
A('')
A('**Category weights are in the BASE only: %s weigh 2** (leading), '
  '**%s weigh 1** (confirming). **The calibrator has no weights** \u2014 '
  'the day is the unit (LD-98).' % (' \u00b7 '.join(sorted(c.replace('_',' ') for c in ft.LEADING)), ' \u00b7 '.join(sorted(c.replace('_',' ') for c in ft.CONFIRMING))))
A('')
_sizes = [len([c for c in ORDER if BAND[c] == b])
          for b in ('STRONG', 'NEUTRAL', 'WEAK')]
_ties = {}
for c in ORDER:
    _ties.setdefault(round(SC[c], 4), []).append(c)
_tied = [v for v in _ties.values() if len(v) > 1]
A('**Bands target 3 / 2 / 3 by rank and a tie is never split** (LD-100). '
  '**This week the board comes out %d / %d / %d.**%s'
  % (_sizes[0], _sizes[1], _sizes[2],
     ' ' + ' '.join('**%s tie at %+.2f, so they share a band.**'
                    % (' and '.join(g), SC[g[0]]) for g in _tied)
     if _tied else ''))
A('')
A('### \u26a0 What the calibrator changed')
A('')
A('| CCY | Base | Calib | Final | Effect |')
A('|---|---|---|---|---|')
for c in sorted(ORDER, key=lambda x: -abs(F[x]['cal'])):
    if not F[c]['cal']:
        continue
    _eff = ('**%s \u2192 %s**' % (BBAND[c], BAND[c])
            if BBAND[c] != BAND[c] else 'stays %s' % BAND[c])
    A('| **%s** | %+.2f (#%d) | **%+.2f** | %+.2f (#%d) | %s |'
      % (c, F[c]['base'], BRANK[c], F[c]['cal'], F[c]['total'],
         FRANK[c], _eff))
A('')
_spread = SC[ORDER[0]] - SC[ORDER[-1]]
_changed = len([c for c in ORDER if F[c]['cal']])
A('**%d of 8 currencies move band on the week ahead** (%d take a non-zero '
  'adjustment). **The board is tightly packed — the whole final spread '
  'is %.2f points — so a term bounded at ±5 re-ranks it readily**, '
  'which is what a calibrator is for.' % (len(MOVED), _changed, _spread))
A('')

# ------------------------------------------------------------------ 2
A('## \u00a72 \u2014 The calibrator, day by day (LD-98)')
A('')
A('**The DAY is the unit.** One question per currency per day \u2014 *is this '
  'currency positive or negative on Monday?* **A currency with three '
  'releases on Tuesday scores Tuesday once**, so a crowded calendar cannot '
  'outvote the macro base by accident.')
A('')
A('| CCY | Mon 7 | Tue 8 | Wed 9 | Thu 10 | Fri 11 | **Week** |')
A('|---|---|---|---|---|---|---|')
days = [dt.date(2026, 9, d) for d in (7, 8, 9, 10, 11)]
for c in ORDER:
    cells = []
    for d in days:
        e = CALD[c]['days'].get(d)
        cells.append('\u2014' if e is None else
                     ('**%+.2f**' % e[0] if e[0] else '%+.2f' % e[0]))
    A('| **%s** | %s | **%+.2f** |'
      % (c, ' | '.join(cells), CALD[c]['total']))
A('')
A('**A dash is a day with no scheduled whitelist row.**%s'
  % ((' **%s ha%s no rows at all this week**, so %s calibrator term%s '
      '+0.00 by absence \u2014 not by balance.'
      % (' and '.join(QUIET), 's' if len(QUIET) == 1 else 've',
         'its' if len(QUIET) == 1 else 'their',
         ' is' if len(QUIET) == 1 else 's are')) if QUIET else ''))
A('')
A('### Every scheduled row, and how it scored')
A('')
A('| When (PHT) | CCY | Indicator | Previous | Cons / Fcst | Threshold | Score |')
A('|---|---|---|---|---|---|---|')
for r in sorted(ROWS, key=lambda x: (x['day'] or dt.date.max, x['when'] is None,
                                  x['when'].strftime('%H:%M') if x['when'] else '')):
    rng = r['cons'] if r['cons'] else ''
    if r['fcst'] and r['fcst'] != r['cons']:
        rng = ('%s \u2013 %s' % (rng, r['fcst'])) if rng else r['fcst']
    sc = ('**%+d**' % r['score']) if r['score'] else (
        '0' if r['score'] == 0 else '\u2014')
    # F-116: a row can have NO published time - NZD Global Dairy Trade is
    # scheduled by TE without one. The old code called .strftime() on None
    # and killed the whole build. NO EVENT IS EVER DROPPED (F-36): the row
    # is published with its day and an explicit "no time", never hidden.
    _when = (r['when'].strftime('%a %d %H:%M') if r['when']
             else ('%s \u2014' % r['day'].strftime('%a %d')
                   if r.get('day') else 'no time'))
    # LD-132: publish the THRESHOLD alongside the score - the rule that
    # produced it, so a +1 can be checked rather than taken on trust.
    _thr = THR.get((r['ccy'], r['name']), '\u2014')
    # LD-134: mark high-impact rows (Employment, Inflation, Interest Rate,
    # GDP) as a caution. No score changes - the calibrator is unaffected.
    _hi = hot(r['ccy'], r['name'])
    A('| %s | %s | %s%s | %s | %s | `%s` | %s |'
      % (_when, r['ccy'], r['name'],
         ' **\u26a0 HIGH**' if _hi else '',
         r['prev'] or '\u2014', rng or '\u2014', _thr, sc))
A('')
A('**%d of %d rows are scorable, and %d carry a real TE consensus.** '
  '**That is the value of building on Sunday rather than a week out** \u2014 '
  'the same pipeline run against 14\u201318 Sep could score only 13 of 20, '
  'because **TE publishes consensus close to the release.**'
  % (n_scor, len(ROWS), n_cons))
A('')
A('### The collision rules, generated from the run')
A('')
_days = sorted(set(r['day'] for r in ROWS if r['day']))
for _d in _days:
    for _c in ORDER:
        _e = CALD[_c]['days'].get(_d)
        if not _e:
            continue
        _val, _rule, _keep, _drop = _e
        if len(_keep) + len(_drop) < 2:
            continue
        A('**%s, %s \u2014 %d rows, %s.**'
          % (_d.strftime('%a %-d') if os.name != 'nt'
             else _d.strftime('%a %d').replace(' 0', ' '), _c,
             len(_keep) + len(_drop),
             'RULE 1 \u2014 latest month wins' if _rule == 'latest month'
             else 'RULE 2 \u2014 same month, shared'))
        A('')
        A('| Row | Ref month | Score | Kept? |')
        A('|---|---|---|---|')
        for _r in _keep + _drop:
            _kept = _r in _keep
            _mon = (_r['raw'] or '')[-3:].upper()
            # F-118: an unscorable row shows an em-dash, not a 0 - a 0 is a
            # NEUTRAL verdict and this row has no verdict at all.
            _sc = ('—' if _r['score'] is None
                   else ('**%+d**' % _r['score'] if _r['score'] else '0'))
            A('| %s | %s | %s | %s |'
              % (_r['name'], '**%s**' % _mon if _kept else _mon, _sc,
                 '**KEPT**' if _kept else
                 ('not scored' if _r['score'] is None else 'dropped')))
        A('')
        # F-118: only SCORABLE rows can be averaged (LD-133).
        # F-118: only SCORABLE rows can be averaged. An unscorable row
        # (LD-133 - dated but untimed) has no score to share, so it is
        # excluded from the arithmetic rather than counted as zero, which
        # would drag the comparison toward neutral on an absence (F-73).
        _sk = [r for r in _keep if r['score'] is not None]
        _sa = [r for r in _keep + _drop if r['score'] is not None]
        if not _sk or not _sa:
            continue
        _kv = sum(r['score'] for r in _sk) / float(len(_sk))
        _all = _sa
        _av = sum(r['score'] for r in _all) / float(len(_all))
        A('**Day score %+.2f.**' % _val)
        if _rule == 'latest month' and abs(_kv - _av) > 0.01:
            A('')
            A('**\u26a0 THE RULE CHANGES THE NUMBER HERE.** Sharing all %d rows '
              'would give **%+.2f**; taking only the latest month gives '
              '**%+.2f**. **The most current read of the economy decides the '
              'day** \u2014 an older row does not dilute it.'
              % (len(_all), _av, _kv))
        elif _rule == 'latest month':
            A('')
            A('**The rule did not change the number here** \u2014 the dropped '
              'rows happen to score the same. **It changed which row the '
              'number came from**, which matters the first week they '
              'disagree.')
        A('')

# ------------------------------------------------------------------ 3
A('## \u00a73 \u2014 The pairs')
A('')
_on = len([c for c in CANDS if c['category'] == 'RISK ON'])
_off = len([c for c in CANDS if c['category'] == 'RISK OFF'])
_ei = len([c for c in CANDS if c['category'] == 'EITHER'])
A('**Risk category is an OUTPUT, not a forecast (LD-99).** Of the **%d '
  'permitted pairings, %d are RISK ON, %d RISK OFF and %d EITHER.** '
  '**Nothing here predicts the regime** \u2014 the roles present in each band '
  'decide which categories can be filled.' % (len(CANDS), _on, _off, _ei))
A('')
A('| Pair | Dir | Category | Tier | **Gap** | Long / short |')
A('|---|---|---|---|---|---|')
for c in CANDS:
    sel = c in PICKED
    nm = '**%s**' % c['pair'] if sel else c['pair']
    g = '**%+.2f**' % c['gap'] if sel else '%+.2f' % c['gap']
    A('| %s | %s | %s | %d | %s | %s over %s |'
      % (nm, c['direction'], c['category'], c['tier'], g,
         c['long'], c['short']))
A('')
A('**Conviction is the SCORE GAP, not the category** \u2014 a RISK OFF pair is '
  'not inherently better than a RISK ON one. **Tier 1 is STRONG vs WEAK; '
  'tier 2 is STRONG vs NEUTRAL or NEUTRAL vs WEAK.**')
A('')
A('**All 28 currency combinations are eligible** (LD-101), each returned in '
  'the symbol the market quotes with the direction carrying the bias.')
A('')
A('### \u2705 SELECTED')
A('')
A('| # | Pair | Bias | Category | **Gap** | Long | Short |')
A('|---|---|---|---|---|---|---|')
for i, c in enumerate(PICKED, 1):
    A('| **%d** | **%s** | **%s** | %s | **%+.2f** | %s %+.2f | %s %+.2f |'
      % (i, c['pair'], c['direction'], c['category'], c['gap'],
         c['long'], SC[c['long']], c['short'], SC[c['short']]))
A('')
used = set()
for c in PICKED:
    used.add(c['long'])
    used.add(c['short'])
# F-128 - THE PAGE ASSERTED LD-19 AFTER LD-126 REPEALED IT.
# This line said "No currency is used twice (LD-19)" on an edition where
# GBP appears twice and AUD three times. LD-126 dropped leg-disjointness
# deliberately; the sentence survived the rule it described. An overlap is
# now a DISCLOSURE, not a violation - the same flagged note pair_select
# already returns.
_ov = ps.leg_overlap(PICKED)
A('**%d pairs. %d currencies used; %s unused.** %s **No rule forced a '
  'particular number** (LD-96).'
  % (len(PICKED), len(used), ' '.join(sorted(set(ft.CCYS) - used)),
     ('**%s** appears in more than one pair (%s) — LD-126 covers every '
      'category and every strong currency, so legs may repeat; the set is '
      'that many reads on overlapping exposure, not independent ones.'
      % (', '.join('%s×%d' % (k, v) for k, v in sorted(_ov.items())),
         'leg overlap')) if _ov else
     'No currency is used twice this week.'))
A('')
_last = PICKED[-1]
if len(PICKED) > 1 and _last['gap'] < 2.0:
    # LD-108: under 0.50 is noise, not a weak view. Say which.
    _noise = _last['gap'] < 0.50
    A(('**⚠ THE LAST PAIR IS NOISE, NOT A VIEW.** ' if _noise else
       '**⚠ THE TAIL IS THIN AND WORTH NAMING.** ')
      + '**%s %s rests on a %+.2f gap** — %s at %+.2f against %s at '
        '%+.2f. %s'
      % (_last['pair'], _last['direction'], _last['gap'],
         _last['long'], SC[_last['long']], _last['short'],
         SC[_last['short']],
         ('**On a ±14 scale that is inside the rounding of a single '
          'indicator flip** — one row changing verdict would reverse it. '
          'It is in the set because it qualified and no rule forces a count '
          'either way (LD-96); **read it as a coin flip, not a signal.**')
         if _noise else
         ('**On a ±14 scale that is a weak view**, and it is in the set '
          'because it qualified, not because anything demanded another '
          'pair.')))
A('')
A('**What the calibrator changed in the SET:**')
A('')
A('| | Base only | **Base + calibrator** |')
A('|---|---|---|')
A('| Pairs | %s | **%s** |'
  % (', '.join('%s %s' % (c['pair'], c['direction']) for c in BPICK),
     ', '.join('%s %s' % (c['pair'], c['direction']) for c in PICKED)))
A('')
_bp = set('%s %s' % (c['pair'], c['direction']) for c in BPICK)
_fp = set('%s %s' % (c['pair'], c['direction']) for c in PICKED)
_gone, _new = sorted(_bp - _fp), sorted(_fp - _bp)
if _gone or _new:
    A('**The calibrator changed the set.** %s%s'
      % (('**Out: %s.** ' % ', '.join(_gone)) if _gone else '',
         ('**In: %s.**' % ', '.join(_new)) if _new else ''))
else:
    A('**The calibrator did not change the set this week** \u2014 it re-ranked '
      'the board without altering which pairs qualify.')
A('')

# ------------------------------------------------------------------ 4
A('## \u00a74 \u2014 Method and limits')
A('')
A('| Term | Range | Source |')
A('|---|---|---|')
# LD-130: 'six fact tables' and the -9..+9 were typed, and GDP leaving the
# base on 2026-09-10 made both wrong. Derive from the weight table.
_nm = {6: 'six', 7: 'seven', 8: 'eight'}.get(len(ft.WEIGHT), str(len(ft.WEIGHT)))
_lim = sum(ft.WEIGHT.values())
A('| Base | \u2212%d .. +%d | %s fact tables, `%s`, %d of %d cells'
  % (_lim, _lim, _nm, MONTH, scored, total) + ' |')
A('| Calibrator | \u22125 .. +5 | **%d scheduled rows, %d scorable, %d with '
  'a TE consensus** |' % (len(ROWS), n_scor, n_cons))
A('| **FINAL** | \u221214 .. +14 | the sum |')
A('')
A('### \u26a0 Vintage \u2014 what this report can and cannot see')
A('')
A('**Built as of Sunday 6 September.** The fact tables were rolled back to '
  'that vintage: **four rows that printed Mon 7 or Tue 8 were reverted to '
  'their August values** \u2014 AUD Job Ads, CHF Unemployment, AUD NAB '
  'Business Confidence and AUD Westpac Consumer Confidence.')
A('')
A('**The five that printed on or before Friday 4 September stay** \u2014 a '
  'Sunday report legitimately sees Friday\'s releases, including **NFP at '
  '+162K against a +56K consensus** and **CAD Employment Change at '
  '\u221241.7K against +15K.**')
A('')
A('**Why this matters: leaving the Mon/Tue prints in would have been a '
  'backtest contaminated with hindsight.** The repo\'s own rule is that an '
  'analysis asking *what was knowable then* must use the vintage available '
  'then, and say which it used. **This one says.**')
A('')
A('### What is not here')
A('')
A('| Absent | Reason |')
A('|---|---|')
A('| Gold, BTC | **Removed** \u2014 forex focus |')
A('| Entry references, falsifiers, charts | **No price data** \u2014 '
  'TradingView was running without CDP, so 9222 never listened |')
A('| News, rate-path commentary | **LD-97** \u2014 the weekly is the decision |')
A('| Lot sizes, entries, stops, targets | **LD-4** \u2014 no money path |')
A('')
A('### Open')
A('')
A('**1. RULE 1a is still unratified.** It did not fire this week \u2014 every '
  'row that collided was scorable \u2014 **but it will fire on the 14\u201318 Sep '
  'build**, where JPY Wed 16 has an unscorable AUG row against a scorable '
  'JUL one.')
A('')
A('**2. No guard suite for the new pipelines.** `render_edition.py`\'s '
  'guards target the old section structure. **This edition was checked by '
  'reading, which the old model taught is not enough.**')
A('')
A('---')
A('')
A('## \u00a75 \u2014 Publish state')
A('')
A('**PREP, UNSEALED.** **Selection for 7\u201311 Sep, built on Sunday 6 Sep '
  'vintage.**')
A('')
A('**Next: the 14\u201318 Sep selection, at the weekend** \u2014 Jeff, 2026-09-09: '
  '*"Then let\'s look at Next week on the Weekend."* **Running the '
  'calibrator on Sunday rather than midweek is what gives it 12 of 12 '
  'scorable rows instead of 13 of 20.**')
A('')

p = OUT
io.open(p, 'w', encoding='utf-8', newline='').write(NL.join(out))
print('wrote %s (%d lines)' % (p, len(out)))
print()
print('base-only :', ', '.join('%s %s' % (c['pair'], c['direction']) for c in BPICK))
print('with calib:', ', '.join('%s %s' % (c['pair'], c['direction']) for c in PICKED))
print('rows: %d scorable of %d, %d with consensus' % (n_scor, len(ROWS), n_cons))
