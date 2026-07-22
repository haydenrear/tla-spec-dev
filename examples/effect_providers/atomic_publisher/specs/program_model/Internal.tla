----------------------------- MODULE Internal -----------------------------
EXTENDS Core

VARIABLES scenario, done, record, result, trace, lastInternalAction

InternalVars == <<scenario, done, record, result, trace, lastInternalAction>>

InternalInit ==
  /\ scenario \in Scenarios
  /\ done = FALSE
  /\ record = BeforeRecord(scenario)
  /\ result = InitialResult
  /\ trace = <<>>
  /\ lastInternalAction = [name |-> "Init", params |-> <<>>]

Finish(actionName) ==
  /\ ~done
  /\ scenario' = scenario
  /\ done' = TRUE
  /\ record' = ExpectedRecord(scenario)
  /\ result' = ExpectedResult(scenario)
  /\ trace' = ExpectedTrace(scenario)
  /\ lastInternalAction' = [name |-> actionName, params |-> [scenario |-> scenario]]

CreateSuccess == /\ scenario = "create_success" /\ Finish("CreateSuccess")
ValidUpdate == /\ scenario = "valid_update" /\ Finish("ValidUpdate")
IdempotentRetry == /\ scenario = "idempotent_retry" /\ Finish("IdempotentRetry")
StaleRevision == /\ scenario = "stale_revision" /\ Finish("StaleRevision")
ReadFailure == /\ scenario = "read_failure" /\ Finish("ReadFailure")
StagedWriteFailure == /\ scenario = "staged_write_failure" /\ Finish("StagedWriteFailure")
ReplaceFailure == /\ scenario = "replace_failure" /\ Finish("ReplaceFailure")

InternalNext ==
  \/ CreateSuccess
  \/ ValidUpdate
  \/ IdempotentRetry
  \/ StaleRevision
  \/ ReadFailure
  \/ StagedWriteFailure
  \/ ReplaceFailure

InternalInvariant ==
  /\ scenario \in Scenarios
  /\ record.revision >= 0
  /\ (done =>
       /\ record = ExpectedRecord(scenario)
       /\ result = ExpectedResult(scenario)
       /\ trace = ExpectedTrace(scenario))

InternalSpec == InternalInit /\ [][InternalNext]_InternalVars

=============================================================================
