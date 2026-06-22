----------------------------- MODULE Internal -----------------------------
EXTENDS Core

VARIABLES accounts, carts, orders, outbox, projections, lastInternalAction

InternalVars == <<accounts, carts, orders, outbox, projections, lastInternalAction>>

InternalInit ==
  /\ accounts = {}
  /\ carts = [a \in Accounts |-> <<>>]
  /\ orders = [o \in Orders |-> [account |-> CHOOSE a \in Accounts : TRUE, items |-> <<>>, status |-> "none"]]
  /\ outbox = {}
  /\ projections = [o \in Orders |-> "none"]
  /\ lastInternalAction = [name |-> "Init", params |-> [ ]]

CreateAccount(a) ==
  /\ a \notin accounts
  /\ accounts' = accounts \cup {a}
  /\ UNCHANGED <<carts, orders, outbox, projections>>
  /\ lastInternalAction' = [name |-> "CreateAccount", params |-> [account |-> a]]

AddCartItem(a, sku) ==
  /\ a \in accounts
  /\ sku \in Skus
  /\ carts' = [carts EXCEPT ![a] = Append(@, sku)]
  /\ UNCHANGED <<accounts, orders, outbox, projections>>
  /\ lastInternalAction' = [name |-> "AddCartItem", params |-> [account |-> a, sku |-> sku]]

Checkout(a, o) ==
  /\ a \in accounts
  /\ o \in Orders
  /\ orders[o].status = "none"
  /\ Len(carts[a]) > 0
  /\ orders' = [orders EXCEPT ![o] = [account |-> a, items |-> carts[a], status |-> "accepted"]]
  /\ outbox' = outbox \cup {o}
  /\ UNCHANGED <<accounts, carts, projections>>
  /\ lastInternalAction' = [name |-> "Checkout", params |-> [account |-> a, order |-> o]]

ProjectOrder(o) ==
  /\ o \in outbox
  /\ projections' = [projections EXCEPT ![o] = "ready_to_ship"]
  /\ outbox' = outbox \ {o}
  /\ UNCHANGED <<accounts, carts, orders>>
  /\ lastInternalAction' = [name |-> "ProjectOrder", params |-> [order |-> o]]

InternalNext ==
  \/ \E a \in Accounts : CreateAccount(a)
  \/ \E a \in Accounts, sku \in Skus : AddCartItem(a, sku)
  \/ \E a \in Accounts, o \in Orders : Checkout(a, o)
  \/ \E o \in Orders : ProjectOrder(o)

InternalInvariant ==
  /\ outbox \subseteq Orders
  /\ \A o \in outbox : orders[o].status = "accepted"

Spec == InternalInit /\ [][InternalNext]_InternalVars
Invariant == InternalInvariant

=============================================================================
