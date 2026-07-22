----------------------------- MODULE External -----------------------------
EXTENDS Core

VARIABLES scenario, queueState, outboxState, notificationCount,
          receiptState, result, lastExternalAction

ExternalVars ==
  <<scenario, queueState, outboxState, notificationCount,
    receiptState, result, lastExternalAction>>

InitScenario(s, q, o, r) ==
  /\ scenario = s
  /\ queueState = q
  /\ outboxState = o
  /\ notificationCount = 0
  /\ receiptState = r
  /\ result = "ready"
  /\ lastExternalAction = [name |-> "Init", params |-> [scenario |-> s]]

ExternalInit ==
  \/ InitScenario("empty", "empty", "none", "none")
  \/ InitScenario("not_due", "ready", "none", "none")
  \/ InitScenario("accepted", "ready", "none", "none")
  \/ InitScenario("retryable", "ready", "none", "none")
  \/ InitScenario("permanent", "ready", "none", "none")
  \/ InitScenario("duplicate", "ready", "sent", "stored")
  \/ InitScenario("pending", "ready", "pending", "none")

RunEmpty ==
  /\ scenario = "empty"
  /\ result = "ready"
  /\ UNCHANGED scenario
  /\ queueState' = "empty"
  /\ outboxState' = "none"
  /\ notificationCount' = 0
  /\ receiptState' = "none"
  /\ result' = "empty"
  /\ lastExternalAction' = [name |-> "RunEmpty", params |-> [scenario |-> scenario]]

RunNotDue ==
  /\ scenario = "not_due"
  /\ result = "ready"
  /\ UNCHANGED scenario
  /\ queueState' = "ready"
  /\ outboxState' = "none"
  /\ notificationCount' = 0
  /\ receiptState' = "none"
  /\ result' = "not_due"
  /\ lastExternalAction' = [name |-> "RunNotDue", params |-> [scenario |-> scenario]]

RunAccepted ==
  /\ scenario = "accepted"
  /\ result = "ready"
  /\ UNCHANGED scenario
  /\ queueState' = "acked"
  /\ outboxState' = "sent"
  /\ notificationCount' = 1
  /\ receiptState' = "stored"
  /\ result' = "accepted"
  /\ lastExternalAction' = [name |-> "RunAccepted", params |-> [scenario |-> scenario]]

RunRetryable ==
  /\ scenario = "retryable"
  /\ result = "ready"
  /\ UNCHANGED scenario
  /\ queueState' = "ready"
  /\ outboxState' = "pending"
  /\ notificationCount' = 1
  /\ receiptState' = "none"
  /\ result' = "retryable"
  /\ lastExternalAction' = [name |-> "RunRetryable", params |-> [scenario |-> scenario]]

RunPermanent ==
  /\ scenario = "permanent"
  /\ result = "ready"
  /\ UNCHANGED scenario
  /\ queueState' = "dead"
  /\ outboxState' = "pending"
  /\ notificationCount' = 1
  /\ receiptState' = "none"
  /\ result' = "permanent"
  /\ lastExternalAction' = [name |-> "RunPermanent", params |-> [scenario |-> scenario]]

RunDuplicate ==
  /\ scenario = "duplicate"
  /\ result = "ready"
  /\ UNCHANGED scenario
  /\ queueState' = "acked"
  /\ outboxState' = "sent"
  /\ notificationCount' = 0
  /\ receiptState' = "stored"
  /\ result' = "duplicate"
  /\ lastExternalAction' = [name |-> "RunDuplicate", params |-> [scenario |-> scenario]]

RunPendingRetry ==
  /\ scenario = "pending"
  /\ result = "ready"
  /\ UNCHANGED scenario
  /\ queueState' = "acked"
  /\ outboxState' = "sent"
  /\ notificationCount' = 1
  /\ receiptState' = "stored"
  /\ result' = "accepted"
  /\ lastExternalAction' = [name |-> "RunPendingRetry", params |-> [scenario |-> scenario]]

ExternalNext ==
  \/ RunEmpty
  \/ RunNotDue
  \/ RunAccepted
  \/ RunRetryable
  \/ RunPermanent
  \/ RunDuplicate
  \/ RunPendingRetry

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

ExternalSpec == ExternalInit /\ [][ExternalNext]_ExternalVars

=============================================================================
