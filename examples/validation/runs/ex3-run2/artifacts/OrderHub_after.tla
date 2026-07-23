---- MODULE OrderHub ----
\* OrderHub: a small order processor. Every operation routes through the hub,
\* stamping the shared mode, audit log, and dirty flag on its way.
EXTENDS Naturals

VARIABLES mode, orders, shipped, retries, auditLog, dirty

vars == <<mode, orders, shipped, retries, auditLog, dirty>>

\* Domains are sized to the distinctions the behavior actually makes:
\* mode is only ever stamped 0..4, orders/shipped are capped at 3 by
\* guard and invariant, retries at 2, and auditLog at 12 (the cap that
\* stops the world). TLC verifies these caps as part of the invariant.
TypeOK ==
    /\ mode \in 0..4
    /\ orders \in 0..3
    /\ shipped \in 0..3
    /\ retries \in 0..2
    /\ auditLog \in 0..12
    /\ dirty \in BOOLEAN

SafetyInv ==
    /\ shipped <= orders
    /\ orders <= 3

Inv == TypeOK /\ SafetyInv

Init ==
    /\ mode = 0
    /\ orders = 0
    /\ shipped = 0
    /\ retries = 0
    /\ auditLog = 0
    /\ dirty = FALSE

PlaceOrder ==
    /\ orders < 3
    /\ auditLog < 12
    /\ orders' = orders + 1
    /\ mode' = 1
    /\ auditLog' = auditLog + 1
    /\ dirty' = ~dirty
    /\ UNCHANGED <<shipped, retries>>

ShipOrder ==
    /\ shipped < orders
    /\ auditLog < 12
    /\ shipped' = shipped + 1
    /\ mode' = 2
    /\ auditLog' = auditLog + 1
    /\ dirty' = ~dirty
    /\ UNCHANGED <<orders, retries>>

RetrySweep ==
    /\ retries < 2
    /\ auditLog < 12
    /\ retries' = retries + 1
    /\ mode' = 3
    /\ auditLog' = auditLog + 1
    /\ dirty' = ~dirty
    /\ UNCHANGED <<orders, shipped>>

AuditSweep ==
    /\ auditLog < 12
    /\ auditLog' = auditLog + 1
    /\ mode' = 4
    /\ dirty' = ~dirty
    /\ UNCHANGED <<orders, shipped, retries>>

Next ==
    \/ PlaceOrder
    \/ ShipOrder
    \/ RetrySweep
    \/ AuditSweep

Spec == Init /\ [][Next]_vars
====
