# RC-01 model delta — the nine MF-026 gaps and the guard-weakening decision

Ticket `RC-01`, `architectural-coherence-epic`, schedule_revision 6.
Baseline: epic tip `d3eb851`.

This is the first ticket in the epic whose whole purpose is model delta, and the
delta is substantial. It is recorded here in the shape AC-01's 4.6x was recorded,
because the standing objective requires an increase to be justified rather than
absorbed.

## What grew, and why each part is not derivable from something already there

| element | kind | gap | why it is not derivable |
|---|---|---|---|
| `architecture_delta` | variable, 6 values | G-8 | `analyze architecture --baseline` reports a direction verdict (`improved`, `worsened`, `unchanged`, `unverified`, `unattributable`) that the ledger records as its `architecture_delta` member. None of its values follows from `architecture_scan`: a coherent scan can sit over any of the five, and two of the five are REFUSALS about the before/after pair rather than measurements of the code. |
| `TicketClosedWeakened` (stage 6) | widened `ticket_state` domain | owner decision | A close taken under `--accept-new` / `--allow-open` bypasses the precondition `CloseTicket` guards on. Nothing else in the model records which close happened. |
| `GenerateCases` | action | G-6 | Case-module generation had no action, no port and no CLI subcommand. It is the epic's flagship feature. |
| `CloseTicketWeakened` | action | owner decision | The transition into stage 6. |
| `WeakenedClosesCertifyNothing` | invariant | owner decision | States positively what a weakened close is, so the narrowing of `ClosedTicketsPassedSpecUnitTests` cannot be read as the model merely having less to say. |
| `TicketReached(t, stage)` | operator | owner decision | Five invariants read the lifecycle with `>=`. Stage 6 is the HIGHEST ordinal and certifies the LEAST, so `>=` answers TRUE for it. |
| `AnalyzeArchitecture: [evidence_report]` | effects row | G-1 | The only non-stutter action with no row at all. |
| `cli_artifact` retarget + `cli_download` + `cli_artifact_delete` + `cli_selftest_process` | ports | G-9 | The install path's real effects, including the network fetch ESC-6 named. |

## The measured cost

### Static declared-representation bound (`analyze complexity`)

| | baseline `d3eb851` | RC-01 | factor |
|---|---|---|---|
| bound | 2,799,360 | 26,671,680 | **9.53x** |
| variables (resolved / total) | 8 / 10 | 9 / 11 | — |
| Next disjuncts | 16 | 18 | — |

Evidence: `rc01-complexity-baseline.txt`, `rc01-complexity-current.txt`.

The factor decomposes exactly, and the decomposition is asserted as a test
(`tests/test_analyze_complexity.py::test_repository_own_model_reproduces_the_recorded_state_space_bound`):

```
2,799,360  x 6            = 16,796,160     architecture_delta, 6-valued
16,796,160 / 216 x 343    = 26,671,680     ticket_state [Tickets -> 0..5] -> 0..6
```

The two new ACTIONS contribute nothing to the bound: both write only
`lastCommand` and `result`, neither of which has a resolvable domain. RP-04's
completeness assertions confirm the chain is still a like-for-like comparison —
the unresolved pair is the same pair before and after.

### Reachable state space (TLC, `MC.cfg`, 3 tickets x 2 spec roots)

| | baseline `d3eb851` | RC-01 | factor |
|---|---|---|---|
| distinct states | 1,292,951 | **10,331,543** | **7.99x** |
| generated states | 32,122,220 | 392,923,694 | 12.23x |
| depth | 26 | **26** | unchanged |
| wall time | 59s | 11min 15s | 11.4x |
| result | no error | **no error** | — |

Evidence: `rc01-tlc-baseline-d3eb851.txt`, `rc01-tlc-current.txt`.

Depth unchanged at 26 is the useful figure: the model got WIDER, not DEEPER. No
new sequence of commands became possible; two new commands and one new stage
became representable at every point where the old ones already were.

### Against the budgets

`max_distinct_states` is 500,000 and `max_state_space_bound` is 1,000,000. Both
were already exceeded before this ticket (AC-01 took distinct states to
1,292,951 and the bound to 2,799,360) and both are further exceeded now. They
stay ADVISORY and they are NOT renegotiated here. Recording the number is the
obligation; making it look better is not.

The one figure worth flagging for the owner is wall time. `budgets.tlc_seconds`
is 120 and this model now takes 675s to check. Nothing enforces that budget —
`scripts/run_tlc.sh` applies no timeout — so nothing failed, but the model has
been over its declared TLC wall-time budget by 5.6x since this ticket and by
0.5x since AC-01. That is a real cost of the epic's model growth and it belongs
in the owner's view of whether the next variable is worth it.

## What did NOT change

- No eval fixture. `examples/validation/` is untouched.
- No guard reads `architecture_delta`; no close or promotion path reads it. The
  epic's `coherence_doctrine` (advisory, never a gate) is intact.
- `specs/program_model` keeps its 9 variables and 15 disjuncts. It is the
  accepted baseline and the workflow close promotes into it; this ticket
  corrected only its stale comments (G-5 wording, G-7 citations) and its
  install-path ports (G-9).
