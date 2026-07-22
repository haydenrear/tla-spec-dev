# Legacy payment HTTP effect experiment

This project measures the difficult monkey-patch shape from
[`../PREREGISTRATION.yaml`](../PREREGISTRATION.yaml): a legacy application owns
`requests.Session`, while a project provider self-installs a bounded
`Session.send` override for each TLC-derived case/iteration. It is an experiment,
not a claim that Python monkey patches universally intercept networking.

## Semantic boundary

`Internal.tla` fixes one of seven outcomes plus the expected decision, reason,
reference class, and attempt count. Its finite inputs produce 56 generated cases
(seven outcomes × two payment ids × two amounts × two idempotency keys). The
provider may choose only concrete representatives inside that semantic outcome:
502/503/504, timeout subclass, JSON layout, response-header casing, malformed
bytes, and opaque authorization-reference bytes. It never rewrites a case.

The application is [`legacy_payment_http_app/application.py`](legacy_payment_http_app/application.py).
The typed `PaymentHttpPort` protocol shape is regenerated from
[`spec_manifest.yaml`](specs/program_model/spec_manifest.yaml). The project-owned
provider and case adapter are
[`provider.py`](payment_effects/provider.py) and
[`adapters.py`](payment_effects/adapters.py). The latter classifies the exact
concrete authorization reference back to the TLA `opaque` class; that visible
two-sided refinement is this design's main duplication cost. This legacy
monkey-patch provider deliberately self-installs and binds `None`; it does not
implement `PaymentHttpPort.send`. The test checks that the generated runtime
protocol shape is available, not provider-to-port conformance.

`External.tla` has the same seven public outcomes. Its adapter starts a real
loopback HTTP server and drives the application in a child Python process; it
does not import the production package in-process. This checks that the internal
patch experiment still has a real-HTTP conformance rung.

## Commands

Run from this directory. A workspace-local cache avoids dependence on an agent's
home-directory permissions.

```bash
export UV_CACHE_DIR=/private/tmp/legacy-payment-http-uv-cache

uv run --project . python scripts/regenerate.py \
  --tlc2 /Users/hayde/.skill-manager/bin/cli/tlc2

uv run --project . python -m unittest discover -s tests -v

uv run --project . python ../../../scripts/run_generated_case_adapters.py \
  generated/testgraph/payment_http_external_cases \
  --mapping specs/program_model/testgraph_bindings.yml \
  --spec-dir specs/program_model --import-root . --view external --batch
```

Run the two preregistered local repetitions only after reviewing the immutable
catalog and campaign gates:

```bash
uv run --project . python scripts/run_experiment.py \
  --label my-local-repetition-1 \
  --output evidence/my-local-repetition-1.json \
  --tlc2 /Users/hayde/.skill-manager/bin/cli/tlc2

uv run --project . python scripts/run_experiment.py \
  --label my-local-repetition-2 \
  --output evidence/my-local-repetition-2.json \
  --compare-to evidence/my-local-repetition-1.json \
  --tlc2 /Users/hayde/.skill-manager/bin/cli/tlc2
```

Labels must be new because raw evidence directories are append-only.

Use the same command with a new `--label fresh-checkout` in a clean checkout.
The runner regenerates cases first, audits every forbidden framework surface
against preregistration commit `141e63b`, refuses a red/incomplete control before
mutants, and executes all 56 × 32 control points. A killed mutant stops after
the first complete failing iteration (56 points at iteration zero in the
accepted runs); only a survivor executes all 32 mutation iterations. Each first
failure must replay with a nonzero exit, the same structured failure, and the
same one-point transcript. Compressed raw transcripts and diagnostics are
preserved under `evidence/raw/<label>/`.

The ordinary four-scenario hand baseline is reported separately. Alternate
HTTP-client and raw-socket probes are also separate and unscored: they prove
those paths bypass `Session.send`; the provider's socket guard blocks and reports
them, so this binding remains compatibility-only even if all scored mutants die.

Machine-readable results are authoritative. Survivors, mismatched detector
attribution, missing transcripts, cleanup leaks, successful outbound sockets, or
forbidden framework changes produce `no_go`; the runner never edits the model,
catalog, seed, thresholds, or framework to improve a score.

## Measured results

The two accepted post-review local repetitions are
[`evidence/reviewed-local-repetition-1.json`](evidence/reviewed-local-repetition-1.json) and
[`evidence/reviewed-local-repetition-2.json`](evidence/reviewed-local-repetition-2.json). Both are
`go`:

- TLC produced 56 complete cases from 57 states at depth two for each of the
  internal and external models. Every one of the seven semantic actions owns
  eight generated cases; no shared helper action collapsed their identity.
- Each control executed all 56 cases over 32 iterations: 1,792 unique points,
  256 executions per outcome, with zero false positives, patch leaks, or
  outbound socket attempts.
- The concrete representatives covered HTTP 502/503/504, both `ConnectTimeout`
  and `ReadTimeout`, four JSON layouts, and three response-header casings.
- PH-01 through PH-12 were killed by their preregistered detectors with nonzero, structured, transcript-exact replay.
  PH-05 first fails on retry attempt two, faithfully preserving the initial idempotency key.
- Repetitions share transcript digest `38c0395b3378b434c01bc727cd22015950d73319939de7f130fb5f96d5ebbf93`,
  mutation-verdict digest `480ad8756ce48bf74baf1fb8e310d2c432f9d9fc399bdb08c846c0d0d6ea1cdf`, and full
  mutation/replay/baseline/probe digest `f821371693993fd1293694118333d66c25c7e545b3227cfc3879a38c4a590062`; JSON binds
  application/provider/adapter/scorer/baseline/probe sources and proves they stayed unchanged.
- All 56 generated external cases passed through the real child-process and
  loopback-HTTP rung; the concise machine-readable record is
  [`evidence/external-validation.json`](evidence/external-validation.json).

The four-scenario hand-written baseline also killed all 12 mutants. For this
catalog, the generated effect campaign therefore adds no mutation-score delta.
Its measured value is instead systematic model coverage, deterministic
representative variation, visibility of the generated protocol shape, isolation
proofs, and exact replay. It does not establish that the self-installing provider
implements the generated port. A follow-up catalog should deliberately include bugs
that require cross-product cases or representation variation if incremental
bug-finding over a strong hand baseline is the claim under test.

The compatibility probes found the expected weak boundary: `urllib` and a raw
socket both bypass `Session.send`. The socket guard blocked both attempts, but a
monkey-patch provider is still compatibility-only; explicit injection or
process/network isolation is the stronger boundary for new code.

## Experiment-informed improvements

1. Keep TLA+ at the semantic level (approved, declined, transient, timeout,
   malformed) and keep concrete response bytes, exception subclasses, casing,
   and status representatives in the provider. Generate the typed port and
   adapter obligations, not a complete wire emulator from TLA+.
2. Generate or centralize the refinement hook that maps provider-owned concrete
   values such as authorization references back to model classes. The current
   exact-value handoff between provider and adapter is small but duplicated.
3. Add collect/continue support to the effect runner. V0 stops after the first
   killing iteration, so a killed mutant proves one complete 56-case iteration
   plus exact replay; only survivors execute all 32 mutation iterations.
4. Preserve the virtualenv interpreter in recorded replay commands. The current
   shared runner resolves its symlink, so this project must pass the active
   dependency site-packages as an explicit import root.
5. Treat method-level monkey patches as declared compatibility surfaces and add
   a standard bypass probe/process-isolation option. That makes interception
   limits visible instead of silently presenting a partial override as complete.

Two failed harness attempts and the two pre-review scored runs are retained
under `evidence/raw/` and explicitly marked unscored; none contributes to the
accepted results. See [`evidence/SUPERSEDED.md`](evidence/SUPERSEDED.md).
