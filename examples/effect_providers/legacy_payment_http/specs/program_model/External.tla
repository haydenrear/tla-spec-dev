----------------------------- MODULE External -----------------------------
EXTENDS Internal

VARIABLE lastExternalAction

ExternalVars == <<InternalVars, lastExternalAction>>

ExternalInit ==
  /\ InternalInit
  /\ lastExternalAction =
       [name |-> "Init",
        params |-> [payment_id |-> "", amount |-> 0,
                    idempotency_key |-> "", outcome |-> "none"]]

MarkExternal(actionName, paymentId, amount, key, selectedOutcome) ==
  lastExternalAction' =
    [name |-> actionName,
     params |-> [payment_id |-> paymentId, amount |-> amount,
                 idempotency_key |-> key, outcome |-> selectedOutcome]]

SubmitApproved(paymentId, amount, key) ==
  /\ AuthorizeApproved(paymentId, amount, key)
  /\ MarkExternal("SubmitApproved", paymentId, amount, key, "approved")

SubmitDeclined(paymentId, amount, key) ==
  /\ AuthorizeDeclined(paymentId, amount, key)
  /\ MarkExternal("SubmitDeclined", paymentId, amount, key, "declined")

SubmitBadRequest(paymentId, amount, key) ==
  /\ AuthorizeBadRequest(paymentId, amount, key)
  /\ MarkExternal("SubmitBadRequest", paymentId, amount, key, "bad_request")

SubmitTransientThenApproved(paymentId, amount, key) ==
  /\ AuthorizeTransientThenApproved(paymentId, amount, key)
  /\ MarkExternal("SubmitTransientThenApproved", paymentId, amount, key,
                  "transient_then_approved")

SubmitTimeoutThenDuplicateApproved(paymentId, amount, key) ==
  /\ AuthorizeTimeoutThenDuplicateApproved(paymentId, amount, key)
  /\ MarkExternal("SubmitTimeoutThenDuplicateApproved", paymentId, amount, key,
                  "timeout_then_duplicate_approved")

SubmitExhaustedUnavailable(paymentId, amount, key) ==
  /\ AuthorizeExhaustedUnavailable(paymentId, amount, key)
  /\ MarkExternal("SubmitExhaustedUnavailable", paymentId, amount, key,
                  "exhausted_unavailable")

SubmitMalformedResponse(paymentId, amount, key) ==
  /\ AuthorizeMalformedResponse(paymentId, amount, key)
  /\ MarkExternal("SubmitMalformedResponse", paymentId, amount, key,
                  "malformed_response")

ExternalNext ==
  \/ \E p \in PaymentIds, a \in Amounts, k \in IdempotencyKeys :
       SubmitApproved(p, a, k)
  \/ \E p \in PaymentIds, a \in Amounts, k \in IdempotencyKeys :
       SubmitDeclined(p, a, k)
  \/ \E p \in PaymentIds, a \in Amounts, k \in IdempotencyKeys :
       SubmitBadRequest(p, a, k)
  \/ \E p \in PaymentIds, a \in Amounts, k \in IdempotencyKeys :
       SubmitTransientThenApproved(p, a, k)
  \/ \E p \in PaymentIds, a \in Amounts, k \in IdempotencyKeys :
       SubmitTimeoutThenDuplicateApproved(p, a, k)
  \/ \E p \in PaymentIds, a \in Amounts, k \in IdempotencyKeys :
       SubmitExhaustedUnavailable(p, a, k)
  \/ \E p \in PaymentIds, a \in Amounts, k \in IdempotencyKeys :
       SubmitMalformedResponse(p, a, k)

ExternalSpec == ExternalInit /\ [][ExternalNext]_ExternalVars

=============================================================================

