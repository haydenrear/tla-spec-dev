----------------------------- MODULE DistributedFulfillment -----------------------------
EXTENDS Naturals, FiniteSets, TLC

CONSTANTS
  Orders,
  NoReason

VARIABLES
  accepted,
  outbox,
  topic,
  projected,
  acked,
  result

vars == << accepted, outbox, topic, projected, acked, result >>

Init ==
  /\ accepted = {}
  /\ outbox = {}
  /\ topic = {}
  /\ projected = {}
  /\ acked = {}
  /\ result = [accepted |-> TRUE, reason |-> NoReason]

\* @command AcceptOrder
\* @result AcceptOrderResult
AcceptOrder(o) ==
  /\ o \notin accepted
  /\ accepted' = accepted \cup {o}
  /\ outbox' = outbox \cup {o}
  /\ UNCHANGED << topic, projected, acked >>
  /\ result' = [accepted |-> TRUE, reason |-> NoReason]

\* @command RejectDuplicateOrder
\* @result AcceptOrderResult
RejectDuplicateOrder(o) ==
  /\ o \in accepted
  /\ UNCHANGED << accepted, outbox, topic, projected, acked >>
  /\ result' = [accepted |-> FALSE, reason |-> "DUPLICATE"]

\* @command PublishOutbox
\* @result PublishOutboxResult
PublishOutbox(o) ==
  /\ o \in outbox
  /\ topic' = topic \cup {o}
  /\ UNCHANGED << accepted, outbox, projected, acked, result >>

\* @command ProjectShipment
\* @result ProjectShipmentResult
ProjectShipment(o) ==
  /\ o \in topic
  /\ projected' = projected \cup {o}
  /\ acked' = acked \cup {o}
  /\ UNCHANGED << accepted, outbox, topic, result >>

Next ==
  \E o \in Orders:
    AcceptOrder(o)
    \/ RejectDuplicateOrder(o)
    \/ PublishOutbox(o)
    \/ ProjectShipment(o)

\* @invariant AcceptedOrdersAreKnown
AcceptedOrdersAreKnown ==
  accepted \subseteq Orders

\* @invariant OutboxOnlyContainsAcceptedOrders
OutboxOnlyContainsAcceptedOrders ==
  outbox \subseteq accepted

\* @invariant PublishedOrdersWereAccepted
PublishedOrdersWereAccepted ==
  topic \subseteq accepted

\* @invariant ProjectedOrdersWerePublished
ProjectedOrdersWerePublished ==
  projected \subseteq topic

\* @invariant AckedOrdersWereProjected
AckedOrdersWereProjected ==
  acked \subseteq projected

Spec ==
  Init /\ [][Next]_vars

=============================================================================
