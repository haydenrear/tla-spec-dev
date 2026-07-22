----------------------------- MODULE External -----------------------------
EXTENDS Internal

VARIABLE lastExternalAction

ExternalVars == <<InternalVars, lastExternalAction>>

ExternalInit ==
  /\ InternalInit
  /\ lastExternalAction = [name |-> "Init", params |-> <<>>]

MarkExternal(actionName) ==
  lastExternalAction' = [name |-> actionName, params |-> [scenario |-> scenario]]

InvokeCreateSuccess == /\ CreateSuccess /\ MarkExternal("InvokeCreateSuccess")
InvokeValidUpdate == /\ ValidUpdate /\ MarkExternal("InvokeValidUpdate")
InvokeIdempotentRetry == /\ IdempotentRetry /\ MarkExternal("InvokeIdempotentRetry")
InvokeStaleRevision == /\ StaleRevision /\ MarkExternal("InvokeStaleRevision")
InvokeReadFailure == /\ ReadFailure /\ MarkExternal("InvokeReadFailure")
InvokeStagedWriteFailure == /\ StagedWriteFailure /\ MarkExternal("InvokeStagedWriteFailure")
InvokeReplaceFailure == /\ ReplaceFailure /\ MarkExternal("InvokeReplaceFailure")

ExternalNext ==
  \/ InvokeCreateSuccess
  \/ InvokeValidUpdate
  \/ InvokeIdempotentRetry
  \/ InvokeStaleRevision
  \/ InvokeReadFailure
  \/ InvokeStagedWriteFailure
  \/ InvokeReplaceFailure

ExternalInvariant == InternalInvariant
ExternalSpec == ExternalInit /\ [][ExternalNext]_ExternalVars

=============================================================================
