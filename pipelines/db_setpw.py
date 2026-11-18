# -*- coding: utf-8 -*-
"""Set or rotate the database password in db/.env, safely.

*** WHY THIS EXISTS. A Supabase password routinely contains characters that
are reserved in a URL - the first one here held $ % & * and psycopg refused
the string with "invalid percent-encoded token", because '%$&' is a
malformed escape. Hand-editing db/.env re-creates that trap every time.

This prompts for the password WITHOUT ECHOING IT, percent-encodes it, and
rewrites only the password portion of the existing URL. The password is
never printed, never passed as a command-line argument (which would land in
shell history), and never appears in any log line.

    python pipelines/db_setpw.py          # prompt, then verify the connection
"""
import io
import os
import re
import sys
import getpass
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ENV = os.path.join(REPO, 'db/.env')


def main():
    if not os.path.exists(ENV):
        print('db/.env does not exist. Create it first:')
        print('  cp db/.env.example db/.env')
        return 1

    s = io.open(ENV, encoding='utf-8').read()
    m = re.search(r'^(SUPABASE_DB_URL=)(\S+)\s*$', s, re.M)
    if not m:
        print('no SUPABASE_DB_URL line in db/.env')
        return 1
    url = m.group(2)

    head, _sep, tail = url.rpartition('@')
    scheme, _, cred = head.partition('//')
    user, _, _old = cred.partition(':')
    if not tail or not user:
        print('could not parse the URL - expected '
              'postgresql://user:password@host:port/db')
        return 1

    print('Updating the password for:')
    print('  user : %s' % user)
    print('  host : %s' % tail)
    print()
    print('Paste the NEW database password (it will not be shown).')
    pwd = getpass.getpass('  password: ')
    if not pwd:
        print('nothing entered - no change made')
        return 1
    again = getpass.getpass('  again   : ')
    if pwd != again:
        print('*** the two entries differ - no change made')
        return 1

    enc = urllib.parse.quote(pwd, safe='')
    reserved = sorted(set(c for c in pwd if c in set('%@/:?#[]!$&\'()*+,;= ')))
    newurl = '%s//%s:%s@%s' % (scheme, user, enc, tail)

    io.open(ENV, 'w', encoding='utf-8', newline='').write(
        s.replace(url, newurl))

    print()
    print('  length            : %d' % len(pwd))
    print('  reserved chars    : %s' % (''.join(reserved) or '(none)'))
    print('  percent-encoded   : %s' % ('yes' if enc != pwd else 'not needed'))
    print('  db/.env updated.')
    print()

    sys.path.insert(0, HERE)
    for mod in ('db_connect',):
        if mod in sys.modules:
            del sys.modules[mod]
    import db_connect as dbc
    # db_connect caches nothing, but os.environ may hold the OLD value from
    # a previous load - _load_env does not overwrite existing vars.
    os.environ.pop('SUPABASE_DB_URL', None)
    return dbc.main()


if __name__ == '__main__':
    sys.exit(main())
