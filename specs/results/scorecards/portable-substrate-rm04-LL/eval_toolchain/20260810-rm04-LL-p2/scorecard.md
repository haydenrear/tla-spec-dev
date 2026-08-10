# Scorecard — eval_toolchain, artifact `LL`, judge pass 2

`run_id`: `20260810-rm04-LL-p2` · scorecard_version 4 · rubric `references/eval_scorecard.md` digest `sha256:497c16ca85adeb4a` · served `sha256:a213a36770ccab09`

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

**Executed own faults:** false

**What was run:**

- No fault of my own was seeded or run. I scored the evidence packet: full-file and grep reads over every `.py` file in `scripts/` (via `wc -l`, targeted `grep -n`, and full reads of `code_complexity.py`, `effect_conformance.py` (in full), `analyze_complexity.py` (structural sections), `extract_spec_manifest.py` (in full), `onboard_program_model.py` (the adapter/provider template region), `scaffold_spec.py` (the same region), `run_generated_case_adapters.py` (class/structure), `close_tickets.py`, `spec_evolution.py`, `complexity_ledger.py`, `kill_test.py`, `case_modules.py`, `tla_spec_dev.py`).
- Did not run `kill_test.py` / `run_kill_test.py` or any pytest suite against `scripts/` — the task explicitly says not to run the test suite, and `kill_test.py`/`run_kill_test.py` are that suite's own mutation runner.
- Did not modify any file in the working tree.

## Your scores

### D2 — complexity

**Score:** 2

**Citations** (`file:line` — the bar is in the scoring rules above):

- `scripts/extract_spec_manifest.py:273` (`parse_simple_yaml`) and `:285` (`load_manifest`) — one fact (manifest parsing) has one write site and is imported, not reimplemented, at `scripts/budgets.py:129`, `scripts/case_modules.py:43`, `scripts/effect_conformance_report.py:43`, `scripts/run_generated_case_adapters.py:49`, `scripts/generate_cases_from_tlc_dump.py:35`, `scripts/testgraph_channels.py:51`, `scripts/generate_python.py:16`, `scripts/generate_docs.py:13`.
- `scripts/close_tickets.py:45` (`SKILL_ROOT = Path(__file__).resolve().parents[1]`) vs `scripts/analyze_complexity.py:80` (`ROOT = Path(__file__).resolve().parents[1]`) — the one counter-example I found: the same fact (repo root) is rederived independently in two places instead of shared. Small and low-stakes, but it is duplication, so I weighed it against a higher score.
- `scripts/code_complexity.py:578-581` (`module_state = len(rebound)`, only names assigned more than once at module scope) and `scripts/effect_conformance.py:929-982` (`WorkingTreeObserver`, the busiest class in the largest file at 1845 lines, has 6 `self.` assignments) — instance state is thin and distributed; no god-object across 762 callables.

**Refuses to claim** (required and non-null for a score of 3): null (score is 2, not top of scale)

**Rationale:** The design's complexity tracks its behavior: one shared manifest-parsing fact with eight read sites and one write site, module-level mutable state reduced to 2 rebound names across the whole 20,005-line scope, and instance state that never concentrates into a god object even in the two largest files. That satisfies anchor 2. Anchor 3 needs a simplification with *both* before and after figures recorded — there is no before tree for this artifact (stated in the task, not invented by me), so 3 is not reachable regardless of the design's merits. I did not let the mechanical block's figures alone decide this — I read the actual write/read sites named above and judged them, per the rubric's instruction that a measured complexity descriptor "on its own... decides nothing."

### D3 — modularity

**Score:** 0

**Citations** (`file:line` — the bar is in the scoring rules above):

- `scripts/close_tickets.py:204`, `scripts/tla_spec_dev.py:408`, `scripts/kill_test.py:585`, `:588`, `:872`, `scripts/spec_evolution.py:99`, `:251`, `:277`, `scripts/complexity_ledger.py:550`, `:1244`, `scripts/case_modules.py:480`, `:823` — a sample of the 20 (of ~32) files in `scripts/` that call `write_text`/`subprocess.run`/`json.dump` directly, inline in ordinary logic, with no shared write gateway or injected port. State is written from everywhere, literally.
- `scripts/onboard_program_model.py:631` (`def adapters_py`) containing `class _InternalAdapter` at `:674` and `class _ExternalAdapter` at `:730`; `scripts/scaffold_spec.py:541` and `:578` (same pattern) — these are the only classes in the codebase that use the actual ports-and-adapters vocabulary (`_InternalAdapter`/`_ExternalAdapter`), and every one of them is Python source living inside a triple-quoted string returned by a template function that `scripts/` writes out to a *consumer* repository during scaffolding. They are never imported or called by `scripts/` itself.
- `scripts/code_complexity.py:213` (`INTERFACE_BASES = frozenset({"Protocol", "ABC", "ABCMeta"})`) and `scripts/generate_python.py:128-134` (which *emits* a `Protocol` class as text for a consumer) — the only other places `Protocol`/`ABC`/`abstractmethod` appear in the scope; none declares a boundary that `scripts/`'s own code is checked against. This matches the mechanical block's `declared_interfaces: 0` (recorded, not scored — I verified it independently by grep rather than trusting the number).

**Refuses to claim** (required and non-null for a score of 4): null (score is 0, not top of scale)

**Rationale:** `scripts/` is the tool that *enforces* ports-and-adapters discipline on other repositories (its `effect_conformance.py` and its generated `adapters.py`/`providers.py` templates are entirely about that). It does not practice that discipline on itself. Effects are performed directly, inline, throughout roughly two-thirds of its own modules, with no port, gateway, or declared interface standing between domain logic and I/O anywhere in the artifact's own runtime code. I looked specifically for a boundary named in prose for `scripts/`'s *own* architecture (as distinct from the boundary it prescribes to consumers) and found none — so anchor 1 ("named... and not followed") does not fit either; there is nothing named. Anchor 0 is the accurate, lowest-satisfied read: no boundary is discernible, and state is written from everywhere. Per the caveat, I did not stop at import topology — the citations above are about what calls `write_text`/`subprocess`/`json.dump` at runtime, not what imports what.

## Your recorded notes — no score

### N-D1 — bug detection

**Citations** (`file:line`):

- `mechanical.json:8` (`"kills": {}`), `mechanical.json:265` (`"case_counts": {}`), `:266` (`"determinism": {}`), `:267` (`"runtime_seconds": null`)
- `scripts/kill_test.py:191` (`class Mutant`), `scripts/run_kill_test.py` (the runner that would exercise it)

**Note:** I could not tell, and here is what I looked at: the mechanical block that sits beside this card records nothing for kills, case counts, determinism, or runtime for `scripts/` in this run — all four fields are empty or null. `scripts/` does carry its own mutation/kill-test machinery (`kill_test.py`, `run_kill_test.py`), so a kill run against this artifact is possible in principle, but I did not run it (the task instructs not to run the test suite, and that machinery is exactly the test suite), and no prior run's kill data is recorded in this card's mechanical block for me to read instead. I did not seed a fault of my own (see judging practice above). So: no evidence of what the cases catch or miss exists for this artifact in this run, and I am not inventing any.

### N-D4 — behavior preservation

**Citations** (`file:line`):

- (none — there is nothing to cite against)

**Note:** There is no baseline for this artifact. The task states this plainly, and I confirmed it: nothing in this card's directory, nor anything I was pointed at in the repo, presents a prior version of `scripts/` to diff against for this run. I have no behaviors to enumerate and nothing to show still holds. That absence is the answer, not a gap in this note.

### N-D5 — honesty

**Citations** (`file:line`):

- `scripts/effect_conformance.py:22-31` (MF-027: "A Java or Kotlin adapter in a separate JVM... is therefore invisible to it")
- `scripts/effect_conformance.py:38-50` (MF-033/MF-028: "every adapter in this repository shells out, so the in-process sandbox saw only the spawn and refused")
- `scripts/effect_conformance.py:945-950` (`WorkingTreeObserver` "does not claim them: `covered_types` is exactly `{filesystem.write, filesystem.delete}`... this class offers no way to pretend otherwise")
- `scripts/effect_conformance.py:104` ("NOTHING DOWNGRADES AN UNOBSERVABLE VERDICT EITHER") and `:1141` ("Non-empty => the run FAILS")
- `scripts/code_complexity.py:894-899` ("effectful_calls undercounts by construction: ... sink names are left out of the vocabulary for colliding with in-memory operations")
- `scripts/onboard_program_model.py:496-498` (`raise NotImplementedError(f"SCAFFOLD: bind generated port {context.port_name}")`) — secondary, since this is a string template handed to a consumer, not `scripts/`'s own runtime behavior.

**Note:** The artifact refuses rather than falsely certifies, repeatedly and in its own words. `effect_conformance.py` names exactly what its own instrumentation cannot see (a child process's network activity, anything outside the working tree, a JVM/Kotlin adapter's effects) and treats an unobservable target as a hard failure rather than a silent pass — the opposite of overclaiming coverage. `code_complexity.py`, the very instrument behind this card's mechanical block, discloses its own undercount by name rather than presenting its figures as complete. The weakest link is that the clearest refusal-to-fake pattern in the onboarding path (`raise NotImplementedError` rather than a fabricated adapter) lives in a generated string template for a consumer repo, not in `scripts/`'s own executed code — so I did not weight it as strongly as the effect-conformance and complexity-instrument disclosures, which are live.

## Verdict

`scripts/` is a well-measured, low-god-state CLI toolchain (D2: 2) that is honest in its own code about what it cannot see, but it enforces ports-and-adapters discipline on the projects it scaffolds without practicing that discipline on itself — effects are written from everywhere in its own modules and it declares no interface of its own (D3: 0).

## Disclosures

- I was served only this card and `mechanical.json`, as instructed; I did not open `references/eval_scorecard.md`, any other card, any `UNBLINDING*`/`SEALED-BEFORE-DISPATCH`/`INSTRUMENT-LOG`/`RESULT.md`, or `examples/validation/scorecards/subjects.toml`, and I learned nothing that identifies which arm `LL` is.
- I read `mechanical.json`'s `commit` field (`82936ef3bce29e3551cd83dd3673bf60f4eec162`) while filling this card; it differs from `git rev-parse HEAD` in the working tree I scored (`dd71b11a0282a662f60d7bca0c34671ba9e12235`). I recorded the latter in `scorecard.json.commit` per the task's instruction to use `git rev-parse HEAD`, and note the mismatch here rather than silently picking one.
- I rejected the mechanical block's `declared_interfaces: 0` and `effectful_calls: 486` figures as inputs to the score itself (rule 7: recorded, never scored) and instead re-derived the same facts independently by grep/read, which is why the citations above are all `scripts/*.py` lines rather than `mechanical.json` lines.
- Nothing was run that changed the tree.
