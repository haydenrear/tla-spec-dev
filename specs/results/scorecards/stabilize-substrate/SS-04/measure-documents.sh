#!/usr/bin/env bash
# SS-04. `scope` over the named, committed list of work-directing documents,
# with the TOOL under test given as an argument so the base and the tip are
# measured by the same script over the same list in the same tree.
#
#   measure-documents.sh <path-to-score_tools.py> [<label>]
#
# Every figure it prints is a joint property of the artifact AND THE TREE, so
# the tree is printed once at the top and the tool's own provenance block
# carries it on every run underneath.
#
# `PYTHON` is honoured and defaults to `python3` DELIBERATELY, because on this
# machine `python3` is 3.9.6 under `/bin/bash` and 3.14.6 under the interactive
# shell, and `score_tools.py` needs `tomllib` (3.11+). An instrument that quietly
# measures under a different interpreter than the one the reader assumes is the
# same shape of error as one that quietly measures in a different tree.
set -u
tool="${1:?usage: measure-documents.sh <score_tools.py> [label]}"
label="${2:-unlabelled}"
PYTHON="${PYTHON:-python3}"
here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/../../../../.." && pwd)"
list="$here/work-directing-documents.txt"

echo "# scope over the work-directing documents -- $label"
echo "# tool   $tool"
echo "# python $($PYTHON -V 2>&1) ($(command -v $PYTHON))"
echo "# root   $root"
echo "# HEAD   $(git -C "$root" rev-parse HEAD 2>/dev/null || echo 'not a checkout')"
echo "# dirty  $([ -n "$(git -C "$root" status --porcelain 2>/dev/null)" ] && echo YES || echo no)"
echo "# list   $list"
echo

total=0
while IFS= read -r doc; do
  case "$doc" in ''|'#'*) continue ;; esac
  out="$(cd "$root" && "$PYTHON" "$tool" scope --path "$doc" 2>&1)"
  code=$?
  line="$(printf '%s\n' "$out" | grep -E '^[0-9]+ counted figure\(s\)' | tail -1)"
  [ -n "$line" ] || line="$(printf '%s\n' "$out" | head -1)"
  n="$(printf '%s' "$line" | grep -oE '^[0-9]+' || true)"
  [ -n "$n" ] && total=$((total + n))
  printf '%-78s exit %s  %s\n' "$doc" "$code" "$line"
done < "$list"
echo
echo "TOTAL counted figures over the list: $total"
