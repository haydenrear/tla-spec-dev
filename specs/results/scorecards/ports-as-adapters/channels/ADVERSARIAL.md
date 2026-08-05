# The fresh adversarial channel — PA-06

One agent, dispatched with this round's headline claims and told to break them.
Its brief: *"a finding that makes the round's headline worse is worth more than
one that confirms it"*, **FILE FINDINGS, FIX NOTHING**, and *"prefer a measured
demonstration to an argument"*. It edited nothing under `examples/validation/`,
`scripts/`, `measure/`, `arms/`, `blind/` or any arm tree; every experiment ran
in copies.

**It returned 12 findings, 5 of which changed `RESULTS.md`, 2 of which corrected
numbers this ticket had already written down, and 1 of which is the most
important methodological result in the round.** It is reproduced here in full
because a channel's value is in what it tried, not only in what it found.

---

## FINDINGS

### AD-F1 — "88 of 88 identical" is entailed by the re-anchoring, not measured about detection *(major)*

Exhaustive observational fingerprint: **every command sequence of length 4 over a
13-action alphabet — 28,561 sequences, 2 tenants, quota 2 — with the full
projection taken after every step, on each arm's own mutated tree.**

- Clean trees: identical on all three.
- Mutated trees: **identical on 10 of 11 rows across arm A, arm B and arm C.**
  Only `M07` on arm B differs.

Two trees with the same observational fingerprint cannot be told apart by any
black-box instrument, so the identity of the verdict tables is a **consequence of
the re-anchoring succeeding**. The experiment can only produce a divergence where
the re-anchoring *fails* — which is exactly and only what happened.

The rival explanation, that the trees are simply too similar, is **measured
false**: 78 against 151 against 202 code lines, `dict[str, bool]` against `set`
for `closed`, plain tuple against dataclass against derived computation for a
held reservation.

### AD-F2 — the strictly comparable denominator is 20% smaller than the evidence supports *(major)*

The exclusion of `{M07, M08, M10}` rests on the syntactic rule "not the same
diff" (`seeded_by = addition` on arm B for M08 and M10). AD-F1 measures M08 and
M10 to be **the same experiment on all three arms**. Under the measured rule the
comparable set is 10 of 11 rows: **80 of 80 identical on every pairing**, with
arm A and arm B differing only on `M07`'s `corpus-neg` and `corpus-slice-led`
cells.

### AD-F3 — no port-scoped column has a positive control capable of being green, and the cause is the projection *(blocking for every port number)*

```
cd <scratch>/specs/corpus-port/spec-unit && python3.14 -c \
"import sys,collections;sys.path.insert(0,'.');from quota_port.cases import CASES;\
print(collections.Counter(frozenset(c.after) for c in CASES))"
# -> {frozenset({'closed','committed','ledger'}): 1855}
```

**All 1,855 port cases compare an `after` of exactly `{closed, committed,
ledger}`.** `M07`'s only observable is `available`; `PA-M14`'s is the recorded
amount `amt`. Neither is compared. So the `294 accepting Reserve cases executed`
witness in every `control_red` entry is true and **is not the operative fact**.
This is `PA-03-DF-02` / `PA-03-DF-03` / `PA-04-DF-01`, all three deferred to
PA-06 and not closed by it, while PA-06 produced three more port columns.

### AD-F4 — `PA-M14`'s declared `observable` is false on 3 of the 4 trees it is declared on *(major)*

Declared: *"available(t) is one too low … immediately after an ACCEPTED
reserve."* Measured after one accepted `reserve("t1", 2)`, clean → mutated:

| tree | `available` |
|---|---|
| `reference_ports` (both wirings) | 1 → **1**, and nothing else in the projection moves |
| arm A | 1 → **1** |
| arm C | 1 → **1** |
| arm B | 1 → **0** |

The three trees that STORE `available` deduct the parameter; only arm B, which
DERIVES it, shows the fault in one step. **Every generated corpus case is
single-action, so `PA-M14` cannot be killed by any corpus on the reference, arm A
or arm C regardless of projection.** Corollary: `PA-03-DF-03`'s diagnosis that
`PA-M14` "lands on `available`" is measurably wrong — it lands on `amt`.

### AD-F5 — the accept-path probe cannot fail for a control that is never observable *(major)*

```
python3.14 examples/validation/ab/check_catalogue.py --controls --tree-root \
  --root <copy of arm_c> --catalogue <noop_control.toml> --impl quota_ledger
# NOOP-control   arm_c   HOLDS
#                        invisible until an accepted reserve executes
```

The mutant is `self._next_id: int = 1` → the identical line plus a comment.
Declared `control_role = "positive"`, **it passes.** The probe tests only
"invisible *before* an accepted reserve"; nothing tests "visible *with* one". So
`P07`'s `HOLDS ×3` is not evidence that the control works, and with AD-F4 it is
evidence of the opposite on arm A and arm C.

### AD-F6 — the one diverging cell is "the mutated file was not executed" *(major)*

Separating experiment, run directly against `port_corpus_run.py`:

| arm B tree | wiring=real | wiring=fake |
|---|---|---|
| unmutated | 0 failed | 0 failed |
| `M09` in `file_journal.py` (as catalogued) | **854 failed** | 0 failed |
| the same semantic in `memory_journal.py` | 0 failed | **854 failed** |

Exact mirror, identical count. The cell tracks which side of the port the mutant
sits on relative to the wiring — **which is what this round claims, now
separated from the alternative by a measurement rather than an argument.**

Two costs beside it. `case_adapters.arm-{a,c}-port.toml` declare no `fake =`, so
the `:fake` column on arms A and C is a **byte-identical rerun of `:real`** —
`evidence['corpus-port-swap:real'] == evidence['corpus-port-swap:fake']` for all
11 rows on both arms. And `run_port_swap.py` keeps **no executability accounting
at the mutated-line level**, so it attaches a 294-accepting-`Reserve` witness to
a cell in which the mutant executed zero times.

### AD-F7 — the port-bound corpus scored zero unique kills anywhere in the round *(major)*

In each 8-instrument arm table, **no instrument has a unique kill at all**,
`corpus-port` included. On `reference_ports`: `PA-M11` is killed by
`{action-bound:real, action-bound:fake, port-swap:real, suite-real}`, `PA-M12` by
`{port-swap:fake, suite-fake}`, `PA-M13` by `{suite-fake}` only, `PA-M14` by the
two suite columns only. On every arm, `corpus-action-bound` — the declared
pre-PA-04 world — kills exactly the same set as `corpus-port-swap`.

**`suite-fake` strictly dominates `corpus-port-swap:fake`:** it kills everything
that column kills plus `PA-M13`, which the port corpus misses because
`_project_ledger` takes `parts[0:3]` and a truncated COMMIT line projects
identically. The measured "port reach" result is produced by the four-line
`quota_ledger_fake.py` composition point plus the pre-existing hand-written
suite; the `[ports.*]` mapping machinery adds a **strictly weaker** instrument.

### AD-F8 — `corpus-port` in the 8-instrument table is not port-bound *(minor)*

```
python3.14 -c "import json;d=json.load(open('kill-table-arm-a.json'));\
print(d['controls_on_unmutated_code']['corpus-port']['mapping'])"
# -> case_adapters.map-none.toml
```

It is the port *corpus* through the ordinary action oracle. **No column in the
8-instrument table is port-bound.** The name reads otherwise.

### AD-F9 — `check_catalogue.py` cannot pass on any per-arm catalogue *(major)*

Independently reproduces `PA-06-DF-01`, and adds the mechanism: `REQUIRED_CLASSES`
demands `adapter_internal`, `ADAPTER_IMPLEMENTATIONS` is hardcoded to
`reference_ports/journal_{file,memory}.py`, and no arm tree contains those files,
so checks 6 and 8 are unsatisfiable by construction. It also dates the sealed
certificate: `catalogue-integrity-arm-a.txt` was produced by the pre-PA-01
harness, whose `controls: 1 positive, 1 negative` line no longer exists in the
current output. **Mitigation it insisted on stating:** the load-bearing per-row
checks pass on all three arms, so the numbers *are* re-derivable; it is the exit
code and the sealed record that are not.

### AD-F10 — "reproduces the predecessor cell for cell" holds against one baseline and not the other *(minor)*

Against `eval-suppress/arm-b-repaired-sealed-catalogue.json`: 0 moved. Against
`hexagonal-prompting-rerun/GOAL-catch-bugs/kill-table-arm-b.json`: **1 cell
moved**, `M07 / corpus-slice-led`, `NOT_DECIDABLE → SURVIVED`. Arm A: 0 either
way.

*PA-06's note:* that is the cell `EVAL-SUPPRESS` itself published as moving under
the repaired driver, and PA-03 recorded it too. This round's claim is stated
against **PA-03's sealed tables at `f052d3c`** and is 0 of 88 on both arms
against those. The channel is right that the baseline has to be named, and
`RESULTS.md` names it.

### AD-F11 — the length-match number is measured on a file that is not the prompt arm C received *(major)*

`check_catalogue.py --arms` measures `examples/validation/ab/arm_c/PROMPT.md`
(198 lines, Sections 1–7, no Section 8) and reports +3.8%. The dispatched prompt
carried a working-directory preamble, a run hint, three extra forbidden entries
and a **Section 8** asking for `REJECTED.md` — and arm C did produce one.
**PA-06 did not preserve what it sent.**

*PA-06's action:* the dispatched prompt is reconstructed at
`measure/arm_c_dispatched_prompt.md` and re-measured: **124 unique lines vs arm
A, 1.181 = +18.1%, outside the declared ±10% tolerance, and 4 of 124 lines carry
architectural vocabulary rather than 0 of 109** — two of those four being paths
PA-06 itself introduced (`…/ports-as-adapters/arms/arm_c/` and
`PORTS-AS-ADAPTERS-EPIC.md`). Filed as `PA-06-DF-10`. The channel's secondary
observation is also correct and corrected in place: `arm_c/PROMPT.md` lists
**two** of the three files `PA-01-DF-02` names, not three.

### AD-F12 — the sanitiser's verification cannot catch a leak phrased in its own substitution vocabulary *(major for a blinded round)*

Injected into a copy: *"This is ARM B, the hexagonal treatment arm of the
ports-as-adapters comparison. I was given the HEXAGONAL prompt by HP-02 and
PA-01; the other arm (arm A) got the plain one."*

`make_blind_copies.py` flagged **one** line — on `ports-as-adapters`, the only
forbidden token with no substitution rule. The sentence *"I was given the
structured prompt by `<ticket>` and `<ticket>`; another artifact (this artifact)
got the plain one"* passed **clean**, as did a docstring reading *"this artifact,
produced by the structured prompt."* **Every other `FORBIDDEN` alternative is
substituted before the grep runs, so it cannot fire.** The verification is
vacuous by construction, exactly as `AD-F5` is for the control probe — the same
defect shape, twice, in two scripts written for this round.

Two observations on the real packets: `artifact_U/EVIDENCE.md` and
`artifact_W/EVIDENCE.md` are byte-identical apart from one label cell; and
`seeded_by = addition` appears on `M08`/`M10` in `artifact_T` only, which is a
per-artifact signal in a document the judges read.

---

## WHAT HELD

Recorded because a negative result from an attack is a result.

- **Attack on the arm-C catalogue fails outright.** Every row produces the
  observable it declares. **Zero equivalent mutants.** Nothing is seeded to
  flatter or penalise arm C.
- **The arms are behaviourally identical on unmutated code**, once two genuinely
  unspecified echoes are normalised (`is_closed` on an unknown tenant; the
  reservation-id echo on `commit`/`release`/`close_tenant`). The only clean-code
  disagreements are outside the feature.
- **Determinism holds.** Three runs of `port_corpus_run.py` byte-identical; a
  full independent re-run of `run_port_swap.py --subject arm_b` byte-identical
  to this round's artifact.
- **`PA-M12` dies for the reason claimed.** Could not be made to survive by any
  change the channel would call irrelevant.
- **`check_catalogue.py --arms` passes its own checks**: no arm's content is a
  subset of another's; 0 architectural hits in the on-disk arm C against 44 in
  arm B.
- **The `FORBIDDEN` grep finds nothing in the real blind copies** — 0 hits across
  all three `NOTES.md` and all three `EVIDENCE.md`.
- **An injected harness fault is LOUD.** Renaming `self._journal` to
  `self._ledger_port` in arm B (4 occurrences, no behaviour change) makes the
  fake wiring fail 1,225 of 1,543 cases, because `_seed_journal` falls back to
  writing `ledger.txt` — and `run_port_swap.py` marks the whole column
  `CONTROL_RED` rather than reporting kills. Worth knowing that the fake wiring
  depends on the tree exposing `book._journal`; arm B does, arms A and C do not,
  so their before-ledger is installed by writing the file. **A real per-arm
  asymmetry in how the "same" instrument works, which moved no cell this round.**

## WHAT THE CHANNEL REJECTED

- **Full re-derivation of the three 8-instrument tables.** Hours; substituted a
  byte-exact re-derivation of the cheaper swap table plus cell-for-cell diffs
  against both predecessor baselines (AD-F10).
- **Regenerating the corpora.** The generator is unchanged since PA-03 and the
  corpora are inputs to, not claims of, this round.
- **Attacking the complexity instrument's counting rules.** Recorded as never
  scored, and MF-020 already caveats it. One observation kept: its largest
  separation, `code_lines` 151 vs 78, is between two trees measured to be
  observationally identical — **so it separates verbosity, not architecture, and
  the long prompt produced the shortest code.**
- **Editing the port projection, or seeding a port-region control to see whether
  the columns come alive.** Forbidden by the brief, and it is precisely the
  "repair an instrument after seeing an unflattering signal" move `PA-04-DF-01`
  refuses.
- **Dispatching a fourth arm to test whether the length effect replicates.**
  Outside a channel's remit; that is a new round.
