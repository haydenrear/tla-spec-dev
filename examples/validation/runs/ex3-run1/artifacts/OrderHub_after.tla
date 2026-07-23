---- MODULE OrderHub ----
\* OrderHub: a small order processor. Every operation routes through the hub
\* and is counted in the audit log; the audit cap stops the world.
\*
\* Domains are sized to the distinctions the behavior actually makes:
\* orders/shipped are capped at 3, retries at 2, auditLog at 12. The former
\* mode/dirty stamps were bookkeeping no guard, invariant, or test read;
\* they were refactored out of the program (see
\* validation_artifacts/complexity_decision.md).
EXTENDS Naturals

VARIABLES orders, shipped, retries, auditLog

vars == <<orders, shipped, retries, auditLog>>

TypeOK ==
    /\ orders \in 0..3
    /\ shipped \in 0..3
    /\ retries \in 0..2
    /\ auditLog \in 0..12

SafetyInv ==
    /\ shipped <= orders
    /\ orders <= 3

Inv == TypeOK /\ SafetyInv

Init ==
    /\ orders = 0
    /\ shipped = 0
    /\ retries = 0
    /\ auditLog = 0

PlaceOrder ==
    /\ orders < 3
    /\ auditLog < 12
    /\ orders' = orders + 1
    /\ auditLog' = auditLog + 1
    /\ UNCHANGED <<shipped, retries>>

ShipOrder ==
    /\ shipped < orders
    /\ auditLog < 12
    /\ shipped' = shipped + 1
    /\ auditLog' = auditLog + 1
    /\ UNCHANGED <<orders, retries>>

RetrySweep ==
    /\ retries < 2
    /\ auditLog < 12
    /\ retries' = retries + 1
    /\ auditLog' = auditLog + 1
    /\ UNCHANGED <<orders, shipped>>

AuditSweep ==
    /\ auditLog < 12
    /\ auditLog' = auditLog + 1
    /\ UNCHANGED <<orders, shipped, retries>>

Next ==
    \/ PlaceOrder
    \/ ShipOrder
    \/ RetrySweep
    \/ AuditSweep

Spec == Init /\ [][Next]_vars
====
