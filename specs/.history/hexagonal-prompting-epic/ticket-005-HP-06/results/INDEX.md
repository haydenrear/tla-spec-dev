# Scorecards — hexagonal-prompting

scorecard_version 1. See `references/eval_scorecard.md`.

**Never average across examples.** `ex6_jenga` is a deliberately
incoherent fixture and is supposed to score low on D3; averaging it
with `ex4` produces a number about nothing.

| example | arm | D1 bug detection | D2 complexity | D3 modularity | D4 behavior preservation | D5 honesty | total | contested |
|---|---|---|---|---|---|---|---|---|
| ab_quota_ledger | A-control-reference | 0 | 2 | 1 | 2 | 3 | **8**/20 | — |
| ab_quota_ledger | X | 3 | 2 | 4 | 3 | 3 | **15**/20 | — |
| ab_quota_ledger | X | 3 | 2 | 4 | 3 | 3 | **15**/20 | — |
| ab_quota_ledger | Y | 3 | 2 | 2 | 2 | 4 | **13**/20 | — |
| ab_quota_ledger | Y | 2 | 2 | 2 | 2 | 3 | **11**/20 | — |

- **ab_quota_ledger** (20260804-hp06-X-p1): A genuinely ported design whose real-adapter/fake parity is demonstrated rather than asserted (D3=4, verified by running its suite), reaching the refusal class only through the eval's generated negative corpus and never through anything it wrote itself; treat its D1 and D4 numbers as bounded by a positive control that had to be substituted, and do not compare its raw kill count to the other arm's.
- **ab_quota_ledger** (20260804-hp06-X-p2): A genuinely hexagonal implementation whose one port is proved swappable by a real-adapter/fake parity suite asserting literal values (D3=4), but whose own cases were never shown capable of catching anything - all fault-detection and failure-capability evidence is harness-authored, and the artifact records no simplification and no red result of its own.
- **ab_quota_ledger** (20260804-hp06-Y-p1): A correct, unusually self-critical single-module implementation that meets the content-assertion and refusal-class bars for bug detection, but exposes no injectable durable-write port and carries model-derived kill numbers measured under a red positive control -- treat every corpus row for this artifact as a floor and repair Reserve-argument recovery before any D1 comparison between the arms is believed.
- **ab_quota_ledger** (20260804-hp06-Y-p2): A correct, honest, conventionally-structured single module whose durable side is a respected but hard-wired seam -- treat its 5-of-10 corpus kill row as unusable until the red Reserve-argument control is fixed and the corpus-neg rows are reconciled with it, and read the modularity gap as the arm effect rather than a defect.
- **ab_quota_ledger** (20260804-owner-pre): Pre-treatment control at 8/20. D1 = 0 and D3 = 1 are the two numbers this epic is built to move, and both are honestly at the floor: no model-derived case exists, and the domain writes its own file. D5 = 3 is already high because the fixture refuses to overclaim, which is the property most worth not losing.
