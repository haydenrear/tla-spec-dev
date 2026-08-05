# Scorecards — architectural-coherence

scorecard_version 1. See `references/eval_scorecard.md`.

**Never average across examples.** `ex6_jenga` is a deliberately
incoherent fixture and is supposed to score low on D3; averaging it
with `ex4` produces a number about nothing.

| example | arm | D1 bug detection | D2 complexity | D3 modularity | D4 behavior preservation | D5 honesty | total | contested |
|---|---|---|---|---|---|---|---|---|
| ex1_scaffold_only | — | 2 | 2 | 1 | 3 | 3 | **11**/20 | — |
| ex1_scaffold_only | — | 2 | 2 | 1 | 2 | 3 | **10**/20 | — |
| ex3_over_complex | — | 2 | 3 | 1 | 3 | 3 | **12**/20 | — |
| ex3_over_complex | — | 2 | 3 | 2 | 3 | 3 | **13**/20 | — |
| ex4_pipeline_coherent | — | 2 | 2 | 3 | 3 | 4 | **14**/20 | — |
| ex4_pipeline_coherent | — | 2 | 2 | 3 | 4 | 3 | **14**/20 | — |
| ex5_pipeline_divergent | — | 1 | 2 | 1 | 2 | 4 | **10**/20 | — |
| ex5_pipeline_divergent | — | 1 | 2 | 1 | 2 | 4 | **10**/20 | — |
| ex6_jenga | — | 0 | 1 | 0 | 0 | 4 | **5**/20 | — |
| ex6_jenga | — | 0 | 1 | 1 | 0 | 4 | **6**/20 | — |

- **ex1_scaffold_only** (20260803-j1): The entry-path fixture works and its four runs are honest about the friction, but it is a single-file program whose domain does its own I/O, whose declared port is an environment variable pointing at a path, and whose entire bug-detection evidence is one seeded fault -- from which its own record concludes that an era is over.
- **ex1_scaffold_only** (20260803-j2): The scaffold-only entry path is honestly measured and its one content fault is genuinely killed, but the port exists only on the test side, the mid-run simplification's behavior-preservation leg is missing from the record, and the run write-up claims a class-level win from a single probe.
- **ex3_over_complex** (20260803-j1): The only fixture in the set that measures a simplification with committed before and after descriptors, four times over, and the one place the toolchain demonstrably changed behavior -- but half its headline reduction is a variable deletion validated by six tests that never read the deleted variables, and its shipped code has no boundary at all.
- **ex3_over_complex** (20260803-j2): The deliberately over-complex fixture produced the epic's best-evidenced simplification -- deletions I could verify were unread by any guard, with the deleted-edge red flag checked -- but its modularity is one effect port over an unchanged god-state, and its ordering assertion has never been probed.
- **ex4_pipeline_coherent** (20260803-j1): The strongest of the five: a real injected port swapped between two providers and executed under both, a per-arm per-class kill matrix that reproduces cell for cell, and a record that publishes its own false-clean route -- but its bug detection stops exactly where a generated corpus structurally stops, and its own README makes a promise about failed items that the model contradicts and no check can fail on.
- **ex4_pipeline_coherent** (20260803-j2): The strongest measured artifact in the set -- a real port swap proven at runtime, a green control with three independent mutant catalogues, and determinism at 38 of 38 -- whose own numbers say the hard fault classes are still at zero and whose headline `coherent` is conditional on a package-nesting accident its README does not mention.
- **ex5_pipeline_divergent** (20260803-j1): A deliberately divergent fixture that earns its low structural scores exactly as designed, and whose honesty is the highest in the tree because it ships the recipe for defeating itself -- but its only behavior check is eight hand-written assertions that stayed green through both the seeded divergences and the 41-line attack that erased them.
- **ex5_pipeline_divergent** (20260803-j2): The answer key is exact and reproduces on demand -- 4 divergences at their stated file:line, 1 absence, 0 false positives on the twin -- but the fixture detects structure through static imports only, and its own record shows a 41-line file erasing every finding while the coupling keeps running; the honesty of keeping that result is the fixture's real contribution.
- **ex6_jenga** (20260803-j1): A refusal control that earns four near-floor scores exactly as intended and one of the two highest honesty scores in the tree: it names a better piece of evidence than itself, calls its own declared partition useless, pre-commits the ways it could be misread, and files the hole in the mechanism it exists to demonstrate.
- **ex6_jenga** (20260803-j2): A control that does exactly one thing and does it honestly: the refusal reproduces on demand with two basis limits, and the fixture argues against its own importance while filing a finding against the mechanism it exists to prove -- with no detection instrument, no behavior check and, by construction, no modularity.
