# Tree at six tickets merged — f45a245

Raw output: `pytest-6-merged-f45a245.txt` (sealed, THIS FILE IS SECOND).
Command: `uv run --with pytest --with pyyaml -m pytest tests -q`, exit 1, 35:01.
Measured by the epic owner in the epic worktree, working tree clean at f45a245.

## Five buckets, and they sum

| bucket     | baseline 436c78c | here f45a245 | movement |
|------------|------------------|--------------|----------|
| failed     | 17               | 7            | −10      |
| passed     | 1483             | 1598         | +115     |
| skipped    | 4                | 0            | −4       |
| xfailed    | 0                | 1            | +1       |
| **collection** | **1504**     | **1606**     | **+102** |

`7 + 1598 + 0 + 1 = 1606`. The baseline sums too: `17 + 1483 + 4 + 0 = 1504`.

**THE COLLECTION ROSE BY 102.** That is the denominator moving, and it moves
because six tickets each added demonstrated cases. A red count falling from 17
to 7 against a denominator that grew by 102 is NOT the same claim as 17 → 7
against a fixed denominator, and this table exists so the two cannot be
confused.

## Independent corroboration

SS-06's review round measured `7 / 1598 / 0 / 1 / 1606` at `5c06db8` — the same
five buckets, a different commit, a different measurer, a different worktree.
Two independent runs agree. That is the strongest statement available about the
tree here, and it is stronger than either run alone.

## THE SEVEN REDS, BY NODE ID

This list is sealed WITH the total. Recording a total without its decomposition
is what produced the "13 uncollected nodes" error (the true figure was 12; the
13th was the owner's own ledger relocation, and it was inferred rather than
measured because the sealed evidence was four lines with no node list). That
failure mode is closed HERE, by construction, not by remembering.

1. `tests/test_architecture_tags.py::test_the_same_tag_control_holds`
2. `tests/test_instrument_demonstrations.py::test_every_declared_path_exists`
3. `tests/test_instrument_demonstrations.py::test_every_fast_demonstration_reproduces`
4. `tests/test_source_citations.py::test_every_line_citation_resolves_to_the_line_it_cites[specs/current/spec_manifest.yaml]`
5. `tests/test_source_citations.py::test_every_line_citation_resolves_to_the_line_it_cites[specs/desired_program_model/spec_manifest.yaml]`
6. `tests/test_source_citations.py::test_every_line_citation_resolves_to_the_line_it_cites[specs/program_model/spec_manifest.yaml]`
7. `tests/test_ticket_retirement.py::test_repository_canonical_delivered_plan_has_matching_close_receipts`

## Attribution

**Red 7 IS CAUSED BY THIS EPIC BEING OPEN AND BY NOTHING ELSE.** Its assertion
message is `ticket SS-05 is not closed: status=planned` plus one more of the
same shape. It is a receipt check over the canonical delivered plan, and two
tickets are still `planned` by design. IT WILL GO GREEN WHEN SS-05 AND SS-08
CLOSE, AND NOT BECAUSE ANYONE REPAIRED ANYTHING. Predicting that it clears is a
prediction; it is recorded here as one so it can be checked at the tip rather
than asserted afterwards as a mechanism. (The epic has already made this exact
error once — "four skips unskip when SS-01 repoints" was false, and repointing
alone made them four reds.)

Reds 4–6 are three parametrisations of ONE citation check over three manifests,
not three independent defects; the visible instance is an anchor that moved from
`scripts/tla_spec_dev.py:353` to `:369`. Counting them as three is correct for
the bucket total and misleading as a count of causes.

Reds 1–3 are carried, pre-existing at the baseline, and unattributed to any
ticket in this epic. NOT INVESTIGATED HERE — saying so is the point; an
unattributed red silently rolled into a headline is the failure this goal
exists to prevent.

## What this measurement does NOT establish

It is one run at one commit with SS-05 outstanding. It does not establish that
the tree converges — two agreeing runs at nearby commits are consistency, not
convergence. The tip figure after SS-05 merges is the one GOAL-tree-stabilizes
is judged against, and it is expected to move in BOTH directions: collection up
by every demonstration SS-05 adds, reds possibly up as repaired instruments
begin refusing inputs they used to pass.
