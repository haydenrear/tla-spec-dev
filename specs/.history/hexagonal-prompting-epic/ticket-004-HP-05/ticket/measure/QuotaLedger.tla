---- MODULE QuotaLedger ----
(***************************************************************************)
(* The quota-ledger feature of ../FEATURE.md, as a state machine.          *)
(*                                                                         *)
(* This is the model BOTH arms are measured through. It is identical for   *)
(* both, because the A/B varies the IMPLEMENTATION PROMPT and holds the    *)
(* specification fixed -- if each arm generated its own model, a D1        *)
(* difference could be a difference in the models and nobody could tell.   *)
(*                                                                         *)
(* Two aspects, and the eval slices on them:                               *)
(*                                                                         *)
(*   RESERVATIONS   available, live, holder, amt, closed                   *)
(*   LEDGER         committed, ledger                                      *)
(*                                                                         *)
(* Commit and CloseTenant are the CROSS-ASPECT actions: their guards read  *)
(* RESERVATIONS and their effects write LEDGER. M03 and M08 in             *)
(* ../seeded_faults.toml are seeded exactly there, because a slice built   *)
(* for one aspect alone cannot constrain the other.                        *)
(*                                                                         *)
(* `status` and `reason` are modeled deliberately. The predecessor         *)
(* measured that a state-only oracle cannot see a fault where the          *)
(* transition is correct and the REPORTED OUTCOME is wrong (M06), and that *)
(* a corpus containing no rejected input cannot see guard relaxation at    *)
(* all. Both need the outcome in the state.                                *)
(***************************************************************************)
EXTENDS Naturals, FiniteSets, Sequences

CONSTANTS
    Tenants,        \* the tenant names
    ResIds,         \* the reservation ids that may be allocated
    Amounts,        \* the reservable amounts
    Quota           \* every tenant's quota (one number keeps the space small)

NoTenant == "none"

VARIABLES
    available,      \* [Tenants -> Nat]      RESERVATIONS
    committed,      \* [Tenants -> Nat]      LEDGER
    closed,         \* SUBSET Tenants        RESERVATIONS
    live,           \* SUBSET ResIds         RESERVATIONS
    holder,         \* [ResIds -> Tenants \cup {NoTenant}]
    amt,            \* [ResIds -> Nat]
    ledger,         \* Seq-like: the durable append-only lines   LEDGER
    status,         \* "accepted" | "rejected" | "init"
    reason          \* the rejection reason, or "none"

vars == << available, committed, closed, live, holder, amt, ledger, status, reason >>

Reasons == { "unknown_tenant", "tenant_closed", "amount_not_positive",
             "quota_exceeded", "unknown_reservation", "outstanding_reservations",
             "none" }

(* The amount a tenant currently holds in live reservations. *)
RECURSIVE SumHeld(_, _)
SumHeld(S, t) ==
    IF S = {} THEN 0
    ELSE LET r == CHOOSE x \in S : TRUE
         IN (IF holder[r] = t THEN amt[r] ELSE 0) + SumHeld(S \ {r}, t)

Held(t) == SumHeld(live, t)

TypeInvariant ==
    /\ available \in [Tenants -> 0..Quota]
    /\ committed \in [Tenants -> 0..Quota]
    /\ closed \subseteq Tenants
    /\ live \subseteq ResIds
    /\ holder \in [ResIds -> Tenants \cup {NoTenant}]
    /\ amt \in [ResIds -> 0..Quota]
    /\ status \in { "accepted", "rejected", "init" }
    /\ reason \in Reasons

(* R1 -- conservation. The invariant M02, M07, M08 and M10 all break. *)
Conservation ==
    \A t \in Tenants : available[t] + Held(t) + committed[t] = Quota

(* R3 -- a closed tenant has no outstanding reservations. The invariant M03
   breaks, and it is CROSS-ASPECT: `closed` is written by a LEDGER-writing
   action whose guard reads RESERVATIONS. *)
ClosedHasNoOutstanding ==
    \A t \in closed : \A r \in live : holder[r] # t

(* R4 -- a rejection changes nothing. Expressed as: a rejected step leaves
   every variable but status/reason alone. This is what makes the negative
   corpus (HP-03) able to say anything at all: without it, a refused call has
   no modeled consequence to assert. *)
RejectionIsInert ==
    status = "rejected" => reason \in Reasons \ {"none"}

Init ==
    /\ available = [t \in Tenants |-> Quota]
    /\ committed = [t \in Tenants |-> 0]
    /\ closed = {}
    /\ live = {}
    /\ holder = [r \in ResIds |-> NoTenant]
    /\ amt = [r \in ResIds |-> 0]
    /\ ledger = << >>
    /\ status = "init"
    /\ reason = "none"

(* ------------------------------------------------------------------ *)
(* Accepting actions                                                   *)
(* ------------------------------------------------------------------ *)

Reserve(t, a, r) ==
    /\ t \notin closed
    /\ r \notin live
    /\ holder[r] = NoTenant          \* ids are never reused
    /\ a >= 1
    /\ a <= available[t]
    /\ available' = [available EXCEPT ![t] = @ - a]
    /\ live' = live \cup {r}
    /\ holder' = [holder EXCEPT ![r] = t]
    /\ amt' = [amt EXCEPT ![r] = a]
    /\ status' = "accepted"
    /\ reason' = "none"
    /\ UNCHANGED << committed, closed, ledger >>

Commit(r) ==
    /\ r \in live
    /\ live' = live \ {r}
    /\ committed' = [committed EXCEPT ![holder[r]] = @ + amt[r]]
    /\ ledger' = Append(ledger, << "COMMIT", holder[r], amt[r] >>)
    /\ status' = "accepted"
    /\ reason' = "none"
    /\ UNCHANGED << available, closed, holder, amt >>

Release(r) ==
    /\ r \in live
    /\ live' = live \ {r}
    /\ available' = [available EXCEPT ![holder[r]] = @ + amt[r]]
    /\ status' = "accepted"
    /\ reason' = "none"
    /\ UNCHANGED << committed, closed, holder, amt, ledger >>

CloseTenant(t) ==
    /\ t \notin closed
    /\ \A r \in live : holder[r] # t
    /\ closed' = closed \cup {t}
    /\ ledger' = Append(ledger, << "CLOSE", t, committed[t] >>)
    /\ status' = "accepted"
    /\ reason' = "none"
    /\ UNCHANGED << available, committed, live, holder, amt >>

(* ------------------------------------------------------------------ *)
(* Refusing actions -- the DISABLED edges, made explicit.               *)
(*                                                                     *)
(* These exist because of a measured, replicated zero: a corpus built   *)
(* from accepting edges alone never once asks the program to reject,    *)
(* so guard relaxation scored 0 of 3, 0 of 3 and 0 of 4 across three    *)
(* catalogues. Every refusal below leaves ALL domain state unchanged    *)
(* and reports a reason, which is exactly the assertion HP-03's         *)
(* negative corpus needs to emit.                                      *)
(* ------------------------------------------------------------------ *)

Refuse(rsn) ==
    /\ status' = "rejected"
    /\ reason' = rsn
    /\ UNCHANGED << available, committed, closed, live, holder, amt, ledger >>

RefuseReserveClosed(t, a, r) ==
    /\ t \in closed
    /\ Refuse("tenant_closed")

RefuseReserveNotPositive(t, a, r) ==
    /\ t \notin closed
    /\ a = 0
    /\ Refuse("amount_not_positive")

RefuseReserveOverQuota(t, a, r) ==
    /\ t \notin closed
    /\ a >= 1
    /\ a > available[t]
    /\ Refuse("quota_exceeded")

RefuseCommitUnknown(r) ==
    /\ r \notin live
    /\ Refuse("unknown_reservation")

RefuseReleaseUnknown(r) ==
    /\ r \notin live
    /\ Refuse("unknown_reservation")

RefuseCloseAlreadyClosed(t) ==
    /\ t \in closed
    /\ Refuse("tenant_closed")

RefuseCloseOutstanding(t) ==
    /\ t \notin closed
    /\ \E r \in live : holder[r] = t
    /\ Refuse("outstanding_reservations")

(* ------------------------------------------------------------------ *)

Next ==
    \/ \E t \in Tenants, a \in Amounts, r \in ResIds : Reserve(t, a, r)
    \/ \E r \in ResIds : Commit(r)
    \/ \E r \in ResIds : Release(r)
    \/ \E t \in Tenants : CloseTenant(t)
    \/ \E t \in Tenants, a \in Amounts, r \in ResIds : RefuseReserveClosed(t, a, r)
    \/ \E t \in Tenants, a \in Amounts, r \in ResIds : RefuseReserveNotPositive(t, a, r)
    \/ \E t \in Tenants, a \in Amounts, r \in ResIds : RefuseReserveOverQuota(t, a, r)
    \/ \E r \in ResIds : RefuseCommitUnknown(r)
    \/ \E r \in ResIds : RefuseReleaseUnknown(r)
    \/ \E t \in Tenants : RefuseCloseAlreadyClosed(t)
    \/ \E t \in Tenants : RefuseCloseOutstanding(t)

Spec == Init /\ [][Next]_vars

====
