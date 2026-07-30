--------------------- MODULE Scenario_DurableOutcome ---------------------
\* ASPECT: "a delivery either succeeds or fails ... either way the ledger
\* records each outcome, and the ledger is persisted through the store port"
\* (README, "What the service promises", second and third sentences).
\*
\* FORM: given. Init is REPLACED by an asserted pre-state, so the aspect does
\* not re-enumerate the intake path it would otherwise have to walk.
\*
\* CLAIM (this is the modeling claim the Given makes, and the thing to review):
\*
\*   What happens to a delivered item -- whether it fails, whether it reaches
\*   the ledger, and what the durable store ends up holding -- is INDEPENDENT
\*   OF the intake path the item took to become delivered, i.e. of which
\*   reachable (inbox, accepted, queue) configuration it was delivered from.
\*
\* Falsifiable: it is false the moment Fail or Record reads inbox, accepted or
\* queue. Today neither does (see Pipeline.tla), so the Given is sound; a
\* change that makes either read the ingest side must revisit this module.
\*
\* Every one of the view's six variables is constrained below. Leaving one
\* free would put TLC's whole-domain enumeration back and the module would be
\* neither the reduction nor the situation described.
EXTENDS Pipeline

DurableOutcomeInit ==
  /\ inbox = {}            \* intake is finished ...
  /\ accepted = Items      \* ... every item was accepted ...
  /\ queue = {}            \* ... and the queue has been drained.
  /\ delivered = Items     \* Both items are delivered, awaiting an outcome.
  /\ failed = {}           \* Nothing has failed yet.
  /\ ledger = {}           \* Nothing has been recorded yet.

DurableOutcomeNext ==
  \/ \E i \in Items : Fail(i)
  \/ \E i \in Items : Record(i)

DurableOutcomeSpec == DurableOutcomeInit /\ [][DurableOutcomeNext]_vars
==============================================================================
