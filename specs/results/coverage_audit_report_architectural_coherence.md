# Coverage Audit Report — architectural-coherence epic (MF-026 gate)

**Round 3 — re-audited against RC-01 at `05acf8c`.** Rounds 1 (`b1fc5fe`,
`incomplete`, 12 gaps) and 2 (`b76eaf1`, `fail`, 9 gaps) are preserved in this
file's git history; their raw enumerations are preserved unmodified under
`coverage-audit-arch-coherence-raw/`.

**Round 3 RE-ENUMERATES.** Rounds 1→2 reused the raws because only the scope
declaration changed. RC-01 changed the *program* — a new CLI subcommand, two new
actions, a new variable, four new ports — so the surface was swept fresh into
`coverage-audit-arch-coherence-raw/round3/`. Sweeping RC-01's additions as a
claim rather than as surface is precisely what this gate exists to refuse.

## VERDICT

- **Verdict:** **`fail`**
- **In-scope gaps:** **3** — all three are surface **RC-01 created**; 8 of the 9
  round-2 gaps are closed and the ninth is closed in half
- **Escalations: 0.** For the first time in this audit's history every row in the
  enumerated surface carries a real disposition.
- **Out-of-model inventory:** 6,064 of 6,104 source rows, every one traced to a
  quoted `out_of_model` line
- **`scope_source`:** `specs/desired_program_model/ticket_plan.yaml:259-282`
  (`representation_scope`, schedule_revision 6), governed by `:26-96`
  (`semantic_model_rule`) and `:97-106` (`representation_scope_rule`)

| | Round 1 | Round 2 | **Round 3** |
|---|---|---|---|
| Verdict | `incomplete` | `fail` | **`fail`** |
| In-scope gaps | 12 | 9 | **3** |
| Escalations | 7 (187 rows) | 4 (121 rows) | **0 (0 rows)** |
| In-model surface | undeterminable | 46 files | **52 files** |
| Rows inferred, in-model | 86% overall | 0 of 46 | **0 of 52** |

> **The three remaining gaps are all new.** RC-01 closed nine gaps and opened
> three, two of which are the *same class it was closing* — a port with no site,
> and an unconstrained `--out`. That is not a criticism of RC-01's competence; it
> is the measurement this gate exists to produce, and it is the strongest
> available evidence that new surface needs the gate rather than a review.

- **Model audited:** `specs/desired_program_model/TlaSpecDevCli.tla` (11 variables,
  18 `Next` disjuncts), byte-equal in semantics to `specs/current`.
- **Date:** 2026-08-01 · **Commit:** `05acf8c`
- **Raw outputs:** `specs/results/coverage-audit-arch-coherence-raw/round3/`
- **Reproducer:** `round3/cac_ac_classify_v3.py`
- **Independent verification performed** (not read from RC-01's evidence): a TLC
  reproduction of the guard-flag invariant claim, and a full `MC.cfg` run. §6.

---

## 1. Per-gap verdict on RC-01

Every claim below was checked against the tree, not against
`specs/results/rc01-gap-closure.md`. **No forbidden disposition appears anywhere
in RC-01's closure record** — `grep -niE 'justified|accept as-is|acceptable
risk|out of contract|low priority|not worth modeling|unlikely in practice'`
returns nothing, and each gap is closed as `model it` or `change the program`.

| Gap | Claim | Verified? | Evidence |
|---|---|---|---|
| **G-1** | `AnalyzeArchitecture: [evidence_report]` in all three manifests + matching `@port` | **CLOSED** — with a correction to the claim | Row present at `specs/current/spec_manifest.yaml:325` and `specs/desired_program_model/spec_manifest.yaml:323`; `@port TlaSpecDevCliPort.evidence_report` at `TlaSpecDevCli.tla:790`. **`specs/program_model` correctly has no such row** — its module has no `AnalyzeArchitecture` (36 top-level defs vs 42; no `architecture_scan`). "All three" would have been the defect, not the fix. |
| **G-2** | `--out` refused outside `results/` | **CLOSED — change the program** | `scripts/spec_paths.py:76-95` `resolve_evidence_out` resolves the path first (so `..` cannot escape) and checks `results` as a path **component**, not a prefix. Applied at `analyze_architecture.py:1122` and `architecture_reflexion.py:2300`. |
| **G-3** | same for `analyze complexity` | **CLOSED — change the program** | `analyze_complexity.py:2297`. |
| **G-4** | `TlaSpecDevCli.tla:649` replaced | **CLOSED** | The false `\* No @port: … and prints` is gone; `@port TlaSpecDevCliPort.evidence_report` at `:790` immediately precedes `AnalyzeArchitecture(root) ==` at `:791`. |
| **G-5** | my finding was partly wrong | **CLOSED, and RC-01 IS RIGHT — see §3** | |
| **G-6** | `generate cases` shipped + `GenerateCases` modeled | **CLOSED as a representation gap** — but the new command path carries **N-2** | `tla_spec_dev.py:161-181` dispatches to `generate_cases_from_tlc_dump.run`; `GenerateCases(root)` at `TlaSpecDevCli.tla`; manifest row `GenerateCases: [corpus_process, spec_tree, spec_tree_delete]` at `:340`/`:342`. Records no verdict, as claimed — it touches only `lastCommand` and `result`. |
| **G-7** | both comments rewritten in all three manifests | **CLOSED** | `specs/*/spec_manifest.yaml` `source_model` note now names the live citation (`service_catalog.known_gaps`, the "RESTORED 2026-08-01" entry) and says plainly that no 22 July amendment exists. A test checks the citation resolves. |
| **G-8** | `architecture_delta` as its own 6-valued variable | **CLOSED — model it** | `TlaSpecDevCli.tla:918`: `architecture_delta \in {"unknown","improved","worsened","unchanged","unverified","unattributable"}`; assigned at `:800` conditioned on `architecture_scan'`. The reasoning given — that modelling only the measurements would represent exactly the half that can be gamed — is sound and matches AC-04's own gaming probe. |
| **G-9** | `cli_artifact` retargeted; `cli_download`, `cli_artifact_delete`, `cli_selftest_process` added; boundaries 22 → 26 | **CLOSED IN HALF — see N-1** | The write is now declared (`cli_artifact` target `**/.venv/**` → `*`). **The other three ports are declared in the ports block and referenced by NO action row, in all three trees.** So the network download, the delete and the self-test spawn remain undeclared *for the actions that perform them*. |
| **Guard flags** | `CloseTicketWeakened` / `TicketClosedWeakened` + `guard_weakening` in close history | **CLOSED — model it, and it earned its cost. See §6.** | |

**Boundary count independently recomputed:** 12 ports + 14 `MC.cfg` invariants =
**26**, matching RC-01's "22 → 26". `kill_mutants.toml` seeds all 26, plus two
orphans — `port-tlc_process` and `inv-SpecUnitTestsRequireAnalyzedGate`, both for
boundaries CD-09 removed. `git log -S` dates both to `58d785c`, the epic's
opening commit: **pre-existing, not RC-01's**, and harmless because the kill test
recomputes the required set from the model rather than trusting the catalog.
Recorded, not charged to this ticket.

---

## 2. Gaps RC-01 CREATED (3)

The coordinator asked for this specifically. All three were found by sweeping the
new surface, not by reading RC-01's account of it.

### N-1 — three ports declared, referenced by no action. Dead model surface, in all three trees. **[major]**

`cli_download`, `cli_artifact_delete` and `cli_selftest_process` are declared
under `effects.components.TlaSpecDevCliPort.ports`
(`specs/desired_program_model/spec_manifest.yaml:180`, `:188`, `:195`, and the
`current`/`program_model` twins) and appear in **no `effects.actions` row**:

```
BuildSkillCli:   [cli_artifact]     # spec_manifest.yaml:283
InstallLocalCli: [cli_artifact]     # spec_manifest.yaml:284
```

Mechanically confirmed across all three trees: `DECLARED-BUT-UNUSED =
['cli_artifact_delete', 'cli_download', 'cli_selftest_process']`. The model's
`@port` annotations agree with the rows and not with the ports block — every
`@port` line in `TlaSpecDevCli.tla` names one of the ten pre-existing ports.

**Why this is a gap and not a cosmetic issue.** Three independent rules in this
repository are violated at once:

1. `spec_manifest.yaml`'s own schema note: *"a declared port no case ever
   exercises is DEAD MODEL SURFACE"* — a HARD FAILURE, not a warning. This is the
   exact rule CD-09 used to delete `tlc_process` and CD-11 used to delete
   `AnalyzeCorpus`'s `evidence_report`.
2. `TlaSpecDevCli.tla:214-222`: *"each action's `@port` lines mirror its row in
   `effects.actions`."* Round-2 G-1 was this rule violated in one direction (an
   action with `@port` lines and no row); N-1 is the same rule violated in the
   other (ports that no action's `@port` lines mirror).
3. **`effect_conformance.py:511-518` binds ports to actions strictly through
   `effects.actions`.** A port absent from an action's row is not declared *for
   that action*. So G-9's substance — the `curl` download at
   `install-tlc2.sh:37`, the `mv` unlink at `:38`, the wrapper self-test spawn at
   `install-tla-spec-dev.sh:31` — **is still undeclared on the
   `BuildSkillCli` / `InstallLocalCli` path.** RC-01 wrote the ports, wrote
   correct comments explaining which action path each belongs to, and did not
   attach them.

**Disposition: model it.** Add `cli_download`, `cli_artifact_delete` and
`cli_selftest_process` to the `BuildSkillCli` / `InstallLocalCli` rows in
`specs/current` and `specs/desired_program_model` (and at promotion, to
`specs/program_model` — where the ports are *already* declared against a
14-action manifest, so that tree carries the dead surface with no path to
exercise it at all), and add the matching `@port` lines at `TlaSpecDevCli.tla:239`
and `:256`.

**The sharpest thing about N-1:** it is exactly the defect
`run effect-conformance` is built to catch. `effect_conformance.py:977` emits
`DEAD MODEL SURFACE: port {qualified}` and `:1026-1027` returns
`VERDICT_DEAD_SURFACE`. One oracle run would have found it. See §5.

### N-2 — `generate cases` ships the unconstrained-`--out` class RC-01 fixed three commands for, including a destructive delete. **[major]**

`resolve_evidence_out` was written into `scripts/spec_paths.py` in this commit
and applied to `analyze_architecture.py`, `analyze_complexity.py` and
`architecture_reflexion.py`. It is **not applied** to
`generate_cases_from_tlc_dump.py` — `grep -n resolve_evidence_out scripts/*.py`
returns four sites, none in the generator.

The new `tla-spec-dev generate cases` path therefore performs, at
caller-controlled locations:

| Site | Effect | Declared port | Covered? |
|---|---|---|---|
| `generate_cases_from_tlc_dump.py:96` | `dot_path.parent.mkdir(parents=True)` | `spec_tree` (`**/specs/**`) | **only if `--dot` happens to point under `specs/`** |
| `:116` | `subprocess.run(command, cwd=spec_dir, env=env)` — java/TLC, binary from `--tlc2` | `corpus_process` (`*`) | yes |
| **`:140`** | **`shutil.rmtree(metadir, ignore_errors=True)`**, where `metadir = dot_path.parent / ".tlc-states" / tla_path.stem` | `spec_tree_delete` (`**/specs/**`) | **only if `--dot` happens to point under `specs/`** |
| `:669` | `package_dir.mkdir(parents=True)` | `spec_tree` | **only if `--out` happens to point under `specs/`** |
| `:882-883` | `path.parent.mkdir(...)`; `path.write_text(content)` | `spec_tree` | same |

`--out` is `required=True` with no location constraint
(`generate_cases_from_tlc_dump.py:1153-1157`); `--dot` and `--tlc2` are
unconstrained too. **The `rmtree` is the serious one**: a destructive delete at a
path the caller chooses, on a newly modeled action, declared by a port that
targets a tree the caller need not be in.

**Disposition: change the program** (the disposition RC-01 itself chose for the
identical class in G-2/G-3) — route `--out` and `--dot` through a
`resolve_spec_tree_out` sibling of `resolve_evidence_out`, refusing anything
outside `specs/`. Modelling it instead would mean widening `spec_tree` and
`spec_tree_delete` to `*`, which would weaken two ports that are currently
precise and that `CloseTicket` depends on.

### N-3 — a citation that went stale in the commit that wrote it. **[minor]**

`generate_cases_from_tlc_dump.py:1145-1146`, written by RC-01, reads: *"never saw
the java spawn at :115, the metadir `rmtree` at :139, the package writes at
:881-882"*. The actual lines are **`:116`, `:140`, `:882-883`** — RC-01's own
edits shifted them by one and the docstring was not updated. This is the G-5/G-7
class — a record that contradicts the thing beside it — reappearing one commit
after being closed twice.

**Disposition: model it** (correct the record). Trivial to fix and reported at
its true weight: a one-line inaccuracy. It is listed because the class, not the
severity, is the finding — three consecutive tickets have now shipped a stale
internal citation, which argues for a check rather than more care.

### Reported, deliberately NOT counted as a gap: three ports at target `*`

`cli_artifact`, `cli_download` and `cli_artifact_delete` all now target `*`
(`spec_manifest.yaml:170`, `:182`, `:190`). A `filesystem.write` port at `*`
**cannot express a gap for its action** — the same shape RP-01 refused for
partitions ("a partition that cannot express a divergence cannot yield
`coherent`").

I am not filing it as a gap, and the reason should be on the record rather than
assumed: RC-01 recorded its reasoning at `:155-168`, the reasoning is sound
(`SKILL_MANAGER_BIN_DIR` and `SKILL_MANAGER_CACHE_DIR` are required env vars that
nothing in either script constrains), it follows a precedent the manifest already
carries for `corpus_process`, and the schema has no variable interpolation with
which to write anything narrower. `*` is honest where `**/.venv/**` was a lie.
**But the cost is real and unrecorded elsewhere: two modeled actions can now
write anywhere and no effect-conformance run can ever report a gap for them.** If
the schema ever gains env-var interpolation, this is the first place to use it.

---

## 3. G-5 adjudicated: RC-01 is right and my round-2 finding was overstated

Stated plainly, as asked.

**Round 2 said:** all three `spec_manifest.yaml` files carry a stale "9 variables
and 15 actions" figure for a model with 10 and 16.

**That was wrong for one of the three, and RC-01 is correct.** Measured directly
from the modules at `05acf8c`'s parent:

| Tree | Variables | `Next` disjuncts | Round-2 claim | Correct? |
|---|---|---|---|---|
| `specs/current` | 11 (was 10) | 18 (was 16) | stale — **right** | ✅ my finding held |
| `specs/desired_program_model` | 11 (was 10) | 18 (was 16) | stale — **right** | ✅ my finding held |
| **`specs/program_model`** | **9** | **15** | stale — **WRONG** | ❌ **its figure was correct** |

`specs/program_model` is the accepted baseline; it predates AC-01 and contains no
`architecture_scan` and no `AnalyzeArchitecture`. **Its "9 variables and 15
actions" described the module sitting beside it accurately.** I compared all
three manifests against one model's figures instead of against each manifest's
own module — the identical error class I have been filing against others all
epic, committed by me, in the report that filed them.

RC-01's fix is better than the one I proposed. I suggested updating three
comments; RC-01 shipped `tests/test_spec_manifest_records.py`, parametrized over
all three trees, which parses the module beside each manifest and asserts
`variables`, `Next` disjuncts and `@command` count agree — and it "cannot be
satisfied by copying one number into three files." That converts the class from
"found by targeted reading" to "checked mechanically", which is what round 2's
own attestation asked for and did not expect to get.

**Round 2's G-5 is hereby corrected in the record: it was two-thirds right.**

---

## 4. Re-classification and the surface

**Enumeration (re-run at `05acf8c`):**

```bash
git ls-files '*.py' '*.sh' '*.kt' '*.kts' '*.java' '*.j2' | sort > round3/sweep1-surface.txt
wc -l < round3/sweep1-surface.txt     # 6,104   (round 2: 5,998 — +106, of which
                                      #          6 are live source, 100 archived)
python3 round3/cac_ac_classify_v3.py
```

**N = 6,104; M = 6,104; `N == M` ✅** (asserted in-script).

| Class | Rows |
|---|---|
| IN MODEL | **40** (34 `scripts/*.py` + 6 spec adapters) |
| out-of-model (inventory) | 6,064 |
| **ESCALATION** | **0** |

**Zero escalations.** No filter was applied this round — `specs/.history/**` is
enumerated and dispositioned by plan line `:277` rather than dropped by an
auditor's `grep -v`, which was round 1's ESC-5 and round 2's standing caveat.
The scope completions at `:273` (adapters), `:281` (`specs/tickets/**`) and
`:282` (`specs/results/**`) answered round-2 ESC-9, ESC-8 and ESC-10; the ruling
(2) rewrite at `:45-60` answered ESC-11.

**In-model surface = 52 files** (40 `.py` + 12 non-source: three
`TlaSpecDevCli.tla`, three `spec_manifest.yaml`, three `MC.cfg`, three
`MCsmall.cfg`). **All 52 read. 0 inferred.**

Effect sweep restricted to the in-model surface (`round3/effects-*.txt`):
filesystem 240, subprocess 107, network 10. **Real destructive in-model sites: 7**
— `spec_evolution.py:154/:385/:477` (declared, `spec_tree_delete` on
`CloseTicket`), `close_spec_workflow.py:49` and `close_tickets.py:127/:232`
(inventory `:83-96`, no modeled action performs them), and
**`generate_cases_from_tlc_dump.py:140` — now on a modeled action path, at a
caller-chosen location (N-2).** The only change in this category since round 2 is
that the generator's `rmtree` moved from unmodeled surface to a modeled action
with an under-constrained port.

---

## 5. Does `generate cases` make the effect oracle reachable?

The coordinator called this the single most useful thing available this round.
**Answer: it converts the limit from structural to operational. It does not lift
it, and the distinction is load-bearing.**

**What changed.** Before RC-01, `build_parser` never referenced
`generate_cases_from_tlc_dump`, so an import-closure walk of the shipped CLI
never reached case generation at all — round 2 confirmed this mechanically (14 of
34 modules unreachable, the generator among them). There was **no path through
the shipped CLI to produce a corpus for this model**, and therefore no path to
run the effect oracle against it. That was structural.

Now `tla-spec-dev generate cases <tla> <cfg> --out …` exists, registers the
generator's own arguments rather than a drifting copy, and is modeled.

**What has not changed.** All three manifests still carry
`case_codegen.generation_status: planned`; `state_fields`, `actions` and `ports`
are still empty placeholders; `specs/current/generated/` and
`specs/desired_program_model/generated/` **do not exist**; and
`git ls-files 'specs/*/generated/*'` returns nothing. **No corpus exists, so the
effect oracle still has never executed against this model.** Every `declared`
verdict in this report remains a declaration that has never been checked against
an observation.

**N-1 is the proof, and it is a clean one.** `effect_conformance.py:977` emits
`DEAD MODEL SURFACE: port {qualified}` for a declared port no case exercises, and
`:1026-1027` makes it a hard verdict. Three such ports were introduced in this
very commit. **One run of the now-reachable oracle would have caught the gap that
the now-reachable oracle's unreachability allowed.** That is the whole thesis of
this gate in one commit: the four oracles are bounded to what is modeled *and to
what is executed*, and coverage is not the same as either.

**The single most useful thing the next ticket can do is run it** — generate a
corpus for `specs/current`, flip `generation_status`, and let
`run effect-conformance` execute once. Round 2 said a dead port survived four
audits because no oracle ran; round 3 shows a fourth dead port arriving three
audits later by the same mechanism.

---

## 6. The two specifics, verified independently

### 6.1 The guard-flag invariants — **CONFIRMED, by reproduction, not by reading**

RC-01 reports that modelling the guard flags immediately cost five invariants,
that stage 6 is the highest ordinal so every `>=` reader answered TRUE for it,
that `SpecUnitTestsRequireMeasuredCorpus` was violated in 1,094 states, and that
`ClosedTicketsPassedSpecUnitTests` had been true by accident of the encoding.

**I did not take this from RC-01's evidence.** I copied the shipped module to a
scratch tree, reverted RC-01's helper to the pre-RC-01 encoding — the only edit —
and ran TLC on both:

```
TicketReached(t, stage) == ticket_state[t] \in stage..TicketClosed   # shipped
TicketReached(t, stage) == ticket_state[t] >= stage                  # reverted
```

| Run | Result |
|---|---|
| **Reverted (`>=`)** | **`Error: Invariant SpecUnitTestsRequireMeasuredCorpus is violated.`** exit 12, at 879 states generated / 560 distinct |
| **Shipped (`stage..TicketClosed`)** | **No error.** 3,678,218 generated / 118,573 distinct / depth 16, 5s |

I also re-ran the full `MC.cfg` model check from scratch rather than reading
RC-01's number. **It reproduces the headline exactly: `392,923,694 states
generated, 10,331,543 distinct states found, 0 states left on queue`, depth 26,
no error, 11min 22s** (RC-01 reported 10,331,543 / depth 26 / 11m16s). The
9.53× bound growth and the 7.99× distinct-state growth at **unchanged depth 26**
are confirmed. Raw:
`round3/verify-tlc-shipped-encoding-mc.txt`,
`round3/verify-tlc-shipped-encoding-mcsmall.txt`,
`round3/verify-tlc-reverted-encoding-mcsmall.txt`,
`round3/verify-tlc-reverted-encoding.diff` (the one-line revert).

The counterexample TLC produced is exactly the mechanism claimed:

```
tla-spec-dev open ticket           ticket_state = (cli_entrypoint :> 1)   corpus_gate = "unknown"
tla-spec-dev close ticket --accept-new
                                   ticket_state = (cli_entrypoint :> 6)   corpus_gate = "unknown"
```

With `>=`, a ticket at `TicketClosedWeakened` (6) satisfies
`>= TicketSpecUnitTestsPassed` (4), the invariant's antecedent fires, and
`corpus_gate /= "unknown"` is false. **A ticket closed under `--accept-new`
without any corpus ever being measured was being counted as a ticket that passed
spec-unit tests.**

Five invariants carry the fix — `CurrentRequiresDesired`,
`SpecUnitTestsRequireCurrent`, `SpecUnitTestsRequireMeasuredCorpus`,
`SpecUnitTestsRequireMeasuredEffects`, `ClosedTicketsPassedSpecUnitTests` —
matching the claim of five. **What I did not confirm** is the precise figure
*1,094 states*: TLC halts at the first violation, so reproducing a count requires
a continue-mode run I did not do. The violation, the mechanism, the identity of
the invariant and the count of affected invariants are all confirmed; the state
count is RC-01's and is not independently checked.

**My read: this is the strongest single piece of evidence in the epic, and
stronger than the framing suggests.** The claim is usually stated as "modelling
the flags cost five invariants." The accurate statement is worse and better at
once: **`ClosedTicketsPassedSpecUnitTests` was not merely fragile, it was true
for the wrong reason.** It held over 1,292,951 states because the program's
bypass was not in the state space at all — not because the bypass was safe. The
round-2 reservation said "no oracle can see the difference"; modelling the
difference made TLC see it in under six seconds on a reduced config. **A
1,292,951-state proof of a property the program has a documented flag to violate
is exactly the "invisible to all four gates" defect this gate was built for, and
this is the first time in the epic it has been demonstrated rather than argued.**

### 6.2 The emergent-decomposition flip — **a CORRECTNESS problem, not a coverage one; and RC-01 was right to file it**

Confirmed at the tip (`specs/results/rc01-architecture-current.txt:30-38`):

```
graph modularity Q = 0.012
[OK  ] component_count: measured 2, rule >= 2
[OK  ] modularity_q: measured 0.011605, rule > 0
MEASURED RESULT: the partition is a cut -- every criterion above is met.
```

**Coverage or correctness?** **Correctness — in `analyze_architecture.py`'s
criterion, not in the model's coverage of the program.** The flip changes nothing
about what `TlaSpecDevCli.tla` represents, so this gate correctly does not fail
on it, and I have not counted it as a gap.

**But it is not therefore harmless to this gate, and I would not file it as
merely a threshold that is set too low.** Three sharper points:

1. **The criterion is `> 0`, so it cannot fail.** Any partition with the faintest
   positive modularity passes. Q = 0.0116 is ~26× below the Newman threshold the
   tool itself prints. A criterion that admits everything measures nothing — the
   same structural objection RP-01 sustained against a partition that cannot
   express a divergence, and AC-02's `unfalsifiable_coherence` guard does not fire
   here because two components *can* technically express one.
2. **The trigger is the finding.** Nothing was tuned; one variable was added. So
   the criterion is sensitive to **model size** rather than to **structure** —
   which is a stronger and more damaging statement than "the threshold is low",
   because it means the verdict can be moved by any ticket that adds state,
   including a ticket whose whole purpose is to add state.
3. **It lands on an input this gate's siblings consume.** AC-01's recorded finding
   was that this repository "does NOT yield a usable architecture"; AC-02
   published `consumable_as_architecture = false` so the reflexion check would say
   `unmappable` rather than a false `coherent`. That refusal is now bypassed by
   arithmetic. AC-02's own caution — *"a merely COARSE partition still reports a
   real-looking clean"* — has become live on this repository.

**RC-01 was right not to retune it.** Changing a threshold inside the same delta
that moved the measurement destroys the measurement, which is this epic's
standing rule (EV-02: "findings are filed, never fixed inline — fixing inline
destroys the measurement"). Filing RC-01-DF-01 as `major` against
`scripts/analyze_architecture.py` is the correct disposition, and the honest
label for the successor to inherit is: **`modularity_q > 0` is not a criterion,
it is the absence of one.**

---

## 7. Round-2's own limits, re-checked

Asked for directly. Two of four moved; two did not.

| Round-2 limit | Round-3 status |
|---|---|
| **Sweeps 2/3 never run over YAML/TLA/CFG; four of nine gaps were manifest defects found by targeted reading** | **Partly fixed, and not by me.** RC-01 shipped `tests/test_spec_manifest_records.py`, parametrized over all three trees, which parses each module beside its manifest and fails on disagreement — that converts the *count* class to a mechanical check. I also swept all 12 in-model non-source files this round (0 inferred). **The limit is narrowed, not closed, and N-1 is the proof: it is a manifest defect, in an in-model file, in the same commit, and nothing shipped caught it.** I found it with a script I wrote for this report. A port-to-action consistency check belongs beside the count check. |
| **No oracle has ever executed against this model** | **Unchanged in fact; changed in reachability.** See §5. |
| **86% of rows dispositioned from path** | **Not applicable any more, and I will not claim credit for that.** Rows needing a coverage judgment are the 52 in-model files; all 52 were read. The other 6,064 are classified from path against an explicit glob, which is classification, not coverage. The ratio improved because the plan shrank the surface, not because I read more. |
| **Escalations left 121 rows unclassified** | **Closed. 0 escalations, 0 unclassified rows.** |

---

## 8. Dispositions

### 8.1 In-scope gaps — HARD, block promotion (3)

| # | Gap | Disposition | Remediation (advisory) |
|---|---|---|---|
| **N-1** | Three ports declared, referenced by no action row, in all three trees — dead model surface, and G-9's effects still undeclared for the actions that perform them | **model it** | Add the three ports to the `BuildSkillCli` / `InstallLocalCli` rows and add matching `@port` lines |
| **N-2** | `generate cases` writes and **deletes** at caller-chosen locations against ports targeting `**/specs/**` | **change the program** | A `resolve_spec_tree_out` sibling of `resolve_evidence_out`, applied to `--out` and `--dot` |
| **N-3** | `generate_cases_from_tlc_dump.py:1145-1146` cites `:115`/`:139`/`:881-882`; actual `:116`/`:140`/`:882-883` | **model it** (correct the record) | Fix the three numbers; consider a check, since this is the third consecutive ticket to ship a stale internal citation |

### 8.2 Out-of-model inventory — does not gate

6,064 source rows against `:275-282`; plus the External view (83 of 93 items,
`:253`), the 72 non-guard CLI options (`:61-75`, `:255`), the wrapper/close/start/scaffold
scripts and advisory internals (`:83-96`), and `specs/.history/**` (`:277`). The
six guard-weakening flags **left inventory this round** — they are modeled, and
§6.1 is what that bought.

### 8.3 Escalations

**None.**

---

## 9. Verdict

- In-scope gaps: **3** — N-1, N-2, N-3, all created by RC-01
- Escalations: **0**
- **Verdict: `fail`**

`fail` because three in-scope gaps exist and there is no fourth disposition. It
should be read alongside what it replaced: 12 gaps and an unusable scope in round
1, 9 gaps and 121 unclassifiable rows in round 2, **3 gaps and nothing
unclassified** now. Nine of nine round-2 gaps were addressed, eight fully, one
(G-9) in half — and every one by `model it` or `change the program`, with no
justification, no accepted risk and no waiver anywhere in the closure record.

**The remaining blocker is a modeling gap, not a coverage limit.** N-1 and N-3
are closed by editing declarations; N-2 by a fifteen-line change to the program.
None is "I could not see this."

**One coverage limit persists and it is the same one:** the effect oracle has
still never executed against this model. It is now *reachable* — that is real
progress and it is RC-01's — but reachable is not run, and N-1 is a port-with-no-
site that a single run would have caught, arriving in the very commit that made
running it possible.

The proposed ledger block is at
`.../round3/coverage_audit_ledger_input_proposed.yaml` and is **not applied**.

---

## 10. Attestation

1. **Row counts.** Sweep 1: N = M = 6,104, asserted in `cac_ac_classify_v3.py`.
   In-model: 40 `.py` + 12 non-source = 52, all read, 0 inferred. Effect sweeps
   over the in-model surface: filesystem 240, subprocess 107, network 10; raw
   files in `round3/`. Rounds 1 and 2 raws are unmodified — `git diff` over them
   is empty — so all three rounds remain diffable.
2. **Surface not walked.** Non-source files outside the 12 in-model ones (JSON,
   TOML, remaining YAML, `.tla` under `examples/**`) were not swept; all are
   out-of-model by plan line. **No code was executed except TLC** — the effect
   and behavior findings remain pattern-derived.
3. **Read vs inferred.** 52 of 52 in-model rows read. 6,064 out-of-model rows
   classified from path against an explicit glob — classification, not coverage.
4. **Scope decided by reasoning rather than a quoted line:** none. Zero
   escalations, and no filter was applied.
5. **Reproducible?** Yes for row sets (`cac_ac_classify_v3.py` over
   `round3/sweep1-surface.txt`) and yes, unusually, for the central verification:
   the §6.1 TLC reproduction is a two-line recipe anyone can repeat.
6. **Findings about the prompt.** Round 1's and round 2's stand. Round 3 adds
   one, and it is the important one: **`prompts/coverage_audit.md` has no
   procedure for auditing a remediation.** It assumes a model and a program that
   have not just been changed *in response to it*. Two of this round's three gaps
   are in surface the remediation created, and one of them (N-1) is the same
   class the remediation was closing. Nothing in the prompt says "sweep the fix as
   surface"; the coordinator had to say it. It should be Step 8: **a remediation
   commit is new program surface and is swept as such, not verified against its
   own account of itself.** Had this round audited RC-01's claims instead of the
   tree, it would have reported `pass` — every claim RC-01 made is true, and three
   gaps would have shipped.
