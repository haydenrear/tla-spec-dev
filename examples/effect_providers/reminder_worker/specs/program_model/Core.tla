----------------------------- MODULE Core -----------------------------
EXTENDS Naturals, TLC

Scenarios == {"empty", "not_due", "accepted", "retryable", "permanent", "duplicate", "pending"}
QueueStates == {"empty", "ready", "acked", "dead"}
OutboxStates == {"none", "pending", "sent"}
ReceiptStates == {"none", "stored"}
Results == {"ready", "empty", "not_due", "accepted", "retryable", "permanent", "duplicate"}

=============================================================================
