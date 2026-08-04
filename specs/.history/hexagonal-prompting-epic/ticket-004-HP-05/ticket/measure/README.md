# HP-05 measurement instruments

Ticket-local. `specs/tickets/**` is out of the modeled representation scope:
this is what HP-05 measured WITH, not shipped surface. The thing under
measurement — the content-asserting effect provider — is shipped, and is
imported from the generated package rather than reimplemented here.

    spec_manifest.yaml            the fixture's durable boundary, restated in
                                  the form a provider can bind to, plus the one
                                  `content:` sentence. Fed to SHIPPED codegen.
    QuotaLedger.tla / .cfg        HP-01's model, copied so the manifest
                                  validates. Never edited.
    generated/                    what `scripts/generate_python.py` emitted from
                                  the manifest above. Regenerable; committed so
                                  a reader can see the provider that ran.
    quota_effect_adapter.py       HP-03's adapter plus one change: the durable
                                  append goes through the port as well as to
                                  the file.
    run_mapping_kill_table.py     the driver. One corpus, three mappings.
    case_adapters.map-*.toml      the three instruments, as three declared
                                  files, so a reader of a number can see which
                                  mapping produced it.

## Reproducing the table

The 43,128-case corpus is NOT committed (105 MB). Regenerate it:

    python3 scripts/tla_spec_dev.py --spec-root specs generate cases \
      examples/validation/ab/model/QuotaLedger.tla \
      examples/validation/ab/model/QuotaLedger.cfg \
      --out $PWD/specs/tickets/HP-05/measure/corpus-whole \
      --package quota_whole --view internal

This exits NONZERO: the corpus is 43,128 cases against a cap of 200 and the
command refuses to accept it while writing every case to disk (HP-03-DF-02, the
cap the owner has not moved). That is the expected outcome and the corpus is
complete.

Regenerate the package, then run the table:

    python3 scripts/generate_python.py \
      specs/tickets/HP-05/measure/spec_manifest.yaml \
      --out $PWD/specs/tickets/HP-05/measure/generated

    python3 specs/tickets/HP-05/measure/run_mapping_kill_table.py \
      --catalogue examples/validation/ab/seeded_faults.toml \
      --reference examples/validation/ab/reference \
      --corpus specs/tickets/HP-05/measure/corpus-whole/spec-unit/quota_whole \
      --suite examples/validation/ab/tests/test_behavior.py \
      --out specs/tickets/HP-05/results/kill-table-mapping.json

Two full runs were byte-identical, failing executions included
(`results/determinism.txt`).
