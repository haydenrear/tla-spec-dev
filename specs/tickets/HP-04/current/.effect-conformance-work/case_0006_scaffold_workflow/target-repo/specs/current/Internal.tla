----------------------------- MODULE Internal -----------------------------
\* INTERNAL VIEW: fine-grained program/component state.
\*
\* Actions here generate spec-unit cases. They are executed by the spec-unit
\* adapters in adapters.py, mapped by case_adapters.toml.
\*
\* SCAFFOLD: replace these placeholder actions with the repository's real
\* internal transitions.
EXTENDS Core

VARIABLES owners, records, outbox, projections, lastInternalAction

InternalVars == <<owners, records, outbox, projections, lastInternalAction>>

InternalInit ==
  /\ owners = {}
  /\ records = [r \in Records |-> [owner |-> CHOOSE a \in Actors : TRUE, status |-> "none"]]
  /\ outbox = {}
  /\ projections = [r \in Records |-> "none"]
  /\ lastInternalAction = [name |-> "Init", params |-> <<>>]

\* @action RegisterActor
\* @layer internal
\* @controllability unit_direct
RegisterActor(a) ==
  /\ a \in Actors
  /\ a \notin owners
  /\ owners' = owners \cup {a}
  /\ UNCHANGED <<records, outbox, projections>>
  /\ lastInternalAction' = [name |-> "RegisterActor", params |-> [actor |-> a]]

\* @action AcceptRecord
\* @layer internal
\* @controllability unit_direct
AcceptRecord(a, r) ==
  /\ a \in owners
  /\ r \in Records
  /\ records[r].status = "none"
  /\ records' = [records EXCEPT ![r] = [owner |-> a, status |-> "accepted"]]
  /\ outbox' = outbox \cup {r}
  /\ UNCHANGED <<owners, projections>>
  /\ lastInternalAction' = [name |-> "AcceptRecord", params |-> [actor |-> a, record |-> r]]

\* @action PublishRecord
\* @layer internal
\* @controllability unit_direct
PublishRecord(r) ==
  /\ r \in outbox
  /\ projections' = [projections EXCEPT ![r] = "published"]
  /\ outbox' = outbox \ {r}
  /\ UNCHANGED <<owners, records>>
  /\ lastInternalAction' = [name |-> "PublishRecord", params |-> [record |-> r]]

InternalNext ==
  \/ \E a \in Actors : RegisterActor(a)
  \/ \E a \in Actors, r \in Records : AcceptRecord(a, r)
  \/ \E r \in Records : PublishRecord(r)

\* @invariant InternalInvariant
InternalInvariant ==
  /\ owners \subseteq Actors
  /\ outbox \subseteq Records
  /\ \A r \in outbox : records[r].status = "accepted"
  /\ \A r \in Records :
       projections[r] = "published" => records[r].status = "accepted"

InternalSpec == InternalInit /\ [][InternalNext]_InternalVars

=============================================================================
