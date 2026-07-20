---------------------------- MODULE GodObjectCli ----------------------------
\* MF-036 probe: an ordinary 5-variable, 10-command CLI over shared state.
\* This reproduces the model whose HARD FAIL motivated the reframe:
\*
\*   VERDICT: FAIL -- component C1 is touched by 10 actions,
\*                    exceeding max_component_actions 8   (exit 1)
\*
\* It is a plain god-object CLI: a single shared `status` variable that every
\* command reads and writes, plus four domain variables each command touches one
\* of. Every command therefore touches only TWO variables (status + one domain),
\* yet the shared variable couples all ten commands into one component.
\*
\* Each command leaves the three variables it does not use alone with an explicit
\* `v' = v` frame condition -- the written-out form of UNCHANGED. Before the
\* MF-036 frame-condition fix the R/W matrix counted those `v' = v` conjuncts as
\* "touched", so ALL FIVE variables showed as touched by all ten commands: a
\* fully dense 10/10 god-state over-report. After the fix only the genuinely
\* shared `status` is a 10/10 dense row; the four domain variables drop to their
\* real 2-or-3-of-10 coupling.
EXTENDS Integers

VARIABLES status, v1, v2, v3, v4

TypeInvariant ==
  /\ status \in 0..2
  /\ v1 \in 0..2
  /\ v2 \in 0..2
  /\ v3 \in 0..2
  /\ v4 \in 0..2

Init ==
  /\ status = 0
  /\ v1 = 0
  /\ v2 = 0
  /\ v3 = 0
  /\ v4 = 0

\* Ten commands. Each reads and writes the shared `status` plus exactly one
\* domain variable; the other three domain variables are pinned with `v' = v`.
Cmd01 == /\ status' = (status + 1) % 3 /\ v1' = (v1 + 1) % 3 /\ v2' = v2 /\ v3' = v3 /\ v4' = v4
Cmd02 == /\ status' = (status + 2) % 3 /\ v1' = (v1 + 2) % 3 /\ v2' = v2 /\ v3' = v3 /\ v4' = v4
Cmd03 == /\ status' = (status + 1) % 3 /\ v1' = (v1 + 2) % 3 /\ v2' = v2 /\ v3' = v3 /\ v4' = v4
Cmd04 == /\ status' = (status + 2) % 3 /\ v2' = (v2 + 1) % 3 /\ v1' = v1 /\ v3' = v3 /\ v4' = v4
Cmd05 == /\ status' = (status + 1) % 3 /\ v2' = (v2 + 2) % 3 /\ v1' = v1 /\ v3' = v3 /\ v4' = v4
Cmd06 == /\ status' = (status + 2) % 3 /\ v2' = (v2 + 1) % 3 /\ v1' = v1 /\ v3' = v3 /\ v4' = v4
Cmd07 == /\ status' = (status + 1) % 3 /\ v3' = (v3 + 1) % 3 /\ v1' = v1 /\ v2' = v2 /\ v4' = v4
Cmd08 == /\ status' = (status + 2) % 3 /\ v3' = (v3 + 2) % 3 /\ v1' = v1 /\ v2' = v2 /\ v4' = v4
Cmd09 == /\ status' = (status + 1) % 3 /\ v4' = (v4 + 1) % 3 /\ v1' = v1 /\ v2' = v2 /\ v3' = v3
Cmd10 == /\ status' = (status + 2) % 3 /\ v4' = (v4 + 2) % 3 /\ v1' = v1 /\ v2' = v2 /\ v3' = v3

Next ==
  \/ Cmd01 \/ Cmd02 \/ Cmd03 \/ Cmd04 \/ Cmd05
  \/ Cmd06 \/ Cmd07 \/ Cmd08 \/ Cmd09 \/ Cmd10

Spec == Init /\ [][Next]_<<status, v1, v2, v3, v4>>
=============================================================================
