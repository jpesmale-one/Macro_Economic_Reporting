-- ===========================================================================
-- observations - the append-only calendar archive  (POSTGRES / SUPABASE)
-- ===========================================================================
--
-- The SQLite twin in schema.sql proved the shape against real history; this
-- is the same table with the types and protections Postgres can actually
-- enforce. See schema.sql for why the table exists at all (F-185/186/187).
--
-- Run once against a new project:
--     psql "$SUPABASE_DB_URL" -f db/schema_pg.sql
--
-- It is idempotent - re-running changes nothing.

create table if not exists observations (
    -- WHO SAW IT, AND WHEN ----------------------------------------------
    -- captured_at is the VINTAGE: when WE read this value, not when the
    -- event happened. Half the primary key, which is what makes the table
    -- append-only by construction rather than by discipline.
    captured_at   timestamptz not null,
    capture_file  text        not null,
    source        text        not null,

    -- WHAT IT IS --------------------------------------------------------
    iso           text        not null,
    event         text        not null,
    event_date    date        not null,
    event_time    text,

    -- The whitelist name week_ahead.match() resolved this to, or null when
    -- it matched nothing we score. Kept either way - R-50's lesson: a row
    -- that matches nothing today may match after a whitelist change, and
    -- discarding it would silently shrink history.
    indicator     text,

    -- THE VALUES --------------------------------------------------------
    -- *** F-73 - NULL IS NOT ZERO. These are nullable precisely so that
    -- "we did not see it" is representable. The check constraint below
    -- makes the empty string impossible, so an absence can never be read
    -- as a value.
    actual        text,
    consensus     text,
    forecast      text,
    previous      text,

    source_url    text,
    importance    text,

    primary key (iso, event, event_date, captured_at),

    constraint obs_no_empty_strings check (
        actual   is distinct from '' and
        consensus is distinct from '' and
        forecast is distinct from '' and
        previous is distinct from ''
    ),
    -- *** NOT RESTRICTED TO OUR EIGHT, DELIBERATELY. An earlier version
    -- checked `iso in (our eight)` and would have rejected the rest of the
    -- captured calendar. catalyst.py tier 4 counts EVERY row that landed on
    -- a day to say "N rows landed, none for NZD" - the honesty signal behind
    -- UNEXPLAINED - so dropping other countries turned 83 into 44 and
    -- weakened the claim. Filter at the point of use, never at storage
    -- (R-50's lesson). A two-letter shape is all we require.
    constraint obs_iso_shape check (char_length(iso) between 2 and 3)
);

create index if not exists obs_lookup
    on observations (iso, indicator, event_date, captured_at desc);

create index if not exists obs_vintage
    on observations (captured_at);

-- ===========================================================================
-- The two temporal questions, as functions
-- ===========================================================================
--
-- Keeping these in the database means the dashboard asks them the same way
-- the pipeline does, rather than each re-implementing the cutoff rule and
-- drifting apart.

-- The expectation a print was scored against.
--
-- *** THE CUTOFF IS THE FIRST SIGHTING CARRYING AN ACTUAL, NOT MIDNIGHT ON
-- THE EVENT DATE. NZ's Q3 CPI was dated 2026-10-21 and its consensus 3.8%
-- first appears in the capture taken 2026-10-21 14:03 - hours before the
-- release, same calendar day. A midnight cutoff discards it, falls back to
-- a stale 3.7% forecast, and scores the row GOOD where the answer is BAD:
-- the original F-187 bug, reintroduced by its own fix.
--
-- A value is an expectation for exactly as long as the row has no actual.
create or replace function expectation_at(
        p_iso text, p_indicator text, p_date date)
    returns table (consensus text, forecast text)
    language sql stable
as $$
    select o.consensus, o.forecast
      from observations o
     where o.iso = p_iso
       and o.indicator = p_indicator
       and o.event_date = p_date
       and (o.consensus is not null or o.forecast is not null)
       and o.captured_at <= coalesce(
             (select min(a.captured_at) from observations a
               where a.iso = p_iso and a.indicator = p_indicator
                 and a.event_date = p_date and a.actual is not null),
             'infinity'::timestamptz)
     order by o.captured_at desc
     limit 1;
$$;

-- What we knew at a past instant - F-183b's question. Rebuilding a
-- published edition must use the vintage it was built on, never today's.
create or replace function known_as_of(p_moment timestamptz)
    returns table (iso text, indicator text, event_date date,
                   actual text, consensus text, forecast text,
                   captured_at timestamptz)
    language sql stable
as $$
    select distinct on (o.iso, o.indicator, o.event_date)
           o.iso, o.indicator, o.event_date,
           o.actual, o.consensus, o.forecast, o.captured_at
      from observations o
     where o.captured_at <= p_moment
       and o.indicator is not null
       and o.actual is not null
     order by o.iso, o.indicator, o.event_date, o.captured_at desc;
$$;

-- ===========================================================================
-- Append-only, enforced by the database
-- ===========================================================================
--
-- The primary key already makes a revision a NEW ROW rather than an edit.
-- This stops anything from rewriting or deleting history even by mistake:
-- a trigger, because revoking UPDATE from the owner role is not possible
-- and Supabase's service key runs as owner.
create or replace function observations_append_only()
    returns trigger language plpgsql as $$
begin
    raise exception
      'observations is append-only (F-187): % refused. A revision is a new '
      'row with a later captured_at, never an edit.', tg_op;
end;
$$;

drop trigger if exists observations_no_update on observations;
create trigger observations_no_update
    before update or delete on observations
    for each row execute function observations_append_only();

-- Read-only to everyone else; writes go through the loader with the
-- service key. A published dashboard can read history but never alter it.
alter table observations enable row level security;

drop policy if exists obs_read on observations;
create policy obs_read on observations for select using (true);
