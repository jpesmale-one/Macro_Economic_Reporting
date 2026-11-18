# -*- coding: utf-8 -*-
"""Where the database lives, and how we reach it.

*** CREDENTIALS NEVER GO IN THE REPO. The connection string is read from the
environment, or from db/.env which is gitignored. Nothing here is committed
with a secret in it, and nothing prints one.

Set it once:

    # db/.env  (gitignored)
    SUPABASE_DB_URL=postgresql://postgres.<ref>:<password>@<host>:6543/postgres

Then every tool uses it automatically. With no URL set, everything falls
back to the local SQLite file, so the pipeline keeps working offline and a
missing credential degrades to "local" rather than to a crash.

    python pipelines/db_connect.py        # report what we would connect to
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ENV = os.path.join(REPO, 'db/.env')
SQLITE = os.path.join(REPO, 'data/macro.db')


def _load_env():
    """db/.env -> os.environ, without overwriting a real env var."""
    if not os.path.exists(ENV):
        return
    for line in io.open(ENV, encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


def url():
    """The Postgres URL, or None to mean 'use SQLite'."""
    _load_env()
    return (os.environ.get('SUPABASE_DB_URL')
            or os.environ.get('DATABASE_URL') or None)


def redacted(u):
    """A URL safe to print - the password becomes ***."""
    if not u:
        return '(none)'
    if '@' not in u or '//' not in u:
        return '(set)'
    head, tail = u.split('@', 1)
    scheme, cred = head.split('//', 1)
    user = cred.split(':', 1)[0]
    return '%s//%s:***@%s' % (scheme, user, tail)


def is_pg():
    return url() is not None


def advise(u):
    """Problems we can see in the URL itself, before dialling out.

    Both of these produce confusing failures: the placeholder authenticates
    as a password literally called '[YOUR-PASSWORD]', and the direct host is
    IPv6-only on the free tier, so it fails with a network error that looks
    like the project is down.
    """
    out = []
    if not u:
        return out
    if 'YOUR-PASSWORD' in u or 'YOUR_PASSWORD' in u:
        out.append('the password placeholder is still in the URL - paste the '
                   'real database password from step 1')
    if 'YOUR_PROJECT_REF' in u:
        out.append('the project ref placeholder is still in the URL')
    # *** THE THREE MODES DIFFER BY HOST AS WELL AS PORT, so editing the
    # port on a DIRECT string yields a host/port pair that exists nowhere.
    # Say which mode this actually is rather than leaving it to the eye.
    pooler = '.pooler.supabase.com' in u
    if not pooler and 'supabase' in u:
        out.append('MODE: direct connection (db.<ref>.supabase.co). This is '
                   'IPv6-only on the free tier and usually fails from home '
                   'networks. Do NOT just change the port - the pooler has a '
                   'different HOST and username too. Re-copy from Connect -> '
                   'Transaction pooler.')
    elif pooler and ':5432/' in u:
        out.append('MODE: session pooler (port 5432). Transaction pooler '
                   '(6543) suits short-lived script connections better. Here '
                   'the host is already right, so changing 5432 to 6543 is '
                   'all that differs - safe to edit by hand.')
    elif pooler and ':6543/' in u:
        pass                      # transaction pooler - what we want
    return out


def connect():
    """An open connection, plus a flag saying which engine it is.

    Returns (conn, 'pg'|'sqlite'). The caller closes it.
    """
    u = url()
    if u:
        import psycopg
        return psycopg.connect(u), 'pg'
    import sqlite3
    return sqlite3.connect(SQLITE), 'sqlite'


def ph(engine, n):
    """Parameter placeholders - sqlite uses ?, psycopg uses %s."""
    return ','.join(['?' if engine == 'sqlite' else '%s'] * n)


def main():
    u = url()
    print('DATABASE TARGET')
    print('  engine : %s' % ('postgres (supabase)' if u else 'sqlite (local)'))
    print('  url    : %s' % redacted(u))
    if not u:
        print('  file   : %s' % SQLITE)
        print('           exists: %s' % os.path.exists(SQLITE))
        print()
        print('  To point at Supabase:')
        print('    1. cp db/.env.example db/.env')
        print('    2. paste the Transaction pooler URI from the dashboard')
        print('       (Connect button in the project top bar)')
        print('    3. re-run this command')
        return 0

    warn = advise(u)
    if warn:
        print()
        for w in warn:
            print('  *** %s' % w)
        print()

    try:
        con, eng = connect()
        with con.cursor() as cur:
            cur.execute('select version()')
            v = cur.fetchone()[0]
            cur.execute("select to_regclass('public.observations')")
            tbl = cur.fetchone()[0]
            n = 0
            if tbl:
                cur.execute('select count(*) from observations')
                n = cur.fetchone()[0]
        con.close()
        print('  server : %s' % v.split(',')[0])
        print('  table  : %s' % (('observations, %d row(s)' % n) if tbl
                                 else 'NOT CREATED - run db/schema_pg.sql'))
    except Exception as e:
        print('  *** CANNOT CONNECT: %s' % e)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
