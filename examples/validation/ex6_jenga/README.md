# ex6 — the synthetic Jenga, and why it is the CONTROL and not the evidence

The issue asked for "the enterprise-Jenga example: shared mutable state with no
single writer, every command reaching every module, coordination by polling
rather than protocol state," with its divergences enumerated in advance.

## The decision, and the reason

**The primary Jenga in this epic is real and is not in this directory.** It is
`specs/program_model/TlaSpecDevCli.tla` — this toolchain's own model. Measured
on this branch:

```
$ python3 scripts/analyze_architecture.py specs/program_model/TlaSpecDevCli.tla specs/program_model/MC.cfg
  graph modularity Q = 0.000
  [FAIL] component_count: measured 1, rule >= 2
  MEASURED RESULT: this model DOES NOT DECOMPOSE under this partition.
  Single-writer violations: NOT MEASURABLE (one component)
  architecture_scan = unmappable
```

`lastCommand` and `result` are written by all fifteen commands. Nobody built it
to fail, which is exactly what makes it better evidence than anything written
on purpose. **Use it as the primary incoherent example.**

**So does the synthetic one add anything? Yes — one thing, and only one.** The
real Jenga refuses at the *model* stage under the emergent partition: the
reflexion comparison never runs, so there are no divergences to enumerate and
no answer key to score against. Given its declared four-component partition
(`specs/program_model/architecture_components.yaml`) it does run — and reports
**0 divergences over 263 edges**, a genuine falsifiable negative about a real
codebase, but still not an answer key with known-positive rows.

The synthetic fixture supplies the one configuration neither of those covers:
**a god-state model WITH a declared partition AND a production tree, where the
correct answer is known in advance and is not `coherent`.** That is a positive
test for the `unfalsifiable_coherence` refusal, which is the single mechanism
standing between this epic and a green lie on a codebase with no architecture.
Without it, that refusal is exercised only by unit tests and by one line of the
AC-02 dogfood.

Everything else the synthetic fixture might have offered is worse than the real
one, and it is labelled the CONTROL for that reason.

---

## ANSWER KEY

```bash
cd examples/validation/ex6_jenga
python3 ../../../scripts/architecture_reflexion.py \
  specs/program_model/Jenga.tla specs/program_model/Jenga.cfg \
  --components specs/program_model/architecture_components.yaml \
  --code hub --map specs/program_model/architecture_map.yaml
```

| fact | value |
|---|---|
| `verdict.architecture_scan` | **`unmappable`** |
| blind spot | **`unfalsifiable_coherence`** |
| exit code | 0 |
| convergences | 7 |
| **divergences** | **0 — and this is NOT a clean result** |
| absences | 0 |
| `measured.divergence_detectable` | **`false`** |
| unported pairs | **none** — all 3 pairs are ported |

Model side, declared partition:

```
graph modularity Q = -0.186
[OK  ] component_count: 3
[FAIL] modularity_q: -0.1856          (rule > 0)
[FAIL] crossing_action_fraction: 0.8  (rule <= 0.5)
MEASURED RESULT: this model DOES NOT DECOMPOSE under this partition.

Single-writer violations: auditLog, dirty, lastCommand, status
  -- every variable, written from all three components
```

Model side, emergent partition (no `--components`): one component, Q = 0.000,
`architecture_scan = unmappable`, reason `model_has_no_architecture`.

### The scoring rule

There is nothing to find here, and **the fixture is scored on whether that
absence is reported honestly**:

- **PASS**: the run reports `unmappable` with the `unfalsifiable_coherence`
  reason, and says in words that zero divergences here is a property of the
  declared architecture rather than a measurement of the code.
- **FAIL**: the run reports `coherent`, or reports "0 divergences" as a clean
  result, or presents the 7 convergences as evidence the code respects a
  boundary.
- **FAIL**: the run "fixes" the fixture by declaring a partition under which
  something can diverge. Every partition of this model ports every pair,
  because every action writes every variable; a partition that appears to
  escape that has changed the model.

### The finding this fixture pins, which is bigger than the fixture

`consumable_as_architecture` is **`true` for any DECLARED partition, including
one that fails all three decomposition criteria** — measured here:
`decomposes = false`, `consumable_as_architecture = true`, and the reflexion
comparison ran. That is documented behavior (`analyze_architecture.py:500`: "a
declared partition is consumable because the project named it"), and it is
defensible. But it means the criteria table does **not** stand between a
project and a false clean on the declared path. Only `unfalsifiable_coherence`
does, and by its own documentation it "catches the fully degenerate case only".

**A partition that fails all three criteria AND leaves one component pair
unported would report a real-looking `coherent`.** Nothing in the shipped
surface stops that. Recorded in `PREDICTIONS.md` as degenerate path **DP-2b**
and filed as **EV-01-DF-02**.

---

## Layout

```
specs/program_model/Jenga.tla     4 variables, every action writes all four
                    Jenga.cfg     Ids = {o1, o2}; TLC 441 generated / 166 distinct / depth 8
                    architecture_components.yaml   the honest, useless cut
                    architecture_map.yaml
hub/                the production tree: orders / billing / notify, each
                    importing both others, plus DirtyFlags.poll -- coordination
                    by polling, with no protocol state to wait on
evidence/           descriptor-emergent.txt, descriptor-declared.txt,
                    reflexion.txt, reflexion.json
```
