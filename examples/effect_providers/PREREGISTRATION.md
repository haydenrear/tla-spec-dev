# EP-03 preregistration

This is a measurement, not a showcase. The immutable machine-readable
experiment contract is [PREREGISTRATION.yaml](PREREGISTRATION.yaml). It was
committed before any control or mutant campaign.

| Project | Shape | Fixed campaign | Fixed target |
| --- | --- | --- | --- |
| `atomic_publisher` | explicit `FilesystemPort` injection | 12 mutants, 16 iterations | AP-01..08 and at least 10/12 killed |
| `legacy_payment_http` | self-installed `requests.Session.send` patch | 12 scored mutants, 32 iterations | 12/12 killed; bypass probes reported separately |
| `reminder_worker` | four explicit providers plus shared journal | 12 mutants, 25 iterations | 12/12 go; 10–11 investigate; below 10 redesign |

The TLA+ action fixes the semantic outcome and expected transition. Providers
may deterministically concretize values inside that outcome, but may not rewrite
a case or change its semantic class. Every effectful campaign must execute the
case package regenerated from that project's checked `Internal.tla`; ordinary
fixtures count only toward the separately reported hand-written baseline.

No example may change framework source to improve a result. A red control,
framework rescue edit, post-run mutant/seed/threshold change, shallow
existence/exit-code oracle, or substitution of hand-written cases invalidates
the score. Survivors and bypasses remain visible findings.

Each project must preserve raw JSON evidence for TLC counts, action/outcome and
case execution, runtime p50/p95, every mutant and triggered detector, first
discovery/replay, cleanup/isolation, two local repetitions, and the final fresh
checkout run. It must also record the files and lines read/changed by its
implementer so retrieval cost is measured rather than inferred.
