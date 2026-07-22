# Validation examples — restart of the MF-037 plan (issue #62)

Three example projects, real agents doing real tickets, repeated runs.
Re-aimed after the complexity-descriptor epic (#71/#72/#73): the things under
test are the **descriptor** (CD-01), the **intuition doc** (CD-02), and the
**fitness functions** (CD-03) — there are no gates and no suggested moves.

| Example | Project | Tests |
| --- | --- | --- |
| ex1 scaffold-only | `ex1_scaffold_only/taskq` — small CLI, no specs yet | the new-user entry path: scaffold, scan, judge, configure fitness functions |
| ex2 ticket workflow | `../distributed_history` | a real ticket end-to-end on the internal/external example that the old gate regime made unusable |
| ex3 over-complex | `ex3_over_complex/order_hub` — god-state model, oversized domains | descriptor + intuition must lead an agent to a validated complexity-lowering refactor |

Protocol:

1. `PREDICTIONS.md` is committed BEFORE any dispatch.
2. Each run copies its example project into a scratch workspace; agents never
   work in this tree and are never shown `PREDICTIONS.md` or other runs'
   records.
3. The toolchain is used from the epic checkout via
   `python3 <repo>/scripts/tla_spec_dev.py` (never the PATH wrapper).
4. After each run the epic owner collects the agent's report and key
   artifacts under `runs/<example>-run<N>/` and scores it against the
   predictions.
5. Each example runs at least twice. Findings are filed, never fixed inline.
