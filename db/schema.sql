-- ===========================================================================
-- observations - the append-only calendar archive
-- ===========================================================================
--
-- *** THE DEFECT THIS TABLE EXISTS TO RETIRE.
--
-- F-185/186/187 all have one shape: the EXPECTATION a print was scored
-- against had rolled out of the source's window before we read it. We held
-- the data - 43 whole-file captures going back to 29 August - but each
-- capture is a snapshot, and load_inflation() reads ONE file. A value that
-- has rolled off the back of the newest capture is unreachable even though
-- an older capture on the same disk still holds it.
--
-- The fix is not more captures. It is one row per (observation, sighting),
-- so "what did we expect before this print landed" becomes a query instead
-- of a file hunt:
--
--     select forecast, consensus from observations
--      where iso = 'JP' and indicator = 'Inflation Rate YoY'
--        and event_date = '2026-10-22'
--        and captured_at < '2026-10-22'
--      order by captured_at desc
--      limit 1;
--
-- *** APPEND-ONLY IS THE POINT, NOT A STYLE CHOICE.
--
-- A row is never updated. When a later capture shows a different actual for
-- the same event, that is a NEW ROW with a later captured_at, and both are
-- kept. Three things fall out of that:
--
--   1. revisions are visible rather than silently overwritten;
--   2. "what did we know on date X" is answerable forever, which is what
--      F-183b needs when rebuilding a published edition;
--   3. a late-arriving actual - biquote fills rows in over days - lands as
--      a new sighting without destroying the earlier expectation.
--
-- *** PORTABILITY. Written to run on both Postgres (Supabase) and SQLite,
-- because the schema is the valuable part and it should not wait on a
-- hosted project existing. Postgres-only refinements are marked and kept
-- out of the core DDL.

create table if not exists observations (
    -- WHO SAW IT, AND WHEN ----------------------------------------------
    -- captured_at is the vintage: the moment WE read this value, not when
    -- the event happened. It is half the primary key, which is what makes
    -- the table append-only by construction.
    captured_at   text    not null,
    capture_file  text    not null,   -- provenance back to the raw snapshot
    source        text    not null,   -- 'biquote' | 'tradingeconomics' | agency

    -- WHAT IT IS --------------------------------------------------------
    iso           text    not null,   -- US EA GB JP AU NZ CA CH
    event         text    not null,   -- the source's own name, lowercased
    event_date    text    not null,   -- the date the print belongs to
    event_time    text,               -- 'HH:MM AM/PM' as captured, may be ''

    -- the whitelist name week_ahead.match() resolved this to, or null when
    -- the row matched nothing we score. Kept either way: an unmatched row
    -- today may be matchable after a whitelist change, and discarding it
    -- would silently shrink history (R-50's lesson).
    indicator     text,

    -- THE VALUES --------------------------------------------------------
    -- *** F-73 - NULL IS NOT ZERO. An absent value is absent. These columns
    -- are nullable precisely so that "we did not see it" is representable;
    -- writing 0 or '' here would be a guessed reading.
    actual        text,
    consensus     text,
    forecast      text,
    previous      text,

    source_url    text,
    importance    text,

    -- One sighting of one event. A second sighting with new values is a new
    -- row because captured_at differs - that IS the append-only guarantee,
    -- enforced by the key rather than by convention.
    primary key (iso, event, event_date, captured_at)
);

-- The temporal lookup above is the whole point, so index for it.
create index if not exists obs_lookup
    on observations (iso, indicator, event_date, captured_at);

-- Sweeping a whole vintage (one capture) must stay cheap.
create index if not exists obs_vintage
    on observations (captured_at);

-- ===========================================================================
-- latest_known - the question the old code could not ask
-- ===========================================================================
--
-- For every (iso, indicator, event_date), the most recent sighting AS OF a
-- given moment. In Postgres this would be a view taking a parameter via a
-- function; expressed here as a view over "all sightings" so both engines
-- can read it, with the as-of filter applied by the caller.
create view if not exists observation_history as
select iso, indicator, event, event_date, captured_at,
       actual, consensus, forecast, previous, source, capture_file
  from observations
 where indicator is not null;

-- ===========================================================================
-- Postgres / Supabase only - NOT executed by the SQLite proof.
-- ===========================================================================
-- Append-only enforced by the database rather than by discipline:
--
--   revoke update, delete on observations from authenticated, anon;
--
-- and row-level security so a published dashboard can read without being
-- able to rewrite history:
--
--   alter table observations enable row level security;
--   create policy obs_read on observations for select using (true);
--
-- captured_at and event_date become timestamptz and date. They are text
-- here because SQLite has no date type and ISO-8601 text sorts correctly in
-- both engines, so every query in this file behaves identically on each.
