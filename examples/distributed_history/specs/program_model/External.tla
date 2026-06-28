----------------------------- MODULE External -----------------------------
EXTENDS Internal

CONSTANTS Clients

VARIABLES responses, serviceHealth, lastServiceRoute, lastExternalAction

Services == {
  "gateway-service",
  "account-service",
  "cart-service",
  "checkout-service",
  "worker-service",
  "database-service",
  "queue-service"
}

CreateAccountRoute == <<"gateway-service", "account-service", "database-service">>
CartRoute == <<"gateway-service", "cart-service", "database-service">>
CheckoutReadRoute == <<"gateway-service", "checkout-service", "database-service">>
CheckoutAcceptRoute == <<"gateway-service", "checkout-service", "database-service", "queue-service">>
WorkerRoute == <<"gateway-service", "worker-service", "queue-service", "database-service">>

ExternalVars == <<InternalVars, responses, serviceHealth, lastServiceRoute, lastExternalAction>>

ExternalInit ==
  /\ InternalInit
  /\ responses = [c \in Clients |-> [status |-> 0, body |-> <<>>]]
  /\ serviceHealth = [service \in Services |-> "up"]
  /\ lastServiceRoute = [client |-> CHOOSE c \in Clients : TRUE, services |-> <<>>]
  /\ lastExternalAction = [name |-> "Init", params |-> <<>>]

ServicesAvailable(route) ==
  \A service \in SeqToSet(route) : serviceHealth[service] = "up"

MarkExternal(c, actionName, params, route) ==
  /\ serviceHealth' = serviceHealth
  /\ lastServiceRoute' = [client |-> c, services |-> route]
  /\ lastExternalAction' = [name |-> actionName, params |-> params]

SubmitCreateAccount(c, a) ==
  /\ c \in Clients
  /\ ServicesAvailable(CreateAccountRoute)
  /\ CreateAccount(a)
  /\ responses' = [responses EXCEPT ![c] = [status |-> 201, body |-> [account |-> a]]]
  /\ MarkExternal(c, "SubmitCreateAccount", [client |-> c, account |-> a, route |-> CreateAccountRoute], CreateAccountRoute)

SubmitDuplicateCreateAccount(c, a) ==
  /\ c \in Clients
  /\ ServicesAvailable(CreateAccountRoute)
  /\ a \in accounts
  /\ UNCHANGED InternalVars
  /\ responses' = [responses EXCEPT ![c] = [status |-> 201, body |-> [account |-> a]]]
  /\ MarkExternal(c, "SubmitDuplicateCreateAccount", [client |-> c, account |-> a, route |-> CreateAccountRoute], CreateAccountRoute)

SubmitAddCartItem(c, a, sku) ==
  /\ c \in Clients
  /\ ServicesAvailable(CartRoute)
  /\ AddCartItem(a, sku)
  /\ responses' = [responses EXCEPT ![c] = [status |-> 202, body |-> [account |-> a, sku |-> sku]]]
  /\ MarkExternal(c, "SubmitAddCartItem", [client |-> c, account |-> a, sku |-> sku, route |-> CartRoute], CartRoute)

SubmitDuplicateAddCartItem(c, a, sku) ==
  /\ c \in Clients
  /\ ServicesAvailable(CartRoute)
  /\ a \in accounts
  /\ sku \in Skus
  /\ CartContains(carts[a], sku)
  /\ UNCHANGED InternalVars
  /\ responses' = [responses EXCEPT ![c] = [status |-> 202, body |-> [account |-> a, sku |-> sku]]]
  /\ MarkExternal(c, "SubmitDuplicateAddCartItem", [client |-> c, account |-> a, sku |-> sku, route |-> CartRoute], CartRoute)

SubmitAddCartItemMissingAccount(c, a, sku) ==
  /\ c \in Clients
  /\ ServicesAvailable(CartRoute)
  /\ a \notin accounts
  /\ sku \in Skus
  /\ UNCHANGED InternalVars
  /\ responses' = [responses EXCEPT ![c] = [status |-> 404, body |-> [error |-> "account_not_found"]]]
  /\ MarkExternal(c, "SubmitAddCartItemMissingAccount", [client |-> c, account |-> a, sku |-> sku, route |-> CartRoute], CartRoute)

SubmitCheckout(c, a, o) ==
  /\ c \in Clients
  /\ ServicesAvailable(CheckoutAcceptRoute)
  /\ Checkout(a, o)
  /\ responses' = [responses EXCEPT ![c] = [status |-> 202, body |-> [order |-> o, status |-> "accepted"]]]
  /\ MarkExternal(c, "SubmitCheckout", [client |-> c, account |-> a, order |-> o, route |-> CheckoutAcceptRoute], CheckoutAcceptRoute)

SubmitCheckoutMissingAccount(c, a, o) ==
  /\ c \in Clients
  /\ ServicesAvailable(CheckoutReadRoute)
  /\ a \notin accounts
  /\ o \in Orders
  /\ UNCHANGED InternalVars
  /\ responses' = [responses EXCEPT ![c] = [status |-> 404, body |-> [error |-> "account_not_found"]]]
  /\ MarkExternal(c, "SubmitCheckoutMissingAccount", [client |-> c, account |-> a, order |-> o, route |-> CheckoutReadRoute], CheckoutReadRoute)

SubmitCheckoutEmptyCart(c, a, o) ==
  /\ c \in Clients
  /\ ServicesAvailable(CheckoutReadRoute)
  /\ a \in accounts
  /\ o \in Orders
  /\ Len(carts[a]) = 0
  /\ orders[o].status = "none"
  /\ UNCHANGED InternalVars
  /\ responses' = [responses EXCEPT ![c] = [status |-> 409, body |-> [error |-> "empty_cart"]]]
  /\ MarkExternal(c, "SubmitCheckoutEmptyCart", [client |-> c, account |-> a, order |-> o, route |-> CheckoutReadRoute], CheckoutReadRoute)

SubmitDuplicateCheckout(c, a, o) ==
  /\ c \in Clients
  /\ ServicesAvailable(CheckoutReadRoute)
  /\ a \in accounts
  /\ o \in Orders
  /\ orders[o].status # "none"
  /\ UNCHANGED InternalVars
  /\ responses' = [responses EXCEPT ![c] = [status |-> 200, body |-> [order |-> o, idempotent |-> TRUE]]]
  /\ MarkExternal(c, "SubmitDuplicateCheckout", [client |-> c, account |-> a, order |-> o, route |-> CheckoutReadRoute], CheckoutReadRoute)

ProjectAllOutbox ==
  /\ outbox # {}
  /\ projections' = [o \in Orders |-> IF o \in outbox THEN "ready_to_ship" ELSE projections[o]]
  /\ outbox' = {}
  /\ UNCHANGED <<accounts, carts, orders>>
  /\ lastInternalAction' = [name |-> "ProjectAllOutbox", params |-> [orders |-> outbox]]

RunFulfillmentWorker(c) ==
  /\ c \in Clients
  /\ ServicesAvailable(WorkerRoute)
  /\ ProjectAllOutbox
  /\ UNCHANGED responses
  /\ MarkExternal(c, "RunFulfillmentWorker", [client |-> c, limit |-> Cardinality(outbox), route |-> WorkerRoute], WorkerRoute)

RunFulfillmentWorkerNoop(c) ==
  /\ c \in Clients
  /\ ServicesAvailable(WorkerRoute)
  /\ outbox = {}
  /\ UNCHANGED InternalVars
  /\ UNCHANGED responses
  /\ MarkExternal(c, "RunFulfillmentWorkerNoop", [client |-> c, limit |-> 0, route |-> WorkerRoute], WorkerRoute)

HiddenInternalProgress ==
  /\ InternalNext
  /\ UNCHANGED <<responses, serviceHealth, lastServiceRoute, lastExternalAction>>

ExternalNext ==
  \/ \E c \in Clients, a \in Accounts : SubmitCreateAccount(c, a)
  \/ \E c \in Clients, a \in Accounts : SubmitDuplicateCreateAccount(c, a)
  \/ \E c \in Clients, a \in Accounts, sku \in Skus : SubmitAddCartItem(c, a, sku)
  \/ \E c \in Clients, a \in Accounts, sku \in Skus : SubmitDuplicateAddCartItem(c, a, sku)
  \/ \E c \in Clients, a \in Accounts, sku \in Skus : SubmitAddCartItemMissingAccount(c, a, sku)
  \/ \E c \in Clients, a \in Accounts, o \in Orders : SubmitCheckout(c, a, o)
  \/ \E c \in Clients, a \in Accounts, o \in Orders : SubmitCheckoutMissingAccount(c, a, o)
  \/ \E c \in Clients, a \in Accounts, o \in Orders : SubmitCheckoutEmptyCart(c, a, o)
  \/ \E c \in Clients, a \in Accounts, o \in Orders : SubmitDuplicateCheckout(c, a, o)
  \/ \E c \in Clients : RunFulfillmentWorker(c)
  \/ \E c \in Clients : RunFulfillmentWorkerNoop(c)
  \/ HiddenInternalProgress

ExternalInvariant ==
  /\ InternalInvariant
  /\ \A service \in Services : serviceHealth[service] = "up"
  /\ \A service \in SeqToSet(lastServiceRoute.services) : service \in Services

Spec == ExternalInit /\ [][ExternalNext]_ExternalVars
Invariant == ExternalInvariant

=============================================================================
