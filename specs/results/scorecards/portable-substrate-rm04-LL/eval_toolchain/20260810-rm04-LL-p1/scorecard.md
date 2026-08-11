# Scorecard — eval_toolchain, artifact `LL`, judge pass 1

`run_id`: `20260810-rm04-LL-p1` · scorecard_version 4 · rubric `references/eval_scorecard.md` digest `sha256:497c16ca85adeb4a` · served `sha256:a213a36770ccab09`

**You are scoring artifact `LL`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

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

**Executed own faults:** true

**What was run:**

- `python3 scripts/code_complexity.py scripts --json` at HEAD. The `totals_code_only` block it printed reproduces `mechanical.json` exactly — 31 code modules, 24880/20005 lines, 762 callables, 3110 branch points, 486 effectful calls in 28 modules, 0 declared interfaces, 31 instance-state names, 2 module-state names, `parsed_fraction` 1.0. The mechanical block is therefore reproducible at this commit, and I still did not score it (rule 7).
- **A fault I seeded and ran.** The declared boundary for this tree says every case-generation/docs write lands under a `specs/` tree (`spec_tree`, `target: "**/specs/**"`). I pointed a shipped CLI at a path outside every `specs/` tree: `python3 scripts/generate_docs.py examples/effect_providers/atomic_publisher/specs/program_model/spec_manifest.yaml --out <scratchpad>/outside/nowhere/docs.md`. It wrote the file and **exited 0** with no refusal. That is an undeclared `filesystem.write` performed by the artifact on demand.
- The control for that fault: in a throwaway interpreter I called `spec_paths.resolve_evidence_out()` and `spec_paths.resolve_spec_tree_out()` on the *same* out-of-tree path. Both raised (`--out must write under a 'results/' directory`, `case generation must write under a 'specs/' directory`). The guard works; it is simply not on the call path the fault took.
- `git diff --stat 82936ef..HEAD -- scripts/` and `git log dbf355c..HEAD -- scripts/` — both empty. `scripts/` is byte-identical across the whole of this epic, which is how I established there is no before tree.
- `python3 scripts/generate_docs.py specs/program_model/spec_manifest.yaml --out ...` — the toolchain's own program model fails the artifact's own `validate_manifest` with four missing-key errors.
- Nothing in the repository was modified. Every byte I wrote went to the session scratchpad.

## Your scores

### D2 — complexity

**Score:** 1

**Citations** (`file:line` — the bar is in the scoring rules above):

- `scripts/code_complexity.py:17` — "It **reports**. It refuses nothing, it proposes nothing, and nothing in this toolchain gates on its output."
- `scripts/code_complexity.py:31` — "this module emits **no verdict, no comparison, and no direction**: there is no ``--compare`` mode and no delta output".
- `scripts/effect_conformance.py:1649` — `ensure_import_roots(roots)`, returns the roots it added, does not prepend the skill root.
- `scripts/run_generated_case_adapters.py:1215` — a second `ensure_import_roots(import_roots)`, returns `None`, prepends `Path(__file__).resolve().parents[1]`. Same name, same fact, two write sites, already out of agreement.
- `scripts/generate_cases_from_tlc_dump.py:1077` and `scripts/generate_python.py:851` — `def write(path, content)` byte-identical in two modules.
- `scripts/effect_conformance.py:1764` — `from run_generated_case_adapters import ...` inside a function body, deferred because the module-scope import at `scripts/run_generated_case_adapters.py:42` runs the other way.
- `scripts/case_modules.py:763` and `scripts/generate_cases_from_tlc_dump.py:33` — the second mutual pair, same deferral trick.
- `scripts/testgraph_channels.py:144` and `scripts/run_generated_case_adapters.py:51` — the third.

**Refuses to claim** (required and non-null for a score of 3): _n/a — not a top-of-scale score._

**Rationale:**

Complexity of this tree **is** measured, by an instrument the tree itself ships, and I reproduced the mechanical figures from it at HEAD. So this is not 0: nothing is unmeasured and nothing is ignored. What the artifact does not do is argue a relationship between the figures and the design — and that is deliberate and stated: `code_complexity.py:17` and `:31` remove every verdict, comparison and direction from the instrument on purpose, citing MF-020. Anchor 1 describes that state almost word for word.

I considered 2 and rejected it. The read-first instruction asks whether one fact is stored twice, kept in agreement by hand across several write sites. It is. The policy for what goes on `sys.path` before adapters are imported is written twice, in two modules that import each other, and **the two copies do not agree**: `effect_conformance.py:1649` inserts only the roots it was given and returns them; `run_generated_case_adapters.py:1215` silently prepends the skill root as well and returns nothing. Both are named `ensure_import_roots`; either can be the one in force depending on which entry point ran. `def write(path, content)` is likewise duplicated byte-for-byte across two 1000+ line modules. And three module pairs import each other in a cycle that is survivable only because one side hides its import inside a function body (`effect_conformance.py:1764`, `case_modules.py:763`, `testgraph_channels.py:144`). A design whose acyclicity depends on deferring imports to call time is not one whose complexity I can call proportional to its behavior.

Torn between 1 and 2 in one respect, and I took the lower: `module_state` is 2 across 20005 code lines, so the second half of anchor 2 — "no god-state, no variable written from everywhere" — is genuinely met. It is the first half, proportionality, that fails, and anchor 2 requires both.

3 is unreachable here for a reason that is a fact about the scope and not a judgement about the tree: **there is no before tree.** `git diff --stat 82936ef..HEAD -- scripts/` is empty and no commit on this branch touches `scripts/`, so no simplification was made in this window and `mechanical.json` carries an `after` block and no `before` block. I am saying that plainly rather than inventing a baseline.

Prose quality tempted me on this dimension and I am recording it: `code_complexity.py`'s docstring is the most disciplined statement of the MF-020 problem I have read anywhere in this tree. It is prose. It moved no score.

### D3 — modularity

**Score:** 1

**Citations** (`file:line` — the bar is in the scoring rules above):

- `specs/program_model/spec_manifest.yaml:134` — `effects:` declaring component `TlaSpecDevCliPort` with named ports; `:137` `ports:`; `spec_tree` → `target: "**/specs/**"`, `evidence_report` → `target: "**/results/**"`. This is the declaration `scripts/` is judged against; its comments cite `scripts/*.py` by name.
- `scripts/effect_conformance.py:14` — the declared rule: "A port is the only way anything leaves a component."
- `scripts/spec_paths.py:69` — the artifact's own claim that the constraint is "constrained HERE, in one place, so the declaration in spec_manifest.yaml is true of every caller rather than true of the documented one."
- `scripts/generate_docs.py:20` and `scripts/generate_docs.py:31` — `--out` taken as a bare `Path` and written with `args.out.write_text(...)`, no guard. **This is the call path my seeded fault took: it wrote outside every `specs/` tree at exit 0.**
- `scripts/run_kill_test.py:102` and `:225` — `--out` documented in its own help text as "ticket evidence", written via `report.write(args.out, catalog)` with no `resolve_evidence_out`.
- `scripts/tla_spec_dev.py:593` — `--out` documented as "ticket results/ evidence", unguarded.
- `scripts/effect_conformance_report.py:170`, `scripts/infer_action_params.py:872`, `scripts/generate_python.py:992`, `scripts/export_testgraph_cases.py:174` — four more unguarded `--out` write sites.
- `scripts/analyze_complexity.py:2361` and `scripts/generate_cases_from_tlc_dump.py:3280` — the only two sites that do route through the guards. Two of ten.
- `scripts/effect_conformance.py:780` and `:815` — the boundary is not injected, it is monkeypatched process-wide: `builtins.open`, `os`, `shutil`, `Path`, `subprocess`, `socket` are rebound for the duration of the run.
- `scripts/effect_conformance.py:632` and `:745` — `RecordingTransport`, the one fake adapter in the tree, and `EffectSandbox.transport()` which mints it. Nothing under `scripts/` ever calls `.transport(...)`; the only caller in the repository is `tests/test_effect_conformance.py:159`, and there is no real transport for it to stand in for.
- `scripts/code_complexity.py:89` — the artifact's own instrument defines `declared_interfaces` as "the code analogue of a declared port"; measured over `scripts/` it is **0**, which I reproduced.

**Refuses to claim** (required and non-null for a score of 4): _n/a — not a top-of-scale score._

**Rationale:**

Not 0. A boundary is discernible and in places well kept: thin argparse shims delegate to named library functions (`scripts/start_ticket.py:26`, `scripts/generate_docs.py:31` calling a pure `render_docs`), `spec_paths.py` is a genuine shared chokepoint, and `module_state` of 2 is the opposite of "state written from everywhere."

Not 2, and I am not torn. Anchor 2 needs the code to *follow* the declared boundaries and cross-boundary calls to go through something identifiable as a port. Both fail, and the second fails structurally: there is no port object anywhere in `scripts/`. Effects are performed by direct `Path.write_text` / `open` / `subprocess.run` calls in whatever module owns the logic, and the "port" exists only as a glob that a sandbox matches against observations *after the fact* by rebinding `builtins.open` process-wide (`effect_conformance.py:780`). A boundary you enforce by monkeypatching the standard library underneath your own code is the inverse of an injected seam — the artifact's own descriptor agrees, scoring `declared_interfaces: 0` over this tree using a definition that explicitly calls that figure the code analogue of a port (`code_complexity.py:89`).

The first failure is the one I ran rather than read, because the caveat asks for evidence about what *calls* what at runtime. `spec_paths.py:69` claims the port targets are enforced "in one place, so the declaration in spec_manifest.yaml is true of every caller." It is true of two callers. Ten `--out` flags exist under `scripts/`; two route through `resolve_evidence_out` / `resolve_spec_tree_out`, eight do not, and two of the eight describe their own output as ticket evidence in their help text — exactly the `evidence_report` surface. I seeded the corresponding fault and it landed: `generate_docs.py` wrote a spec-tree artifact to an arbitrary filesystem location and exited 0, while the guard refused the identical path when I called it directly. Declared boundary, code does not follow it: anchor 1.

Nothing above depends on import topology, per the caveat — the decisive evidence is a process I ran and a file that appeared where no declared port covers it. For completeness on the upper rungs: 4 is independently unreachable because the tree's only fake (`RecordingTransport`) has no real counterpart and no caller inside the artifact, so no driven port is exercised by both a real adapter and a fake.

Prose tempted me hard on this dimension and I am recording it under rule 4. The docstrings in `spec_paths.py` and `effect_conformance.py` reason about ports better than most codebases implement them, and reading them alone would have earned a 3. The score is what executing the code showed.

## Your recorded notes — no score

### N-D1 — bug detection

**Citations** (`file:line`):

- `specs/program_model/spec_manifest.yaml:80` — `case_codegen: generation_status: planned`.
- `specs/program_model/spec_manifest.yaml:153` — the manifest's own words: "`case_codegen.generation_status` is still `planned`, which is the single largest coverage limit in this repository."
- `specs/program_model/spec_manifest.yaml:104-106` — `state_fields: []`, `actions: []`, `ports: {}`, the empty generated-content placeholders.
- `scripts/generate_docs.py:31` — where my seeded fault landed.
- `scripts/extract_spec_manifest.py:324` — `validate_manifest` requiring `state`, `commands`, `results`.

**Note:**

The cases caught nothing about this artifact, because over this artifact there are none. The toolchain's own program model sits at `generation_status: planned`, its generated-case index stanzas are empty placeholders, and the manifest says so itself in the plainest terms available — it calls this its single largest coverage limit. So the honest answer to "what did the cases catch" is: no generated case has ever executed against `scripts/`, and every claim about this tree's effect behavior rests on hand-written adapter tests outside the declared scope plus reading.

I seeded one fault, and I name it: **an undeclared `filesystem.write` outside every declared port target.** I ran a shipped CLI (`generate_docs.py`) with `--out` pointing outside any `specs/` tree. It wrote the file and exited 0. The class this demonstrably misses is therefore *port-target violations at unguarded call sites* — the declared `spec_tree`/`evidence_report` targets are enforced at two of ten `--out` sites, and nothing that exists today would have caught the other eight. This is the exact defect class `spec_paths.py:59-76` records as already found twice (RC-01 G-2/G-3, then RC-02 N-2 on a new command path); finding it a third time on a third command path is the finding, and it is a direct consequence of the empty case corpus above.

A second, smaller thing fell out while I was setting the fault up: `extract_spec_manifest.validate_manifest` demands keys (`state`, `commands`, `results`) that the repository's *own* `specs/program_model/spec_manifest.yaml` does not carry, so `generate_docs.py` refuses the toolchain's own model with four errors. Legacy-schema manifests elsewhere in the tree still pass, so this is drift between the validator and the current manifest schema rather than dead code — but no case notices it.

### N-D4 — behavior preservation

**Citations** (`file:line`):

- `mechanical.json` — the `complexity_of_produced_code` block carries an `after` object and no `before` object.
- Repository history: `git diff --stat 82936ef..HEAD -- scripts/` is empty; `git log dbf355c..HEAD -- scripts/` is empty; the last commit to touch `scripts/` is `946b1ee`, the previous epic's merge.

**Note:**

**There is no baseline, and that is the answer.** `scripts/` is byte-identical between the commit `mechanical.json` records (`82936ef`) and HEAD (`dd71b11`), and no commit on this branch modifies it at all. There is no "before" tree to enumerate behaviors from and no "after" to check them against, which is also why D2 cannot reach 3: the anchor requires before *and* after figures and only one exists.

What I can report instead, because it is a fact and not a substitute for the missing baseline: the one behavior I did enumerate and exercise — "an `--out` path is constrained to the target its declared port covers" — holds at the two sites that call the guards and does not hold at the eight that do not. That is a statement about the current tree, not about preservation across a change, and I am not going to dress it up as one.

### N-D5 — honesty

**Citations** (`file:line`):

- `scripts/effect_conformance.py:23` — "**The sandbox observes the in-process CPython runtime and nothing else**"; `:28` names JVM/JBang/uv/child-process adapters as invisible to it; `:35` — a refused target "is a **failure**, not a clean report."
- `scripts/effect_conformance.py:673`, `:678`, `:682` — `record_unobservable`, `record_skip`, `record_out_of_process`, each documented as having no matching `clear`/`waive`.
- `scripts/code_complexity.py:42` — "**It exits 0 on every input.** A file it cannot parse costs *completeness*, which is reported as a fact with the path and the reason, and never causes a refusal."
- `scripts/code_complexity.py:37` — no threshold, no gate, no nonzero exit path.
- `scripts/code_complexity.py:98` — the `effectful_calls` figure names the three ways a sink escapes it ("a sink reached through an alias, a local variable, or ``getattr`` is not seen"), and `:728` prints "This figure UNDERCOUNTS by construction" in the report's own definitions block.
- `scripts/spec_paths.py:69` — the overclaim.
- `specs/program_model/spec_manifest.yaml:153` — the self-named largest coverage limit.

**Note:**

Mostly yes, and unusually so. This tree refuses in the right direction repeatedly: an unobservable target produces a *failure* verdict rather than a clean one, and the three recorders that hold refusals, skips and out-of-process evidence are each built with no method to withdraw an entry — the absence of a `waive` is documented as the design, which is the strongest form of this I have seen here. The complexity instrument names its own undercount and its own incompleteness as reported facts rather than swallowing them. And the manifest volunteers, in its own comments, that its case codegen has never run and that this is its biggest blind spot. Those are refusals, not certifications, and I am pointing at them.

The absence is one sentence, and it matters because it is the sentence a reader would most reasonably rely on. `spec_paths.py:69` states that the port target is "constrained HERE, in one place, so the declaration in spec_manifest.yaml is true of every caller rather than true of the documented one." It is true of the documented one. Eight of ten `--out` write sites never reach that code, and I demonstrated one of them writing outside the declared target at exit 0. Everywhere else this artifact names what it cannot see; here it names a property it does not have, in the file whose whole purpose is that property.

## Verdict

Route the eight unguarded `--out` write sites (`generate_docs.py:20`, `run_kill_test.py:102`, `tla_spec_dev.py:593`, `effect_conformance_report.py:170`, `infer_action_params.py:872`, `generate_python.py:992`, `export_testgraph_cases.py:174`) through `spec_paths.resolve_evidence_out`/`resolve_spec_tree_out`, or declare ports that cover them, and correct the "true of every caller" claim at `spec_paths.py:69` — a fault I seeded wrote outside every declared port target at exit 0, which is why this scores D3 1 and not 2.

## Disclosures

- **No arm leak.** `LL` remains opaque to me; I did not read `references/eval_scorecard.md`, any other `scorecard.json`/`scorecard.md`, any `UNBLINDING*`, `SEALED-BEFORE-DISPATCH.md`, `INSTRUMENT-LOG.toml`, `RESULT.md`, `examples/validation/scorecards/subjects.toml`, or anything under `specs/results/scorecards/` outside this directory. I did run `git log --oneline`, which showed commit subjects for this epic's tickets including one reading "seal the predictions and declare three toolchain subjects before dispatch". That tells me three toolchain subjects exist; it does not tell me which one `LL` is, and I did not open the sealed file. Recording it because it is a thing I saw.
- **Path names seen via `git status --porcelain`, run to confirm I had changed nothing else.** Its output listed, as already-modified-before-I-started, `specs/results/scorecards/INSTRUMENT-LOG.toml` and card directories `portable-substrate-rm04-GG` (p1, p2), `portable-substrate-rm04-JJ` (p1, p2) and my own `-LL` p1 and p2. So I know there are three blinded subjects in this round, two judge passes each, and that a second pass exists on my own artifact. **I opened none of them** — not the sibling cards, not the p2 card on `LL`, not `INSTRUMENT-LOG.toml`. Path names are not contents and none of this maps `LL` to an arm, but I saw them and rule 6 is worth more than my convenience, so it is recorded. Separately, `git log --oneline` showed this epic's ticket subjects, one of which reads "seal the predictions and declare three toolchain subjects before dispatch" — consistent with the above and equally uninformative about which subject `LL` is. I did not open the sealed file.
- **Commit mismatch, and why it does not bind.** `mechanical.json` records `82936ef3bce29e3551cd83dd3673bf60f4eec162`; `git rev-parse HEAD` is `dd71b11a0282a662f60d7bca0c34671ba9e12235`, which is what I put in `commit` as instructed. `scripts/` is byte-identical between the two, and re-running `scripts/code_complexity.py scripts --json` at HEAD reproduced the recorded `totals_code_only` block figure for figure. The mechanical block binds at HEAD.
- **Out-of-scope file read, deliberately.** I read `specs/program_model/spec_manifest.yaml`, which is outside the declared scope of `scripts/`. I read it because it is where the boundaries `scripts/` is judged against are *declared*, and D3's anchor 1 cannot be evaluated without seeing the declaration. Every score citation is anchored in `scripts/` except the declaration lines themselves, which are labelled as such.
- **What I ran that touched a filesystem.** The seeded fault and both probes wrote only into the session scratchpad (`.../scratchpad/outside/nowhere/`). No file in the repository was created, modified or deleted; no test suite was run; no commit was made. `git status` was clean before and after.
- **Rejected — `declared_interfaces: 0` as a score.** The mechanical block's zero would on its own have supported a lower D3, and I refused to use it that way: rule 7 forbids scoring it, and the D3 caveat specifically warns that interface/import topology is not modularity. It appears in my citations only as corroboration *after* the runtime probe, never as the reason.
- **Rejected — `module_state: 2` as a route to D2 2.** The absence of god-state is real and I said so, but anchor 2 is a conjunction and the proportionality half fails. Taking the lower.
- **Rejected — D2 0.** Tempting on the grounds that nothing in the toolchain measures `scripts/` for itself: `complexity_ledger.py` records TLA+ model figures, and `code_complexity.py` is imported by no other module in the tree (it appears in zero of the 58 internal import edges). But the instrument exists, it is the one that produced the recorded figures, and its output is reproducible — that is measured and reported, not unmeasured or ignored.
- **Rejected — scoring the docstrings.** Twice, on both dimensions, the prose in this tree argued for a score the code did not. `code_complexity.py`'s MF-020 discussion and `spec_paths.py`'s port reasoning are better than the artifact they describe. Rule 4 applies and I have said so in both rationales.
- **Rejected — inventing a before tree.** I could have diffed `specs/current` against `specs/program_model`, or reached back to `946b1ee`, to manufacture a baseline for D2 3 and N-D4. Neither is a before-tree for the declared scope. I said there is none.
