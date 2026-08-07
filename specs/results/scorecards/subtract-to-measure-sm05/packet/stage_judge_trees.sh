#!/bin/bash
# SM-05 -- stage the two ends of the toolchain removal for a blind judge.
#
# The subject of this arm is a REPOSITORY, so the ordinary "here is a directory,
# do not read the rest of the repo" blinding of prior rounds does not reach. The
# judge has to read scripts/, tests/ and examples/validation/ -- and every prior
# round's scorecards, the rubric file, the sealed predictions and the epic
# charters sit in the same tree.
#
# So the contaminating paths are REMOVED from the trees a judge is handed,
# rather than forbidden by a list the judge is trusted to honour. The manifest
# below is the whole redaction and it is committed beside the result, so the
# trees are reproducible from two SHAs plus this file.
set -euo pipefail

REPO="$1"; BEFORE_SHA="$2"; AFTER_SHA="$3"; DEST="$4"

redact() {
  local root="$1"
  # (a) the card itself, the sealed cards, the plan and the findings ledger
  rm -rf "$root/specs/.history"
  rm -rf "$root/specs/desired_program_model"
  rm -rf "$root/specs/results/scorecards"
  rm -rf "$root/specs/tickets"
  rm -f  "$root/references/eval_scorecard.md"
  rm -f  "$root"/examples/validation/PREDICTIONS*.md
  rm -f  "$root"/*EPIC*.md
  rm -f  "$root/NEXT-EPIC.md" "$root/EPIC-HANDOFF.md"
  # (b) THE CLASS NOTHING WAS WATCHING. Statements of how a DIMENSION HAS
  # SCORED, in files outside specs/results/scorecards/. The `one-home` check
  # added at SM-06 watches for statements OF the card -- a dimension, an anchor,
  # a scoring rule -- and deliberately exempts a citation of a score. These are
  # citations of scores, so they are exempt, so they were never counted, and
  # every one of them is a prior D-result sitting in the tree a judge reads.
  rm -f  "$root/specs/results/complexity_ledger.json"
  rm -f  "$root/specs/results/skill_feedback.md"
  rm -f  "$root"/specs/results/deferred_findings_*.yaml
  rm -f  "$root/references/architecture_advice.md"
  rm -f  "$root/references/hexagonal_prompting.md"
  rm -f  "$root/PORTS-AS-ADAPTERS-STARTER-PROMPT.md"
}
# NOT REDACTED, AND DISCLOSED TO EVERY JUDGE INSTEAD, because they are part of
# the subject and removing them would change the artifact being scored:
#   tests/test_card_has_one_home.py      -- carries "D2 = 2 on 27 of 27 cards"
#                                           twice, as fixture data for the test
#                                           that a score citation is NOT a
#                                           statement of the card.
#   tests/test_score_tools.py            -- carries checker messages naming
#                                           D1/D3/D4 scores.
#   examples/validation/ab/reference_ports/{README.md,journal_memory.py}
#                                        -- "the fake that earned arm B its
#                                           D3 = 4".

for pair in "before:$BEFORE_SHA" "after:$AFTER_SHA"; do
  name="${pair%%:*}"; sha="${pair##*:}"
  rm -rf "$DEST/$name"; mkdir -p "$DEST/$name"
  git -C "$REPO" archive "$sha" | tar -x -C "$DEST/$name"
  redact "$DEST/$name"
done
echo "staged before=$BEFORE_SHA after=$AFTER_SHA into $DEST"
