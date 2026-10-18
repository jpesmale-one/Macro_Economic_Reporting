# -*- coding: utf-8 -*-
"""THE ROWS THAT RE-PRINTED, FOR THE Oct-26 ROLL.

Jeff, 2026-10-04: "Don't forget to refresh the macro data"

Every value below was raised by R-45 (vs the TE indicator page), R-40 (vs the
capture) or R-41, and cross-read against the TE page before landing here. The
three checks overlap but do not agree exactly - R-45 sees all 70 rows through
indicator pages, R-40/R-41 see only what a capture window reached - so the
union is what gets refreshed and each row is confirmed on the page that owns
it (LD-3: a calendar is a SCHEDULE authority, never a VALUE authority).

*** TWO ROWS THE CHECKS RAISED AND ARE **NOT** REFRESHED, both known:

  AUD Employment Change   R-41 calls '39.5K (FT -6.3K, PT +45.8K)' stale
                          against TE's '39.5K'. It is not - that is F-139,
                          a string compare against our own house style, and
                          LD-57 requires the split. R-40 handles it.

  NZD Global Dairy        R-41 compares against the newest CAPTURE, and the
                          1 Sep capture carries the older 0.9% print. We hold
                          -1.1% for 15 Sep, which the TE page confirms is
                          still the latest. The CELL is current; the capture
                          is not.

THE HEADLINE OF THIS REFRESH: USD Non Farm Payrolls 162K -> 29K. Not a
revision - the September print, released Fri 2 Oct, and a collapse against a
100K consensus. USD Unemployment 4.1% -> 4.2% the same morning.
"""

# (CCY, Indicator) -> the actual AS PUBLISHED (LD-112 - store the print, let
# derive_scores.py do the grading)
UPDATES = {
    # ---- 2026-10-18 BUILD: prints that landed 12-16 Oct -------------------
    # R-45 swept all 70 rows and found FIFTEEN stale. Every value read from
    # the TE INDICATOR PAGE (LD-3 owns the value); the six marked
    # [page+capture] agree with our own 2026-10-18 capture as well.
    ('USD', 'Industrial Production YoY'):          '2.2%',                            # Sep/26, rel 16 Oct  [page]
    ('USD', 'Manufacturing Production YoY'):       '1.1%',                            # Sep/26, rel 16 Oct  [page]
    ('EUR', 'Industrial Production YoY'):          '-1.1%',                           # Aug/26, rel 15 Oct  [page+capture]
    ('GBP', 'Industrial Production YoY'):          '1.6%',                            # Aug/26, rel 15 Oct  [page]
    ('GBP', 'Manufacturing Production YoY'):       '3%',                              # Aug/26, rel 15 Oct  [page]
    ('JPY', 'Industrial Production YoY Final'):    '2.7%',                            # Aug/26, rel 15 Oct  [page+capture]
    ('JPY', 'Machinery Orders YoY'):               '18.6%',                           # Aug/26, rel 14 Oct  [page]
    ('USD', 'Retail Sales YoY'):                   '6.3%',                            # Sep/26, rel 15 Oct  [page]
    ('AUD', 'NAB Business Confidence'):            '-13',                             # Sep/26, rel 13 Oct  [page]
    ('EUR', 'Balance of Trade'):                   'EUR-16.1B',                       # Aug/26, rel 16 Oct  [page+capture]
    ('GBP', 'Balance of Trade'):                   'GBP-0.920B',                      # Aug/26, rel 15 Oct  [page]
    ('AUD', 'Employment Change'):                  '-39.3K (FT +34.4K, PT -73.7K)',   # Sep/26, rel 15 Oct  [page+capture, all 3 legs]
    ('AUD', 'Unemployment Rate'):                  '4.7%',                            # Sep/26, rel 15 Oct  [page+capture]
    ('USD', 'Inflation Rate YoY'):                 '3.7%',                            # Sep/26, rel 14 Oct  [page]
    ('EUR', 'Inflation Rate YoY Final'):           '3.8%',                            # Sep/26, rel 16 Oct  [page+capture]
    # *** THREE MORE R-45 COULD NOT SEE, CAUGHT BY R-37 INSTEAD.
    # All three sit in R-45's "NO PAGE" list - the slug does not resolve - so
    # only the capture (R-37/R-40) could find them. THIS IS WHY BOTH CHECKS
    # EXIST: 13 rows have no usable indicator page, and for those the capture
    # is the only authority available.
    ('NZD', 'Business NZ PMI'):                '56.5',   # Sep/26, rel 15 Oct [capture]
    ('NZD', 'Electronic Retail Card Spending YoY'): '0.9%',  # Sep/26, rel 15 Oct [capture, YoY not MoM]
    ('CAD', 'Building Permits MoM'):           '8.8%',   # Aug/26, rel 14 Oct [TE page read directly]
    # *** USD CB CONSUMER CONFIDENCE - THE "NEVER VERIFIED" ROW, FINALLY READ.
    # Its TE slug resolves to /united-states/consumer-confidence = UNIVERSITY
    # OF MICHIGAN sentiment, a DIFFERENT survey, so R-45 can never check it and
    # the dark-row ledger has carried it as UNVERIFIED since it was created.
    # Read from the Conference Board release instead and CONFIRMED BY THREE
    # INDEPENDENT SOURCES before changing a scoring row: 81.9 for September,
    # down 6.7 from 88.6 in August, against a 89.2 consensus - the lowest since
    # 2014. (Present Situation 109.3, Expectations 63.6.)
    # The SCORE is -1 either way (89.4 vs 90.2 also fell), so the board does
    # not move - but the PRINTED value was wrong by 7.5 points and two
    # vintages, and a row nothing can check is exactly the row to read by hand.
    ('USD', 'CB Consumer Confidence'):         '81.9',   # Sep/26, rel 29 Sep [Conference Board, 3 sources]
    # ---- 2026-10-11 BUILD: prints that landed 5-9 Oct ---------------------
    # Every value raised by R-45 against the TE indicator page and confirmed
    # on the page that owns it (LD-3).
    ('CAD', 'Employment Change'):   '-68.3K (FT -35.4K, PT -32.9K)',
    ('CAD', 'Unemployment Rate'):   '6.5%',
    ('CAD', 'Balance of Trade'):    'C$4.2B',
    ('USD', 'Balance of Trade'):    '$-105.6B',
    ('EUR', 'Retail Sales YoY'):    '0.8%',
    ('JPY', 'Machine Tool Orders YoY'): '60.4%',
    ('JPY', 'Household Spending YoY'):  '-3.1%',
    ('JPY', 'Consumer Confidence'): '35.4',
    ('CHF', 'Consumer Confidence'): '-36',
    ('CHF', 'Unemployment Rate'):   '3%',
    ('AUD', 'ANZ-Indeed Job Ads MoM'): '2.2%',
    ('AUD', 'Building Permits YoY Final'): '10.3%',   # Aug/26, rel 7 Oct
    ('AUD', 'Westpac Consumer Conf Change'): '-4.7%', # Oct/26, rel 5 Oct

    # *** F-147 - A ROW DROPPED FROM THIS DICT IS SILENTLY REVERTED.
    # roll_month copies the PREVIOUS column forward for every row it does not
    # find here, so removing a corrected row does not leave it alone - it
    # restores the pre-correction value from the month before. Three PMI
    # fixes from the 2026-10-04 build (USD ISM 54.5, GBP 51.9, AUD 49.6) were
    # overwritten by exactly that on the first roll after they landed, and
    # AUD's is the one that took the board from +1.67 to -2.33.
    #
    # SO EVERY CORRECTION STAYS IN THIS DICT UNTIL ITS SERIES RE-PRINTS,
    # not just in the week it was made.
    ('USD', 'ISM Manufacturing PMI'):   '54.5',   # Sep/26, rel 1 Oct
    ('GBP', 'S&P Global Mfg PMI Final'): '51.9',  # Sep/26, rel 1 Oct
    ('AUD', 'S&P Global Mfg PMI Final'): '49.6',  # Sep/26, rel 30 Sep
    # the RBA hike (F-142) is a CELL IN THE FACT TABLE TOO, and the roll
    # reverted it for the same reason. R-46 step 6 caught it; this stops it
    # recurring every Sunday.
    ('AUD', 'RBA Interest Rate Decision'): '4.60%',

    # ---- the 2026-10-04 build, kept for the record ------------------------

    # ---- EMPLOYMENT -------------------------------------------------------
    ('USD', 'Non Farm Payrolls'):            '29K',      # Sep/26, rel 2 Oct
    ('USD', 'Unemployment Rate'):            '4.2%',     # Sep/26, rel 2 Oct
    ('EUR', 'Unemployment Rate'):            '6.4%',     # Aug/26, rel 1 Oct
    ('JPY', 'Unemployment Rate'):            '2.5%',     # Aug/26, rel 1 Oct

    # ---- INFLATION --------------------------------------------------------
    ('AUD', 'Inflation Rate YoY'):           '4.0%',     # Aug/26, rel 30 Sep
    ('CHF', 'Inflation Rate YoY'):           '1%',       # Sep/26, rel 1 Oct

    # ---- SPENDING ---------------------------------------------------------
    ('USD', 'Personal Spending MoM'):        '0.9%',     # Aug/26, rel 30 Sep
    ('JPY', 'Retail Sales YoY'):             '2.7%',     # Aug/26, rel 29 Sep
    ('CHF', 'Retail Sales YoY'):             '3.2%',     # Aug/26, rel 1 Oct
    ('AUD', 'Household Spending YoY'):       '6.8%',     # Aug/26, rel 29 Sep
    ('EUR', 'Consumer Confidence Final'):    '-16.5',    # Sep/26, rel 29 Sep
    ('NZD', 'ANZ Business Confidence'):      '51.9',     # Sep/26, rel 30 Sep
    ('NZD', 'ANZ Roy Morgan Consumer Conf'): '97.6',     # Sep/26, rel 2 Oct

    # ---- TRADE ------------------------------------------------------------
    ('AUD', 'Balance of Trade'):             'A$0.495B',  # Aug/26, rel 1 Oct

    # ---- PRODUCTION (the Thu 1 Oct PMI sweep) -----------------------------
    ('CAD', 'S&P Global Mfg PMI'):           '51.5',     # Sep/26, rel 1 Oct
    ('CHF', 'Procure.ch-UBS Mfg PMI'):       '55.3',     # Sep/26, rel 1 Oct
    ('EUR', 'S&P Global Mfg PMI Final'):     '52.9',     # Sep/26, rel 1 Oct
    ('JPY', 'S&P Global Mfg PMI Final'):     '54.1',     # Sep/26, rel 1 Oct
}
