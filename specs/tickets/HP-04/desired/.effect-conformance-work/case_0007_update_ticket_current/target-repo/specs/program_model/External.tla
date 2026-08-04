----------------------------- MODULE External -----------------------------
\* EXTERNAL VIEW: the behavior a test harness can drive or observe from
\* outside the program. This is a projection of the internal semantics, not an
\* independent business model.
\*
\* Actions here generate Test Graph cases. They are executed by the Test Graph
\* adapters in adapters.py, mapped by testgraph_bindings.yml.
\*
\* External does NOT mean distributed. For an HTTP service it is requests. For
\* a CLI it is command invocations plus filesystem assertions. For a library it
\* is the public API surface and the files/streams it produces. Model whatever
\* a caller can actually see.
\*
\* SCAFFOLD: replace these placeholder submissions with this repository's real
\* public surface, including negative/duplicate cases. See
\* references/edge-cases.md for choosing boundary cases.
EXTENDS Internal

CONSTANTS Clients

VARIABLES responses, lastExternalAction

ExternalVars == <<InternalVars, responses, lastExternalAction>>

ExternalInit ==
  /\ InternalInit
  /\ responses = [c \in Clients |-> [status |-> 0, body |-> <<>>]]
  /\ lastExternalAction = [name |-> "Init", params |-> <<>>]

MarkExternal(actionName, params) ==
  lastExternalAction' = [name |-> actionName, params |-> params]

\* @action SubmitRegisterActor
\* @layer external
\* @controllability e2e_direct
SubmitRegisterActor(c, a) ==
  /\ c \in Clients
  /\ RegisterActor(a)
  /\ responses' = [responses EXCEPT ![c] = [status |-> 201, body |-> [actor |-> a]]]
  /\ MarkExternal("SubmitRegisterActor", [client |-> c, actor |-> a])

\* @action SubmitDuplicateRegisterActor
\* @layer external
\* @controllability e2e_direct
SubmitDuplicateRegisterActor(c, a) ==
  /\ c \in Clients
  /\ a \in owners
  /\ UNCHANGED InternalVars
  /\ responses' = [responses EXCEPT ![c] = [status |-> 200, body |-> [actor |-> a, idempotent |-> TRUE]]]
  /\ MarkExternal("SubmitDuplicateRegisterActor", [client |-> c, actor |-> a])

\* @action SubmitAcceptRecord
\* @layer external
\* @controllability e2e_direct
SubmitAcceptRecord(c, a, r) ==
  /\ c \in Clients
  /\ AcceptRecord(a, r)
  /\ responses' = [responses EXCEPT ![c] = [status |-> 202, body |-> [record |-> r, status |-> "accepted"]]]
  /\ MarkExternal("SubmitAcceptRecord", [client |-> c, actor |-> a, record |-> r])

\* @action SubmitAcceptRecordUnknownActor
\* @layer external
\* @controllability e2e_direct
SubmitAcceptRecordUnknownActor(c, a, r) ==
  /\ c \in Clients
  /\ a \in Actors
  /\ a \notin owners
  /\ r \in Records
  /\ UNCHANGED InternalVars
  /\ responses' = [responses EXCEPT ![c] = [status |-> 404, body |-> [error |-> "actor_not_found"]]]
  /\ MarkExternal("SubmitAcceptRecordUnknownActor", [client |-> c, actor |-> a, record |-> r])

\* @action SubmitDuplicateAcceptRecord
\* @layer external
\* @controllability e2e_direct
SubmitDuplicateAcceptRecord(c, a, r) ==
  /\ c \in Clients
  /\ a \in owners
  /\ r \in Records
  /\ records[r].status # "none"
  /\ UNCHANGED InternalVars
  /\ responses' = [responses EXCEPT ![c] = [status |-> 409, body |-> [error |-> "record_exists"]]]
  /\ MarkExternal("SubmitDuplicateAcceptRecord", [client |-> c, actor |-> a, record |-> r])

\* @action RunPublishWorker
\* @layer external
\* @controllability e2e_direct
RunPublishWorker(c) ==
  /\ c \in Clients
  /\ outbox # {}
  /\ projections' = [r \in Records |-> IF r \in outbox THEN "published" ELSE projections[r]]
  /\ outbox' = {}
  /\ UNCHANGED <<owners, records>>
  /\ lastInternalAction' = [name |-> "PublishAllOutbox", params |-> [records |-> outbox]]
  /\ UNCHANGED responses
  /\ MarkExternal("RunPublishWorker", [client |-> c, pending |-> Cardinality(outbox)])

\* @action RunPublishWorkerNoop
\* @layer external
\* @controllability e2e_direct
RunPublishWorkerNoop(c) ==
  /\ c \in Clients
  /\ outbox = {}
  /\ UNCHANGED InternalVars
  /\ UNCHANGED responses
  /\ MarkExternal("RunPublishWorkerNoop", [client |-> c, pending |-> 0])

\* @action HiddenInternalProgress
\* @layer internal
\* @controllability hidden
HiddenInternalProgress ==
  /\ InternalNext
  /\ UNCHANGED <<responses, lastExternalAction>>

ExternalNext ==
  \/ \E c \in Clients, a \in Actors : SubmitRegisterActor(c, a)
  \/ \E c \in Clients, a \in Actors : SubmitDuplicateRegisterActor(c, a)
  \/ \E c \in Clients, a \in Actors, r \in Records : SubmitAcceptRecord(c, a, r)
  \/ \E c \in Clients, a \in Actors, r \in Records : SubmitAcceptRecordUnknownActor(c, a, r)
  \/ \E c \in Clients, a \in Actors, r \in Records : SubmitDuplicateAcceptRecord(c, a, r)
  \/ \E c \in Clients : RunPublishWorker(c)
  \/ \E c \in Clients : RunPublishWorkerNoop(c)
  \/ HiddenInternalProgress

\* @invariant ExternalInvariant
ExternalInvariant ==
  /\ InternalInvariant
  /\ \A c \in Clients :
       responses[c].status \in {0, 200, 201, 202, 404, 409}

Spec == ExternalInit /\ [][ExternalNext]_ExternalVars
Invariant == ExternalInvariant

=============================================================================
