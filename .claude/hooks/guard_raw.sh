#!/usr/bin/env bash
# PreToolUse hook (matcher: Edit|Write) - raw-data immutability wall.
#
# CLAUDE.md section 6: files under data/raw/ are IMMUTABLE once landed.
# A correction lands as a NEW vintage alongside the old one; it never
# overwrites, because the old value is the evidence for what was knowable
# at the time. Same reasoning as TRTM's MT5 boundary: the rules explain
# the wall, this hook IS the wall.
#
# Creating a NEW file under data/raw/ is allowed (that is landing a
# vintage). Modifying one that already exists is denied.
# Exit 2 = deny, and stderr is surfaced to Claude.

input="$(cat)"

fp="$(
  printf '%s' "$input" | python -c 'import sys,json
try:
    print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))
except Exception:
    pass' 2>/dev/null
)"

[ -n "$fp" ] || exit 0

# Normalize backslashes so Windows-style paths match too. Everything
# downstream - the pattern match AND the existence test - uses $norm;
# testing -f on the raw backslash form silently fails on Windows paths
# and lets an overwrite through.
norm="$(printf '%s' "$fp" | tr '\\' '/')"

# A drive-letter path (c:/Users/...) cannot be stat'd by bash - it needs
# the Git Bash form (/c/Users/...). Without this, -f returns false on
# every Windows absolute path and the wall silently opens.
case "$norm" in
  [A-Za-z]:/*)
    drive="$(printf '%s' "${norm%%:*}" | tr 'A-Z' 'a-z')"
    norm="/${drive}${norm#*:}"
    ;;
esac

case "$norm" in
  */data/raw/*|data/raw/*) ;;
  *) exit 0 ;;
esac

# New vintage = new file = allowed. Existing file = immutable.
if [ -f "$norm" ]; then
  {
    echo "DENIED: $norm is under data/raw/ and already exists."
    echo "Raw data is immutable (CLAUDE.md section 6). Corrections and"
    echo "revisions land as a NEW vintage file alongside this one, and the"
    echo "change is recorded in STATE.md. Never overwrite a landed vintage."
  } >&2
  exit 2
fi

exit 0
