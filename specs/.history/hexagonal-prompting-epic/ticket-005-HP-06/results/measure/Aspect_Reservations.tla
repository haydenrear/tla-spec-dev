---- MODULE Aspect_Reservations ----
(***************************************************************************)
(* HP-06 measurement instrument -- the RESERVATIONS aspect slice declared   *)
(* in examples/validation/ab/model/spec_manifest.yaml.                     *)
(*                                                                         *)
(* Form 1 (slice): restrict Next, keep Init. The action list is copied      *)
(* verbatim from the manifest's `case_modules.Aspect_Reservations.actions`. *)
(* Nothing here is authored freely: a slice that entered actions the        *)
(* manifest does not declare would not be the slice whose gap M08 was       *)
(* seeded into.                                                            *)
(*                                                                         *)
(* The manifest's `claim` also says this slice does NOT project `committed` *)
(* or the ledger. That half is carried by the state projector in            *)
(* aspect_projectors.py, because a TLA+ slice inherits every VARIABLE of    *)
(* the module it extends and the projection is a generator-side choice.     *)
(***************************************************************************)
EXTENDS QuotaLedger

NextReservations ==
    \/ \E t \in Tenants, a \in Amounts, r \in ResIds : Reserve(t, a, r)
    \/ \E r \in ResIds : Release(r)
    \/ \E t \in Tenants, a \in Amounts, r \in ResIds : RefuseReserveClosed(t, a, r)
    \/ \E t \in Tenants, a \in Amounts, r \in ResIds : RefuseReserveNotPositive(t, a, r)
    \/ \E t \in Tenants, a \in Amounts, r \in ResIds : RefuseReserveOverQuota(t, a, r)
    \/ \E r \in ResIds : RefuseReleaseUnknown(r)

SpecReservations == Init /\ [][NextReservations]_vars

====
