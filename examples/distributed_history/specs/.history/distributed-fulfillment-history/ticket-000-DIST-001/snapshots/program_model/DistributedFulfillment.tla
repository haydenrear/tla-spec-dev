----------------------------- MODULE DistributedFulfillment -----------------------------
EXTENDS Naturals, FiniteSets, TLC

CONSTANTS
  Orders,
  NoReason

VARIABLES
  accepted,
  result

vars == << accepted, result >>

Init ==
  /\ accepted = {}
  /\ result = [accepted |-> TRUE, reason |-> NoReason]

\* @command AcceptOrder
\* @result AcceptOrderResult
AcceptOrder(o) ==
  /\ o \notin accepted
  /\ accepted' = accepted \cup {o}
  /\ result' = [accepted |-> TRUE, reason |-> NoReason]

\* @command RejectDuplicateOrder
\* @result AcceptOrderResult
RejectDuplicateOrder(o) ==
  /\ o \in accepted
  /\ UNCHANGED accepted
  /\ result' = [accepted |-> FALSE, reason |-> "DUPLICATE"]

Next ==
  \E o \in Orders:
    AcceptOrder(o) \/ RejectDuplicateOrder(o)

\* @invariant AcceptedOrdersAreKnown
AcceptedOrdersAreKnown ==
  accepted \subseteq Orders

Spec ==
  Init /\ [][Next]_vars

=============================================================================
