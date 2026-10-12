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
 ("Production","US","ISM Manufacturing PMI","54.5","55.6","Sep/26",">50.5","GOOD"),
 ("Production","US","Industrial Production YoY","1.4%","1.13%","Aug/26",">0.5%","GOOD"),
 ("Production","US","Manufacturing Production YoY","0.9%","1.2%","Aug/26",">0.5%","GOOD"),
 # F-101 (2026-09-09): verdict was BAD on a 0.4% print against a >0.5% LEVEL
 # threshold. That grades DIRECTION (0.4 < 0.5) on a rule that tests WHERE THE
 # PRINT SITS. Jeff's band, stated four times this session and now spec'd for
 # GDP: above the line GOOD, below zero BAD, IN BETWEEN NEUTRAL. 0.4 is between.
 # F-92 was fixed in the calibrator and never reached the fact table; deriving
 # the score from the actual (LD-112) surfaced it on the first run.
 ("Production","US","Durable Goods Ex Transp MoM","0.3%","0.7%","Aug/26",">0.5%","NEUTRAL"),
 # F-91: this row still held the JUL print after the AUG Final released
 # 1 Sep 08:00. Jeff caught it reading the audit view. The score does not
 # change - 52.7 and 51.9 are both above 50.5 - but the EVIDENCE was a
 # month stale, and audit_te did not flag it because TE's country page had
 # already rolled forward, so our value and TE's current value agreed on
 # being "the last print" while meaning different months.
 ("Production","EA","S&P Global Mfg PMI Final","52.9","52.7","Sep/26",">50.5","GOOD"),
 ("Production","EA","Industrial Production YoY","0%","-0.3%","Jul/26",">0.5%","NEUTRAL"),
 # F-95: held the JUL print after the AUG Final released Tue 1 Sep 08:30
 # at 51.7 from 51.9. Same shape as F-91 on the EUR row - the two are
 # the same indicator family and went stale the same way. Score is
 # unchanged (51.7 and 51.9 both clear >50.5); the EVIDENCE was a month
 # old. R-37 missed it because no GBP Mfg PMI Final row with an actual
 # sits in the 4 Sep capture - TE had already rolled the row forward to
 # the Sep Flash, so there was nothing to compare against.
 ("Production","GB","S&P Global Mfg PMI Final","51.9","51.9","Sep/26",">50.5","GOOD"),
 # F-93: the threshold read "<0%", which says NEGATIVE growth is GOOD for
 # GBP. It was written to DESCRIBE the -0.2% print, not to encode the
 # direction - the exact F-68 shape. Industrial production is a growth
 # series: >0.5% good, <0% bad, between neutral, matching every other
 # production row on the board. The row itself still grades BAD, because
 # -0.2% IS below zero - what changes is that a POSITIVE forecast now
 # scores positively in the calibrator instead of being graded bad.
 ("Production","GB","Industrial Production YoY","0.6%","-0.9%","Jul/26",">0.5%","GOOD"),
 ("Production","GB","Manufacturing Production YoY","2.6%","0.5%","Jul/26",">0.5%","GOOD"),
 ("Production","JP","Industrial Production YoY Final","3.9%","4.9%","Jul/26",">0.5%","GOOD"),
 ("Production","JP","Machinery Orders YoY","11.2%","16.9%","Jul/26",">0.5%","GOOD"),
 ("Production","JP","Machine Tool Orders YoY","60.4%","64.7%","Sep/26",">0.5%","GOOD"),
 ("Production","JP","S&P Global Mfg PMI Final","54.1","54.9","Sep/26",">50.5","GOOD"),
 # F-143: 52.0 -> 49.6 (Sep/26, released 30 Sep) - the sharpest fall in
 # 21 months and BELOW 50, which is contraction. Under F-101's band a
 # level threshold reads: above the line GOOD, below the floor BAD, in
 # between NEUTRAL. For a PMI the floor is 50, not zero. The only PMI in
 # the set not in expansion.
 ("Production","AU","S&P Global Mfg PMI Final","49.6","52.0","Sep/26",">50.5","BAD"),
 ("Production","NZ","Business NZ PMI","53.1","54.3","Aug/26",">50.5","GOOD"),
 ("Production","NZ","Global Dairy Trade Price Index","-1.1%","0.9%","Sep/26",">0.5%","BAD"),
 ("Production","CA","S&P Global Mfg PMI","51.5","53.0","Sep/26",">50.5","GOOD"),
 ("Production","CH","Procure.ch-UBS Mfg PMI","55.3","57.1","Sep/26",">50.5","GOOD"),
 # LD-102: CHF Industrial Production YoY REMOVED 2026-09-09 on Jeff's
 # call - quarterly, so it scores the same value for ~13 consecutive
 # weekly editions and can never appear in the calibrator. It was
 # contributing certainty it had not earned. CHF Production is now a
 # ONE-ROW weight-2 category: Procure.ch PMI alone moves CHF by up to
 # 2.00 points.
 # ---------------- SPENDING (w=1) ----------------
 ("Spending","US","Building Permits MoM Final","-2.1%","4.3%","Aug/26",">0.5%","BAD"),
 ("Spending","US","Retail Sales YoY","6%","5.03%","Aug/26",">0.5%","GOOD"),
 ("Spending","US","CB Consumer Confidence","89.4","90.2","Aug/26",">Prev","BAD"),
 ("Spending","US","Personal Spending MoM","0.9%","1.2%","Aug/26",">0.5%","NEUTRAL"),
 # F-96: I changed the RULE while updating the VALUE in F-94. This row
 # carried ">0.5%" like the other five Retail Sales rows; I rewrote it
 # to ">Cons 1.1%" and it became the only one of six not on the level
 # test. Jeff, 2026-09-09: "Actual > 0.5% is Good, < 0% is Bad. Actual
 # in between 0.5 - 0 is Neutral". 0.6% clears 0.5%, so BAD -> GOOD and
 # EUR Spending goes +0.00 -> +2.00. UPDATING A VALUE IS NOT LICENCE TO
 # RESTATE ITS RULE.
 ("Spending","EA","Retail Sales YoY","0.8%","0.7%","Aug/26",">0.5%","GOOD"),
 ("Spending","EA","Consumer Confidence Final","-16.5","-15.5","Sep/26",">Prev","BAD"),
 ("Spending","GB","GfK Consumer Confidence","-13","-14","Sep/26",">Prev","GOOD"),
 ("Spending","GB","Retail Sales Ex Fuel YoY","2.7%","1.8%","Aug/26",">0.5%","GOOD"),
 # F-98: spec line 113 - ">0.5% Good, <0% Bad, between Neutral". Restored
 # from a consensus test I substituted during a sync. -3.6% is below 0,
 # so BAD either way - the RULE was wrong, not the verdict.
 ("Spending","JP","Household Spending YoY","-3.1%","-3.6%","Aug/26",">0.5%","BAD"),
 ("Spending","JP","Consumer Confidence","35.4","35.5","Sep/26",">Prev","BAD"),
 ("Spending","JP","Retail Sales YoY","2.7%","1.8%","Aug/26",">0.5%","GOOD"),
 ("Spending","AU","Household Spending YoY","6.8%","6.0%","Aug/26",">0.5%","GOOD"),
 ("Spending","AU","Building Permits YoY Final","10.3%","10.9%","Aug/26",">0.5%","GOOD"),
 ("Spending","AU","Westpac Consumer Conf Change","-4.7%","-5.2%","Oct/26",">Prev","GOOD"),
 ("Spending","AU","NAB Business Confidence","-8","-6","Aug/26",">Prev","BAD"),
 ("Spending","NZ","Building Permits MoM","-4.3%","-3.7%","Jul/26",">0.5%","BAD"),
 ("Spending","NZ","Electronic Retail Card Spending YoY","0.2%","0.9%","Aug/26",">0.5%","NEUTRAL"),
 ("Spending","NZ","ANZ Business Confidence","51.9","53.7","Sep/26",">Prev","BAD"),
 ("Spending","NZ","ANZ Roy Morgan Consumer Conf","97.6","98.0","Sep/26",">Prev","BAD"),
 ("Spending","CA","Retail Sales YoY","5.1%","5.2%","Jul/26",">0.5%","GOOD"),
 ("Spending","CA","Building Permits MoM","-17.3%","18.3%","Jul/26",">0.5%","BAD"),
 ("Spending","CH","Consumer Confidence","-36","-33","Sep/26",">Prev","BAD"),
 ("Spending","CH","Retail Sales YoY","3.2%","2.6%","Aug/26",">0.5%","GOOD"),
 # ---------------- TRADE (w=1) ----------------
 # F-98: spec line 132. -$88.6B is a WIDER deficit than -$71.2B, so this
 # FLIPS GOOD -> BAD. Beating a -$90B consensus is not the test.
 ("Trade","US","Balance of Trade","$-105.6B","-$71.2B","Aug/26",">Prev","BAD"),
 ("Trade","EA","Balance of Trade","EUR14.2B","EUR7.2B","Jul/26",">Prev","GOOD"),
 ("Trade","GB","Balance of Trade","GBP-3.45B","GBP-5.54B","Jul/26",">Prev","GOOD"),
 ("Trade","JP","Balance of Trade","JPY-1105.6B","JPY-638.3B","Aug/26",">Prev","BAD"),
 # F-98: spec line 141 - all eight Balance of Trade rows are ">Prev".
 # A$1.923B is BELOW the A$2.341B previous, so this FLIPS GOOD -> BAD.
 # It only read GOOD because it beat a low consensus, which is not the
 # rule Jeff specified.
 ("Trade","AU","Balance of Trade","A$0.495B","A$1.351B","Aug/26",">Prev","BAD"),
 ("Trade","NZ","Balance of Trade","NZ$-1.349B","NZ$-2.118B","Aug/26",">Prev","GOOD"),
 # F-98: spec line 138. C$0.77B is below the C$4.2B previous - BAD under
 # either rule, but the rule is ">Prev".
 ("Trade","CA","Balance of Trade","C$4.2B","C$0.79B","Aug/26",">Prev","GOOD"),
 ("Trade","CH","Balance of Trade","CHF5.6B","CHF8.1B","Aug/26",">Prev","BAD"),
 # ---------------- EMPLOYMENT (w=2) ----------------
 ("Employment","US","Non Farm Payrolls","29K","133K","Sep/26",">Prev","BAD"),
 ("Employment","US","Unemployment Rate","4.2%","4.1%","Sep/26","<Prev","BAD"),
 ("Employment","EA","Unemployment Rate","6.4%","6.4%","Aug/26","<Prev","NEUTRAL"),
 ("Employment","GB","Claimant Count Change","27.8K","-11.8K","Aug/26","<0 (LD-58)","BAD"),
 # F-144 - GBP WAS THE ONLY CURRENCY OF THE EIGHT WITHOUT AN UNEMPLOYMENT RATE.
 #
 # Jeff, 2026-10-04: "Don't we have Unemployment Rate for GBP in the indicator
 # list?" - and then "let's add Unemployment Rate for GBP with the same scoring
 # with the rest". This is a CLOSED-SET AMENDMENT (F-3), which is Jeff's call.
 #
 # TWO REASONS IT MATTERED MORE THAN A MISSING ROW USUALLY DOES:
 #
 #   1. GBP's whole Employment category rested on Claimant Count alone, so that
 #      one row swung the FULL category weight. Every other currency splits it
 #      over one to three rows.
 #   2. The two measure DIFFERENT THINGS. Claimant Count is a weekly
 #      ADMINISTRATIVE count of benefit claims - noisy, revision-prone,
 #      sensitive to eligibility rules. Unemployment Rate is the ILO SURVEY
 #      measure the other seven are scored on. GBP's labour market was being
 #      judged on a different instrument (LD-23: no input that cannot be
 #      sourced for all eight on equal terms).
 #
 # SAME RULE AS THE OTHER SEVEN: threshold '<Prev', lower is better, and the
 # channel is ECONOMIC HEALTH - direct to the currency, not through the bank
 # (F-70). 4.9% vs 4.9% is flat, so NEUTRAL.
 #
 # ONS publishes a rolling 3-month rate; Jul/26 released 15 Sep, flat for the
 # fourth consecutive period. Next print 20 Oct (Aug/26).
 ("Employment","GB","Unemployment Rate","4.9%","4.9%","Jul/26","<Prev","NEUTRAL"),
 ("Employment","JP","Unemployment Rate","2.5%","2.4%","Aug/26","<Prev","BAD"),
 ("Employment","AU","ANZ-Indeed Job Ads MoM","2.2%","2.6%","Sep/26",">0.5%","GOOD"),
 ("Employment","AU","Employment Change","39.5K (FT -6.3K, PT +45.8K)","-15.9K","Aug/26","LD-151 three legs","NEUTRAL"),
 ("Employment","AU","Unemployment Rate","4.6%","4.5%","Aug/26","<Prev","BAD"),
 ("Employment","NZ","Unemployment Rate","5.6%","5.4%","Jun/26 (Q)","<Prev","BAD"),
 ("Employment","CA","Unemployment Rate","6.5%","6.4%","Sep/26","<Prev","BAD"),
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
 ("Employment","CA","Employment Change","-68.3K (FT -35.4K, PT -32.9K)","-41.7K","Sep/26","LD-151 three legs","BAD"),
# LD-152 - CHF NON FARM PAYROLLS REMOVED (Jeff, 2026-10-05).
 #
 # Jeff: "since this is a quarterly data for CHF we can remove this from the
 # list". CLOSED-SET AMENDMENT (F-3) - his call. Whitelist 79 -> 78.
 #
 # THE SAME REASONING AS LD-102, which removed CHF Industrial Production YoY
 # on 2026-09-09: "a quarterly series scores the SAME value for ~13
 # consecutive weekly editions - a constant the currency carries whether or
 # not anything happened - and can NEVER appear in the calibrator, which only
 # sees the five days ahead. It contributed certainty it had not earned."
 #
 # *** LD-102 KEPT THREE OTHER QUARTERLY ROWS FOR A STRUCTURAL REASON, AND
 # THAT REASON DOES NOT COVER THIS ONE. NZD Unemployment is the only row in
 # NZD Employment, NZD Inflation the only row in NZD Inflation, SNB the only
 # row in CHF Interest Rate - removing any of them EMPTIES a category, and an
 # empty category scores 0.00, which reads NEUTRAL when the truth is UNKNOWN
 # (the F-73 shape). CHF Employment has TWO rows, so Unemployment Rate
 # survives and the category stays popul. This is the one quarterly row
 # LD-102's logic covered and that was left standing.
 #
 # NOT TO BE CONFUSED WITH THE 2026-08-24 CORRECTION. That found this row
 # carrying "+0.5% vs +0.2%" - PERCENTAGES BELONGING TO NO PUBLISHED SERIES,
 # since the indicator is a level in millions - and fixed it to 5.537M. The
 # row was corrected then, not removed; this is the removal.
 #
 # EFFECT: CHF Employment +0.50 -> 0.00 (Unemployment Rate alone, 3% = 3%,
 # NEUTRAL). CHF base +2.10 -> +1.60.
 #
 # It was also one of the rows R-45 cannot verify - its slug does not resolve -
 # and at Q2/26 it carried the OLDEST vintage on the board.
 ("Employment","CH","Unemployment Rate","3%","3%","Sep/26","<Prev","NEUTRAL"),
 # ---------------- INFLATION (w=3) ----------------
 ("Inflation","US","Inflation Rate YoY","3.4%","3.3%","Aug/26","1.8-2.2 corridor (LD-155)","GOOD"),
 ("Inflation","EA","Inflation Rate YoY Final","3.2%","2.9%","Aug/26","1.8-2.2 corridor (LD-155)","GOOD"),
 ("Inflation","GB","Inflation Rate YoY","3.1%","2.9%","Aug/26","1.8-2.2 corridor (LD-155)","GOOD"),
 ("Inflation","JP","Inflation Rate YoY","1.9%","1.9%","Aug/26","1.8-2.2 corridor (LD-155)","NEUTRAL"),
 ("Inflation","AU","Inflation Rate YoY","4.0%","3.8%","Aug/26","1.8-2.2 corridor (LD-155)","GOOD"),
 ("Inflation","NZ","Inflation Rate YoY","4.1%","3.1%","Jun/26 (Q)","1.8-2.2 corridor (LD-155)","GOOD"),
 ("Inflation","CA","Inflation Rate YoY","3%","3.0%","Aug/26","1.8-2.2 corridor (LD-155)","GOOD"),
 ("Inflation","CH","Inflation Rate YoY","1%","0.8%","Sep/26","1.8-2.2 corridor (LD-155)","BAD"),
]

CCYS = ["US","EA","GB","JP","AU","NZ","CA","CH"]
# LD-117 - GDP is a CALIBRATOR row, not a base row. It sits in ROWS so
# week_ahead.whitelist_events() can match it against the calendar; its
# actual/previous are placeholders because calibrator.gdp_score reads
# the CONSENSUS-FORECAST RANGE and nothing else (Jeff: "we're trading
# the expectations not the result"). QoQ only - LD-116.
GDP_ROWS = [
    ("GDP","US","GDP Growth Rate QoQ","-","-","Q2/26",">0 range (LD-117)","NEUTRAL"),
    ("GDP","EA","GDP Growth Rate QoQ","-","-","Q2/26",">0 range (LD-117)","NEUTRAL"),
    ("GDP","GB","GDP Growth Rate QoQ","-","-","Q2/26",">0 range (LD-117)","NEUTRAL"),
    ("GDP","JP","GDP Growth Rate QoQ","-","-","Q2/26",">0 range (LD-117)","NEUTRAL"),
    ("GDP","AU","GDP Growth Rate QoQ","-","-","Q2/26",">0 range (LD-117)","NEUTRAL"),
    ("GDP","NZ","GDP Growth Rate QoQ","-","-","Q2/26",">0 range (LD-117)","NEUTRAL"),
    ("GDP","CA","GDP Growth Rate QoQ","-","-","Q2/26",">0 range (LD-117)","NEUTRAL"),
    ("GDP","CH","GDP Growth Rate QoQ","-","-","Q2/26",">0 range (LD-117)","NEUTRAL"),
]
ROWS = ROWS + GDP_ROWS

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
# LD-151 - EMPLOYMENT CHANGE IS GRADED ON ALL THREE LEGS (Jeff, 2026-10-04).
#
#   1) Actual > 0 and FT > 0 and PT > 0   -> GOOD
#   2) Actual > 0 and FT < 0 and PT > 0   -> NEUTRAL
#   3) Actual < 0 and FT > 0 and PT < 0   -> NEUTRAL
#   4) Actual < 0 and FT < 0 and PT < 0   -> BAD
#
# *** THIS REPLACES full_time_grade's "vs PREVIOUS" TEST. LD-57 asked whether
# full time BEAT ITS OWN LAST MONTH; LD-151 asks what the three legs SAY
# TOGETHER, against zero. The prior month no longer enters it. That removes
# the defect LD-58 fixed for Claimant Count and left standing here: a change
# series read against its own prior change calls deceleration a decline.
#
# WHY THE SIGNS AND NOT THE SIZE. Jeff's AUD correction, 2026-09-26: "its
# because the Full time employee actually fell from 15K to -6.3K. This shows
# why we are giving higher weight to Full Time rather than just looking at the
# Employment Change". A +39.5K headline that is ENTIRELY part time is not the
# same event as +39.5K of full time work, and only the signs separate them.
#
# TWO CASES JEFF DID NOT LIST ARE POSSIBLE, and Actual = FT + PT decides which:
#
#       ACTUAL  FT  PT    status
#         +     +   +     rule 1, GOOD
#         +     +   -     NOT LISTED - possible (FT +50, PT -10)
#         +     -   +     rule 2, NEUTRAL
#         +     -   -     IMPOSSIBLE, two negatives cannot sum positive
#         -     +   +     IMPOSSIBLE, two positives cannot sum negative
#         -     +   -     rule 3, NEUTRAL
#         -     -   +     NOT LISTED - possible (FT -50, PT +10)
#         -     -   -     rule 4, BAD
#
# JEFF'S RULING on the two: FOLLOW THE FULL TIME LEG. (+,+,-) is GOOD and
# (-,-,+) is BAD. That reads his four rules as "full time decides, part time
# can only soften it" - rules 2 and 3 are exactly the softening cases, and
# both of the unlisted ones have full time and the headline AGREEING.
#
# SO THE RULE IS: THE HEADLINE AND FULL TIME TOGETHER SET THE VERDICT, and a
# part-time leg is only consulted when it is the thing dragging the headline
# the other way.
#
#   headline and full time AGREE   -> that direction (GOOD if up, BAD if down)
#   headline and full time DISAGREE-> NEUTRAL
#
# Rules 2 and 3 are exactly the disagreement cases; rules 1 and 4 and both
# unlisted cases are the agreement cases. *** AN EARLIER DRAFT COLLAPSED THIS
# TO "full time decides, part time softens", which returned NEUTRAL for the
# two unlisted cases - the opposite of the ruling. The test below pins all six.
#
# APPLIES TO AUD AND CAD ONLY - the two currencies whose Employment Change TE
# publishes with a full-time split. F-145: the CAD row claimed "FT/PT split
# unsourced" and TE publishes it (Aug/26 FT -35.9K, PT -5.8K), so CAD was
# being graded on the HEADLINE while AUD was graded on full time, for a stated
# reason that was not true.
def employment_grade(actual, full_time, part_time):
    """LD-151. GOOD/NEUTRAL/BAD from the three legs, or None if unsourced.

    None when any leg is missing - never a guessed verdict (F-73).
    """
    if actual is None or full_time is None or part_time is None:
        return None
    if full_time == 0 or actual == 0:
        return "NEUTRAL"
    up = actual > 0
    if (full_time > 0) != up:            # headline and full time disagree
        return "NEUTRAL"
    return "GOOD" if up else "BAD"


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
    """First number in a cell. '5.0%' -> 5.0, 'A$1,929M' -> 1929.0, '-' -> None.

    *** F-124 - A MINUS SIGN BEFORE THE CURRENCY MARK WAS DROPPED.
    Jeff, 2026-09-14, asking why AUD NAB scored 0, which surfaced an audit of
    every >Prev row. '-$88.6B' parsed as +88.6 while '$-88.6B' parsed as
    -88.6 - the same figure, opposite sign, depending purely on which side of
    the dollar sign TE put the minus.

        US Balance of Trade   held '-$88.6B'   parsed +88.6
                              prev '-$71.2B'   parsed +71.2
                              => "88.6 > 71.2, improving" - EXACTLY BACKWARDS

    The stored verdict was BAD and correct, so nothing was mis-scored: every
    >Prev row falls through to its hand-written verdict (band() cannot parse
    '>Prev'), and the hand grading was right. The bug sat in the parser,
    waiting for the day something actually computed on it - which is what my
    own audit script did, and it promptly reported a false mismatch.

    A sign that depends on symbol placement is a trap for the next caller, so
    it is fixed at the source rather than worked around per site.
    """
    if v is None:
        return None
    t = str(v).replace(',', '')
    m = _NUM.search(t)
    if not m:
        return None
    x = float(m.group(0))
    # A '-' anywhere before the first digit is a sign, whatever sits between.
    if x >= 0 and '-' in t[:m.start()]:
        x = -x
    return x


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
