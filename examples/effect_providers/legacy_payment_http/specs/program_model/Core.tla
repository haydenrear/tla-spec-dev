------------------------------- MODULE Core -------------------------------
EXTENDS Naturals, FiniteSets, Sequences

CONSTANTS PaymentIds, Amounts, IdempotencyKeys

Outcomes == {
  "none",
  "approved",
  "declined",
  "bad_request",
  "transient_then_approved",
  "timeout_then_duplicate_approved",
  "exhausted_unavailable",
  "malformed_response"
}

Decisions == {
  "none",
  "approved",
  "declined",
  "bad_request",
  "unavailable",
  "malformed_response"
}

Reasons == {
  "",
  "insufficient_funds",
  "invalid_request",
  "transport_exhausted",
  "invalid_json"
}

ReferenceClasses == {"none", "opaque"}

=============================================================================

