---- MODULE Scenario_DeliveryPath ----
EXTENDS Pipeline

DeliveryPathNext ==
  \/ \E i \in Items : Accept(i)
  \/ \E i \in Items : Enqueue(i)
  \/ \E i \in Items : Deliver(i)

DeliveryPathSpec == Init /\ [][DeliveryPathNext]_vars
====
