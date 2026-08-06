---- MODULE Scenario_RecordAfterDelivery ----
EXTENDS Pipeline

RecordAfterDeliveryInit ==
  \E i \in Items :
    /\ inbox = Items \ {i}
    /\ accepted = {i}
    /\ queue = {}
    /\ delivered = {i}
    /\ failed = {}
    /\ ledger = {}

RecordAfterDeliveryNext ==
  \/ \E i \in Items : Record(i)
  \/ \E i \in Items : Fail(i)

RecordAfterDeliverySpec ==
  RecordAfterDeliveryInit /\ [][RecordAfterDeliveryNext]_vars
====
