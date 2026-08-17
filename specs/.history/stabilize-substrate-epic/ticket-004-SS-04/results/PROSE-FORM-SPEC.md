# SS-04 — the prose counted-figure recogniser, specified BEFORE it was written

**Sealed 2026-08-17T03:25:10Z, in a commit, before one line of the recogniser
existed and before its demonstration corpus was opened.** This document is the
`MF-020` defence and it is worth nothing if it is written afterwards, so it is
committed on its own, ahead of the implementation, and the commit that carries it
carries no regex.

`MF-020`: **never add an axis, test, rung or case fitted to a known answer.** The
issue that assigns this ticket names five counted figures — `0 of 9`, `1 of 38`,
`four rounds' claims`, `8 failed, 1490 passed`, `seven epics, zero bugs` — **and
I know all five answers.** A recogniser tuned until those five parse is fitted,
and fails clause (d) of `GOAL-counted-figures-reach-the-record` *even if it
works*. So the shape is fixed here, from what an English counted figure is,
before anything is measured.

---

## 1. What is being recognised

**A counted figure is a numerator, a denominator, and the population they count.**

    <n> of <m> <counted noun>

`scope` today recognises exactly one sentence form, `D<n> = <v> … <n> of <m>`
(`CLAIM_FORM_A` / `CLAIM_FORM_B`), in which the count is bound to a dimension and
a value. **The dimension is what makes that form re-derivable and it is also what
makes it rare.** The record is written in ordinary prose, and this is the form
that has actually hurt this project.

FORM P recognises the count **without the dimension binder**.

## 2. Recognition rules — fixed here

1. **The numerator and the denominator are each** an Arabic numeral (thousands
   separators permitted: `1,490`) **or** an English number word from a closed
   list: `zero one two three four five six seven eight nine ten eleven twelve
   thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty`. The two
   sides are independent — `3 of the four` is one figure.
   **Decimals are not numbers here** (`1.5 of 3` is not a count).
2. **The separator is `of`**, optionally preceded by `out` (`8 out of 9`), and
   optionally followed by **one** determiner from a closed list: `the a an its
   their our my these those all every` .
3. **The counted noun is up to three word tokens** following the denominator, in
   the manner of the existing `_NOUN`, and it may be empty.
4. **Matching is line-based**, exactly as `find_claims` already is. A figure
   broken over a line break is a known miss and is declared as one; a
   paragraph-wide window is what lets a figure bind to a scope three sentences
   away, which is the defect `scope` exists to refuse.
5. **A figure the dimension-bound forms already matched on the same line with the
   same `(n, m)` is NOT re-reported.** `FORM_A` / `FORM_B` keep their verdicts
   untouched. **No figure that has a verdict today may get a different one.**

## 3. Verdict rules — fixed here, and deliberately weak

**UNREACHABLE IS THE DEFAULT, AND FORM P CAN NEVER RETURN `REFUTED`.**

That is not a caution, it is a property of the code, and it is pinned by a test.
A false REFUTED is worse than an UNREACHABLE; clause (b) says an uncertain
sentence is UNREACHABLE, never HOLDS and never REFUTED. A prose figure carries no
predicate this repository can evaluate — `0 of 9 content bugs` names no card, no
dimension and no value — so **there is nothing to refute and nothing to
confirm.**

Two verdicts are available to FORM P, and only two:

| verdict | when |
|---|---|
| `UNREACHABLE` | the default, always, unless the row below fires |
| `COUNT-MOVED` | the counted noun is a **card noun** (`card`, `cards`, `scorecard(s)`, `judge-score(s)`, `judges`, `rows`) with **no narrowing qualifier**, and the card population on disk differs from `<m>` |

`HOLDS` is **not available to FORM P**. A card-noun figure whose denominator
re-derives exactly is still `UNREACHABLE`, with the reason
`numerator has no predicate`: the denominator was checked and the numerator was
not, and reporting that as HOLDS would be the instrument claiming to have checked
a claim it only half-read. **That asymmetry is the whole point.**

`REFUTED` is **not available to FORM P**, at any denominator, for any noun.

### Named UNREACHABLE reasons — the taxonomy is the product

Every UNREACHABLE row names which of these it is, because *"it reaches few and
here is exactly which forms it misses"* is the honest outcome and the reason has
to be enumerable to say that:

- `non-card noun` — the counted noun is something this cannot read (findings,
  tickets, epics, bugs, goals, tests, …)
- `unresolved qualifier` — a card noun narrowed by a word the corpus does not
  define (`23 of 27 blind-judged v4 cards`)
- `no counted noun` — nothing follows the denominator
- `numerator has no predicate` — card noun, denominator re-derives, numerator
  names no property
- `arm-scoped` / `anaphoric scope` — as the dimension-bound forms already report

## 4. What this is NOT

**NOT A GATE.** Nothing refuses, nothing blocks a close, and **no exit code
changes for any input that resolves.** `cmd_scope` exits 1 iff some figure is
REFUTED; FORM P cannot produce one; therefore every existing invocation over an
existing tree exits exactly what it exited before. **That is pinned by a test,
not asserted here.**

The one exit-code change is the opposite of a gate and `SS-02` requires it: an
input that is **absent, unreadable or empty** is answered UNDECIDED (exit 2)
instead of PASS (exit 0). See §6.

## 5. Declared misses — written down BEFORE measuring

These are refused by the specification above, not discovered afterwards. **Three
of the five figures the issue names are in this list**, which is the strongest
evidence available that the shape was not drawn around them:

- **A counted figure with no `<n> of <m>` in it.** `8 failed, 1490 passed` is two
  counts and a denominator that must be added; `seven epics, zero bugs` is a
  numerator and a population that is named nowhere; `four rounds' claims` has no
  denominator at all. **The ticket names these as figures that hurt this project
  and FORM P cannot see any of them.** Extending to them means inventing the
  denominator, which is exactly what `prediction-seal` declined to do one layer
  down.
- Spelled-out numbers above twenty (`thirty-one of forty`).
- A figure split across a line break.
- A percentage or a ratio (`19%`, `2/2 -> 4`) — `2/2` is this repository's
  movement notation between two judge passes and is not a count.
- `N in M` and `N out of every M`.
- Any figure inside `specs/.history/**`, which `sweep_paths` excludes by a
  decision this ticket does not touch.

## 6. The recogniser's own absent input (`SS-02`'s extension, three states)

`scope --scorecards /nonexistent` today prints `0 REFUTED, 82 UNREACHABLE` and
**exits 0**. That is one of `CA-10`'s 48 and it is in this ticket's conflict key.
All three states are answered UNDECIDED, never PASS, and each says which one it
hit:

| state | input | required answer |
|---|---|---|
| absent | `--path` naming a file that is not in the tree; `--scorecards` naming a directory that is not there | UNDECIDED, exit 2, naming the path |
| unreadable | a document whose bytes do not decode as text; a scorecard root that is a file, or holds no card | UNDECIDED, exit 2, naming the path |
| empty | a document of zero bytes, or one that is all whitespace | UNDECIDED, exit 2, and **explicitly not "no figures, all clear"** |

**An empty document must not read as "no counted figures".** `absent` and
`checked, none found` are different claims and this project has been caught
conflating them; a zero-byte charter and a charter with no figures in it are also
different claims, and the second is a real answer while the first is not.

## 7. Two findings routed to this ticket, both consumed rather than cited

**`SS-01-DF-03` — a `scope` verdict is a joint property of the file AND THE TREE
IT IS SWEPT IN**, and `scope`'s output records nothing about which root it swept.
The same ledger bytes score `21/18/3` under a bare `--root` and `20/17/3` inside
the repository. **Fix: every `scope` run prints its provenance** — the resolved
root, whether it is a git checkout and at which HEAD, the resolved scorecard
root, the card population, and the number of files swept — in both `text` and
`json`. A `--root` figure is then distinguishable from a repository one **on the
face of the output**.

**`SS-00-DF-04` — never publish a joint claim from two separate marginals.** The
owner read `by file 20/3` and `by verdict 20 REFUTED / 3 UNREACHABLE`, assumed
they cross-tabulated, and published *"20 REFUTED, all from the ledger"*. They do
not: it is 17+3 / 3. **Fix: `scope` computes and prints the `file × verdict`
cross-tabulation**, so the joint distribution is on the page and nobody has to
multiply two marginals to get it. Where a joint distribution is not computed the
honest output is the two marginals **stated as marginals**; here it can be
computed, so it is.

## 8. How MF-020 is defended, concretely

1. **This document is committed before the recogniser exists.** The commit that
   carries it carries no `FORM_P` regex.
2. **The demonstration corpus is not opened until the recogniser is frozen.** At
   sealing time I have read `STABILIZE-SUBSTRATE-EPIC.md` (mandatory — the
   assignment requires it before touching git, so it is **contaminated and
   disclosed as such**) and the `scope` section of `score_tools.py`. I have
   **not** read `CUT-THE-APPARATUS-EPIC.md`, `NEXT-EPIC.md`, any goal baseline,
   any price table, or any sealed `RESULT.md`. Those are the held-out set.
3. **Recall is measured against a mechanical superset, not against my
   expectations.** Every occurrence of a bare `\d+\s*(?:of|/)\s*\d+`-ish shape in
   the named documents is enumerated by a *separate, deliberately over-broad*
   scanner, and every occurrence FORM P did not take is classified by hand into a
   named category. That produces a numerator and a denominator for "what it
   misses" that do not depend on my knowing any answer.
4. **The five known figures are looked at LAST**, after the recogniser is frozen
   and measured, and whatever they do is reported as an observation. **If a
   change to the recogniser would make one of them parse, the change is not
   made.**

## 9. Prediction, sealed here, before any of it runs

Written now, so that agreeing with the result later costs nothing and disagreeing
with it is on the record. **If every prediction passes, that is an ALARM and is
reported as one.**

- **P1.** FORM P finds **more than 20 and fewer than 400** counted figures over
  the default sweep at this tree.
- **P2.** **Over 85%** of what it finds is UNREACHABLE with reason
  `non-card noun` — the record counts findings, tickets, instruments and goals,
  not cards.
- **P3.** FORM P produces **zero** REFUTED. (Guaranteed by construction; stated
  so the guarantee is checked rather than trusted.)
- **P4.** `STABILIZE-SUBSTRATE-EPIC.md` moves off **0** and reads **more than
  10** counted figures.
- **P5.** `CUT-THE-APPARATUS-EPIC.md` moves off **0**.
- **P6.** The whole-record REFUTED count is **unchanged** from the base figure I
  re-derive at `8dd0442`, and the process exit code of `scope` with no arguments
  is **unchanged**.
- **P7.** The over-broad recall scanner finds **at least 15%** more shapes than
  FORM P takes — i.e. the honest answer is that it misses a real fraction, not a
  rounding error.
- **P8.** At least **two** of the five figures the issue names do **not** parse.
