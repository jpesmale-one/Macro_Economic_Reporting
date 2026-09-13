# TE indicator-page cache (R-45)

`indicator_pages.py` reads TE's PER-INDICATOR pages, which carry a release
history table the calendar does not keep. Cached here as provenance (LD-3):
the calendar is a SCHEDULE authority, these pages are the VALUE authority for
a released actual.

Re-fetch with `--refresh`. Without it, cached copies are reused so a sweep
costs nothing and can run before every edition.
