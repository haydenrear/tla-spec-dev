----------------------------- MODULE External -----------------------------
EXTENDS Internal

VARIABLES responses, lastExternalAction

ExternalVars == <<InternalVars, responses, lastExternalAction>>

ExternalInit ==
  /\ InternalInit
  /\ responses = [a \in Accounts |-> [status |-> 0, body |-> [ ]]]
  /\ lastExternalAction = [name |-> "Init", params |-> [ ]]

SubmitCreateAccount(a) ==
  /\ CreateAccount(a)
  /\ responses' = [responses EXCEPT ![a] = [status |-> 201, body |-> [account |-> a]]]
  /\ lastExternalAction' = [name |-> "SubmitCreateAccount", params |-> [account |-> a]]

SubmitAddCartItem(a, sku) ==
  /\ AddCartItem(a, sku)
  /\ responses' = [responses EXCEPT ![a] = [status |-> 202, body |-> [account |-> a, sku |-> sku]]]
  /\ lastExternalAction' = [name |-> "SubmitAddCartItem", params |-> [account |-> a, sku |-> sku]]

SubmitCheckout(a, o) ==
  /\ Checkout(a, o)
  /\ responses' = [responses EXCEPT ![a] = [status |-> 202, body |-> [order |-> o, status |-> "accepted"]]]
  /\ lastExternalAction' = [name |-> "SubmitCheckout", params |-> [account |-> a, order |-> o]]

RunFulfillmentWorker ==
  /\ \E o \in Orders : ProjectOrder(o)
  /\ UNCHANGED responses
  /\ lastExternalAction' = [name |-> "RunFulfillmentWorker", params |-> [ ]]

HiddenInternalProgress ==
  /\ InternalNext
  /\ UNCHANGED <<responses, lastExternalAction>>

ExternalNext ==
  \/ \E a \in Accounts : SubmitCreateAccount(a)
  \/ \E a \in Accounts, sku \in Skus : SubmitAddCartItem(a, sku)
  \/ \E a \in Accounts, o \in Orders : SubmitCheckout(a, o)
  \/ RunFulfillmentWorker
  \/ HiddenInternalProgress

ExternalInvariant == InternalInvariant

Spec == ExternalInit /\ [][ExternalNext]_ExternalVars
Invariant == ExternalInvariant

=============================================================================
