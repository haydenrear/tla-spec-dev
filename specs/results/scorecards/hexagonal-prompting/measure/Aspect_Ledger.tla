---- MODULE Aspect_Ledger ----
(***************************************************************************)
(* HP-06 measurement instrument -- the LEDGER aspect slice declared in      *)
(* examples/validation/ab/model/spec_manifest.yaml.                        *)
(*                                                                         *)
(* Form 1 (slice): restrict Next, keep Init. The action list is copied      *)
(* verbatim from `case_modules.Aspect_Ledger.actions`.                     *)
(*                                                                         *)
(* NOTE, and it is a real limit of this slice rather than an oversight:     *)
(* with Reserve excluded, `live` is empty in every reachable state, so      *)
(* Commit is DISABLED everywhere and the slice enters only CloseTenant and  *)
(* the refusals. That is a property of the manifest's declared action list, *)
(* not of this file. It is reported rather than repaired -- widening the    *)
(* slice to make Commit reachable would make it a different slice from the  *)
(* one M08 was seeded against.                                             *)
(***************************************************************************)
EXTENDS QuotaLedger

NextLedger ==
    \/ \E r \in ResIds : Commit(r)
    \/ \E t \in Tenants : CloseTenant(t)
    \/ \E r \in ResIds : RefuseCommitUnknown(r)
    \/ \E t \in Tenants : RefuseCloseAlreadyClosed(t)
    \/ \E t \in Tenants : RefuseCloseOutstanding(t)

SpecLedger == Init /\ [][NextLedger]_vars

====
