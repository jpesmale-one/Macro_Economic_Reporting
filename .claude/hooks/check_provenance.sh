#!/usr/bin/env bash
# PostToolUse hook (matcher: Edit|Write) - provenance reminder for landed data.
#
# CLAUDE.md section 6: every series under data/ carries its source, series
# ID, retrieval timestamp, and the release/vintage it represents. A bare
# CSV with no provenance is not usable evidence.
#
# This hook cannot know whether a sidecar is CORRECT - it checks only that
# one exists. Convention: <datafile>.provenance.md next to the data file.
# Exit 2 surfaces the gap to Claude loudly; it does not undo the write.

input="$(cat)"

fp="$(
  printf '%s' "$input" | python -c 'import sys,json
try:
    print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))
except Exception:
    pass' 2>/dev/null
)"

[ -n "$fp" ] || exit 0

# Normalize backslashes first, then test on the normalized form - a
# Windows-style path fails -f in bash and would skip the check entirely.
norm="$(printf '%s' "$fp" | tr '\\' '/')"

# A drive-letter path (c:/Users/...) cannot be stat'd by bash - it needs
# the Git Bash form (/c/Users/...). Without this, -f returns false on
# every Windows absolute path and the check silently passes.
case "$norm" in
  [A-Za-z]:/*)
    drive="$(printf '%s' "${norm%%:*}" | tr 'A-Z' 'a-z')"
    norm="/${drive}${norm#*:}"
    ;;
esac

[ -f "$norm" ] || exit 0

# Only police data files under data/; docs and reports pass untouched.
case "$norm" in
  */data/*|data/*) ;;
  *) exit 0 ;;
esac

case "$norm" in
  *.csv|*.tsv|*.json|*.parquet|*.xlsx) ;;
  *) exit 0 ;;
esac

if [ ! -f "${norm}.provenance.md" ]; then
  {
    echo "PROVENANCE MISSING for $norm"
    echo "CLAUDE.md section 6 requires a sidecar: ${norm}.provenance.md"
    echo "It must record source, series ID, retrieval timestamp, and the"
    echo "release/vintage this file represents. Without it the file is not"
    echo "usable evidence and no figure derived from it may be published."
  } >&2
  exit 2
fi

exit 0
