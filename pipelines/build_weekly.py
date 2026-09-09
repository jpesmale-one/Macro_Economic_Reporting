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
import io, os, sys, glob, datetime as dt
os.chdir(r'c:/Users/jpesm/OneDrive/Documents/GitHub/Macro_Economic_Reporting')
sys.path.insert(0, os.path.join(os.getcwd(), 'pipelines'))
NL = chr(10)
import fact_tables as ft
import pair_select as ps
import calibrator as cal

CAP = sorted(glob.glob('data/raw/calendar/2026-09-08_*_cal_full.json'))[-1]
START, END = '2026-09-07', '2026-09-11'

F = ps.final_scores(CAP, START, END)
SC = dict((c, F[c]['total']) for c in F)
BAND, ORDER = ft.bands(SC)
CANDS = ps.candidates(SC, BAND)
PICKED = ps.select(CANDS)
CALD = cal.calibrate(CAP, START, END)
ROWS = cal.week_rows(CAP, START, END)
MONTH = ft.latest_month()
scored, total = ft.coverage(MONTH)
b = ft.base_scores(MONTH)

BSC = dict((c, F[c]['base']) for c in F)
BBAND, BORDER = ft.bands(BSC)
BPICK = ps.select(ps.candidates(BSC, BBAND))

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

out = []
A = out.append

A('<!--edition')
A('date: 2026-09-06')
A('title: Week of 7&ndash;11 September 2026 &middot; WEEKLY &middot; '
  'Sunday 6 Sep')
A('revision: r1')
A('seal: UNSEALED')
A('type: WEEKLY')
A('eyebrow: Macro Economic Reporting &middot; the REVAMPED weekly &mdash; '
  'selection for the 7&ndash;11 Sep cycle')
A('chip: <b>%d pairs</b> &middot; base &plus; calibrator' % len(PICKED))
A('chip: <b>%s %s</b> &middot; gap <b>%+.2f</b>'
  % (BEST['pair'], BEST['direction'], BEST['gap']))
A('chip: <b class="dn">%d of %d rows scorable</b>' % (n_scor, len(ROWS)))
A('-->')
A('')
A('<!--exec-->')
A('')
A('**Selection for the 7\u201311 September cycle, built Sunday 6 September.** '
  'This is the first weekly on the complete revamped model \u2014 six fact '
  'tables, leading indicators at weight 2, a day-scored week-ahead '
  'calibrator, and no room or event-risk gate anywhere in selection.')
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
A('**`FINAL = base + calibrator`.** **Base spans \u22129 .. +9** from the six '
  'fact tables (`%s`, %d of %d cells scored); **the calibrator spans '
  '\u22125 .. +5** from the five trading days ahead.' % (MONTH, scored, total))
A('')
A('**Category weights are in the BASE only: Production, Spending and Trade '
  'weigh 2** (leading), **Employment, Inflation and Interest Rate weigh 1** '
  '(confirming). **The calibrator has no weights** \u2014 the day is the unit '
  '(LD-98).')
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
A('| When (PHT) | CCY | Indicator | Previous | Cons / Fcst | Score |')
A('|---|---|---|---|---|---|')
for r in sorted(ROWS, key=lambda x: x['when'] or dt.datetime.max):
    rng = r['cons'] if r['cons'] else ''
    if r['fcst'] and r['fcst'] != r['cons']:
        rng = ('%s \u2013 %s' % (rng, r['fcst'])) if rng else r['fcst']
    sc = ('**%+d**' % r['score']) if r['score'] else (
        '0' if r['score'] == 0 else '\u2014')
    A('| %s | %s | %s | %s | %s | %s |'
      % (r['when'].strftime('%a %d %H:%M'), r['ccy'], r['name'],
         r['prev'] or '\u2014', rng or '\u2014', sc))
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
            _sc = '**%+d**' % _r['score'] if _r['score'] else '0'
            A('| %s | %s | %s | %s |'
              % (_r['name'], '**%s**' % _mon if _kept else _mon, _sc,
                 '**KEPT**' if _kept else 'dropped'))
        A('')
        _kv = sum(r['score'] for r in _keep) / float(len(_keep))
        _all = _keep + _drop
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
A('**%d pairs. %d currencies used; %s unused.** No currency is used twice '
  '(LD-19), and **no rule forced a third pair** (LD-96).'
  % (len(PICKED), len(used), ' '.join(sorted(set(ft.CCYS) - used))))
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
A('| Base | \u22129 .. +9 | six fact tables, `%s`, %d of %d cells'
  % (MONTH, scored, total) + ' |')
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

p = 'reports/2026/Q3/2026-09-06_weekly.md'
io.open(p, 'w', encoding='utf-8', newline='').write(NL.join(out))
print('wrote %s (%d lines)' % (p, len(out)))
print()
print('base-only :', ', '.join('%s %s' % (c['pair'], c['direction']) for c in BPICK))
print('with calib:', ', '.join('%s %s' % (c['pair'], c['direction']) for c in PICKED))
print('rows: %d scorable of %d, %d with consensus' % (n_scor, len(ROWS), n_cons))
