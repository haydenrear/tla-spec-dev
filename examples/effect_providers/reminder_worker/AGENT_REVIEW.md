# EP-06 agent review: reminder worker

## Outcome

The repeatable validation passed under run id `agent-ep06-reminder-v2`:

```sh
python3 examples/effect_providers/reminder_worker/validate.py \
  --run-id agent-ep06-reminder-v2
```

The common-schema result is
`evidence/validation-runs/agent-ep06-reminder-v2/result.json`. The shared
validator accepted it without qualification. The run completed in 6.254670
seconds and produced 824 KiB across 128 files. Its measured results were:

| Check | Result |
| --- | ---: |
| Generated cases | 14 (7 internal, 7 external) |
| Control points | 175/175 |
| Distinct concretization seeds | 175 |
| Fixed mutants killed | 12/12 |
| Exact first-failure replays | 12/12 |
| Clean point teardowns | 271/271 |
| External CLI cases | 7/7 |
| Focused tests | 7/7 |
| Active provider points after campaign | 0 |
| Hand-written baseline | 8/12 mutants killed |

The 271 cleanup checks account for 175 controls, 84 mutant points (all twelve
mutants ran one complete seven-case iteration), and 12 one-case replays. The
generated/effectful cases found four bugs missed by the four-scenario hand
baseline: RW-03, RW-04, RW-11, and RW-12.

Both regenerated TLC models completed well below the 120-second bound. Internal
and External each generated 14 distinct states at depth 2 in 0.926217 and
0.869145 seconds respectively. Regeneration as a whole took 1.906325 seconds;
the real CLI rung took 0.495759 seconds and the focused tests took 0.696478
seconds.

The failed `agent-ep06-reminder-v1` evidence is intentionally preserved. It
showed that all controls, mutants, replays, cleanup, and TLC work were already
green, but external capability enforcement correctly rejected the declared
`process` channel. The adapter actually invokes a command-line program, so all
seven mappings now declare the built-in `cli` channel. An isolated rerun then
validated seven mappings and executed seven cases before v2 was launched.

The existing EP-03 evidence corpus was checked against a pre-change SHA-256
manifest and remained byte-identical. The v1 validation tree also retained the
same aggregate digest before and after v2. A second invocation with the v2 run
id exited immediately with `refusing to overwrite existing evidence`.

## Generated signature correction

EP-05's strict runner checks the exact generated Protocol surface, including
parameter names, kinds, resolved annotations, and returns. Its preflight found
that the project bindings used `_command: Any`; the generated ports require a
parameter named `command` with a generated command type. The generated contract
was correct and did not change. The project bindings now match it exactly:

- `ClockBinding.now(command: ReadClock) -> int`
- `QueueBinding.claim(command: ClaimJob) -> object`
- `QueueBinding.acknowledge/release/dead_letter(command: QueueMutation) -> None`
- `OutboxBinding.lookup(command: LookupOutbox) -> object`
- `OutboxBinding.stage(command: StageMessage) -> None`
- `OutboxBinding.mark_sent(command: MarkSent) -> None`
- `NotifierBinding.send(command: SendMessage) -> str`

A focused conformance test walks every method on all four generated Protocols,
so a future generated/binding drift fails before a campaign is scored.

## Cost and benefit

The semantic gain is real: seven generated outcomes plus provider-owned
assertions raised the fixed mutation score from 8/12 to 12/12, while 175
different Unicode/message/time/receipt/exception bundles stayed green and
replayed exactly. The CLI rung also demonstrated that terminal semantics survive
a child-process and file-persistence boundary.

The cost is also substantial. The current project has 258 lines of TLA+, 21
lines of projection, 107 generated contract lines, 339 provider lines, 109
adapter lines, and 325 application/CLI lines. EP-06 added roughly 704 lines and
removed 25 before this review: 546 lines for the repeatable validator, 69 lines
for the usage descriptor, 24 lines for signature conformance, and smaller
run-local generation, work-directory, external-import, mapping, and README
changes. The pre-existing experiment driver itself is 747 lines. This is a
high-value example, but not yet a low-authoring-cost user experience.

Fuzz breadth did not improve mutant discovery in this catalog. Every mutant was
killed in iteration zero, so iterations 1-24 prove that more representatives do
not break a correct implementation; they do not show an additional bug found by
later data. Future value claims should separate semantic-case gain (+4 mutants
here) from incremental fuzz-data gain (0 mutants here).

## Oracle ownership

TLA+ owns the seven abstract outcomes, expected output, terminal queue/outbox/
notification/receipt/result projection, and the delivery invariant. It does not
select concrete recipients, times, receipts, or exception subclasses.

The user-owned provider currently owns more than concretization. It creates one
correlated bundle, chooses the concrete success or exception response, checks
payload identity and per-port cardinality, maintains a cross-port journal,
asserts `stage < send` and `send < mark < acknowledge`, projects concrete state
back to TLA fields, and manages reverse-order cleanup.

The passive/external layer owns bypass and integration evidence. A socket guard
can observe and block a direct-network attempt, while direct `datetime` access
is confirmed to bypass `ClockPort`. The CLI rung uses real file-backed queue and
outbox behavior but separate clock/notifier doubles; it validates terminal
semantics, not identity with the in-process provider implementation.

This division confirms the suspected weak spot. Terminal TLA cases are not rich
enough to generate the provider behavior by themselves. `providers.py` manually
maps scenario names to response classes, cardinality, order, and projection.
The global `_POINTS` registry and synthetic `__reminder_bundle__` seed are also
project machinery needed to correlate four independently bound ports. A model
could encode every call and response, but doing so directly would turn a compact
state machine into a brittle call script.

## Recommendations

1. Keep the framework contract generic and providers user-owned. Do not promote
   these concrete reminder adapters into a library from one example.
2. Generate an abstract effect expectation per case, not a concrete mock script.
   TLA annotations or projection metadata should be able to state operation,
   symbolic response class, cardinality, partial-order constraints, and relevant
   state delta. The provider would map those symbols to fuzzed concrete values
   and concrete exception subclasses. This removes duplicated semantic rules
   without enumerating a response for every fuzz value.
3. Add a framework-level signature preflight for every generated port/provider
   binding. This run caught a real mismatch before application execution; the
   check is generic and much cheaper than discovering it during a campaign.
4. Add an explicit point-local shared scope to `EffectProviderContext`, with a
   cleanup stack and stable point identity. That would replace `_POINTS`, manual
   four-binding reference counting, and ad hoc correlated seeds while preserving
   independently pluggable ports.
5. Add collect/continue and shrinking, then use data-dependent mutants. Until a
   later representative kills something iteration zero misses, describe the
   25-iteration schedule as robustness coverage rather than bug-finding lift.
6. Make bypass policy a separate, opt-in passive layer. Explicit injection cannot
   police direct clocks, sockets, brokers, databases, filesystems, threads, or
   child processes; the result should report which boundaries were guarded.
7. For external and future Java adapters, exchange generated case JSON plus a
   normalized semantic result/effect trace. Keep language entrypoints thin and
   compare that trace to the same abstract expectations. This avoids trying to
   reuse Python monkey patches across runtimes while retaining one oracle.
8. After the other two EP-06 examples confirm the common shape, factor the 546-
   line validation orchestration into a shared runner driven by small project
   callbacks/configuration. Preserve run-local generation, immutable evidence,
   exact-interpreter replay, and the real external rung as non-negotiable gates.

The evidence supports continuing Python-first. It does not yet support calling
the design the gold standard: the adapter boundary is viable and valuable, but
effect response semantics and cross-port state still require too much duplicated
project code. Abstract generated effect expectations plus a framework-owned
point scope are the two changes most likely to make the approach simple enough
to earn its keep before a Java implementation is added.
