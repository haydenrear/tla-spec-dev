# Effect-provider contract reduction

Date: 2026-07-22

## Decision

The shipped V0 surface is the generic, agent-authored provider SDK:

- generated repository-specific effect-port Protocols;
- one required `EffectProvider.bind(context)` object interface;
- standard context-manager lifecycle;
- deterministic per-point context, failure evidence, and exact replay;
- fail-closed action, port, provider, and binding resolution.

The framework ships no domain effect implementations. The three projects under
`examples/effect_providers/` are experimental consumers used to measure the
cost and value of repository-owned implementations.

## Prior audit disposition

`specs/results/coverage_audit_report.md` remains the canonical historical
audit, unchanged. Its verdict remains `FAIL` and all twelve hard gaps remain
valid for the audit's exact scope: the complete non-mutant runtime behavior of
the seven listed example application/entrypoint files against each example's
Internal and External models.

That audit explicitly excludes the host EP-01/EP-02 framework runtime and
project provider/helper implementations. It therefore qualifies claims about
the completeness of the three example application models. It does not show
that an arbitrary repository agent cannot implement the generic provider
interface.

No gap is waived, suppressed, reclassified, or counted as SDK coverage.
Repeatable example validation must continue to report:

1. whether the generic provider SDK discovers, scopes, validates, seeds, and
   replays repository providers correctly;
2. the application-specific modeling, assertion, isolation, and entrypoint
   costs;
3. the twelve historical model-completeness gaps until separately resolved.

## Consequence

Framework readiness and example completeness are now separate claims:

- SDK readiness is decided by generic contract and lifecycle tests.
- Example value is decided by repeated, project-local validation evidence.
- Full-application model completeness remains failed until a later ticket
  resolves or deliberately narrows every audited behavior.
