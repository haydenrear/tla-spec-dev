# Purge Shipped Degeneracy From The Toolchain

Status: Open

The 2026-07-18 degeneracy audit purged the escape hatches from the doctrine and
from every unstarted ticket. Three of them had **already shipped into code** and
must be removed there too, or the doctrine and the tool disagree — the failure
mode already tracked as #33.

Governing rules: `references/architecture_tractability.md`, "No Degenerate
Escapes".

## 1. `--allow-over-budget` (MF-011)

`scripts/generate_cases_from_tlc_dump.py` accepts an override that proceeds
past a failed complexity gate. Eight references across the scripts.

An override flag on a complexity gate converts a hard limit into a suggestion,
and it is reached for under exactly the budget pressure that makes exceeding
the limit dangerous. MF-022's own ticket already observed that routine use
"defeats the gate entirely."

**Remove it.** Over the gate, the architecture changes. A program that
genuinely needs more room raises its budget in `spec_manifest.yaml` with a
recorded rationale — visible and reviewable in a way a command-line flag is
not.

## 2. Budgets fallback with a warning (MF-012)

`scripts/budgets.py::load_budgets` falls back to documented defaults with a
warning when the `budgets:` block is missing.

This defeats the point of MF-012, whose entire purpose was that budgets are
**negotiated per program** with a recorded rationale per adjusted value. A
warning-and-proceed means a program can run its whole life on generic defaults
that nobody ever agreed to, and the warning scrolls past.

**Make a missing `budgets:` block fail**, naming the scaffold command that
creates one. Note this is a real behavior change for any existing consumer;
enumerate what breaks and fix it in the same ticket rather than softening the
rule.

## 3. Self-disabling justification check (MF-011)

`scripts/analyze_complexity.py:1084` prints *"no justification table in the
manifest — dead-weight analysis skipped."*

A check that silently disables itself when its input is absent is the purest
form of the pattern: the model with **no** justification table is precisely the
one most likely to carry unjustified variables, and it is the one case the
analysis declines to examine. Absence of the table is itself the finding.

**Make the missing table a failure**, not a skip. Per the CEGAR section of
`architecture_tractability.md`, every element of the model earns its place by
killing a mutant, carrying an effect, or supporting an invariant — an
unjustifiable model is the thing being looked for.

## Acceptance criteria

- No code path accepts `--allow-over-budget` or any equivalent override of a
  complexity or case-cap gate. Grep proves zero references outside historical
  snapshots.
- A missing `budgets:` block fails with a message naming the scaffold command
  that creates one. Every existing consumer that relied on the fallback is
  identified and fixed, not exempted.
- A missing justification table fails rather than skipping the analysis.
- **Regression tests prove each escape stays gone** — a test per escape,
  asserting the failure. These are the guard against reintroduction, which is
  the real risk, since each of these was added in good faith the first time.
- `references/modular_fuzzing.md` and `references/architecture_tractability.md`
  match the shipped behavior exactly.
- Any *new* escape introduced while doing this — a flag, a default, a
  conditional — is itself a failure of this ticket.

## Note

Expect this to break things. Three gates that were effectively optional become
mandatory, and this repository's own model does not currently pass all of them
(the `C1 touched by 11 actions` finding is live and is resolved at the root by
MF-023). **Do not fix a newly-failing gate by weakening it.** Report what now
fails; that report is a legitimate and valuable output of this ticket.
