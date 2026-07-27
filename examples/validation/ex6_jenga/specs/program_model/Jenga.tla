------------------------------- MODULE Jenga -------------------------------
\* EV-01 SYNTHETIC INCOHERENT FIXTURE -- the control, not the primary evidence.
\*
\* The primary Jenga in this epic is REAL: `specs/program_model/TlaSpecDevCli.tla`,
\* this toolchain's own model, one component at Q = 0.000, `lastCommand` and
\* `result` written by all fifteen commands. Nobody built it to fail, which is
\* what makes it better evidence than anything written on purpose. This module
\* exists to answer the one question the real one cannot: what does the check
\* report when a god-state model IS given a declared partition AND a production
\* tree, with the answer known in advance.
\*
\* The three shapes the issue names, all present:
\*   shared mutable state with no single writer -- every action writes every
\*     variable, so no variable is confined to a component under ANY partition;
\*   every command reaching every module -- the code tree mirrors that;
\*   coordination by polling rather than protocol state -- `Poll` is an action
\*     whose entire job is to look at `status` and re-stamp `dirty`, which is
\*     what a program does when it has no protocol state to wait on.
EXTENDS Naturals

CONSTANTS Ids

VARIABLES status, auditLog, dirty, lastCommand

vars == << status, auditLog, dirty, lastCommand >>

Statuses == {"new", "billed", "notified", "closed"}

TypeInvariant ==
  /\ status \in [Ids -> Statuses]
  /\ auditLog \in 0..6
  /\ dirty \in BOOLEAN
  /\ lastCommand \in {"none", "place", "bill", "notify", "close", "poll"}

Init ==
  /\ status = [i \in Ids |-> "new"]
  /\ auditLog = 0
  /\ dirty = FALSE
  /\ lastCommand = "none"

\* Every action below writes all four variables. That is the fixture.

Place(i) ==
  /\ status[i] = "new"
  /\ status' = [status EXCEPT ![i] = "new"]
  /\ auditLog' = IF auditLog < 6 THEN auditLog + 1 ELSE auditLog
  /\ dirty' = TRUE
  /\ lastCommand' = "place"

Bill(i) ==
  /\ status[i] = "new"
  /\ status' = [status EXCEPT ![i] = "billed"]
  /\ auditLog' = IF auditLog < 6 THEN auditLog + 1 ELSE auditLog
  /\ dirty' = TRUE
  /\ lastCommand' = "bill"

Notify(i) ==
  /\ status[i] = "billed"
  /\ status' = [status EXCEPT ![i] = "notified"]
  /\ auditLog' = IF auditLog < 6 THEN auditLog + 1 ELSE auditLog
  /\ dirty' = TRUE
  /\ lastCommand' = "notify"

Close(i) ==
  /\ status[i] = "notified"
  /\ status' = [status EXCEPT ![i] = "closed"]
  /\ auditLog' = IF auditLog < 6 THEN auditLog + 1 ELSE auditLog
  /\ dirty' = FALSE
  /\ lastCommand' = "close"

\* Coordination by polling: no protocol state, so the program re-reads
\* everything and re-stamps the same flags.
Poll ==
  /\ dirty = TRUE
  /\ status' = status
  /\ auditLog' = auditLog
  /\ dirty' = FALSE
  /\ lastCommand' = "poll"

Next ==
  \/ \E i \in Ids : Place(i)
  \/ \E i \in Ids : Bill(i)
  \/ \E i \in Ids : Notify(i)
  \/ \E i \in Ids : Close(i)
  \/ Poll

Spec == Init /\ [][Next]_vars
=============================================================================
