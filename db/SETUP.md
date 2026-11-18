# Supabase setup

Everything on this side is ready. These are the steps that need a browser,
and the one command that finishes the job.

## 1. Create the project

<https://supabase.com/dashboard> → **New project**

| Field | Value |
|---|---|
| Name | `macro-reporting` (anything) |
| Region | Southeast Asia (Singapore) — nearest to Manila |
| Plan | **Free** is enough |
| Database password | generate one and keep it |

The free tier gives 500 MB, which is ample: the whole archive is **27,114
rows**, a few MB. Note that a free project **pauses after 7 days with no
activity** — it resumes on the next connection, but a nightly capture keeps
it awake anyway.

## 2. Copy the connection string

**Project Settings → Database → Connection string → URI**, and tick
**Use connection pooling** (port `6543`). The pooler is the right choice for
short-lived script connections; the direct port `5432` is for long-lived
ones.

It looks like:

```
postgresql://postgres.abcdefghijklm:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

## 3. Save it locally — never in the repo

Create `db/.env` (already gitignored, verified):

```
SUPABASE_DB_URL=postgresql://postgres.abcdefghijklm:your-password@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

Check it without printing the password:

```bash
python pipelines/db_connect.py
```

It reports the server and whether `observations` exists, with the password
redacted.

## 4. Create the table and load the history

```bash
psql "$SUPABASE_DB_URL" -f db/schema_pg.sql     # idempotent
python pipelines/db_backfill.py --write          # 27,114 rows
python pipelines/test_db.py                      # the F-187 proof
```

`db_backfill.py` targets Postgres automatically once `SUPABASE_DB_URL` is
set — no flag needed. It is idempotent, so re-running after every capture is
safe and is how new vintages get in.

## What the Postgres schema adds over the local SQLite one

- `captured_at timestamptz`, `event_date date` — real types, so date maths
  and sorting are the database's job rather than string luck.
- **Append-only enforced by a trigger.** `update` and `delete` raise. The
  primary key already makes a revision a new row; this stops history being
  rewritten by accident. Supabase's service key runs as owner, so revoking
  the privilege would not have been enough.
- **Check constraints** for F-73 — an empty string cannot be stored, so an
  absence can never be read back as a value — and for the eight-currency ISO
  whitelist.
- **`expectation_at()` and `known_as_of()`** as database functions, so a
  dashboard asks the temporal questions exactly the way the pipeline does
  instead of re-implementing the cutoff rule and drifting.
- **Row-level security**, read-only to everyone but the loader.

## If the project pauses or the URL changes

Delete `db/.env`, and everything falls back to the local SQLite file
automatically — the pipeline keeps working offline. Re-create the file to
point back at Supabase. Nothing else changes.
