-------------------------- MODULE Scenario_CheckoutHappyPath --------------------------
\* BDD PROBE: a case-generator module for ONE aspect of the program --
\* "a client can create an account, fill a cart, check out, and see the order
\* become ready to ship". It adds no state and no actions; it imports the
\* External view and restricts the next-state relation to the entry points
\* this aspect exercises.
EXTENDS External

CheckoutHappyPathNext ==
  \/ \E c \in Clients, a \in Accounts : SubmitCreateAccount(c, a)
  \/ \E c \in Clients, a \in Accounts, sku \in Skus : SubmitAddCartItem(c, a, sku)
  \/ \E c \in Clients, a \in Accounts, o \in Orders : SubmitCheckout(c, a, o)
  \/ \E c \in Clients : RunFulfillmentWorker(c)

CheckoutHappyPathSpec == ExternalInit /\ [][CheckoutHappyPathNext]_ExternalVars

=============================================================================
