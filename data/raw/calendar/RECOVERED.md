# Rows recovered from the TE INDICATOR page, not the calendar

R-42 (`capture_gap.py`) lists every whitelist row that printed while no capture
could see it. Those rows can never be recovered from the calendar — TE's
rolling window has moved past them — so R-42 would keep reporting them forever
even after the value is safely in the fact table.

This ledger records the ones that have been recovered and from where, so R-42
can separate **still outstanding** from **already dealt with**. A row listed
here is not a gap any more; it is a gap that was closed by hand.

Format: `CCY | ROW | scheduled | actual | source URL`

Jeff, 2026-09-13: *"we cannot afford to have dirty data as we're doing
forecasting. We need to be accurate on the pulls"*

---

GBP | Industrial Production YoY | 2026-09-11 | 0.6% | https://tradingeconomics.com/united-kingdom/industrial-production
GBP | Manufacturing Production YoY | 2026-09-11 | 2.6% | https://tradingeconomics.com/united-kingdom/manufacturing-production
GBP | Balance of Trade | 2026-09-11 | GBP-3.45B | https://tradingeconomics.com/united-kingdom/balance-of-trade
USD | Inflation Rate YoY | 2026-09-11 | 3.4% | https://tradingeconomics.com/united-states/inflation-cpi
JPY | Household Spending YoY | 2026-09-05 | -3.6% | https://tradingeconomics.com/japan/household-spending

<!-- RECORDED 2026-09-21. These rows printed inside 14-18 Sep, were recovered
     from TE indicator pages during that week's corrections, and are already
     applied to the fact tables - but were never written here, so R-42 kept
     reporting them as outstanding. A ledger only closes a gap if the entry
     is actually made; leaving it out is how a guard learns to cry wolf. -->
CAD | Inflation Rate YoY | 2026-09-14 | 3% | https://tradingeconomics.com/canada/inflation-cpi
CHF | Consumer Confidence | 2026-09-14 | -33 | https://tradingeconomics.com/switzerland/consumer-confidence
EUR | Balance of Trade | 2026-09-15 | EUR14.2B | https://tradingeconomics.com/euro-area/balance-of-trade
GBP | Claimant Count Change | 2026-09-15 | 27.8K | https://tradingeconomics.com/united-kingdom/claimant-count-change
GBP | Inflation Rate YoY | 2026-09-16 | 3.1% | https://tradingeconomics.com/united-kingdom/inflation-cpi
JPY | Industrial Production YoY Final | 2026-09-14 | 3.9% | https://tradingeconomics.com/japan/industrial-production
JPY | Industrial Production YoY Final | 2026-09-15 | 3.9% | https://tradingeconomics.com/japan/industrial-production
NZD | Business NZ PMI | 2026-09-14 | 53.1 | https://tradingeconomics.com/new-zealand/manufacturing-pmi
NZD | Electronic Retail Card Spending YoY | 2026-09-14 | 0.2% | https://tradingeconomics.com/new-zealand/retail-sales-annual
NZD | Electronic Retail Card Spending YoY | 2026-09-15 | 0.2% | https://tradingeconomics.com/new-zealand/retail-sales-annual
NZD | Global Dairy Trade Price Index | 2026-09-15 | -1.1% | https://tradingeconomics.com/new-zealand/global-dairy-trade-price-index
USD | Retail Sales YoY | 2026-09-16 | 6% | https://tradingeconomics.com/united-states/retail-sales-annual

## 2026-09-30 - HAND CHECK OF THE SIX ROWS R-45 CANNOT RESOLVE

Jeff, 2026-09-30: "do we have stale data other than the ones released this
week?" R-45's five STALE rows all released 29-30 Sep, so the answer turns
entirely on the six rows the sweep reports as NO PAGE AND NO CAPTURED PRINT -
the only rows where nothing in the repo can see a drift.

Checked by hand against the live TE page, 2026-09-30:

  USD  Non Farm Payrolls        162K  Aug/26  rel 4 Sep   MATCHES  next 2 Oct
  NZD  Unemployment Rate        5.6%  Q2/26   rel 4 Aug   MATCHES  next 3 Nov
  NZD  Inflation Rate YoY       4.1%  Q2/26   rel 20 Jul  MATCHES  next 21 Oct
  NZD  Global Dairy Trade      -1.1%  15 Sep  rel 15 Sep  MATCHES  next 6 Oct
  USD  CB Consumer Confidence   89.4  Aug/26              NOT VERIFIED
  NZD  Electronic Retail Card    0.2% Aug/26              NOT VERIFIED

*** TWO SLUGS ARE WRONG, AND THEY FAIL QUIETLY.

  'CB Consumer Confidence' -> /united-states/consumer-confidence
      That page is the UNIVERSITY OF MICHIGAN sentiment index (48.1 Sep/26),
      a DIFFERENT SERIES from the Conference Board's. The slug resolves, the
      page loads, and the number on it has nothing to do with our row. Had
      the parser managed to read it we would have silently adopted 48.1 for
      a row that holds 89.4 - a wrong value arriving through a working check.

  'Electronic Retail Card Spending YoY' -> /new-zealand/retail-sales-annual
      Returns LEVELS in NZD millions (7017.0 for Aug/26), not the YoY
      percentage the row holds (0.2%). Same shape: right country, right
      topic, wrong series and wrong unit.

These are worse than NO PAGE. A missing page is honest about its blind spot;
a wrong page that happens not to parse is a blind spot wearing a slug. NO
PAGE is the only reason neither has caused a bad value yet.

NZD Global Dairy: R-41 reports this STALE, and R-41 IS WRONG. We hold -1.1%
(15 Sep), which TE confirms as the latest. R-41 compares against the newest
CAPTURE, and the 1 Sep capture carries the older 0.9% print. The cell is
current; the capture is not. Same false-positive class as F-139.

ANSWER TO THE QUESTION: no stale data outside this week's releases, on 68 of
70 rows. Two rows (CB Consumer Confidence, NZD Card Spending) remain
unverifiable until their slugs are corrected.

## 2026-10-04 - THE 28 SEP - 2 OCT PRINTS, RECOVERED FOR THE Oct-26 ROLL

R-42 raised 13 rows as "lost to a capture gap". NINE of them were already
recovered this session from their TE INDICATOR pages via R-45 and rolled into
Oct-26, which is the recovery R-42 asks for - the calendar window missed them,
the indicator page did not.

FOUR more were in R-42's list but not R-45's, because R-45 has no working slug
for them. Checked by hand against the TE page that owns each one:

  USD  ISM Manufacturing PMI     54.6 -> 54.5   Sep/26, rel 1 Oct   APPLIED
       (the slug /united-states/ism-manufacturing-pmi does not carry the
        history table; /united-states/business-confidence does)
  GBP  S&P Global Mfg PMI Final  51.7 -> 51.9   Sep/26, rel 1 Oct   APPLIED
       (lives at /united-kingdom/manufacturing-pmi)
  USD  GDP Growth Rate QoQ       held '-', Q2/26, NEUTRAL           NO CHANGE
  GBP  GDP Growth Rate QoQ       held '-', Q2/26, NEUTRAL           NO CHANGE
       (both are LD-117 range rows carrying no actual; the Q3 print is not
        due until late October)

*** ONE ROW REMAINS GENUINELY UNRECOVERED, AND IT IS THE KNOWN BAD SLUG.

  USD  CB Consumer Confidence    held 89.4 Aug/26

It was scheduled Tue 29 Sep and almost certainly printed. We cannot read it,
because 'CB Consumer Confidence' resolves to
/united-states/consumer-confidence - the UNIVERSITY OF MICHIGAN sentiment
index, a different survey by a different publisher on a different scale. Two
other candidate URLs were tried today and neither carries the Conference
Board history either.

THE ROW IS HELD AT ITS AUGUST VALUE AND SAID TO BE SO. That is the F-73 rule:
an absence we cannot see is a fact about OUR WINDOW, not about the world, and
it is named rather than guessed. R-47 (sweep rate cells against TE) and the
two broken slugs are both carried to the 31 Oct review.

TWO ROWS R-41 FLAGS THAT ARE NOT STALE, both previously established:
  AUD Employment Change  - the FT/PT annotation LD-57 requires (F-139)
  NZD Global Dairy       - we hold the 15 Sep print; the 1 Sep CAPTURE is the
                           stale half, not the cell

### The ledger table R-42 actually parses

`recovered()` reads PIPE-DELIMITED rows: `CCY | ROW | DATE | VALUE | SOURCE`.
Every recovery before today was written as PROSE, so R-42 has been re-reporting
closed issues since it was built - the exact "guard that keeps crying about a
closed issue" its own docstring warns about.

AUD | Household Spending YoY | 2026-09-29 | 6.8% | TE /australia/household-spending
AUD | Inflation Rate YoY | 2026-09-30 | 4.0% | TE /australia/inflation-cpi
EUR | Consumer Confidence Final | 2026-09-29 | -16.5 | TE /euro-area/consumer-confidence
GBP | S&P Global Mfg PMI Final | 2026-10-01 | 51.9 | TE /united-kingdom/manufacturing-pmi
JPY | Retail Sales YoY | 2026-09-30 | 2.7% | TE /japan/retail-sales-annual
NZD | ANZ Business Confidence | 2026-09-30 | 51.9 | TE /new-zealand/business-confidence
USD | ISM Manufacturing PMI | 2026-10-01 | 54.5 | TE /united-states/business-confidence
USD | Non Farm Payrolls | 2026-10-02 | 29K | TE /united-states/non-farm-payrolls
USD | Personal Spending MoM | 2026-09-30 | 0.9% | TE /united-states/personal-spending
USD | Unemployment Rate | 2026-10-02 | 4.2% | TE /united-states/unemployment-rate
GBP | GDP Growth Rate QoQ | 2026-09-30 | - | LD-117 range row, no actual, Q3 not due
USD | GDP Growth Rate QoQ | 2026-09-30 | - | LD-117 range row, no actual, Q3 not due
USD | CB Consumer Confidence | 2026-09-29 | 89.4 (HELD) | UNRECOVERED - slug resolves to U.Michigan, a different survey

## 2026-10-04 - GBP UNEMPLOYMENT RATE ADDED TO THE WHITELIST (F-144)

Jeff: "let's add Unemployment Rate for GBP with the same scoring with the rest"

A newly added row has never passed through a capture window, so R-42 flags it
on sight - correctly. The value comes from the TE indicator page, which is the
VALUE authority (LD-3); the calendar only ever establishes schedule.

GBP | Unemployment Rate | 2026-09-15 | 4.9% | TE /united-kingdom/unemployment-rate

Jul/26 print, released 15 Sep, ONS rolling three-month rate. Flat at 4.9% for a
fourth consecutive period, against a 5.0% consensus. Next print 20 Oct (Aug/26).

Scored on the same rule as the other seven - threshold '<Prev', lower is
better, economic-health channel (F-70). 4.9% = 4.9% is flat, so NEUTRAL.

R-45 verifies it independently against the same page from this build onward,
so this entry closes the gap for the one capture-less week only.
