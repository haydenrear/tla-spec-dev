------------------------------- MODULE Pipeline -------------------------------
\* Owner probe: does ANY model satisfy AC-01's decomposition criteria?
\* Two components joined by one queue port. Ingest owns inbox+accepted;
\* Dispatch owns delivered+failed; `queue` is the crossing.
EXTENDS Naturals, FiniteSets

CONSTANTS Items

VARIABLES inbox, accepted, queue, delivered, failed

TypeInvariant ==
  /\ inbox \subseteq Items
  /\ accepted \subseteq Items
  /\ queue \subseteq Items
  /\ delivered \subseteq Items
  /\ failed \subseteq Items

Init ==
  /\ inbox = Items
  /\ accepted = {}
  /\ queue = {}
  /\ delivered = {}
  /\ failed = {}

Accept(i) ==
  /\ i \in inbox
  /\ inbox' = inbox \ {i}
  /\ accepted' = accepted \cup {i}
  /\ UNCHANGED << queue, delivered, failed >>

Enqueue(i) ==
  /\ i \in accepted
  /\ i \notin queue
  /\ queue' = queue \cup {i}
  /\ UNCHANGED << inbox, accepted, delivered, failed >>

Deliver(i) ==
  /\ i \in queue
  /\ queue' = queue \ {i}
  /\ delivered' = delivered \cup {i}
  /\ UNCHANGED << inbox, accepted, failed >>

Fail(i) ==
  /\ i \in delivered
  /\ i \notin failed
  /\ failed' = failed \cup {i}
  /\ delivered' = delivered \ {i}
  /\ UNCHANGED << inbox, accepted, queue >>

Next ==
  \/ \E i \in Items : Accept(i)
  \/ \E i \in Items : Enqueue(i)
  \/ \E i \in Items : Deliver(i)
  \/ \E i \in Items : Fail(i)

Spec == Init /\ [][Next]_<< inbox, accepted, queue, delivered, failed >>
=============================================================================
