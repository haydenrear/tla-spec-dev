-------------------------- MODULE Scenario_IdempotentResubmit --------------------------
\* BDD PROBE, scenario 2: "a client that resubmits an already-applied command
\* gets the same answer and changes nothing".
\*
\* The GIVEN is an initial-state predicate, not a replay of the setup actions:
\* the account exists, the cart is filled, order-1 is accepted and queued. That
\* is what keeps the slice small -- the prefix is asserted, not enumerated.
EXTENDS External

IdempotentGiven ==
  /\ accounts = Accounts
  /\ carts = [a \in Accounts |-> <<"sku-1">>]
  /\ orders = [o \in Orders |->
        IF o = "order-1"
        THEN [account |-> "acct-1", items |-> <<"sku-1">>, status |-> "accepted"]
        ELSE [account |-> "acct-1", items |-> <<>>, status |-> "none"]]
  /\ outbox = {"order-1"}
  /\ projections = [o \in Orders |-> "none"]
  /\ lastInternalAction = [name |-> "Given", params |-> <<>>]
  /\ responses = [c \in Clients |-> [status |-> 0, body |-> <<>>]]
  /\ serviceHealth = [service \in Services |-> "up"]
  /\ lastServiceRoute = [client |-> CHOOSE c \in Clients : TRUE, services |-> <<>>]
  /\ lastExternalAction = [name |-> "Given", params |-> <<>>]

IdempotentNext ==
  \/ \E c \in Clients, a \in Accounts : SubmitDuplicateCreateAccount(c, a)
  \/ \E c \in Clients, a \in Accounts, sku \in Skus : SubmitDuplicateAddCartItem(c, a, sku)
  \/ \E c \in Clients, a \in Accounts, o \in Orders : SubmitDuplicateCheckout(c, a, o)
  \/ \E c \in Clients : RunFulfillmentWorker(c)
  \/ \E c \in Clients : RunFulfillmentWorkerNoop(c)

IdempotentSpec == IdempotentGiven /\ [][IdempotentNext]_ExternalVars

=============================================================================
