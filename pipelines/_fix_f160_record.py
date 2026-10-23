# -*- coding: utf-8 -*-
"""F-160 - the weekly .md header carried FIVE values pinned to 28 Sep.

Jeff, 2026-10-23: "can you check the link in our 2026-10-18_weekly.md? The
link doesn't seem to be directing me to this week's weekly report"

He is right, and the link is only the half he could see.
"""
import io

P = 'c:/Users/jpesm/OneDrive/Documents/GitHub/Macro_Economic_Reporting/pipelines/build_weekly.py'
s = io.open(P, encoding='utf-8').read()

OLD_CONST = """# LD-130 - the published pages, so the repo copy carries its own pointers.
ARTIFACT = 'https://claude.ai/artifact/DU6Y3sC2T6eoPRu7Jkx82T'
RETRO = 'https://claude.ai/artifact/4PNbyCZETwNq19pTjepWP1'
"""

NEW_CONST = '''# LD-130 - the published pages, so the repo copy carries its own pointers.
#
# *** F-160 (Jeff, 2026-10-23): "the link doesn't seem to be directing me to
# this week's weekly report". He was right, and the link was only the half he
# could SEE. FIVE values in this header were pinned to the 28 Sep-2 Oct
# edition and had been copied forward by every build since:
#     url:     DU6Y3sC2T6eoPRu7Jkx82T   (the 28 Sep page)
#     retro:   4PNbyCZETwNq19pTjepWP1   (the retro before it)
#     date:    2026-09-27
#     title:   Week of 28 Sep-2 Octtember 2026   (note the typo, carried too)
#     eyebrow: selection for the 28 Sep-2 Oct cycle
#
# THIS IS F-130's DEFECT IN THE ONE PLACE F-130's GUARD DOES NOT LOOK. R-46
# step 8 scans build_weekly.py - but only for START/END date PAIRS and
# dt.date() literals. A bare `date: 2026-09-27` string, a title and a URL are
# invisible to it, so the check passed on every build while the header told
# Jeff he was reading a four-week-old report.
#
# THE FIX IS A PER-EDITION MANIFEST KEYED ON THE WINDOW, not a new constant to
# forget. EDITIONS[START] holds what only a human can supply - the published
# URL and the previous retrospective - and everything else is DERIVED from
# START/END, which R-46 step 8 already guards. A window with no entry yields
# no url line rather than a WRONG one: absence is honest, a stale pointer is
# not (the F-73 principle - never a guessed value).
EDITIONS = {
    '2026-10-19': ('https://claude.ai/artifact/NhyqPwGB11jK1uwSxwzi3N',
                   'https://claude.ai/artifact/MrfibJq6Q6iG3wnST8aDjA'),
    '2026-10-12': ('https://claude.ai/artifact/VYdPphZ1WtGXuBUrfGtK9n',
                   'https://claude.ai/artifact/4PNbyCZETwNq19pTjepWP1'),
    '2026-09-28': ('https://claude.ai/artifact/DU6Y3sC2T6eoPRu7Jkx82T',
                   'https://claude.ai/artifact/4PNbyCZETwNq19pTjepWP1'),
}
ARTIFACT, RETRO = EDITIONS.get(START, ('', ''))
if not ARTIFACT:
    print('  NOTE: no published URL recorded for the %s edition - the md will '
          'carry no url line (F-160: absence beats a stale pointer). Add it to '
          'EDITIONS once the page is published.' % START)

# DERIVED HEADER IDENTITY (F-160). Everything below comes from START/END, which
# R-46 step 8 guards, so a window change cannot leave the header behind.
_D0 = dt.datetime.strptime(START, '%Y-%m-%d').date()
_D1 = dt.datetime.strptime(END, '%Y-%m-%d').date()
_SUN = _D0 - dt.timedelta(days=1)          # the build day: the Sunday before
_MON = '%d %s' % (_D0.day, _D0.strftime('%b'))
_FRI = '%d %s' % (_D1.day, _D1.strftime('%b'))
# "19-23 Oct" when the month is shared, "28 Sep-2 Oct" when it is not
_SPAN = ('%d&ndash;%s' % (_D0.day, _FRI)) if _D0.month == _D1.month \\
        else ('%s&ndash;%s' % (_MON, _FRI))
_TITLE = 'Week of %s %d &middot; WEEKLY &middot; %s' \\
         % (_SPAN, _D1.year, _SUN.strftime('%a %-d %b').replace('Sun', 'Sunday')
            if False else 'Sunday %d %s' % (_SUN.day, _SUN.strftime('%b')))
_EYEBROW = ('Macro Economic Reporting &middot; weekly &mdash; selection for '
            'the %s cycle' % _SPAN)
'''

assert OLD_CONST in s, 'constant block not found'
s = s.replace(OLD_CONST, NEW_CONST, 1)

# the three literal header lines
s = s.replace("A('date: 2026-09-27')", "A('date: %s' % _SUN.isoformat())", 1)
old_title = """A('title: Week of 28 Sep&ndash;2 Octtember 2026 &middot; WEEKLY &middot; '
  'Sunday 27 Sep')"""
assert old_title in s, 'title line not found'
s = s.replace(old_title, "A('title: %s' % _TITLE)", 1)
old_eye = """A('eyebrow: Macro Economic Reporting &middot; the REVAMPED weekly &mdash; '
  'selection for the 28 Sep&ndash;2 Oct cycle')"""
assert old_eye in s, 'eyebrow line not found'
s = s.replace(old_eye, "A('eyebrow: %s' % _EYEBROW)", 1)

# the retro line must not print an empty pointer either
old_retro = """A("> **Last week&#39;s retrospective** &middot; %s" % RETRO)"""
new_retro = """if RETRO:
    A("> **Last week&#39;s retrospective** &middot; %s" % RETRO)"""
assert old_retro in s, 'retro line not found'
s = s.replace(old_retro, new_retro, 1)

# OUT must follow the window too, not a pinned filename
s = s.replace("OUT = 'reports/2026/Q4/2026-10-18_weekly.md'",
              "OUT = 'reports/2026/Q4/%s_weekly.md' % _SUN.isoformat()", 1)

if 'import datetime as dt' not in s:
    s = s.replace('import io', 'import datetime as dt\nimport io', 1)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('build_weekly.py: five pinned values now derived')
