------------------------------- MODULE Core -------------------------------
EXTENDS Naturals, Sequences, FiniteSets

CONSTANTS Accounts, Skus, Orders

Status == {"none", "accepted"}
VisibleStatus == {"ready_to_ship"}

EmptyState ==
  [ accounts |-> {},
    carts |-> [a \in Accounts |-> <<>>],
    orders |-> [o \in Orders |-> [account |-> CHOOSE a \in Accounts : TRUE, items |-> <<>>, status |-> "none"]],
    outbox |-> {},
    projections |-> [o \in Orders |-> "none"] ]

CartContains(cart, sku) == sku \in SeqToSet(cart)

=============================================================================
