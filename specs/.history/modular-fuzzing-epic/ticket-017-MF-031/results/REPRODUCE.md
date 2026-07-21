# MF-031 — reproducing the evidence

All commands run from the repo root with `tlc2` on PATH
(`/Users/hayde/.skill-manager/bin/cli`). The toolchain pin applies:
`python3 scripts/tla_spec_dev.py`, never `tla-spec-dev` from PATH.

## 1. Generate a tractable corpus
The full `MC.cfg` corpus is 5,619,356 transitions / ~11 GB of `cases.py` and is
intractable to load (MF-034's surface). Use a reduced single-ticket config:

```
# MC-reduced.cfg: SpecRoots={default_specs}  Tickets={cli_entrypoint}
python3 scripts/generate_cases_from_tlc_dump.py \
  <current>/TlaSpecDevCli.tla MC-reduced.cfg \
  --out <out> --package tlc_state_graph_cases --view internal --tlc2 tlc2
# -> 61,081 cases
```

## 2. Execute the two adapters end to end (real runner)
Bind every corpus label (the coverage gate is whole-corpus) with the mapping in
`case_adapters_mf031.toml`, then execute one case per adapter. This mapping is
NOT the production `case_adapters.toml` — binding the corpus into production is
MF-023's surface (the same separation MF-028's spike used).

```
python3 scripts/run_generated_case_adapters.py <out>/spec-unit/tlc_state_graph_cases \
  --mapping case_adapters_mf031.toml --import-root specs/current \
  --case case_0178_update_ticket_desired --batch     # -> case-execution-desired.txt
  --case case_1621_update_ticket_current --batch      # -> case-execution-current.txt
```

## 3. Projection detail + negative controls
`case-execution-projection.txt` shows the CHECKED/UNCHECKED fields, the
except-index-recovered ticket, and three deliberately-wrong after-states per
adapter, each proven to make the check FAIL.

## 4. Coverage re-measurement
`corpus-coverage.txt` buckets every case by its before-state ticket-lifecycle
stage: executable rises 26.0% -> 81.6%; ticket segment 74.0% (vs MF-028's 72.5%).

## 5. CloseTicket collision
`closeticket-collision.txt` enumerates the four `action_name="CloseTicket"`
classes and the one-label-to-one-adapter mapping — a binding-model limitation.

Also in-tree spec-unit coverage:
`specs/current/tests/test_tla_spec_dev_update_ticket_adapter.py`
(2 end-to-end + 3 negative-control + 1 can_run tests).
