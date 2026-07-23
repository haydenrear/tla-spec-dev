----------------------------- MODULE Internal -----------------------------
EXTENDS Core

VARIABLES completed, outcome, decision, reason, referenceClass, attempts,
          lastInternalAction

InternalVars ==
  <<completed, outcome, decision, reason, referenceClass, attempts,
    lastInternalAction>>

InternalInit ==
  /\ completed = FALSE
  /\ outcome = "none"
  /\ decision = "none"
  /\ reason = ""
  /\ referenceClass = "none"
  /\ attempts = 0
  /\ lastInternalAction =
       [name |-> "Init",
        params |-> [payment_id |-> "", amount |-> 0,
                    idempotency_key |-> "", outcome |-> "none"]]

AuthorizeApproved(paymentId, amount, key) ==
  /\ ~completed
  /\ paymentId \in PaymentIds
  /\ amount \in Amounts
  /\ key \in IdempotencyKeys
  /\ completed' = TRUE
  /\ outcome' = "approved"
  /\ decision' = "approved"
  /\ reason' = ""
  /\ referenceClass' = "opaque"
  /\ attempts' = 1
  /\ lastInternalAction' =
       [name |-> "AuthorizeApproved",
        params |-> [payment_id |-> paymentId, amount |-> amount,
                    idempotency_key |-> key, outcome |-> "approved"]]

AuthorizeDeclined(paymentId, amount, key) ==
  /\ ~completed
  /\ paymentId \in PaymentIds
  /\ amount \in Amounts
  /\ key \in IdempotencyKeys
  /\ completed' = TRUE
  /\ outcome' = "declined"
  /\ decision' = "declined"
  /\ reason' = "insufficient_funds"
  /\ referenceClass' = "none"
  /\ attempts' = 1
  /\ lastInternalAction' =
       [name |-> "AuthorizeDeclined",
        params |-> [payment_id |-> paymentId, amount |-> amount,
                    idempotency_key |-> key, outcome |-> "declined"]]

AuthorizeBadRequest(paymentId, amount, key) ==
  /\ ~completed
  /\ paymentId \in PaymentIds
  /\ amount \in Amounts
  /\ key \in IdempotencyKeys
  /\ completed' = TRUE
  /\ outcome' = "bad_request"
  /\ decision' = "bad_request"
  /\ reason' = "invalid_request"
  /\ referenceClass' = "none"
  /\ attempts' = 1
  /\ lastInternalAction' =
       [name |-> "AuthorizeBadRequest",
        params |-> [payment_id |-> paymentId, amount |-> amount,
                    idempotency_key |-> key, outcome |-> "bad_request"]]

AuthorizeTransientThenApproved(paymentId, amount, key) ==
  /\ ~completed
  /\ paymentId \in PaymentIds
  /\ amount \in Amounts
  /\ key \in IdempotencyKeys
  /\ completed' = TRUE
  /\ outcome' = "transient_then_approved"
  /\ decision' = "approved"
  /\ reason' = ""
  /\ referenceClass' = "opaque"
  /\ attempts' = 2
  /\ lastInternalAction' =
       [name |-> "AuthorizeTransientThenApproved",
        params |-> [payment_id |-> paymentId, amount |-> amount,
                    idempotency_key |-> key,
                    outcome |-> "transient_then_approved"]]

AuthorizeTimeoutThenDuplicateApproved(paymentId, amount, key) ==
  /\ ~completed
  /\ paymentId \in PaymentIds
  /\ amount \in Amounts
  /\ key \in IdempotencyKeys
  /\ completed' = TRUE
  /\ outcome' = "timeout_then_duplicate_approved"
  /\ decision' = "approved"
  /\ reason' = ""
  /\ referenceClass' = "opaque"
  /\ attempts' = 2
  /\ lastInternalAction' =
       [name |-> "AuthorizeTimeoutThenDuplicateApproved",
        params |-> [payment_id |-> paymentId, amount |-> amount,
                    idempotency_key |-> key,
                    outcome |-> "timeout_then_duplicate_approved"]]

AuthorizeExhaustedUnavailable(paymentId, amount, key) ==
  /\ ~completed
  /\ paymentId \in PaymentIds
  /\ amount \in Amounts
  /\ key \in IdempotencyKeys
  /\ completed' = TRUE
  /\ outcome' = "exhausted_unavailable"
  /\ decision' = "unavailable"
  /\ reason' = "transport_exhausted"
  /\ referenceClass' = "none"
  /\ attempts' = 3
  /\ lastInternalAction' =
       [name |-> "AuthorizeExhaustedUnavailable",
        params |-> [payment_id |-> paymentId, amount |-> amount,
                    idempotency_key |-> key,
                    outcome |-> "exhausted_unavailable"]]

AuthorizeMalformedResponse(paymentId, amount, key) ==
  /\ ~completed
  /\ paymentId \in PaymentIds
  /\ amount \in Amounts
  /\ key \in IdempotencyKeys
  /\ completed' = TRUE
  /\ outcome' = "malformed_response"
  /\ decision' = "malformed_response"
  /\ reason' = "invalid_json"
  /\ referenceClass' = "none"
  /\ attempts' = 1
  /\ lastInternalAction' =
       [name |-> "AuthorizeMalformedResponse",
        params |-> [payment_id |-> paymentId, amount |-> amount,
                    idempotency_key |-> key, outcome |-> "malformed_response"]]

InternalNext ==
  \/ \E p \in PaymentIds, a \in Amounts, k \in IdempotencyKeys :
       AuthorizeApproved(p, a, k)
  \/ \E p \in PaymentIds, a \in Amounts, k \in IdempotencyKeys :
       AuthorizeDeclined(p, a, k)
  \/ \E p \in PaymentIds, a \in Amounts, k \in IdempotencyKeys :
       AuthorizeBadRequest(p, a, k)
  \/ \E p \in PaymentIds, a \in Amounts, k \in IdempotencyKeys :
       AuthorizeTransientThenApproved(p, a, k)
  \/ \E p \in PaymentIds, a \in Amounts, k \in IdempotencyKeys :
       AuthorizeTimeoutThenDuplicateApproved(p, a, k)
  \/ \E p \in PaymentIds, a \in Amounts, k \in IdempotencyKeys :
       AuthorizeExhaustedUnavailable(p, a, k)
  \/ \E p \in PaymentIds, a \in Amounts, k \in IdempotencyKeys :
       AuthorizeMalformedResponse(p, a, k)

TypeInvariant ==
  /\ completed \in BOOLEAN
  /\ outcome \in Outcomes
  /\ decision \in Decisions
  /\ reason \in Reasons
  /\ referenceClass \in ReferenceClasses
  /\ attempts \in 0..3

ResultInvariant ==
  /\ (~completed) =>
       /\ outcome = "none"
       /\ decision = "none"
       /\ attempts = 0
  /\ (outcome = "approved") =>
       /\ decision = "approved"
       /\ referenceClass = "opaque"
       /\ attempts = 1
  /\ (outcome = "declined") =>
       /\ decision = "declined"
       /\ reason = "insufficient_funds"
       /\ attempts = 1
  /\ (outcome = "bad_request") =>
       /\ decision = "bad_request"
       /\ reason = "invalid_request"
       /\ attempts = 1
  /\ (outcome = "transient_then_approved") =>
       /\ decision = "approved"
       /\ referenceClass = "opaque"
       /\ attempts = 2
  /\ (outcome = "timeout_then_duplicate_approved") =>
       /\ decision = "approved"
       /\ referenceClass = "opaque"
       /\ attempts = 2
  /\ (outcome = "exhausted_unavailable") =>
       /\ decision = "unavailable"
       /\ reason = "transport_exhausted"
       /\ attempts = 3
  /\ (outcome = "malformed_response") =>
       /\ decision = "malformed_response"
       /\ reason = "invalid_json"
       /\ attempts = 1

InternalSpec == InternalInit /\ [][InternalNext]_InternalVars

=============================================================================
