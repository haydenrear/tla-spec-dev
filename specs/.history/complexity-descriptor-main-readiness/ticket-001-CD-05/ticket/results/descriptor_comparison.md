# CD-05 descriptor comparison -- before/after the domain-resolution change

The TLA+ model is byte-identical before and after CD-05 (zero model delta);
what changed is the MEASUREMENT machinery (scripts/analyze_complexity.py).
On this repository's own model every previously resolved figure is unchanged:
bound 699,840 over the same 7 bounded dimensions; lastCommand/result stay
honestly unknown. New: a per-dimension 'source' column and the merged
per-variable domain-source order (TypeInvariant > TypeOK > cfg invariants).
The resolver improvements (operator-defined sets, wrapped conjuncts,
multi-view merge) change results only on models exhibiting the VAL-06/16/17
shapes -- demonstrated in tests/test_analyze_complexity.py and
specs/tickets/CD-05/results/domain_resolution_regressions.txt.

## BEFORE (epic tip 8df525f scanner, project specs/current model)

[MEASURED] Dimension table
variable            domain                                                        cardinality  note
------------------  ------------------------------------------------------------  -----------  ---------------------------------------------------------
setup_phase         0..5                                                          6
spec_root           SpecRoots \cup {NoRoot}                                       3
ticket_state        [Tickets -> 0..5]                                             216          6^3 total functions
lastCommand         (unconstrained)                                               unknown      unconstrained by TypeInvariant -- excluded from the bound
result              (unconstrained)                                               unknown      unconstrained by TypeInvariant -- excluded from the bound
complexity_gate     {"unknown", "pass", "fail"}                                   3
corpus_gate         {"unknown", "pass", "fail"}                                   3
effect_conformance  {"unknown", "clean", "gaps", "dead_surface", "unobservable"}  5
kill_test           {"unknown", "pass", "below_floor", "incomplete_catalog"}      4

[MEASURED] State-space upper bound
  bound = 699,840  (product of 7 bounded dimensions; domains from TypeInvariant)

## AFTER (CD-05 scanner, ticket current model -- same model content)

[MEASURED] Dimension table
variable            domain                                                        cardinality  source         note
------------------  ------------------------------------------------------------  -----------  -------------  -------------------------------------------------------------------------------------------------------------
setup_phase         0..5                                                          6            TypeInvariant
spec_root           SpecRoots \cup {NoRoot}                                       3            TypeInvariant
ticket_state        [Tickets -> 0..5]                                             216          TypeInvariant  6^3 total functions
lastCommand         (unconstrained)                                               unknown      -              unconstrained by TypeInvariant / the configured invariants (resolved transitively) -- excluded from the bound
result              (unconstrained)                                               unknown      -              unconstrained by TypeInvariant / the configured invariants (resolved transitively) -- excluded from the bound
complexity_gate     {"unknown", "pass", "fail"}                                   3            TypeInvariant
corpus_gate         {"unknown", "pass", "fail"}                                   3            TypeInvariant
effect_conformance  {"unknown", "clean", "gaps", "dead_surface", "unobservable"}  5            TypeInvariant
kill_test           {"unknown", "pass", "below_floor", "incomplete_catalog"}      4            TypeInvariant
  (domain sources merge per-variable: TypeInvariant, then TypeOK, then the
  configured invariants -- first source that resolves wins. What the resolver
  can and cannot see: references/architecture_tractability.md,
  'What The Domain Resolver Can And Cannot See'.)

  bound = 699,840  (product of 7 bounded dimensions; domains from TypeInvariant)
