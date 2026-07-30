-------------------- MODULE Scenario_IntakeToDelivery --------------------
\* ASPECT: "an item that arrives is accepted, queued, and handed to delivery"
\* (README, "What the service promises", first sentence).
\*
\* FORM: slice. Init is unchanged -- this aspect starts from the start, with
\* everything still in the inbox. Only the next-state relation is restricted,
\* to the three entry points the intake path uses.
\*
\* This module declares no VARIABLES, no CONSTANTS and no actions. Delete it
\* and the program is still fully represented by Pipeline.tla.
EXTENDS Pipeline

IntakeToDeliveryNext ==
  \/ \E i \in Items : Accept(i)
  \/ \E i \in Items : Enqueue(i)
  \/ \E i \in Items : Deliver(i)

IntakeToDeliverySpec == Init /\ [][IntakeToDeliveryNext]_vars
==============================================================================
