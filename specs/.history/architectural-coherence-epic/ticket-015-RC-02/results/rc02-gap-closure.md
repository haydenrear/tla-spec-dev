# RC-02 — per-gap closure record (MF-026 round 3)

Three in-scope gaps, three dispositions, none of them a justification, an
accepted risk or a waiver. Round 3's verdict was `fail` with 3 gaps and 0
escalations; this is what each one became.

---

## N-1 [major] — three ports declared, referenced by no action row

**Disposition: model it.**

`cli_download`, `cli_artifact_delete` and `cli_selftest_process` are now on the
`InstallLocalCli` row in all three trees, with matching `@port` lines in all
three `TlaSpecDevCli.tla` modules:

```yaml
BuildSkillCli:   [cli_artifact]
InstallLocalCli: [cli_artifact, cli_download, cli_artifact_delete, cli_selftest_process]
```

### Why `InstallLocalCli` and not a split across both actions

The audit's advisory said "add the three ports to the `BuildSkillCli` /
`InstallLocalCli` rows". Splitting them — the tlc2 installer on one action, the
tla-spec-dev installer on the other — would have asserted a phase boundary that
no shipped artifact draws. Three artifacts do draw a boundary, and all three put
these effects on `InstallLocalCli`:

1. `InstallLocalCliAdapter.apply()` literally runs
   `bash skill-scripts/install-tla-spec-dev.sh` and then the installed wrapper.
   It is the only adapter in the model that executes an installer.
2. `kill_mutants.toml` already seeds `port-cli_download`,
   `port-cli_artifact_delete` and `port-cli_selftest_process` with
   `refine_action = "InstallLocalCli"` — including the two that live in
   `install-tlc2.sh`. RC-01's own catalog put them there.
3. `BuildSkillCliAdapter.apply()` checks that the entrypoint and the installer
   EXIST and writes nothing; its `run()` comment says so.

Point 3 raises a question about `BuildSkillCli: [cli_artifact]` itself, which is
recorded in the manifest beside the row and filed as **RC-02-DF-01** rather than
decided here.

### The recurrence check

`tests/test_spec_manifest_records.py` gains two parametrized tests over all
three trees:

* `test_every_declared_port_is_attached_to_an_action` — set equality between the
  ports block and the union of the action rows, both directions.
* `test_each_actions_port_annotations_mirror_its_effects_row` — per-action set
  equality between the module's `@port` lines and the manifest row, which
  refuses round-2 G-1's direction and N-1's direction with one assertion.

Both fail on the pre-fix tree (verified by reverting the row: 2 failed,
16 passed). Neither needs a corpus, a TLC run or an adapter — which matters,
because the oracle finding that would have caught this needs all three (below).

### Measured, not asserted

The oracle was run with RC-01's rows and with RC-02's rows over the same corpus.
Attaching the ports removes **two undeclared-effect gaps and one dead port**:
the `bash …/install-tla-spec-dev.sh` spawn, the `…/bin/tla-spec-dev --version`
spawn, and `DEAD MODEL SURFACE: port TlaSpecDevCliPort.cli_selftest_process`.

`cli_download` and `cli_artifact_delete` are **still reported dead** after the
fix, because no adapter executes `install-tlc2.sh`. The declaration gap is
closed; the exercise gap is not, and is not claimed to be.
See `specs/results/rc02-effect-conformance/README.md`.

---

## N-2 [major] — `generate cases` writes and deletes at caller-chosen locations

**Disposition: change the program** — the disposition RC-01 chose for the
identical class in G-2/G-3.

`scripts/spec_paths.py` gains `SpecTreePathError` and `resolve_spec_tree_out`,
the exact sibling of `EvidencePathError` / `resolve_evidence_out` the audit
proposed. `--out` and `--dot` both resolve through it in
`generate_cases_from_tlc_dump.run`, and a path that resolves outside a `specs/`
directory is **refused, not relocated** — rewriting the operator's path would
make the flag lie about where the corpus went.

`specs` is the honest component to check for: `spec_tree` and
`spec_tree_delete` both declare `target: "**/specs/**"`, and
`effect_conformance.PortDeclaration.matches` uses `fnmatch`, whose `*` crosses
separators — so that glob means precisely "under a directory component named
`specs`".

**The `rmtree` is constrained by construction rather than by a second check.**
`run_tlc_dump` derives `metadir = dot_path.parent / ".tlc-states" / stem`, so
constraining `--dot` constrains every path this action deletes. That derivation
is asserted directly in
`test_generate_cases_metadir_delete_stays_inside_the_declared_tree`.

Resolution semantics are unchanged: `resolve_spec_tree_out` still resolves
through `resolve_spec_relative_path`, so a relative `--out` still lands under
the spec directory exactly as documented. The only paths newly refused are ones
that resolve outside a `specs/` tree — in practice, absolute paths. Four callers
in the repository passed such a path and were moved under `specs/`: two tests
and the `AnalyzeComplexity` advisory probe in `production_adapters.py` (two
trees), plus `GenerateCasesAdapter`'s fixture (two trees).

New tests: `test_generate_cases_out_is_constrained_to_the_declared_spec_tree`
(CLI-level, both flags, asserts nothing was created) and the metadir derivation
test above.

---

## N-3 [minor] — a citation that went stale in the commit that wrote it

**Disposition: model it (correct the record), and kill the class.**

The three numbers are fixed (`:116`, `:140`, `:882-883`) and rewritten in a form
that cannot go stale silently. `tests/test_source_citations.py` enforces a
convention over `scripts/*.py`, the three `spec_manifest.yaml` files and the
three `TlaSpecDevCli.tla` modules:

1. **file-qualified** — a bare `:115` is refused. RC-01's was bare and genuinely
   ambiguous: its sentence named `scripts/tla_spec_dev.py` immediately before
   writing ", never saw the java spawn at :115" about a line in the file the
   docstring was in.
2. **content-anchored** — `file.py:116 (subprocess.run)`; the parenthesised
   token must appear on the cited line. This is the half that catches a
   one-line shift. A "does the cited line exist" check passes on `:115` and
   `:116` alike and would have caught nothing.

Negative control: changing the fixed citation back to `:115` makes the test fail
with `scripts/generate_cases_from_tlc_dump.py:115 does not contain the anchor
'subprocess.run'`.

**Applying the convention found eight more stale citations that nobody had
reported**, all in the three manifests, all fixed here:

| citation as written | actually at | what it means |
|---|---|---|
| `install-tla-spec-dev.sh:22` "cat > $WRAPPER" | `:23` | in RC-01's own G-9 comment block |
| `tla_spec_dev.py:313-339` "executed at `:358`" | built `:346`, executed `:401` | runner spawn |
| `:296-303` "the `uv run --with pytest` child" | `:328-335` | |
| `spec_evolution.py:154` "via `:707` / `:851`" | `:994` / `:1143` | ticket / workflow close |
| `spec_evolution.py:99` "via `:801` / `:903`" | `:1093` / `:1195` | git_metadata call sites |
| `tla_spec_dev.py:91`/`:118` "printed at" | `:94` / `:121` | budget_prompt prints |
| `corpus_diagnostics.py:835-852` add_arguments | `:842` | |
| `:902-935` run() | `:909` | |

Nine of eleven citations in that surface were wrong in some tree. That is the
finding the audit asked for: the class was not RC-01's carelessness, it was that
nothing checked.

**Scope is declared, not assumed.** `tests/`, `references/`, `specs/results/`
and the planning YAML are out of scope: results and history are append-only
records of what was true when written, and rewriting them to satisfy a checker
would be the opposite of the point.

---

## The thing that was not a gap

`cli_artifact`, `cli_download` and `cli_artifact_delete` still target `*`. Not
touched, on the owner's instruction and for the reason the auditor recorded: the
schema has no env-var interpolation, `SKILL_MANAGER_BIN_DIR` and
`SKILL_MANAGER_CACHE_DIR` are unconstrained required inputs, and `*` is honest
where `**/.venv/**` was a lie. Narrowing it needs schema support, not a patch.

The oracle run does put a number on the cost: of the 12 declared ports, the
three at `*` cannot express a gap for their actions, and two of them
(`cli_download`, `cli_artifact_delete`) additionally report dead on every run
that can be executed. Recorded, not filed.
