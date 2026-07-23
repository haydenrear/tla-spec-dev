----------------------------- MODULE Internal -----------------------------
EXTENDS Core

VARIABLES scenario, queueState, outboxState, notificationCount,
          receiptState, result, lastInternalAction

InternalVars ==
  <<scenario, queueState, outboxState, notificationCount,
    receiptState, result, lastInternalAction>>

InitScenario(s, q, o, r) ==
  /\ scenario = s
  /\ queueState = q
  /\ outboxState = o
  /\ notificationCount = 0
  /\ receiptState = r
  /\ result = "ready"
  /\ lastInternalAction = [name |-> "Init", params |-> [scenario |-> s]]

InternalInit ==
  \/ InitScenario("empty", "empty", "none", "none")
  \/ InitScenario("not_due", "ready", "none", "none")
  \/ InitScenario("accepted", "ready", "none", "none")
  \/ InitScenario("retryable", "ready", "none", "none")
  \/ InitScenario("permanent", "ready", "none", "none")
  \/ InitScenario("duplicate", "ready", "sent", "stored")
  \/ InitScenario("pending", "ready", "pending", "none")

ProcessEmpty ==
  /\ scenario = "empty"
  /\ result = "ready"
  /\ UNCHANGED scenario
  /\ queueState' = "empty"
  /\ outboxState' = "none"
  /\ notificationCount' = 0
  /\ receiptState' = "none"
  /\ result' = "empty"
  /\ lastInternalAction' = [name |-> "ProcessEmpty", params |-> [scenario |-> scenario]]

ProcessNotDue ==
  /\ scenario = "not_due"
  /\ result = "ready"
  /\ UNCHANGED scenario
  /\ queueState' = "ready"
  /\ outboxState' = "none"
  /\ notificationCount' = 0
  /\ receiptState' = "none"
  /\ result' = "not_due"
  /\ lastInternalAction' = [name |-> "ProcessNotDue", params |-> [scenario |-> scenario]]

ProcessAccepted ==
  /\ scenario = "accepted"
  /\ result = "ready"
  /\ UNCHANGED scenario
  /\ queueState' = "acked"
  /\ outboxState' = "sent"
  /\ notificationCount' = 1
  /\ receiptState' = "stored"
  /\ result' = "accepted"
  /\ lastInternalAction' = [name |-> "ProcessAccepted", params |-> [scenario |-> scenario]]

ProcessRetryable ==
  /\ scenario = "retryable"
  /\ result = "ready"
  /\ UNCHANGED scenario
  /\ queueState' = "ready"
  /\ outboxState' = "pending"
  /\ notificationCount' = 1
  /\ receiptState' = "none"
  /\ result' = "retryable"
  /\ lastInternalAction' = [name |-> "ProcessRetryable", params |-> [scenario |-> scenario]]

ProcessPermanent ==
  /\ scenario = "permanent"
  /\ result = "ready"
  /\ UNCHANGED scenario
  /\ queueState' = "dead"
  /\ outboxState' = "pending"
  /\ notificationCount' = 1
  /\ receiptState' = "none"
  /\ result' = "permanent"
  /\ lastInternalAction' = [name |-> "ProcessPermanent", params |-> [scenario |-> scenario]]

ProcessDuplicate ==
  /\ scenario = "duplicate"
  /\ result = "ready"
  /\ UNCHANGED scenario
  /\ queueState' = "acked"
  /\ outboxState' = "sent"
  /\ notificationCount' = 0
  /\ receiptState' = "stored"
  /\ result' = "duplicate"
  /\ lastInternalAction' = [name |-> "ProcessDuplicate", params |-> [scenario |-> scenario]]

ProcessPendingRetry ==
  /\ scenario = "pending"
  /\ result = "ready"
  /\ UNCHANGED scenario
  /\ queueState' = "acked"
  /\ outboxState' = "sent"
  /\ notificationCount' = 1
  /\ receiptState' = "stored"
  /\ result' = "accepted"
  /\ lastInternalAction' = [name |-> "ProcessPendingRetry", params |-> [scenario |-> scenario]]

InternalNext ==
  \/ ProcessEmpty
  \/ ProcessNotDue
  \/ ProcessAccepted
  \/ ProcessRetryable
  \/ ProcessPermanent
  \/ ProcessDuplicate
  \/ ProcessPendingRetry

TypeInvariant ==
  /\ scenario \in Scenarios
  /\ queueState \in QueueStates
  /\ outboxState \in OutboxStates
  /\ notificationCount \in 0..1
  /\ receiptState \in ReceiptStates
  /\ result \in Results

DeliveryInvariant ==
  /\ outboxState = "sent" => receiptState = "stored"
  /\ queueState = "acked" => result \in {"accepted", "duplicate"}

InternalSpec == InternalInit /\ [][InternalNext]_InternalVars

=============================================================================
