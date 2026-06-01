----------------------------- MODULE DistributedFulfillment -----------------------------
EXTENDS Naturals, FiniteSets, TLC

CONSTANTS
  Orders,
  NoReason

VARIABLES
  accepted,
  outbox,
  topic,
  result

vars == << accepted, outbox, topic, result >>

Init ==
  /\ accepted = {}
  /\ outbox = {}
  /\ topic = {}
  /\ result = [accepted |-> TRUE, reason |-> NoReason]

\* @command AcceptOrder
\* @result AcceptOrderResult
AcceptOrder(o) ==
  /\ o \notin accepted
  /\ accepted' = accepted \cup {o}
  /\ outbox' = outbox \cup {o}
  /\ UNCHANGED topic
  /\ result' = [accepted |-> TRUE, reason |-> NoReason]

\* @command RejectDuplicateOrder
\* @result AcceptOrderResult
RejectDuplicateOrder(o) ==
  /\ o \in accepted
  /\ UNCHANGED << accepted, outbox, topic >>
  /\ result' = [accepted |-> FALSE, reason |-> "DUPLICATE"]

\* @command PublishOutbox
\* @result PublishOutboxResult
PublishOutbox(o) ==
  /\ o \in outbox
  /\ topic' = topic \cup {o}
  /\ UNCHANGED << accepted, outbox, result >>

Next ==
  \E o \in Orders:
    AcceptOrder(o) \/ RejectDuplicateOrder(o) \/ PublishOutbox(o)

\* @invariant AcceptedOrdersAreKnown
AcceptedOrdersAreKnown ==
  accepted \subseteq Orders

\* @invariant OutboxOnlyContainsAcceptedOrders
OutboxOnlyContainsAcceptedOrders ==
  outbox \subseteq accepted

\* @invariant PublishedOrdersWereAccepted
PublishedOrdersWereAccepted ==
  topic \subseteq accepted

Spec ==
  Init /\ [][Next]_vars

=============================================================================
