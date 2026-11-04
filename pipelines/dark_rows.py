# -*- coding: utf-8 -*-
"""F-143b - THE ROWS R-45 CANNOT READ, AND WHO CHECKED THEM.

Jeff, 2026-10-04: "PMIs are not updated. example AUD S&P Global Mfg PMI Final
52.0" ... "Do I need to check the data again 1 by 1?"

NO - but until R-45 can read these pages, SOMETHING has to, and the answer
cannot be "trust the build". This file is that something: a ledger of the rows
no automated check reaches, each with the value, the date it was read, and the
page it came from.

*** WHY R-45 CANNOT READ THEM. It fetches with curl. Several TE indicator
pages render their release table CLIENT-SIDE, so curl gets a 20KB shell with
the right <title> and no data. fetch() returns text, the row regex finds
nothing, and the row is reported NO PAGE - indistinguishable from a bad slug.
The AUD PMI page is the example: it exists, it is correct, and it is empty to
a non-browser client.

*** AND THE OLD REPORT CALLED THEM VERIFIED ANYWAY (F-143). A row that matched
ANY captured event counted as checked, including one from a capture five weeks
old. AUD's PMI matched its AUGUST print from a 1 SEP capture and was listed
under "they are not unchecked" while the SEPTEMBER print (49.6, released 30
Sep) went unseen. Honest coverage is 57 of 70, not 63.

THE RULE: a value here is only as good as its READ_ON date. Anything older
than the row's own release cadence is stale by definition, and `stale()`
reports it rather than waiting to be asked.
"""
import datetime as dt

# (CCY, Indicator) -> (value, ref_month, read_on, source)
READS = {
    ('AUD', 'S&P Global Mfg PMI Final'):
        ('49.6', 'Oct/26', '2026-11-04',
         'the 2026-11-03 CAPTURE carries "s&p global manufacturing pmi final '
         'oct" actual 49.6, previous 49.6, consensus 49.7, released 1 Nov. '
         '*** THE VALUE DID NOT MOVE - 49.6 Sep -> 49.6 Oct - so only the '
         'VINTAGE changed. This is F-123 exactly: a repeated value hides a '
         'stale vintage from any check that compares on value alone. The '
         'previous read was TE /australia/manufacturing-pmi, 52.0 Aug -> '
         '49.6 Sep, the sharpest fall in 21 months, released 30 Sep.'),
    ('NZD', 'Business NZ PMI'):
        ('56.5', 'Sep/26', '2026-10-18',
         'the 2026-10-18 CAPTURE carries "business nz pmi sep" actual 56.5, '
         'previous 53.3 (TE revision marker), released 15 Oct. The indicator '
         'page slug still does not resolve, so the CAPTURE is the authority '
         'for this row - which is exactly why R-37/R-40 exist alongside '
         'R-45: 13 rows have no usable page at all. 53.1 Aug -> 56.5 Sep is '
         'a 3.4-point jump and it took NZD Production from 0 to +1.'),
    ('USD', 'ISM Manufacturing PMI'):
        ('55.5', 'Oct/26', '2026-11-04',
         'the 2026-11-03 CAPTURE carries "ism manufacturing pmi oct" actual '
         '55.5, previous 54.5, consensus 54.6, released 2 Nov - a BEAT. The '
         'capture is the authority here for the same reason as the NZD row '
         'above. Updated in the F-185 sweep, when R-40 found this row one '
         'vintage behind along with 8 others from the same 2 Nov PMI round.'),
    ('GBP', 'S&P Global Mfg PMI Final'):
        ('52.8', 'Oct/26', '2026-11-04',
         'the 2026-11-03 CAPTURE carries "s&p global manufacturing pmi final '
         'oct" actual 52.8, previous 51.9, consensus 52.8 - exactly on '
         'consensus, released 2 Nov. Updated in the F-185 sweep.'),
    ('NZD', 'Global Dairy Trade Price Index'):
        ('2.5%', 'Oct/26', '2026-10-26',
         'TE /new-zealand/global-dairy-trade-price-index - auction for the '
         'two weeks ended 20 Oct, 1.2% -> 2.5%, released 20 Oct. Verified '
         'on the indicator page, which R-45 cannot reach (no slug).'),
    ('NZD', 'Unemployment Rate'):
        ('5.6%', 'Q2/26', '2026-09-30',
         'TE /new-zealand/unemployment-rate - quarterly, Q3 due 3 Nov'),
    ('NZD', 'Inflation Rate YoY'):
        ('3.7%', 'Q3/26', '2026-10-26',
         'TE /new-zealand/inflation-cpi - quarterly, Q3 LANDED 21 Oct: '
         '4.1% -> 3.7%. The ledger had said "Q3 due 21 Oct" and it did.'),
    ('USD', 'Non Farm Payrolls'):
        ('29K', 'Sep/26', '2026-10-04',
         'TE /united-states/non-farm-payrolls - 162K Aug -> 29K Sep vs 100K '
         'consensus, released 2 Oct'),

    # *** UNRESOLVED. The slug points at a DIFFERENT SERIES and no alternative
    # URL has been found. Held at its last known value and SAID to be held
    # (F-73) - never silently carried as if checked.
    ('USD', 'CB Consumer Confidence'):
        ('91.7', 'Oct/26', '2026-11-01',
         'STILL UNREACHABLE BY R-45, AND THE TRAP FIRED AGAIN TODAY. The '
         'slug /united-states/consumer-confidence resolves to University of '
         'Michigan SENTIMENT, a different survey; fetching it on 1 Nov '
         'returned 48.0 Oct/26 where the capture said 91.7 - a wrong-SERIES '
         'read of exactly the F-29/F-37 kind, caught only because the two '
         'disagreed by 44 points. Read instead from the Conference Board '
         'release of 27 Oct: 91.7 for Oct/26, up 7.5 from a REVISED 84.2 '
         'Sep (the 81.9 we held was revised up), against an 81.0 consensus. '
         'A rise over prev scores GOOD, where Sep scored BAD - so this row '
         'FLIPS SIGN this week and the board moves with it.'),
    ('NZD', 'Electronic Retail Card Spending YoY'):
        ('0.9%', 'Sep/26', '2026-10-18',
         'NO LONGER UNVERIFIED. The slug still resolves to '
         '/new-zealand/retail-sales-annual, which returns LEVELS in NZD '
         "millions rather than this row's YoY percentage - that defect "
         'stands. But the 2026-10-18 capture carries the series directly: '
         '"electronic retail card spending YOY sep" actual 0.9%, previous '
         '0.2%, released 15 Oct. *** THE CAPTURE ALSO CARRIES A MOM ROW AT '
         '-0.4% ON THE SAME DAY, and taking that would be an F-37 error - '
         'the transform is part of the series identity. This row is the '
         'YoY.'),
}

# how long a read stays good, by cadence
CADENCE_DAYS = {'Monthly': 35, 'Quarterly': 100, 'Fortnightly': 18}


def stale(today=None, default_days=35):
    """[(ccy, name, read_on, age_days)] for reads older than their cadence."""
    today = today or dt.date.today()
    out = []
    for (c, n), (v, ref, read_on, src) in sorted(READS.items()):
        if read_on == 'UNVERIFIED':
            out.append((c, n, read_on, None))
            continue
        d = dt.datetime.strptime(read_on, '%Y-%m-%d').date()
        age = (today - d).days
        limit = CADENCE_DAYS['Quarterly'] if '(Q' in ref or 'Q' in ref[:2] \
            else default_days
        if age > limit:
            out.append((c, n, read_on, age))
    return out


if __name__ == '__main__':
    print('F-143b  ROWS NO AUTOMATED CHECK REACHES  (%d)' % len(READS))
    print()
    print('  %-4s %-36s %-9s %-9s %s'
          % ('CCY', 'ROW', 'VALUE', 'REF', 'READ ON'))
    for (c, n), (v, ref, read_on, src) in sorted(READS.items()):
        print('  %-4s %-36s %-9s %-9s %s' % (c, n[:36], v, ref, read_on))
    print()
    bad = stale()
    if bad:
        print('*** %d ROW(S) NEED A FRESH READ:' % len(bad))
        for c, n, read_on, age in bad:
            print('    %-4s %-36s %s'
                  % (c, n[:36],
                     'NEVER VERIFIED' if age is None else '%d days old' % age))
    else:
        print('every read is inside its cadence')
