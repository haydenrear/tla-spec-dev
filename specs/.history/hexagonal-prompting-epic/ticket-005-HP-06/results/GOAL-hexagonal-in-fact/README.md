# GOAL-hexagonal-in-fact — the run record

**Statement.** Asking an agent for ports and adapters produces ports and adapters
in FACT — a domain that does not import its I/O, and an adapter that can be
swapped for a fake with the same cases passing against both.

**Metric.** Scorecard D3. Anchor 3 requires evidence about what *calls* what at
runtime, not what imports what; anchor 4 requires a driven port exercised by a
real adapter **and** a fake.

**Baseline** (`ab0dfee`, sealed): D3 = 1 / 1–2 / 3 / 1 / 0–1 across five
fixtures. **Only one reached 3 and nothing ever reached 4.**

**Target.** The prompt arm scores D3 ≥ 3 from both judges on the majority of
produced artifacts, with at least one 4.

## Measured

| artifact | judge pass 1 | judge pass 2 | contested? |
|---|---|---|---|
| **arm B** (the hexagonal ask) | **D3 = 4** | **D3 = 4** | no — exact agreement |
| **arm A** (the ordinary ask) | D3 = 2 | D3 = 2 | no — exact agreement |

Arm B produced one artifact; both judges scored it 4. **Majority of produced
artifacts at ≥ 3: 1 of 1. At least one 4: yes.**

## VERDICT: `met`

**This is the first D3 = 4 the project has ever recorded**, and the first time
any dimension has reached 4 outside D5.

## What the judges actually cited, because a 4 has to be earned twice

Both judges reached anchor 4 by **running the artifact's parity suite themselves**
rather than believing its notes. Both recorded it:

- the domain module imports only `dataclasses` and `typing` — no `pathlib`, no
  `os`, no handle, no path (`arms/arm_b/quota_ledger/domain.py:9-12`);
- the driven port is a `Protocol` the domain declares in its own vocabulary, with
  two methods (`arms/arm_b/quota_ledger/domain.py:15-28` — declared at `:15`, used at `:125` and `:144`);
- one composition point knows both halves and is the only thing that does
  (`arms/arm_b/quota_ledger/__init__.py:21-30`);
- an identical eight-case list runs through the real `FileJournal` and the
  in-memory fake, and **each case asserts a literal expected value rather than
  that the two agree** (`arms/arm_b/tests/test_journal_parity.py`).

That last clause matters more than the rest. HP-02's pilot found a hole in an
earlier draft of this very prompt: the arm it produced wrote
`scenario(fake) == scenario(real)`, two wirings of the same domain, so every
domain-logic fault moved both sides identically and the test could not fail for
any fault in the rules. One sentence was added to the ask afterwards and
deliberately **not** re-measured. **This round is that sentence's first
measurement, and the hole it was written to close is closed** — both judges
independently checked for exactly it.

Arm A stopped at 2 for a reason both judges named identically: `_LedgerFile` is a
real, respected runtime seam and every durable write goes through it, but the
domain constructs it inline (`arms/arm_a/quota_ledger.py:134`) and imports `os`
and `pathlib` in the same module, so **no judge could name a swap that leaves the
domain untouched** — which is precisely what anchor 3 requires. Both judges also
recorded that `FEATURE.md:119-120` explicitly makes this a free choice, so this
is the arm effect and not a defect in arm A.

## Three things that qualify this `met`

**1. It cannot be attributed to "hexagonal".** The two prompts differ by 105
unique lines to 16 — 6.6x unique content. A longer, more specific ask that
demanded any particular structure might have produced any particular structure.
Separating the two needs a third arm as long and as specific as arm B's asking
for something else, and this epic does not run one. Sealed confound 1.

**2. n = 1.** One feature, one artifact per arm. D3 = 4 is a fact about this
artifact, not a property of prompting.

**3. Blinding leaked on the other arm, not this one.** `arms/arm_a/test_quota_ledger.py:1`
says `"""Arm A's own tests`, which both artifact-Y judges could see; artifact X
carried no equivalent marker. See `../UNBLINDING.md` — the leaked arm scored
*higher* on D5 and lower on D3, and a judge rewarding a guessed treatment would
have produced the opposite on D5.

And one limit no sanitising can remove: arm B's `NOTES.md` describes the
structural ask it was given. A judge reading it learns this artifact was asked
for a structure. **Any future round claiming a blind judgement of an architecture
prompt owes the same disclosure.**

## What did NOT follow from the modularity

Recorded because it is the round's own answer to "does structure catch bugs":

* **Arm B's per-mutant kill verdicts are identical to arm A's** on all seven
  mutants seeded identically into both — 49 of 49 cells, across all seven
  instruments. A port did not catch one extra fault.
* **Arm B's own 41 tests appear nowhere in the kill table.** Both judges said so
  and both capped D1 at 3 partly for it: every fault the artifact is credited
  with catching was caught by the harness's generated corpora, not by anything
  the artifact wrote. The parity suite that earned the 4 has never been run
  against a mutant.

That is the honest shape of this result: **the prompt produced the structure it
asked for, and the structure did not, by itself, detect anything extra.**
