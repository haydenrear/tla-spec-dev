-------------------------- MODULE Scenario_RejectedRequests --------------------------
\* BDD PROBE, scenario 3: "requests the program must refuse -- unknown account,
\* empty cart -- are refused with the documented status and change nothing".
\* Starts from the pristine Init because 'no account yet' IS the given here;
\* SubmitCreateAccount is included only as the step that opens the empty-cart
\* rejection.
EXTENDS External

RejectedNext ==
  \/ \E c \in Clients, a \in Accounts : SubmitCreateAccount(c, a)
  \/ \E c \in Clients, a \in Accounts, sku \in Skus : SubmitAddCartItemMissingAccount(c, a, sku)
  \/ \E c \in Clients, a \in Accounts, o \in Orders : SubmitCheckoutMissingAccount(c, a, o)
  \/ \E c \in Clients, a \in Accounts, o \in Orders : SubmitCheckoutEmptyCart(c, a, o)

RejectedSpec == ExternalInit /\ [][RejectedNext]_ExternalVars

=============================================================================
