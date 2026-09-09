# TRTM-style provenance: this file implements LD-13 (weighted category scoring),
import re
# locked 2026-08-19. It is DATA + ARITHMETIC only - no fetching, no I/O.
# The ROWS table is replaced each edition; W and compute() are the model.
#
# NOTE (T1 boundary): this produces numbers Jeff acts on, so if it is ever
# wired to fetch its own data it fires T1/T3 and takes the full gate ladder.
# As a pure scoring function fed by hand-verified rows, it stays LEAN.

# Weighted category scoring per Jeff's spec (2026-08-19).
#   Category weights: Inflation 3, Employment 2, Production/Spending/Trade 1.
#   Within a category, a currency's N indicators split the weight evenly:
#     each indicator is worth weight/N.  GOOD = +w/N, BAD = -w/N, NEUTRAL = 0.
#   Max possible = 3+2+1+1+1 = 8; min = -8.
# MISSING indicators do NOT score (0) but shrink the category's realised
# coverage, which is reported so a thin category is visible.

W = {"Production":1, "Spending":1, "Trade":1, "Employment":2, "Inflation":3}
# Interest Rate is category 6, weight 3 - scored in pipelines/rate_model.py (LD-23).
# Range is therefore +/-11.00, not +/-8.00.

# LD-106: a REF ending in ' (Q)' means the series is QUARTERLY, so an
# old-looking month is its cadence and not a stale row. NZD publishes
# Unemployment and Inflation quarterly and both sit two months behind
# the monthly rows around them; without the marker the audit view
# shows 'Jun/26' beside 'Aug/26' and reads as a defect.
# The suffix is COSMETIC TO THE PARSER - audit_evidence.month_key()
# still reads (26, 6) from 'Jun/26 (Q)' - verified before applying.
# (category, ccy, indicator, actual, prev, ref, rule, score)  score in GOOD/BAD/NEUTRAL/MISSING
ROWS = [
 # ---------------- PRODUCTION (w=1) ----------------
 ("Production","US","ISM Manufacturing PMI","54.6","55.6","Aug/26",">50.5","GOOD"),
 ("Production","US","Industrial Production YoY","1.1%","1.29%","Jul/26",">0.5%","GOOD"),
 ("Production","US","Manufacturing Production YoY","1.2%","1.1%","Jul/26",">0.5%","GOOD"),
 ("Production","US","Durable Goods Ex Transp MoM","0.4%","0.6%","Jul/26",">0.5%","BAD"),
 # F-91: this row still held the JUL print after the AUG Final released
 # 1 Sep 08:00. Jeff caught it reading the audit view. The score does not
 # change - 52.7 and 51.9 are both above 50.5 - but the EVIDENCE was a
 # month stale, and audit_te did not flag it because TE's country page had
 # already rolled forward, so our value and TE's current value agreed on
 # being "the last print" while meaning different months.
 ("Production","EA","S&P Global Mfg PMI Final","52.7","51.9","Aug/26",">50.5","GOOD"),
 ("Production","EA","Industrial Production YoY","0.1%","-0.1%","Jun/26",">0.5%","NEUTRAL"),
 # F-95: held the JUL print after the AUG Final released Tue 1 Sep 08:30
 # at 51.7 from 51.9. Same shape as F-91 on the EUR row - the two are
 # the same indicator family and went stale the same way. Score is
 # unchanged (51.7 and 51.9 both clear >50.5); the EVIDENCE was a month
 # old. R-37 missed it because no GBP Mfg PMI Final row with an actual
 # sits in the 4 Sep capture - TE had already rolled the row forward to
 # the Sep Flash, so there was nothing to compare against.
 ("Production","GB","S&P Global Mfg PMI Final","51.7","51.9","Aug/26",">50.5","GOOD"),
 # F-93: the threshold read "<0%", which says NEGATIVE growth is GOOD for
 # GBP. It was written to DESCRIBE the -0.2% print, not to encode the
 # direction - the exact F-68 shape. Industrial production is a growth
 # series: >0.5% good, <0% bad, between neutral, matching every other
 # production row on the board. The row itself still grades BAD, because
 # -0.2% IS below zero - what changes is that a POSITIVE forecast now
 # scores positively in the calibrator instead of being graded bad.
 ("Production","GB","Industrial Production YoY","-0.2%","1.0%","Jun/26",">0.5%","BAD"),
 ("Production","GB","Manufacturing Production YoY","0.5%","2.0%","Jun/26",">0.5%","NEUTRAL"),
 ("Production","JP","Industrial Production YoY Final","4.9%","-2.1%","Jun/26",">0.5%","GOOD"),
 ("Production","JP","Machinery Orders YoY","16.9%","-1.9%","Jun/26",">0.5%","GOOD"),
 ("Production","JP","Machine Tool Orders YoY","50.4%","52.8%","Jul/26",">0.5%","GOOD"),
 ("Production","JP","S&P Global Mfg PMI Final","54.9","54.5","Aug/26",">50.5","GOOD"),
 ("Production","AU","S&P Global Mfg PMI Final","52.0","52.0","Aug/26",">50.5","GOOD"),
 ("Production","NZ","Business NZ PMI","54.3","60.1","Jul/26",">50.5","GOOD"),
 ("Production","NZ","Global Dairy Trade Price Index","0.9%","2.3%","Sep/26",">0.5%","GOOD"),
 ("Production","CA","S&P Global Mfg PMI","53.0","53.5","Aug/26",">50.5","GOOD"),
 ("Production","CH","Procure.ch-UBS Mfg PMI","57.1","53.2","Aug/26",">50.5","GOOD"),
 # LD-102: CHF Industrial Production YoY REMOVED 2026-09-09 on Jeff's
 # call - quarterly, so it scores the same value for ~13 consecutive
 # weekly editions and can never appear in the calibrator. It was
 # contributing certainty it had not earned. CHF Production is now a
 # ONE-ROW weight-2 category: Procure.ch PMI alone moves CHF by up to
 # 2.00 points.
 # ---------------- SPENDING (w=1) ----------------
 ("Spending","US","Building Permits MoM Final","4.3%","-2.6%","Jul/26",">0.5%","GOOD"),
 ("Spending","US","Retail Sales YoY","5.0%","6.8%","Jul/26",">0.5%","GOOD"),
 ("Spending","US","CB Consumer Confidence","89.4","90.2","Aug/26",">Prev","BAD"),
 ("Spending","US","Personal Spending MoM","0.2%","0.3%","Jul/26",">0.5%","NEUTRAL"),
 # F-96: I changed the RULE while updating the VALUE in F-94. This row
 # carried ">0.5%" like the other five Retail Sales rows; I rewrote it
 # to ">Cons 1.1%" and it became the only one of six not on the level
 # test. Jeff, 2026-09-09: "Actual > 0.5% is Good, < 0% is Bad. Actual
 # in between 0.5 - 0 is Neutral". 0.6% clears 0.5%, so BAD -> GOOD and
 # EUR Spending goes +0.00 -> +2.00. UPDATING A VALUE IS NOT LICENCE TO
 # RESTATE ITS RULE.
 ("Spending","EA","Retail Sales YoY","0.6%","0.7%","Jul/26",">0.5%","GOOD"),
 ("Spending","EA","Consumer Confidence Final","-15.5","-15.9","Aug/26",">Prev","GOOD"),
 ("Spending","GB","GfK Consumer Confidence","-14","-17","Aug/26",">Prev","GOOD"),
 ("Spending","GB","Retail Sales Ex Fuel YoY","2.3%","5.0%","Jul/26",">0.5%","GOOD"),
 # F-98: spec line 113 - ">0.5% Good, <0% Bad, between Neutral". Restored
 # from a consensus test I substituted during a sync. -3.6% is below 0,
 # so BAD either way - the RULE was wrong, not the verdict.
 ("Spending","JP","Household Spending YoY","-3.6%","-3.3%","Jul/26",">0.5%","BAD"),
 ("Spending","JP","Consumer Confidence","35.5","34.9","Aug/26",">Prev","GOOD"),
 ("Spending","JP","Retail Sales YoY","4.0%","0.6%","Jul/26",">0.5%","GOOD"),
 ("Spending","AU","Household Spending YoY","7.0%","6.0%","Jul/26",">0.5%","GOOD"),
 ("Spending","AU","Building Permits YoY Final","8.9%","5.5%","Jun/26",">0.5%","GOOD"),
 ("Spending","AU","Westpac Consumer Conf Change","6.0%","4.1%","Aug/26",">Prev","GOOD"),
 ("Spending","AU","NAB Business Confidence","-6","-6","Jul/26",">Prev","NEUTRAL"),
 ("Spending","NZ","Building Permits MoM","-4.3%","-3.6%","Jul/26",">0.5%","BAD"),
 ("Spending","NZ","Electronic Retail Card Spending YoY","3.4%","1.3%","Jul/26",">0.5%","GOOD"),
 ("Spending","NZ","ANZ Business Confidence","53.7","56.1","Aug/26",">Prev","BAD"),
 ("Spending","NZ","ANZ Roy Morgan Consumer Conf","98.0","99.3","Aug/26",">Prev","BAD"),
 ("Spending","CA","Retail Sales YoY","5.2%","5.9%","Jun/26",">0.5%","GOOD"),
 ("Spending","CA","Building Permits MoM","+18.5%","-3.0%","Jun/26",">0.5%","GOOD"),
 ("Spending","CH","Consumer Confidence","-35","-36","Jul/26",">Prev","GOOD"),
 ("Spending","CH","Retail Sales YoY","2.3%","1.9%","Jul/26",">0.5%","GOOD"),
 # ---------------- TRADE (w=1) ----------------
 # F-98: spec line 132. -$88.6B is a WIDER deficit than -$71.2B, so this
 # FLIPS GOOD -> BAD. Beating a -$90B consensus is not the test.
 ("Trade","US","Balance of Trade","-$88.6B","-$71.2B","Jul/26",">Prev","BAD"),
 ("Trade","EA","Balance of Trade","EUR8.60B","EUR-9.00B","Jun/26",">Prev","GOOD"),
 ("Trade","GB","Balance of Trade","GBP-5.54B","GBP-3.46B","Jun/26",">Prev","BAD"),
 ("Trade","JP","Balance of Trade","JPY-634.5B","JPY-409.9B","Jul/26",">Prev","BAD"),
 # F-98: spec line 141 - all eight Balance of Trade rows are ">Prev".
 # A$1.923B is BELOW the A$2.341B previous, so this FLIPS GOOD -> BAD.
 # It only read GOOD because it beat a low consensus, which is not the
 # rule Jeff specified.
 ("Trade","AU","Balance of Trade","A$1.923B","A$2.341B","Jul/26",">Prev","BAD"),
 ("Trade","NZ","Balance of Trade","NZ$-1.95B","NZ$0.02B","Jul/26",">Prev","BAD"),
 # F-98: spec line 138. C$0.77B is below the C$4.2B previous - BAD under
 # either rule, but the rule is ">Prev".
 ("Trade","CA","Balance of Trade","C$0.77B","C$4.2B","Jul/26",">Prev","BAD"),
 ("Trade","CH","Balance of Trade","CHF8.1B","CHF3.8B","Jul/26",">Prev","GOOD"),
 # ---------------- EMPLOYMENT (w=2) ----------------
 ("Employment","US","Non Farm Payrolls","162K","-23K","Aug/26",">Prev","GOOD"),
 ("Employment","US","Unemployment Rate","4.1%","4.1%","Aug/26","<Prev","NEUTRAL"),
 ("Employment","EA","Unemployment Rate","6.4%","6.3%","Jul/26","<Prev","BAD"),
 ("Employment","GB","Claimant Count Change","-11K","-6.4K","Jul/26","<0 (LD-58)","GOOD"),
 ("Employment","JP","Unemployment Rate","2.4%","2.5%","Jul/26","<Prev","GOOD"),
 ("Employment","AU","ANZ-Indeed Job Ads MoM","+0.8%","-0.1%","Jul/26",">0.5%","GOOD"),
 ("Employment","AU","Employment Change","-15.8K (FT +16.3K, PT -32.2K)","76.3K (FT +29.3K, PT +47.0K)","Jul/26","hdl BAD; FT NEUTRAL (LD-57); PT GOOD","NEUTRAL"),
 ("Employment","AU","Unemployment Rate","4.5%","4.4%","Jul/26","<Prev","BAD"),
 ("Employment","NZ","Unemployment Rate","5.6%","5.4%","Jun/26 (Q)","<Prev","BAD"),
 ("Employment","CA","Unemployment Rate","6.4%","6.4%","Aug/26","<Prev","NEUTRAL"),
 # F-97: the same mistake, and worse - this row's threshold encoded
 # LD-57, a LOCKED four-clause full-time/part-time rule with its own
 # function, and F-94 overwrote it with a bare consensus test without
 # flagging that a locked decision was being changed.
 # THE VERDICT STANDS AT BAD on the headline: -41.7K is negative and
 # far below the +15K consensus, which is BAD under LD-57 clause (c)
 # and under a consensus test alike.
 # >>> THE FT/PT SPLIT COULD NOT BE APPLIED. It was scheduled 4 Sep
 # 20:30 and our last pre-Sunday capture is 4 Sep 08:02, so NO capture
 # holds an actual for it. The threshold below names LD-57 as the
 # governing rule and records that the split is unsourced - it does
 # not silently substitute a different rule.
 ("Employment","CA","Employment Change","-41.7K","75.1K","Aug/26","hdl<0 BAD (LD-57); FT/PT split unsourced","BAD"),
 ("Employment","CH","Non Farm Payrolls","5.698M","5.537M","Q2/26",">Prev","GOOD"),
 ("Employment","CH","Unemployment Rate","3.0%","2.9%","Jul/26","<Prev","BAD"),
 # ---------------- INFLATION (w=3) ----------------
 ("Inflation","US","Inflation Rate YoY","3.4%","3.5%","Jul/26",">2% & falling","NEUTRAL"),
 ("Inflation","EA","Inflation Rate YoY Final","2.9%","2.8%","Jul/26",">2% & rising","GOOD"),
 ("Inflation","GB","Inflation Rate YoY","2.9%","2.6%","Jul/26",">2% & rising","GOOD"),
 ("Inflation","JP","Inflation Rate YoY","1.9%","1.6%","Jul/26","<2% & rising","NEUTRAL"),
 ("Inflation","AU","Inflation Rate YoY","3.5%","3.8%","Jul/26",">2% & falling","NEUTRAL"),
 ("Inflation","NZ","Inflation Rate YoY","4.1%","3.1%","Jun/26 (Q)",">2% & rising","GOOD"),
 ("Inflation","CA","Inflation Rate YoY","3.0%","2.8%","Jul/26",">2% & rising","GOOD"),
 ("Inflation","CH","Inflation Rate YoY","0.8%","0.4%","Aug/26","<2% & rising","NEUTRAL"),
]

CCYS = ["US","EA","GB","JP","AU","NZ","CA","CH"]
LABEL = {"US":"USD","EA":"EUR","GB":"GBP","JP":"JPY","AU":"AUD","NZ":"NZD","CA":"CAD","CH":"CHF"}

# LD-57 - FULL TIME EMPLOYMENT CHANGE, Jeff's rule, 2026-08-24.
# Applies to AUD and CAD, the two currencies whose Employment Change the
# whitelist source scores as a composite "with more weight to Full Time".
#
# WHY IT CHANGED: the previous test was a bare "Actual > Previous", which
# graded a POSITIVE full-time month BAD merely for growing more slowly than
# the month before (+16.3K after +29.3K -> BAD). Jeff: full-time growth that
# decelerates is not the same as full-time contraction, and the model should
# not call it that.
#
#   a) Actual > 0 and Actual >= Previous -> GOOD     growth, holding or better
#   b) Actual > 0 and Actual <  Previous -> NEUTRAL  growth, but slowing
#   c) Actual < 0 and Actual <= Previous -> BAD      contraction, no better
#   d) Actual < 0 and Actual >  Previous -> NEUTRAL  contraction, but easing
#   e) Actual = 0                        -> NEUTRAL  (Jeff's call - zero is
#      neither growth nor contraction, and every >Prev test in the whitelist
#      source already reads "No change is Neutral")
#
# FULL TIME STILL CARRIES MORE WEIGHT than the headline or part-time legs -
# that is unchanged from the source and from LD-56.
def full_time_grade(actual, previous):
    """Grade a Full Time Employment Change print. Returns GOOD/NEUTRAL/BAD."""
    if actual is None or previous is None:
        return None                      # un-runnable; publish as NOT SOURCED
    if actual == 0:
        return "NEUTRAL"
    if actual > 0:
        return "GOOD" if actual >= previous else "NEUTRAL"
    return "BAD" if actual <= previous else "NEUTRAL"


# LD-58 - CLAIMANT COUNT CHANGE, Jeff's rule, 2026-08-24. GBP only.
#
# The series measures the CHANGE in people claiming unemployment benefit, so
# NEGATIVE means fewer claimants and an IMPROVING labour market. The sign is
# the signal; the prior month is not.
#
#   Actual > 0 -> BAD      more claimants
#   Actual < 0 -> GOOD     fewer claimants
#   Actual = 0 -> NEUTRAL  no change
#
# WHY IT CHANGED: the previous test was "Actual < Previous", which produced
# two backwards readings. Claimants falling 2K after falling 11K scored BAD -
# the labour market improved and the model called it bad. Claimants RISING 5K
# after rising 20K scored GOOD - the market deteriorated and the model called
# it good. A change series has to be read against ZERO, not against its own
# prior change.
def claimant_grade(actual):
    """Grade a Claimant Count Change print. Returns GOOD/NEUTRAL/BAD."""
    if actual is None:
        return None
    if actual == 0:
        return "NEUTRAL"
    return "GOOD" if actual < 0 else "BAD"


# ---------------------------------------------------------------------------
# LD-71 - GRADED SCORING.  v1 BASELINE, locked 2026-08-30.
#
# FULL SPEC: docs/SCORING_BASELINE.md - weights, the four rules, the
# DIVISORS AND WHY THEY WERE CHOSEN, a worked example, the baseline board,
# and a numbered list of what v1 deliberately does NOT do.
#
# Do not change a divisor here without updating that file's version table.
# ---------------------------------------------------------------------------

_NUM = re.compile(r'-?[0-9][0-9,]*\.?[0-9]*')


def _num(v):
    """First number in a cell. '5.0%' -> 5.0, 'A$1,929M' -> 1929.0, '-' -> None."""
    if v is None:
        return None
    m = _NUM.search(str(v).replace(',', ''))
    return float(m.group(0)) if m else None


def _clamp(x):
    return max(-1.0, min(1.0, x))


def graded(actual, previous, threshold, verdict=None):
    """Magnitude in [-1, +1] for one indicator, or None to fall back to the
    three-state verdict.

    The SCALE of each rule is deliberately conservative: full marks require a
    clearly decisive print, so an ordinary beat lands mid-range and leaves the
    category room to move. That headroom IS the fix - a slot pinned at 1.00
    cannot respond to the next release.
    """
    a, pv = _num(actual), _num(previous)
    t = (threshold or '').strip()

    # ---- PMI: distance from 50, the series' own natural pivot ----
    m = re.fullmatch(r'>\s*(\d+\.?\d*)%?', t)
    if m and a is not None and float(m.group(1)) >= 45:
        pivot = float(m.group(1))
        return _clamp((a - pivot) / 5.0)          # +5 points clear = full mark

    # ---- '>0.5%' style: distance beyond the line ----
    if m and a is not None:
        line = float(m.group(1))
        return _clamp((a - line) / 3.0)           # 3pp clear of the line = full

    # ---- '>Prev' / '<Prev': size of the change ----
    if t in ('>Prev', '<Prev') and a is not None and pv is not None:
        if abs(pv) < 1e-9:
            return None
        rel = (a - pv) / abs(pv)
        if t == '<Prev':
            rel = -rel
        return _clamp(rel / 0.10)                 # a 10% move = full mark

    return None                                    # not a graded pattern


def graded_signed(actual, previous, threshold, verdict):
    """Magnitude from graded(), SIGN from the verdict column.

    THE BUG THIS FIXES, found 2026-08-30 before any of it shipped: '>Prev' and
    '<Prev' describe the COMPARISON, not the direction of goodness. NZ Balance
    of Trade collapsed from +0.02B to -1.95B, verdict BAD - and graded() scored
    it +1.000, because '<Prev' was read as 'lower is good'. True for
    unemployment, FALSE for a trade balance. NZD jumped from 4th to 1st on it.

    The VERDICT column already carries polarity and Jeff has curated it row by
    row (LD-57, LD-58, LD-59). It is the authority. graded() supplies HOW FAR,
    the verdict supplies WHICH WAY.
    """
    g = graded(actual, previous, threshold)
    if g is None:
        return None
    if verdict == 'GOOD':
        return abs(g)
    if verdict == 'BAD':
        return -abs(g)
    if verdict == 'NEUTRAL':
        return 0.0
    return None


def compute(include_rate=True):
    """Five scored categories plus Interest Rate (LD-23, weight 3) when
    include_rate is True. Rate scores come from pipelines/rate_model.py, which
    scores inflation-vs-own-mandate only - see that file for why steps 2-4
    (priced odds, vote splits, forward paths) were rejected."""
    from collections import defaultdict
    by = defaultdict(list)
    for r in ROWS:
        by[(r[0], r[1])].append(r)
    cat_score, totals, detail = {}, {}, {}
    for ccy in CCYS:
        tot = 0.0
        for cat, w in W.items():
            rows = by[(cat, ccy)]
            n = len(rows)
            if n == 0:
                cat_score[(cat, ccy)] = (0.0, 0, 0)
                continue
            per = w / n
            s = 0.0
            scored = 0
            for r in rows:
                v = r[7]
                # LD-71: graded magnitude where the threshold pattern supports
                # it; the three-state verdict otherwise. A row Jeff specified
                # by hand (LD-57, LD-58) has no graded pattern and therefore
                # keeps its verdict untouched - deliberate, see LD-59.
                g = graded_signed(r[3], r[4], r[6], v)
                if g is not None:
                    s += per * g
                    scored += 1
                elif v == "GOOD":
                    s += per; scored += 1
                elif v == "BAD":
                    s -= per; scored += 1
                elif v == "NEUTRAL":
                    scored += 1
            cat_score[(cat, ccy)] = (s, n, scored)
            tot += s
        if include_rate:
            try:
                from rate_model import compute as _rate
                r = _rate().get(ccy)
                if r:
                    cat_score[("Rate", ccy)] = (r["score"], 1, 1)
                    tot += r["score"]
            except ImportError:
                pass
        totals[ccy] = tot
    return cat_score, totals
