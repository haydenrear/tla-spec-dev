----------------------------- MODULE External -----------------------------
EXTENDS Internal

VARIABLES responses, lastExternalAction

ExternalVars == <<InternalVars, responses, lastExternalAction>>

ExternalInit ==
  /\ InternalInit
  /\ responses = [a \in Accounts |-> [status |-> 0, body |-> <<>>]]
  /\ lastExternalAction = [name |-> "Init", params |-> <<>>]

SubmitCreateAccount(a) ==
  /\ CreateAccount(a)
  /\ responses' = [responses EXCEPT ![a] = [status |-> 201, body |-> [account |-> a]]]
  /\ lastExternalAction' = [name |-> "SubmitCreateAccount", params |-> [account |-> a]]

SubmitDuplicateCreateAccount(a) ==
  /\ a \in accounts
  /\ UNCHANGED InternalVars
  /\ responses' = [responses EXCEPT ![a] = [status |-> 201, body |-> [account |-> a]]]
  /\ lastExternalAction' = [name |-> "SubmitDuplicateCreateAccount", params |-> [account |-> a]]

SubmitAddCartItem(a, sku) ==
  /\ AddCartItem(a, sku)
  /\ responses' = [responses EXCEPT ![a] = [status |-> 202, body |-> [account |-> a, sku |-> sku]]]
  /\ lastExternalAction' = [name |-> "SubmitAddCartItem", params |-> [account |-> a, sku |-> sku]]

SubmitAddCartItemMissingAccount(a, sku) ==
  /\ a \notin accounts
  /\ sku \in Skus
  /\ UNCHANGED InternalVars
  /\ responses' = [responses EXCEPT ![a] = [status |-> 404, body |-> [error |-> "account_not_found"]]]
  /\ lastExternalAction' = [name |-> "SubmitAddCartItemMissingAccount", params |-> [account |-> a, sku |-> sku]]

SubmitCheckout(a, o) ==
  /\ Checkout(a, o)
  /\ responses' = [responses EXCEPT ![a] = [status |-> 202, body |-> [order |-> o, status |-> "accepted"]]]
  /\ lastExternalAction' = [name |-> "SubmitCheckout", params |-> [account |-> a, order |-> o]]

SubmitCheckoutMissingAccount(a, o) ==
  /\ a \notin accounts
  /\ o \in Orders
  /\ UNCHANGED InternalVars
  /\ responses' = [responses EXCEPT ![a] = [status |-> 404, body |-> [error |-> "account_not_found"]]]
  /\ lastExternalAction' = [name |-> "SubmitCheckoutMissingAccount", params |-> [account |-> a, order |-> o]]

SubmitCheckoutEmptyCart(a, o) ==
  /\ a \in accounts
  /\ o \in Orders
  /\ Len(carts[a]) = 0
  /\ orders[o].status = "none"
  /\ UNCHANGED InternalVars
  /\ responses' = [responses EXCEPT ![a] = [status |-> 409, body |-> [error |-> "empty_cart"]]]
  /\ lastExternalAction' = [name |-> "SubmitCheckoutEmptyCart", params |-> [account |-> a, order |-> o]]

SubmitDuplicateCheckout(a, o) ==
  /\ a \in accounts
  /\ o \in Orders
  /\ orders[o].status # "none"
  /\ UNCHANGED InternalVars
  /\ responses' = [responses EXCEPT ![a] = [status |-> 200, body |-> [order |-> o, idempotent |-> TRUE]]]
  /\ lastExternalAction' = [name |-> "SubmitDuplicateCheckout", params |-> [account |-> a, order |-> o]]

RunFulfillmentWorker ==
  /\ \E o \in Orders : ProjectOrder(o)
  /\ UNCHANGED responses
  /\ lastExternalAction' = [name |-> "RunFulfillmentWorker", params |-> <<>>]

RunFulfillmentWorkerNoop ==
  /\ outbox = {}
  /\ UNCHANGED InternalVars
  /\ UNCHANGED responses
  /\ lastExternalAction' = [name |-> "RunFulfillmentWorkerNoop", params |-> <<>>]

HiddenInternalProgress ==
  /\ InternalNext
  /\ UNCHANGED <<responses, lastExternalAction>>

ExternalNext ==
  \/ \E a \in Accounts : SubmitCreateAccount(a)
  \/ \E a \in Accounts : SubmitDuplicateCreateAccount(a)
  \/ \E a \in Accounts, sku \in Skus : SubmitAddCartItem(a, sku)
  \/ \E a \in Accounts, sku \in Skus : SubmitAddCartItemMissingAccount(a, sku)
  \/ \E a \in Accounts, o \in Orders : SubmitCheckout(a, o)
  \/ \E a \in Accounts, o \in Orders : SubmitCheckoutMissingAccount(a, o)
  \/ \E a \in Accounts, o \in Orders : SubmitCheckoutEmptyCart(a, o)
  \/ \E a \in Accounts, o \in Orders : SubmitDuplicateCheckout(a, o)
  \/ RunFulfillmentWorker
  \/ RunFulfillmentWorkerNoop
  \/ HiddenInternalProgress

ExternalInvariant == InternalInvariant

Spec == ExternalInit /\ [][ExternalNext]_ExternalVars
Invariant == ExternalInvariant

=============================================================================
