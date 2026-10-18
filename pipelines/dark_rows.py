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
        ('49.6', 'Sep/26', '2026-10-04',
         'TE /australia/manufacturing-pmi - 52.0 Aug -> 49.6 Sep, sharpest '
         'fall in 21 months, released 30 Sep'),
    ('NZD', 'Business NZ PMI'):
        ('56.5', 'Sep/26', '2026-10-18',
         'the 2026-10-18 CAPTURE carries "business nz pmi sep" actual 56.5, '
         'previous 53.3 (TE revision marker), released 15 Oct. The indicator '
         'page slug still does not resolve, so the CAPTURE is the authority '
         'for this row - which is exactly why R-37/R-40 exist alongside '
         'R-45: 13 rows have no usable page at all. 53.1 Aug -> 56.5 Sep is '
         'a 3.4-point jump and it took NZD Production from 0 to +1.'),
    ('USD', 'ISM Manufacturing PMI'):
        ('54.5', 'Sep/26', '2026-10-04',
         'TE /united-states/business-confidence - 54.6 Aug -> 54.5 Sep, '
         'released 1 Oct'),
    ('GBP', 'S&P Global Mfg PMI Final'):
        ('51.9', 'Sep/26', '2026-10-04',
         'TE /united-kingdom/manufacturing-pmi - 51.7 Aug -> 51.9 Sep, '
         'released 1 Oct'),
    ('NZD', 'Global Dairy Trade Price Index'):
        ('-1.1%', '15 Sep', '2026-09-30',
         'TE /new-zealand/global-dairy-trade-price-index - next auction '
         '6 Oct'),
    ('NZD', 'Unemployment Rate'):
        ('5.6%', 'Q2/26', '2026-09-30',
         'TE /new-zealand/unemployment-rate - quarterly, Q3 due 3 Nov'),
    ('NZD', 'Inflation Rate YoY'):
        ('4.1%', 'Q2/26', '2026-09-30',
         'TE /new-zealand/inflation-cpi - quarterly, Q3 due 21 Oct'),
    ('USD', 'Non Farm Payrolls'):
        ('29K', 'Sep/26', '2026-10-04',
         'TE /united-states/non-farm-payrolls - 162K Aug -> 29K Sep vs 100K '
         'consensus, released 2 Oct'),

    # *** UNRESOLVED. The slug points at a DIFFERENT SERIES and no alternative
    # URL has been found. Held at its last known value and SAID to be held
    # (F-73) - never silently carried as if checked.
    ('USD', 'CB Consumer Confidence'):
        ('81.9', 'Sep/26', '2026-10-18',
         'NO LONGER UNVERIFIED. The slug still resolves to '
         '/united-states/consumer-confidence = University of Michigan '
         'sentiment, a DIFFERENT survey - that defect stands and R-45 can '
         'never check this row. Read from the Conference Board release and '
         'CONFIRMED BY THREE INDEPENDENT SOURCES: 81.9 Sep, down 6.7 from '
         '88.6 Aug, against an 89.2 consensus, lowest since 2014. Score is '
         '-1 either way, so the board did not move - but the held 89.4 was '
         'wrong by 7.5 points and two vintages.'),
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
