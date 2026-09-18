Refs #333

- **Epic branch**: `epic/self-improvement-substrate`
- **Workflow**: `self-improvement-substrate`
- **Assigned spec ticket**: `SI-04` — **left open**; the epic agent owns the model for this epic (`planning_rules.model_ownership_rule`) and closes/promotes at wave merge. No `open ticket`, `close ticket`, `close_tickets.py` or `--accept-new` was run.
- **Branched from**: `994f650c` (the declared `base_sha`/`plan_commit`, and the epic tip at dispatch)
- **Dependency `SI-02`**: PR #350 **merged** at `a42e0f7e`, reachable from `origin/epic/self-improvement-substrate` ✅
- **Promotion predecessor `SI-02`**: satisfied ✅
- **Ticket commits**: `4b72c869` (the slice) and `7ac938e2` (`SI-04-DF-04`). Branch head on GitHub: **`7ac938e2`**
- **Assignment vs canonical plan**: no mismatch found. `specs/tickets/SI-04/ticket.yaml` matches the rendered assignment on conflict keys, goals, wave, promotion order and predecessor.

## What landed

One record schema, and **one reader** for it.

`skill_change: none | proposed(<unit>, <diff or issue>) | applied(<commit>) | declined(<reason>)` — one grammar, carried by all four record files, plus a `goal:` link so a finding and the measurement it should move sit on the same record.

| file | change |
|---|---|
| `skills/spec-double-2/references/bug_attribution.md` | new **§2a**: the field every record kind carries; added to the CATCH / REACH / BLIND / PRICE examples in §4–§7 |
| `skills/spec-double-2/references/consumption.md` | **D4** — *a finding anchored to a skill is consumed only by a change to that skill*; advisory, and explicitly not checked by `disposition.py` |
| `examples/validation/agent_rounds/SELF-IMPROVEMENT-MATRIX.md` | the `skill change` column on the bins table, and why every cell reads `(absent)` |
| `skills/spec-double-2/scripts/improvement_ledger.py` | **new**. Reads all four files, prints findings by disposition, warns per `recorded-local` / missing `skill_change`. Advisory |
| `skills/spec-double-2/scripts/disposition.py` | refactored to expose `read_rows()`; `load()` becomes a thin raising wrapper. Behaviour unchanged |
| `skills/spec-double-2/scripts/skill_feedback.py` | emits the two fields in the template and carries them on `to_record()` |
| `tests/test_disposition_requirement.py` | +13 tests: the grammar, the one-reader property, and the no-exit-path guard |

### Wrap, not replace — the decision the ticket turned on

`disposition.py` **owns the backlog bytes**: the duplicate-key structural guard and the D1/D2/D3 clauses. The ledger needs the same rows but must never refuse, and `load()` raises `SystemExit`.

Rather than give the ledger its own `yaml.safe_load` — a second opinion about the same bytes, which is exactly what `CA-05-DF-06` cost an epic to find — I split `disposition.py` into:

- `read_rows(path) -> (rows, faults)` — detects, raises nothing;
- `load(path)` — `read_rows` plus this script's refusals, behaviour and messages unchanged.

So there is **one parser per file**: backlog rows via `disposition.read_rows`, `SF-NNN` blocks via `skill_feedback.parse_findings`, matrix tables via `improvement_ledger.md_tables`. `test_one_backlog_reader_not_two` pins it by asserting both readers resolve to the same `__file__` *and* that `safe_load` does not appear in the ledger.

**D4 deliberately does not live in `disposition.py`.** That instrument refuses; `skill_change` did not exist when any sealed epic closed, so a refusing D4 would condemn the whole record on a field nobody could have filled — `MF-020`, the error this page has already declined to commit once for D2/D3.

## Goal contribution

| Goal | Contribution | Expected effect | Measured local signal | Decided by |
| --- | --- | --- | --- | --- |
| `GOAL-findings-become-changes` | direct | the field and its reader exist; the ledger prints today's baseline on its first run | **Ran. 90 records across all 4 files: 13 `recorded-local`, 87 with no `skill_change`, 0 unparseable, 47 D4 violations.** Field + reader exist and the baseline is printed — **moved as expected**, with the denominator larger than the issue's (see below) — `specs/results/epic-self-improvement-substrate/tickets/SI-04/local-signal-GOAL-findings-become-changes.txt` | SI-08 |
| `GOAL-no-new-gates` | guard | the ledger warns and exits 0; no refusal path added | **Ledger: 0 matches, exits 0 on every path tried** (incl. a missing PyYAML and a nonexistent root). **`disposition.py` 5 → 6: one net added refusal, disclosed and argued below — not flat.** — `.../local-signal-GOAL-no-new-gates.txt` | SI-08 |

**The baseline numbers moved and I am not restating the issue's.** The issue predicted *"13 recorded-local, 39 rows with no disposition"*, measured on `b7a7d203`. Measured here: **13 recorded-local** (unchanged) and **87** records with no `skill_change`, because the backlog grew from 33 to 48 rows during this epic and the ledger also reads the 6 `deferred_findings_next.yaml` rows and the 7 matrix bins, which the issue's figure did not. Same finding, larger denominator. `MEMORY.md`'s standing lesson about restating a number without re-deriving it is why this is spelled out rather than quietly matched.

**`GOAL-no-new-gates` is a guard and it is NOT flat.** Disclosed rather than netted out: the metric counts one net addition in `disposition.py`, `raise SystemExit("PyYAML is required to read the ledger")`. Before this ticket that input died with an uncaught `ModuleNotFoundError` — already non-zero, already a stop. No input that previously succeeded now refuses; one that previously *crashed* now refuses legibly. The alternative (fall through to the existing `no findings` refusal) greps clean and produces a message pointing at ABSENCE when the cause is a missing package — `SF-305`'s exact class. **The advisory reader this ticket ships carries zero. Whether the +1 counts against the goal is SI-08's call, not mine.**

## Validation

| entry | command | result |
|---|---|---|
| `repository_unit` | `uv run --python 3.12 --with pytest --with pyyaml --with jinja2 --with hypothesis python -m pytest tests -q --ignore=tests/test_score_tools.py` | 10 failed / **1613** passed / 5 skipped — **the identical 10 failure NAMES as baseline** (`diff` of the two sorted name lists is empty). Passed 1594 → 1613: the +19 are this ticket's new tests |
| `spec_unit` | `tla_spec_dev.py run spec-unit-tests --target specs/current` | 7 failed / 49 passed — **same 7 names as baseline** |
| `spec_unit` | `tla_spec_dev.py run spec-unit-tests --target specs/tickets/SI-04/desired` | 7 failed / 46 passed — **same 7 names as baseline** |
| `tlc` | — | `N/A`: the epic agent owns the model for this epic |
| `graphs` | `test-graph/scripts/discover.py` then `run.py cliWorkflow` | discovered (2 steps) and **run**: BUILD SUCCESSFUL |
| `spec_graph` | `test-graph/scripts/discover.py` then `run.py specWorkflow` | discovered (9 steps) and **run**: all 9 nodes executed, BUILD SUCCESSFUL. Worth running rather than waving at — its `spec.workflow.close` node exercises `skill_feedback.py`, which this ticket changed |

**Compared by NAME, never by count**, per the wave-1/2 lesson. Baseline was recorded on the untouched worktree *before the first edit*:

- **repository suite baseline**: 10 failed / 1594 passed / 5 skipped — `.../baseline-repo-unit.txt`
- **spec-unit baseline**: 7 failed on *both* targets — `.../baseline-spec-unit-{project,ticket}.txt`

**`--ticket SI-04` was NOT used.** `SIS-KICKOFF-F-04` records that it resolves both targets and executes only the first, so `specs/current`'s 7 failures would have masked the ticket target entirely. Both targets were run explicitly with `--target`, and both are reported above.

## Deferred findings

| ID | severity | summary |
|---|---|---|
| `SI-04-DF-01` | minor | **The one place "one reader" is not satisfied repository-wide.** `tests/test_every_finding_reaches_the_table.py` parses the matrix with its own regexes; the ledger parses it with `md_tables`. Two parsers, one file. Outside this ticket's conflict keys, and weakening that guard as a refactor side-effect is what it exists to catch |
| `SI-04-DF-02` | minor | `specs/results/skill_feedback.md` contains the four worked examples **twice** (8 `SF-000*` headings for 4 examples), a state the close path should not be able to produce. Found because 37 headings vs 29 parsed records had to be explained rather than assumed. `skill_feedback.md` content is SI-05's |
| `SI-04-DF-03` | major | **`skt ticket new` refused and rolled the worktree back.** The three units that fail to project are the three this epic moved into the plugin; `skt ticket new` forwards no `--allow-unprojected`, so there was no way through the front door |
| `SI-04-DF-04` | major | **`origin` is a sibling worktree, not GitHub, and the push SILENTLY succeeds.** `git push -u origin` prints "Everything up-to-date", exits 0, and `git rev-parse origin/<branch>` then matches local HEAD — so every natural check says it worked, while GitHub 404s the branch |

All four carry a `skill_change:` — this ticket obeys the field it ships.

## Skill changes proposed

| unit | what I hit | proposed change |
|---|---|---|
| `skill-manager` / `skt` | `skt ticket new` refused on an unprojected home and rolled back the worktree; no flag forwards `--allow-unprojected` | Give the projector the contained-skill rung so a plugin's skills project into `.<agent>/skills/`, **or** forward the flag. Same class as `SIS-W2-F-05` one level up. Filed as `SI-04-DF-03`; **not applied** — not in my conflict keys and the unit's repo is not in this checkout |
| `spec-double-2` | the backlog had one reader that could only refuse | **Applied here**: `disposition.read_rows()` + `load()` wrapper, in this PR |
| `spec-double-2` | `skill_feedback.md` blocks had nowhere to record a substrate change | **Applied here**: `skill_change:`/`goal:` in the template and on `to_record()`, in this PR |

## Review input

**Hot spots**

- `skills/spec-double-2/scripts/disposition.py` — the `read_rows`/`load` split. `load`'s refusals and messages are meant to be byte-identical for every pre-existing input; `tests/test_disposition_requirement.py` still passes unchanged, which is the evidence.
- `skills/spec-double-2/scripts/improvement_ledger.py` — new, ~520 lines, and the only new executable surface.
- `examples/validation/agent_rounds/SELF-IMPROVEMENT-MATRIX.md` — **the matrix has a one-writer rule and I am a ticket agent.** I changed its *schema* (one column, under an explicit conflict key) and placed no finding, moved no row and altered no count. Flagging it because the rule says ticket agents do not edit this file.
- `specs/results/deferred_findings_final.yaml` — appended 3 rows at the tip after re-fetching (wave 1's only merge conflict was concurrent appends here). Tip was unmoved at `994f650c`; 45 → 48 rows; re-parsed with PyYAML after appending.

**Decisions and overrides**

- **Wrap, not replace** — nobody specified which; reversing it is a ticket.
- **D4 is advisory and lives in the ledger, not `disposition.py`** — deliberate, argued above.
- **The `skill change` column went on the bins table, not the 13-row anchor table.** The anchor table's rows are already enormous prose; the bins table is where substrate findings and the existing `disposition` concept live. A reviewer may want it on both.
- **`(absent)` is a spelling, not a grammar token.** The reader normalises `(absent)`/`-`/`—`/empty to absent and keeps everything else `malformed`. I widened the grammar exactly this far and no further, after my own 7 matrix cells first parsed as `malformed`.
- **`GOAL-no-new-gates` +1, disclosed** rather than reworded to grep clean.
- No guardrail was skipped, no test weakened, no matrix entry turned into `N/A` by me.

**Where I'd look for bugs in my own change**

1. `md_tables` — hand-rolled markdown parsing. It keys on header *name* specifically so a new column cannot shift a reading, but the separator-row heuristic (`set(p) <= set("-: ")`) would treat a legitimately `-`-only cell as a separator. Cheapest experiment: feed it the matrix's other tables and diff the row counts against `grep -c '^|'`.
2. `unit_for` — decides "is this anchored to a skill", and drives the whole D4 count of 47. It matches `skills/<unit>/` and six legacy prefixes; a finding naming `examples/...` or a bare filename is counted as *not* skill-anchored. The 47 is therefore a **floor**. Cheapest experiment: print the surfaces of the 26 skill-anchored backlog rows and read them.
3. `_guarded`'s broad `except Exception` — it is what makes "exits 0" true, and it can also hide a real bug in a reader as one `NOT read` line. It prints the exception type and message, which is the mitigation, but a silent partial read is the risk. Suspicion, not a reproducible defect.
4. `parse_skill_change` splitting `proposed(a, b)` on the first comma — a unit name containing a comma would mis-split. Not reachable with real unit names.

**Machinery friction**

- **`skt ticket new` could not create this worktree at all** (`SI-04-DF-03`). This is the reportable by-hand case from `git-issue-workflow` SKILL.md — *"you found it and it FAILED"* — and the refusal is quoted verbatim in `.../worktree-front-door-refusal.txt`. I used the documented `git worktree add && bootstrap-home.sh` pair at the declared path with the pinned base. The by-hand route worked, which is exactly why it is named here.
- **`run spec-unit-tests --ticket` is still the trap `SIS-KICKOFF-F-04` describes.** A ticket agent following the assignment's REQUIRED command verbatim gets a green-looking run of the *wrong* target.
- **No `python3` here carries PyYAML** (`SF-105` / `EV-02-DF-05`, still open). The issue's declared local signal is a bare `python3 scripts/...`, which on this machine read **two of four** files. It cost me a real defect: the ledger's first run exited **1** with a traceback, which is how I learned that "no `sys.exit`" does not mean "exits 0". Both spellings are recorded in the evidence.
- **`bootstrap-home.sh` wrote `/specs/` into this clone's shared `.git/info/exclude`**, which is per-clone rather than per-worktree, so every *new* file under `specs/` was invisible to `git status` and silently skipped by `git add -A`. Found by SI-06 (`SI-06-DF-03`, major) and repaired by the epic agent mid-ticket. **No evidence of mine was lost**: I had not committed when the notice arrived and I never ran `git add -A`, so all 11 SI-04 evidence files are in the single commit below. Verified after the repair — `git status --porcelain --untracked-files=all -- specs` lists all 11, `git check-ignore` clears my evidence directory, and the exclude file now carries only the four home directories. Flagged here because the failure mode is silent for *new* files while tracked files keep reporting normally, and because it is the second defect this ticket met that comes from `bootstrap-home.sh` (see `SI-04-DF-03`).
- **`origin` points at `/Users/hayde/IdeaProjects/wt-351-plugin-plumbing`, a sibling worktree, and no GitHub remote for this repository is configured** (`SI-04-DF-04`). The assignment's `git push -u origin feature/<branch>` therefore published **nothing** — and said it had: exit 0, *"Everything up-to-date"*, tracking branch set, and `git rev-parse origin/feature/337-improvement-record` matching local HEAD. GitHub 404'd the branch. I only caught it because `git fetch` printed `From /Users/hayde/IdeaProjects/wt-351-plugin-plumbing`. **This branch is on GitHub because I pushed to the URL explicitly**; I did **not** repoint `remote.origin.url`, because `.git/config` lives in the shared common git dir and would have changed the base and push target of all eight sibling agents mid-flight. Worth the epic owner's attention before the next wave: the failure is invisible to every check an agent would think to run.
- I changed **nothing** inside my worktree's Skill Manager home, so there is nothing for the wave-close reconciliation to carry.

## `home close-out` verdict

**CLEAN.** Run read-only, twice (before and after the work), with a resolved CLI path and `--into` pointing at the **main working tree's** home:

```
skill-manager home close-out --home /Users/hayde/IdeaProjects/wt-337-improvement-record/.skill-manager \
  --into /Users/hayde/IdeaProjects/tla-spec-dev/.skill-manager --json
-> safe: true, exitCode: 0, blockers: [], selfObtainable: []
   26 units, all "unchanged -- already byte-identical to the source"
```

No blockers, nothing published with `unit publish`, and no `home sync` into the project home. The worktree is **left standing** at `../wt-337-improvement-record` for the epic agent to reconcile and sweep.

## Evidence

All under `specs/results/epic-self-improvement-substrate/tickets/SI-04/`:

| file | what it holds |
|---|---|
| `baseline-repo-unit.txt` | the suite **before the first edit** — 10 failed / 1594 passed / 5 skipped |
| `baseline-spec-unit-project.txt`, `baseline-spec-unit-ticket.txt` | spec-unit before, both targets, 7 failed each |
| `after-repo-unit.txt` | the suite after — 10 failed / 1613 passed / 5 skipped, same names |
| `after-spec-unit-specs-current.txt`, `after-spec-unit-SI-04-desired.txt` | spec-unit after, both targets |
| `local-signal-GOAL-findings-become-changes.txt` | the ledger, both interpreter spellings, with exit codes |
| `local-signal-GOAL-no-new-gates.txt` | the grep, the 5→6 disclosure, and exit-0 proof on four paths |
| `test-graph-discovery.txt`, `test-graph-runs.txt`, `test-graph-reports/*.json` | both graphs discovered and run; `status: passed`, 2/2 and 9/9 nodes |
| `worktree-front-door-refusal.txt` | `skt ticket new`'s refusal, verbatim (`SI-04-DF-03`) |
| `remote-origin-is-local.txt` | the silent-success push (`SI-04-DF-04`) |

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01DUdxjqPbjrJ45Bpxw8uZeS

