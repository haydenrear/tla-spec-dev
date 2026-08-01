# RC-01 — the nine MF-026 in-scope gaps, one by one

Audit: `specs/results/coverage_audit_report_architectural_coherence.md`, verdict
`fail`, 9 in-scope gaps. Every gap is closed by MODELLING IT or by CHANGING THE
PROGRAM. No gap is closed by a justification, an accepted risk, or a scope
waiver — those dispositions do not exist for an in-scope gap, and none is
claimed below.

Two of the nine were closed by doing both, and one of the nine turned out to be
partly a defect in the audit rather than in the artifact. That is stated where
it happens rather than smoothed over.

---

## G-1 — `AnalyzeArchitecture` has no `effects.actions` row — **MODEL IT**

Added `AnalyzeArchitecture: [evidence_report]` to all three manifests, and the
matching `@port TlaSpecDevCliPort.evidence_report` line on the action, so the
model's own claim ("each action's `@port` lines mirror its row in
`effects.actions`") is true again.

Not `[]`: the command performs a real write. It became honest to declare
`evidence_report` only because G-2 constrained the path — see below.

Regression check: `tests/test_spec_manifest_records.py::test_every_command_action_has_an_effects_row`
requires the row set and the `@command` set to be equal in BOTH directions, in
all three trees.

## G-2 — `analyze architecture --out` / `architecture_reflexion --out` write anywhere — **CHANGE THE PROGRAM, then model it**

The audit offered two remedies. Took the first: the path is constrained, in one
place, by `scripts/spec_paths.py::resolve_evidence_out`, which resolves the path
and REFUSES (exit 2) anything not under a `results/` directory — the surface
`evidence_report` declares as `**/results/**`.

Refused, not relocated. Rewriting the operator's path would make the flag lie
about where the file went, which is the honest-in-prose / misleading-in-artifact
defect RP-02 was opened for.

Worth recording: **every existing caller in the repository already wrote into a
`results/` directory.** Both pre-existing `--out` tests
(`test_evidence_can_be_written_into_a_results_directory`,
`test_out_writes_the_evidence_file`) passed unchanged. The declaration was
always true of what the program did; it was not true of what the program
allowed.

Regression check: `tests/test_tla_spec_dev_cli.py::test_analyze_out_refuses_a_path_the_evidence_port_does_not_cover`
and `::test_reflexion_out_is_constrained_the_same_way`.

## G-3 — `analyze complexity --out` has the same unconstrained write — **CHANGE THE PROGRAM**

Same helper, same refusal, same test. `AnalyzeComplexity` already declared
`evidence_report`, so this is the case where the declaration existed and the
program did not honour it.

## G-4 — `TlaSpecDevCli.tla:649` claims the scan only prints — **MODEL IT**

The line `\* No @port: the scan reads the model and the source tree and prints.`
is gone, replaced by the `@port` line G-1 created plus a note saying what stood
there and why it was false. The model no longer carries the misleading record.

## G-5 — three manifests say "9 variables and 15 actions" — **MODEL IT, and one correction to the audit**

`specs/current` and `specs/desired_program_model` were stale, exactly as the
audit reported; they now state 11 variables and 18 Next disjuncts.

**`specs/program_model` was not stale, and the audit was wrong about it.** That
tree is the ACCEPTED BASELINE. It predates AC-01, its module has 9 variables and
15 Next disjuncts, and its comment said so correctly. The audit quoted all three
manifests as describing one model. The comment there is rewritten to name the
tree explicitly so the two models cannot be conflated again — but the FIGURE was
right and was not changed to 10/16 or to 11/18, because that would have made a
true record false in order to satisfy an assertion written from a
misclassification.

The durable half, which is what the gap asked for ("add the counts to whatever
check RP-05 used"): `tests/test_spec_manifest_records.py::test_the_manifest_states_the_counts_of_the_model_beside_it`
parses the module sitting beside each manifest and fails if the two disagree. It
derives the figures rather than restating them — a test that hardcoded 11 and 18
would go stale the same way the comment did.

## G-6 — case-module generation entirely unrepresented — **MODEL IT and CHANGE THE PROGRAM**

The headline gap, and the largest piece of this ticket.

**Program:** `tla-spec-dev generate cases <tla> <cfg> --out <dir>` is now a
shipped subcommand, registered in `build_parser` from
`generate_cases_from_tlc_dump.add_arguments` (extracted from its `main()` so the
CLI cannot drift from the file). It also grew `--coverage-json`, which runs the
`case_modules` aggregation over the corpus just written — so `case_modules`'s
report builder is reachable from the shipped parser too, not only its
coverage-record writer. That destination is constrained to the generated package
root, for the same reason G-2 constrained `--out`.

**Model:** `GenerateCases`, guarded on `setup_phase >= 4` (the case caps it
measures against ARE budgets), declaring:

- `corpus_process` — the java/TLC spawn (`run_tlc_dump`);
- `spec_tree` — the generated package, the per-action coverage record
  (`case_modules.write_coverage_record`), the aggregated report, and the
  parameter-recovery audit (round-1 G-11, folded in as the generation-time
  artifact it is);
- `spec_tree_delete` — the metadir `rmtree` in `run_tlc_dump`'s finally branch.

It records no verdict. Generation writes a corpus; `AnalyzeCorpus` measures one.
`corpus_gate` stays UNCHANGED, deliberately: resetting it to `"unknown"` on every
generation would falsify `SpecUnitTestsRequireMeasuredCorpus` for a ticket that
legitimately passed earlier, i.e. it would make the model assert something the
program does not do.

**Recorded residual, not a waiver:** `--out` accepts an absolute path, and a
corpus deliberately written outside the spec tree lands outside `spec_tree`'s
`**/specs/**`. The relative default resolves against the spec directory, which is
the documented and exercised path, and the owner's ruling names `spec_tree`. This
is written into the manifest row rather than left for the next audit to find.

Regression checks: `tests/test_tla_spec_dev_cli.py::test_case_generation_is_reachable_from_the_shipped_parser`
walks the import closure of `build_parser` — the same walk the audit used to
prove it was unreachable — and
`specs/current/tests/test_tla_spec_dev_generation_adapter.py::test_generate_cases_performs_the_effects_it_declares`
drives the real command and checks each declared effect actually happened.

## G-7 — two manifest comments cite an amendment that does not exist — **MODEL IT**

Both comments rewritten in all three manifests. The view-split citation now
points at the live restored ruling (`ticket_plan.yaml`,
`service_catalog.known_gaps`, the entry dated 2026-08-01) and says plainly that
the old dated citation resolved to nothing. The case-generation comment, which
would have become affirmatively FALSE the moment `GenerateCases` landed, now
records the owner's 2026-08-01 decision instead of the superseded ruling.

Regression check: `tests/test_spec_manifest_records.py::test_no_manifest_cites_an_amendment_that_does_not_exist`.

## G-8 — AC-04's `architecture_delta` and its verdicts are unmodeled — **MODEL IT**

Added `architecture_delta` as its own variable rather than widening
`architecture_scan`'s domain. The audit permitted either; a separate variable is
the honest one, because "this scan is coherent" and "the code moved toward the
boundaries the model draws" are different facts that the ledger records
separately and that a run produces together.

Domain: the five direction verdicts `scripts/complexity_ledger.py` actually
records (`improved`, `worsened`, `unchanged`, `unverified`, `unattributable`)
plus `"unknown"` for a scan with no `--baseline`. The two REFUSALS are the reason
the whole domain is modeled: `unattributable` is what the tool returns for the
gaming move AC-04 demonstrated (re-placing one module in the map alone moves this
repository's divergence count 0 -> 6 with no source change), and `unverified` is
the structural MF-020 rule. Modeling only the three measurements would have
represented exactly the half of the command that can be gamed.

One honest constraint is encoded: an `unmappable` scan admits only `"unknown"`,
`"unverified"` or `"unattributable"`, because with no comparable reflexion
report there is no count to compare.

State-space cost recorded in `rc01-model-delta.md` the way AC-01's 4.6x was:
this variable is a 6x factor on the static bound.

## G-9 — the dead `cli_artifact` port — **MODEL IT (retarget), plus three new ports**

`cli_artifact` kept its name and its two actions and was RETARGETED from
`**/.venv/**` — which nothing in this repository writes — to `*`, with the
reasoning recorded inline: `SKILL_MANAGER_BIN_DIR` and `SKILL_MANAGER_CACHE_DIR`
are REQUIRED ENVIRONMENT INPUTS (`: "${SKILL_MANAGER_BIN_DIR:?}"`), the
installers refuse to run without them and constrain neither, so any narrower glob
asserts a constraint the code does not enforce. That is the same reasoning
already recorded in this manifest for `corpus_process`'s `*`.

Retarget rather than removal, so `port-cli_artifact` stays seeded and now lands
on a boundary that exists (`chmod 0755 "$WRAPPER"` in
`install-tla-spec-dev.sh`). Three ports added for what was undeclared:

| port | type | site |
|---|---|---|
| `cli_download` | `network.http` | `install-tlc2.sh:37` `curl -fL "$JAR_URL"` — the network port ESC-6 named and the proviso demanded |
| `cli_artifact_delete` | `filesystem.delete` | `install-tlc2.sh:38` `mv "$JAR_TMP" "$JAR_PATH"` unlinks the temporary |
| `cli_selftest_process` | `process.spawn` | `install-tla-spec-dev.sh:31` `"$WRAPPER" --help` |

Each has a seeded mutant in all three `kill_mutants.toml` trees. Declared
boundaries went 22 -> 26 (12 ports + 14 invariants), and the kill test's own
recomputed obligation set is what enforces that, not this paragraph.

---

## Plus the owner decision: the six guard-weakening flags

**MODEL IT and CHANGE THE PROGRAM.**

**Model:** `TicketClosedWeakened` (stage 6) and `CloseTicketWeakened`. The
transition's guard requires only that the ticket be ACTIVE — `TicketOpened` is
reachable into it — which is the claim: a ticket can reach a closed stage having
passed no spec-unit run.

**Program:** `scripts/spec_evolution.py` writes a `guard_weakening` block into
the append-only close history, naming the flags used and what each bypassed. A
model may not represent a difference the program does not expose, and before this
the record carried only an unlabeled `accept_new` boolean among fifty other keys.

**Five invariants had to be narrowed, and TLC found the first one.**
`TicketClosedWeakened` is 6, every guarded stage is <= 5, and every property that
meant "this ticket has been through stage X" was written as `ticket_state[t] >=
X`. So `>=` answers TRUE for the stage that certifies the LEAST. TLC violated
`SpecUnitTestsRequireMeasuredCorpus` in 1,094 states on the first run: a ticket
sat at stage 6 with `corpus_gate = "unknown"`.

All five now read `TicketReached(t, stage) == ticket_state[t] \in
stage..TicketClosed`, named once and used everywhere.
`ClosedTicketsPassedSpecUnitTests` additionally quantifies over
`GuardedClosedTickets`, with a tombstone recording the narrowing — it would
otherwise have stayed true BY ACCIDENT OF THE ORDINAL ENCODING while a weakened
close never passed anything, which is the model reading as an assurance that
`--accept-new` exists to make false.

One new invariant, `WeakenedClosesCertifyNothing`, states the positive fact, so
the narrowing cannot be read as the model merely having less to say. It has a
seeded mutant (`inv-WeakenedClosesCertifyNothing`) that makes the history record
every close as a guarded one.

**Three of the six flags cannot be seen at the close.** `--validate-only` belongs
to the spec-unit run and `--force` / `--dry-run` to scaffold/open; each weakens a
precondition a later close relies on, and the close path cannot detect it. That
is recorded on `CloseTicketWeakened` as a limit of OBSERVATION and filed as
`RC-01-DF-03`. Three of six covered; before this ticket it was zero of six.
