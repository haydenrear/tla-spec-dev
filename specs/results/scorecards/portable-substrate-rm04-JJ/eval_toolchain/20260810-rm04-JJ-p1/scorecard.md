# Scorecard — eval_toolchain, artifact `JJ`, judge pass 1

`run_id`: `20260810-rm04-JJ-p1` · scorecard_version 4 · rubric `references/eval_scorecard.md` digest `sha256:497c16ca85adeb4a` · served `sha256:a213a36770ccab09`

**You are scoring artifact `JJ`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

Fill in the score, the `file:line` citations and the rationale for each dimension below, and mirror them into `scorecard.json` beside this file. **The anchors are reproduced here so the bar for a score sits in the same file as the score.**

## The mechanical block

`mechanical.json` beside this file holds kill counts, complexity figures, case counts, determinism and runtime. How to read it against your judgement is one of the numbered scoring rules below.

## The rubric you are scoring against

**This is the whole rubric, and it is reproduced here so the bar for a score sits in the same file as the score.** Do NOT go and read `references/eval_scorecard.md`. That file also carries reading rules and prior results about these same dimensions, and a judge who reads those is being handed conclusions about the instrument they are the instrument for.

### The scoring rules

1. **Score artifacts, never claims.** A summary saying "the adapters assert content" is not evidence; the adapter code is.
2. **Every score ≥ 2 cites `file:line`.** A score with no citation is capped at 1, mechanically, by the schema check.
3. **A score at the top of its scale additionally names something the artifact refuses to claim.** The top of every scale requires a stated limit. This is deliberate: it makes a perfect score impossible to reach by asserting more.
4. **Prose quality is never an input.** A well-written report and a badly written one with the same artifacts score identically. Say so in the rationale if the writing tempted you.
5. **Two judges, independently, blind to each other.** Any dimension where they differ by more than 1 is recorded as `contested` and adjudicated by a third pass that must cite new evidence, not re-read the same lines.
6. **Blind to arm.** Where an eval has arms (with-prompt vs without), judges do not learn which artifact came from which until after scoring.
7. **The mechanical block is recorded, never scored.** Kill counts, complexity figures, case counts, determinism, runtime. It sits beside the judgement so a reader can see when the two disagree — and a disagreement is a finding.
8. **Say what you ran.** *(New in version 2.)* Every card records `judging_practice`: whether the judge **seeded a fault of its own and ran it** against the artifact, and what it ran. Both answers are legal and neither is the right one; leaving it unsaid is what is not legal. From version 4 no anchor is gated on it and it is still required, because what a judge did is a variable in what a judge reports and a variable nothing records is a variable nobody can subtract.
9. **A judge is served the card, never the rubric file.** *(New in version 3.)* The scaffolded `scorecard.md` carries the rubric a judge needs. This file carries reading rules and prior results about these dimensions as well, and a judge who reads it is handed conclusions about the instrument they are the instrument for. Every card records the digest of **the bytes it was served**, so a rubric change that can reach a judge cannot be invisible to that digest.
10. **Answer every recorded note.** *(New in version 4.)* N-D1, N-D4 and N-D5 take no score and are required on every filled card. An empty note is not a legal card; *"I could not tell, and here is what I looked at"* is.

**Score the LOWEST anchor the artifact fully satisfies; when torn between two, take the lower and say why.**

### Judging practice — REQUIRED, and it is a field on the card

**Did you seed a fault of your own and run it against this artifact, or did you score the evidence packet?** Both are legal. Neither is the right answer. What is not legal is leaving it unsaid.

Fill `judging_practice` in `scorecard.json`: `executed_own_faults` true or false, and `what_was_run` listing what you actually ran.

**No anchor is gated on your answer.** The anchor that was is a recorded note now. Say what you ran because it is the variable that moves scores, not because a rung depends on it.

### D2 — complexity

*Is the design as simple as its behavior requires, and no simpler?*

Diff the two trees yourself and decide whether one fact is stored twice — kept in agreement by hand across several write sites, and read in one place. Where a measured complexity descriptor exists you may read it, and on its own it decides nothing; where none exists that is not a gap in the evidence.

- **0** — Complexity is unmeasured, or measured and ignored.
- **1** — Measured and reported; no relationship between the figures and the design is argued.
- **2** — The design's complexity is proportional to its behavior; no god-state, no variable written from everywhere.
- **3** — 2, **and** a simplification was made and its effect measured — the before and after figures are both recorded.

> **A drop in a complexity number is not evidence on its own.** MF-020: a metric can improve because an edge was deleted. A D2 of 3 requires the judge to say *what got simpler and how the behavior survived it*.

### D3 — modularity

*Is it ports and adapters in fact — domain independent of I/O, adapters swappable?*

- **0** — No boundary is discernible; state is written from everywhere.
- **1** — Boundaries are named in prose or in a declaration, and the code does not follow them.
- **2** — The code follows the declared boundaries. Cross-boundary calls go through something identifiable as a port.
- **3** — The domain does not import its I/O. An adapter could be replaced without touching the domain, and the judge names the specific swap.
- **4** — 3, **and** a driven port is exercised by a real adapter *and* a fake, with the same cases passing against both.

> **Import topology is not modularity.** Round 2 proved a codebase can pass every import check with its coupling entirely intact. A D3 of 3 or more requires evidence about what *calls* what at runtime, not what imports what.

## The recorded notes — REQUIRED, and they take no score

**Answer each in your own words and cite `file:line` as you would for a score.** There is no 0–4 here and there is no anchor ladder: these questions were scored for three versions and the numbers were measured not to mean the same thing twice. *"I could not tell, and here is what I looked at"* is a correct answer; an empty note is not.

### N-D1 — bug detection

What did the cases catch, and what class did they demonstrably miss? Name the fault you seeded if you seeded one.

### N-D4 — behavior preservation

Which behaviors of the baseline did you enumerate, and is each shown still to hold? If there is no baseline, say so — that is the answer, not a gap in the note.

### N-D5 — honesty

Does the artifact refuse rather than falsely certify, and does it name what it cannot see? Point at the refusal, or at its absence.

### Judging practice — your answer

**Executed own faults:** _true_

**What was run:**

- `git rev-parse HEAD` → `dd71b11a0282a662f60d7bca0c34671ba9e12235`.
- Diffed the two trees by hand: BEFORE is one module (`run_gap_mutants.py`, 633 lines) plus `gap_mutants.toml`; AFTER (declared scope) is `price_removal.py`, `altered_score_probe.py`, `residual_faults.toml`. The before tree's runner is **absent from the after scope and from the repository** (`find . -name run_gap_mutants.py` returns only the before-tree copy and a vendored copy under `.skill-manager/`).
- **Seeded fault A / A' / A''** — built before/after tables in which the after column's verdict is `INERT`, then `NOT_RUN`, then `CONTROL_RED`, and called `price_removal.price()` on each. All three returned **`PRICED`** — "every kill it had is gone; the removal took the detection away" — from a run in which nothing executed.
- **Seeded fault B / C** — the same in the before direction: a before column that reports `INERT` yields `NO-KILL-TO-LOSE` from `price()` and from `entail()`, i.e. a column that did not run is indistinguishable from a fault nothing ever caught.
- **Seeded fault D** — omitted `--head` (it is optional, `price_removal.py:460`) with a lost kill whose node no longer exists. Reported `DETECTOR-WEAKENED`, which is the class `render_audit` headlines as "the class no survivorship test can see".
- **Seeded fault E** — called `altered_score_probe.problems()` against a tree where `score_tools.py` cannot be executed. `check` exited 2 having printed a traceback and no `INVALID` line; `problems()` returned the empty set at both ends, so the subtraction reports no new problem and the probe's verdict rule yields **`UNCAUGHT`**.
- **Refusal check** — `entail()` with one killing detector surviving by name returned `UNDECIDED`, and with every killer deleted returned `ENTAILED-SURVIVES`. The refusal the module's docstring claims is real and executes.
- Read `examples/validation/removal_census/removals.toml` and `removal_census.py`, and `examples/validation/scorecards/score_tools.py`, only far enough to check whether the artifact re-types facts those files own.
- All seeded faults were run as in-process calls against the artifact's own functions with synthetic dicts. **No repository file was edited.** I did not run `price_removal.py audit` and did not run `altered_score_probe.py` end to end — see Disclosures.

## Your scores

### D2 — complexity

**Score:** 1

**Citations** (`file:line` — the bar is in the scoring rules above):

- `examples/validation/gap_mutants/price_removal.py:346` — `RECORD`, a hand-typed Python literal holding, per removal, the landing sha and the before/after table paths.
- `examples/validation/gap_mutants/price_removal.py:362` — `"head": "HEAD"` for `dead-port-binding-report-detector`.
- `examples/validation/removal_census/removals.toml:423` — `head = "bfd04af"` for that same removal. **The two stores disagree today.**
- `examples/validation/gap_mutants/price_removal.py:371` — `audit()` opens that manifest and reads `deletes_detectors` and `gap_mutants` out of it in the same loop that uses the re-typed `head`.
- `examples/validation/removal_census/removals.toml:36` — `gap_mutant_before_table`, the same before-table path `RECORD` re-types at `price_removal.py:350` and `:356`.
- `examples/validation/gap_mutants/price_removal.py:399` — `_agrees` re-types `removal_census`'s verdict strings as literals, in the one function whose job is to compare against that module.
- `examples/validation/gap_mutants/price_removal.py:116` — `UNDECIDABLE = ("INERT", "CONTROL_RED", "NOT_RUN")`, a third copy of a vocabulary the baseline owned as constants at `specs/results/scorecards/portable-substrate/GOAL-dimensions-replicate/RM-04/blind/artifact_JJ_before/run_gap_mutants.py:98`.
- `examples/validation/gap_mutants/residual_faults.toml:51` — `pytest-full`, `instrument-registry`, `registry-enumeration` re-declared, with the same `nodes` / `argv` / `executed_if_stdout_contains`, that `.../artifact_JJ_before/gap_mutants.toml:39` already declares.

**Refuses to claim** (required and non-null for a score of 3): n/a — not a 3.

**Rationale:**

Complexity over this scope is measured and reported (the card's descriptor, both trees). The artifact itself argues no relationship between any figure and its design — it never mentions its own size, and there is no before/after complexity claim anywhere in the three files. That is anchor 1 exactly.

It does not clear anchor 2, on the question the dimension's read-first instruction puts first: **one fact is stored twice, kept in agreement by hand, and the two copies are already out of agreement.** The sha at which a removal landed lives in `removals.toml` (`head = "bfd04af"`, `:423`) and again in `price_removal.py`'s `RECORD` (`"head": "HEAD"`, `:362`). `audit()` reads three fields out of the manifest and re-types the fourth (`:371`, `:379-380`), and when the join key misses it `continue`s silently (`:375-376`). The same shape repeats twice more: the classifier's verdict vocabulary is re-typed as literals in `_agrees` (`:399`) and the kill/undecidable vocabulary is re-typed at `:116` and `:152`, and `residual_faults.toml:51` re-declares three detectors the baseline catalogue already declared. None of this is god-state — `module_state` and `instance_state` are 0 in both trees — but "no god-state" is one clause of anchor 2 and the duplication clause is the one this dimension asks me to decide.

Anchor 3 is out of reach regardless: **no simplification was made in this scope.** The scope grew — 1 module and 633 lines became 2 modules and 706 lines — and the module the before tree *was* is gone from the after tree while `residual_faults.toml` is still written in its schema. The mechanical figures that fell (`effectful_calls` 37→28, `branch_points` 76→72) fell because a 633-line runner left the scope, not because anything got simpler. That is MF-020 in its literal form and I refused to read those figures as evidence.

I was torn between 1 and 2 and took the lower, as the rule directs. The reason: the strongest single fact I have is two hand-maintained copies of one value that currently say different things, and `removals.toml:414-417` records that the `HEAD` spelling was a *known defect* that was pinned — so `RECORD` is carrying the value that was already corrected elsewhere.

Prose quality was not an input, and I want it on the record that it tempted me. These are among the most carefully reasoned docstrings I have read; `price_removal.py:46-73` argues the soundness asymmetry better than most papers would. Rule 4 says that scores identically to the same code with no comments, and I applied it.

### D3 — modularity

**Score:** 1

**Citations** (`file:line` — the bar is in the scoring rules above):

- `examples/validation/gap_mutants/price_removal.py:88` — the boundary, named in prose: "**Not a second implementation of `discriminate`.** `audit` imports the shipped `removal_census.discriminating` and swaps DATA only ... not a re-typed copy of it."
- `examples/validation/gap_mutants/price_removal.py:399` — and the code re-types that module's verdict vocabulary as string literals anyway, in `_agrees`.
- `examples/validation/gap_mutants/price_removal.py:167` — `_show` runs `git show` in a subprocess with `cwd=str(REPO_ROOT)`, a module-level constant computed at import (`:110`).
- `examples/validation/gap_mutants/price_removal.py:261` — `_loss_reason`, part of the verdict computation, calls `node_present` and therefore reaches straight through to that subprocess.
- `examples/validation/gap_mutants/price_removal.py:311` — `entail`, the module's headline "sound direction" function, does the same.
- `examples/validation/gap_mutants/price_removal.py:338` — `_shipped_discriminating` reaches its dependency by mutating `sys.path` globally and never restoring it.
- `examples/validation/gap_mutants/price_removal.py:377` — `audit` reads the filesystem directly, at paths hardcoded in `RECORD`.
- `examples/validation/gap_mutants/altered_score_probe.py:53` — `run()` shells out to the subject tree's CLI.
- `examples/validation/gap_mutants/altered_score_probe.py:60` — `problems()` calls `run()` directly; there is no seam between deciding and executing.

**Refuses to claim** (required and non-null for a score of 4): n/a — not a 4.

**Rationale:**

Above 0: a boundary *is* discernible. The modules are sectioned into reading (`kill_set`), deciding (`price`, `entail`), and rendering (`render_price`, `render_audit`), `fill()` in the probe is pure, and the measured `module_state` and `instance_state` are both 0 — nothing is written from everywhere because almost nothing is written at all.

Not 2, and this is the whole of it: **there is nothing identifiable as a port.** `declared_interfaces` is 0 in both trees, and more to the point the deciding layer calls I/O directly at runtime, not through anything substitutable. `entail(...)` → `node_present(...)` → `_show(...)` → `subprocess.run(["git","show",...], cwd=REPO_ROOT)`. The target of that call is a module-level constant; there is no parameter, no injection point, no alternative implementation, and no fake anywhere in the scope. The same holds for `audit`, which opens files at `REPO_ROOT`-relative literals, and for `altered_score_probe`, where the only way to substitute the subject is to hand it a different directory on disk. `_show` and `run` are single chokepoints for I/O, which is a seam; I rejected the reading that a private module-level helper is a port. I took the caveat seriously and looked at what *calls* what at runtime rather than what imports what — the runtime call chains above are the evidence, and they cross the boundary the file's own sections draw.

That lands it on anchor 1: boundaries are named — clearly, and in more than one place — and the code does not follow them. The sharpest instance is `:88` against `:399`: the file states as a design rule that it never re-types the shipped classifier, imports it correctly at `:341`, and then re-types that classifier's verdict vocabulary as bare literals in the one function that compares the two. If those strings change in `removal_census.py`, `_agrees` silently falls through to its final `return measured == "NOT-IN-TABLE"` and every row reads as a disagreement about table membership.

I considered 2 and rejected it rather than merely leaning away. The best case for 2 is that the import of `removal_census.discriminating` is a real, honored, declared boundary crossing — one implementation, imported, data swapped. That is genuinely good practice and it is the reason I looked hard. But it is one call, it is not a port (no interface, no substitutability, and the path to it is global state mutation at `:338`), and it does not offset a verdict layer that shells out to git.

Prose quality was not an input here either.

## Your recorded notes — no score

### N-D1 — bug detection

**Citations** (`file:line`):

- `examples/validation/gap_mutants/price_removal.py:142` — the limit, stated: "a price computed over them would be a price computed over a column that did not run."
- `examples/validation/gap_mutants/price_removal.py:223` — `undecidable_columns_after` is collected into the row.
- `examples/validation/gap_mutants/price_removal.py:241` — and the verdict branch never consults it.
- `examples/validation/gap_mutants/price_removal.py:246` — `PRICED`, the instrument's strongest claim, is what comes out.
- `examples/validation/gap_mutants/price_removal.py:316` — the refusal that does work: `UNDECIDED` rather than `ENTAILED-DIES`.
- `examples/validation/gap_mutants/altered_score_probe.py:60` — `problems()` never consults `check`'s exit code.
- `examples/validation/gap_mutants/altered_score_probe.py:161` — and the verdict is `"CAUGHT" if new else "UNCAUGHT"` over that set.

**Note:**

There are no test cases in this scope; the artifact's "cases" are its own verdict rules, so I seeded faults against those rules directly (faults A–E and the refusal check, listed under judging practice).

**What the rules do catch, demonstrably.** A mutant id absent from the before-table becomes `NOT-IN-TABLE` and drives a non-zero exit (`price_removal.py:213`, `:501`, `:510`, `:517`) — a real refusal with teeth. A killing node that survives the cut by name yields `UNDECIDED` and never `ENTAILED-DIES`; I ran both directions and got `UNDECIDED` with one surviving killer and `ENTAILED-SURVIVES` with none. A node deleted at a named head is separated from a node whose body changed (`:261-263`), which is the distinction the module was written to draw, and it holds.

**The class it demonstrably misses: a verdict emitted over a column that did not run.** Fault A: a before-table where `pytest-full` killed the mutant, an after-table where the only column reports `INERT`, and `price()` returns `PRICED` — "every kill it had is gone; the removal took the detection away." `NOT_RUN` and `CONTROL_RED` give the same answer. The undecidable columns are recorded on the row and rendered as a trailing line (`:419-420`), but the verdict a reader quotes is computed as if they were survivals. Fault B is the mirror image: a before column that never ran gives `NO-KILL-TO-LOSE`, so "the detector was inert" and "nothing ever caught this" are the same cell. This is not a class the artifact failed to anticipate — `kill_set`'s own docstring at `:142` names it, and `:114-116` names it again as the `FI-06` failure, "a green that nothing executed behind". It is stated and not enforced.

The sibling module has the same hole through a different door. Fault E: `problems()` scrapes `INVALID` lines out of stdout+stderr and ignores the return code, so a `check` that dies produces the empty set at both ends of the subtraction and the probe prints `UNCAUGHT` — "nothing in this tree reports a dimension score altered after the card was written." I ran this and got exit code 2, a traceback, and `UNCAUGHT`. The probe's one guard (`:130-134`, exit 2 when `scaffold` refuses, explicitly so "a broken setup cannot read as UNCAUGHT") covers the scaffold step and not the step that does the measuring.

One smaller miss: `--head` is optional (`:460`), and without it every lost kill on a surviving detector is labelled `DETECTOR-WEAKENED` (fault D), which is precisely the count `render_audit:446-449` headlines as "the class no survivorship test can see". Omitting one optional flag inflates the rarest and most rhetorically loaded number in the report.

### N-D4 — behavior preservation

**Citations** (`file:line`):

- `specs/results/scorecards/portable-substrate/GOAL-dimensions-replicate/RM-04/blind/artifact_JJ_before/run_gap_mutants.py:294` — the baseline's rule: `if observed["executed"] == 0: return INERT`.
- `.../artifact_JJ_before/run_gap_mutants.py:56` — and its stated reason: "A `SURVIVES` with nothing executed is not a survival."
- `.../artifact_JJ_before/run_gap_mutants.py:126` — `sweep_pycache`, the `FI-01-DF-01` guard.
- `.../artifact_JJ_before/run_gap_mutants.py:284` — `new_failures`, baseline subtraction.
- `.../artifact_JJ_before/run_gap_mutants.py:131` — `MutantNotApplied`, the refusal that makes an unapplied mutant loud.
- `examples/validation/gap_mutants/altered_score_probe.py:154` — the subtraction, re-implemented as a set difference.
- `examples/validation/gap_mutants/residual_faults.toml:34` — "It exits non-zero for one reason: a declared fault could not be APPLIED", in a TOML file.
- `examples/validation/gap_mutants/residual_faults.toml:155` — `must_die_on`, which nothing in the declared scope reads.

**Note:**

There is a baseline and I enumerated eight behaviors of it. The dominant fact is structural: **the baseline's only executable module is not in the after scope.** `run_gap_mutants.py` is absent from `examples/validation/gap_mutants/` and from the repository (only the before-tree copy and a vendored `.skill-manager/` copy exist). What survives into the scope is its *data schema* — `residual_faults.toml` is a catalogue in exactly that runner's format — with no executor beside it.

1. **Subprocess isolation against a freshly staged tree** (`before:117-128`): not present. Nothing in scope stages a tree; `altered_score_probe` runs against a `--tree` the caller supplies.
2. **`__pycache__` swept between applications** (`before:126`, `:174`): not preserved. `altered_score_probe` never sweeps, so a stale `.pyc` in the supplied tree is the `FI-01-DF-01` shape the baseline existed to close. (This scope currently ships a `price_removal.cpython-313.pyc`, untracked.)
3. **Nothing executed ⇒ `INERT`, never a survival** (`before:56-60`, `:294-295`): **not preserved, and I demonstrated it twice** — `price()` returns `PRICED` over `INERT`/`NOT_RUN`/`CONTROL_RED` after-columns (fault A), and `problems()` ignores the exit code entirely (fault E).
4. **Verdicts read out of JSON, never from an exit code** (`before:50-54`, `:316-325`): preserved in `price_removal`, which reads tables. Regressed in `altered_score_probe`, which reads neither an exit code nor an executable count.
5. **Baseline subtraction** (`before:284-289`): preserved by re-implementation (`altered_score_probe.py:154`), not by reuse — the probe's docstring at `:34` says so explicitly.
6. **Refusal when a declared mutant did not apply** (`before:131-176`, `:589`): not preserved. `residual_faults.toml:34` still asserts an exit code for itself; a TOML file has none, and the runner that enforced it is out of scope.
7. **`[[not_seedable]]` reported, never dropped** (`before:579-583`, `:619-623`): preserved as *data* (`residual_faults.toml:172-193`, a well-argued row) with nothing in scope to read or render it.
8. **Positive-control accounting, R2** (`before:551-568`): `residual_faults.toml:141-165` still declares a control with `must_die_on`, and nothing in the declared scope consults it.

So: of the two baseline behaviors I could check by execution, neither holds. The rest are absent from the scope rather than broken in it — which is a different finding and I am not scoring it as breakage, but a catalogue whose runner is gone is not a preserved behavior either.

### N-D5 — honesty

**Citations** (`file:line`):

- `examples/validation/gap_mutants/price_removal.py:65` — the `ENTAILED-SURVIVES` bound, stated up front and unprompted.
- `examples/validation/gap_mutants/price_removal.py:73` — "Both are printed; the instrument has no mode that emits only one."
- `examples/validation/gap_mutants/price_removal.py:180` — `node_present` "says nothing about whether the node still asserts what it asserted".
- `examples/validation/gap_mutants/price_removal.py:316` — the refusal, in code: `UNDECIDED`, not `ENTAILED-DIES`.
- `examples/validation/gap_mutants/altered_score_probe.py:130` — `REFUSED ... Nothing here may be read as UNCAUGHT`, return 2.
- `examples/validation/gap_mutants/altered_score_probe.py:92` — a confound the first version walked into, recorded rather than quietly fixed.
- `examples/validation/gap_mutants/price_removal.py:142` — the limit it states about columns that did not run.
- `examples/validation/gap_mutants/price_removal.py:246` — and the `PRICED` it emits over exactly those columns.

**Note:**

It refuses, and some of the refusals are real code rather than prose. I verified two by execution: `entail` returns `UNDECIDED` where the shipped classifier would say `NON-DISCRIMINATING`, and it returns `ENTAILED-SURVIVES` only when every killing pair is deleted. That is the artifact declining to make the claim its own predecessor made, and it is the strongest thing on this card. `altered_score_probe.py:130` is a second real refusal: a tree whose `scaffold` fails returns 2 rather than reporting `UNCAUGHT`. It names what it cannot see in several places without being asked — the bound on `ENTAILED-SURVIVES` (`:65-73`), `node_present`'s blindness to a weakened body (`:180`), "Not a gate" in both modules, and `residual_faults.toml:172-193`, which reports a fault it decided not to seed *and* corrects the record about why the earlier exclusion was wrong.

Against that: the sharpest dishonesty available to an instrument is to name a limit and then breach it, and this one does, twice. `kill_set` states that a price computed over an undecidable column "would be a price computed over a column that did not run" (`:142`), and `price()` computes exactly that and calls it `PRICED` (`:246`) — I ran it. `altered_score_probe` states that a broken setup must not read as `UNCAUGHT` (`:130-134`) and then guards only the scaffold, so a broken `check` reads as `UNCAUGHT` — I ran that too. The honesty is genuine at the level of what the authors knew and wrote down; it is not carried into the verdict rules, which is where a reader will actually take the number from.

One more, minor: `residual_faults.toml:34` claims an exit code for a file that cannot exit, inherited verbatim from a runner that is no longer in the scope. That is stale rather than deceptive, but it is a claim the artifact cannot back.

## Verdict

Gate every verdict on an executable count before quoting any number from this scope — `price()` returns `PRICED` and `altered_score_probe` returns `UNCAUGHT` over columns that provably did not run, both being limits the files themselves state and do not enforce — and delete `price_removal.py`'s hand-typed `RECORD`, which already disagrees with `removals.toml` about where one of its three removals landed.

## Disclosures

**Leak, disclosed.** A recursive `grep` for consumers of `residual_faults.toml` printed three matching content lines from `specs/.history/portable-substrate-epic/ticket-000-RM-01/results/RESULT.md` (a `--catalogue` invocation and two prose mentions) before I could stop it, and the same command listed directory names under `specs/results/scorecards/`, including one belonging to a different arm label. I did not open any of those files and I read no further than the grep lines themselves. From them I learned that files in my scope were authored under tickets of a `portable-substrate` epic and that at least one other arm label exists. **I did not learn what `JJ` maps to and I made no attempt to.** Every finding on this card rests on the declared scope, the before tree, and `removal_census.py` / `removals.toml` / `score_tools.py`, all of which are outside the blinded set. I did not read `references/eval_scorecard.md`, any other scorecard, `subjects.toml`, `INSTRUMENT-LOG.toml`, any `RESULT.md` proper, or the git log.

**Changes to the tree.** Importing `price_removal` and `altered_score_probe` for my seeded faults wrote two `.cpython-314.pyc` files into `examples/validation/gap_mutants/__pycache__/`. I deleted both. The pre-existing untracked `price_removal.cpython-313.pyc` was there before I arrived and I left it. No tracked file in the repository was edited other than this card and its JSON. I ran no test suite and no `git commit`.

**Rejected — the falling complexity figures.** `effectful_calls` 37→28 and `branch_points` 76→72 look like a simplification and are not evidence of one. Modules went 1→2 and lines 633→706; the figures fell because a 633-line runner left the scope, not because a design got simpler. This is MF-020 in its literal form and it is the single reason D2 is not a 3.

**Rejected — `_show` and `run` as ports.** Both are single chokepoints for I/O, which makes them seams. No interface is declared (`declared_interfaces: 0`), no caller can substitute them, and no fake exists in the scope. I would have had to redefine "port" as "the only function that touches subprocess" to reach D3 = 2, and I declined.

**Rejected — the import of `removal_census.discriminating` as proof of modularity.** It is one honored crossing, reached by mutating `sys.path` and never restoring it (`:338`), in a module whose verdict layer shells out to git. Import topology is not modularity; I looked at the runtime call chains instead.

**Rejected on safety grounds — two things I chose not to run.** `price_removal.py audit` would have read before/after tables under `specs/results/scorecards/` that the blinding rules put out of bounds, so I built my own tables instead. `altered_score_probe.py --tree .` scaffolds a card into `specs/results/scorecards/rm01-probe/`, which would have edited the repository; I exercised its `run`/`problems`/`fill` functions directly instead. Both decisions cost me an end-to-end confirmation and I would rather say so than quote a number I did not produce.

**Could not tell.** Whether the absence of `run_gap_mutants.py` from the scope is a deliberate priced cut or an orphaning. `removals.toml:461-465` carries a region naming that exact path, which suggests the former, but nothing inside my declared scope records the cut, its price, or a replacement executor for `residual_faults.toml`. I scored what is in the scope and flagged the gap rather than guessing which it was.
