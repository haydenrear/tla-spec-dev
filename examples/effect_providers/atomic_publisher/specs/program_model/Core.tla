------------------------------- MODULE Core -------------------------------
EXTENDS Naturals, Sequences

Scenarios == {
  "create_success",
  "valid_update",
  "idempotent_retry",
  "stale_revision",
  "read_failure",
  "staged_write_failure",
  "replace_failure"
}

NoRecord == [exists |-> FALSE, revision |-> 0, id |-> "none", payload |-> "none"]
Record(revisionValue, payloadValue) ==
  [exists |-> TRUE, revision |-> revisionValue, id |-> "record", payload |-> payloadValue]

BeforeRecord(scenarioValue) ==
  CASE scenarioValue = "create_success" -> NoRecord
    [] scenarioValue = "stale_revision" -> Record(2, "old")
    [] scenarioValue = "idempotent_retry" -> Record(1, "new")
    [] OTHER -> Record(1, "old")

Result(statusValue, revisionValue, idempotentValue) ==
  [status |-> statusValue, revision |-> revisionValue, idempotent |-> idempotentValue]

InitialResult == Result("not_run", 0, FALSE)

ExpectedRecord(scenarioValue) ==
  CASE scenarioValue = "create_success" -> Record(1, "new")
    [] scenarioValue = "valid_update" -> Record(2, "new")
    [] OTHER -> BeforeRecord(scenarioValue)

ExpectedResult(scenarioValue) ==
  CASE scenarioValue = "create_success" -> Result("success", 1, FALSE)
    [] scenarioValue = "valid_update" -> Result("success", 2, FALSE)
    [] scenarioValue = "idempotent_retry" -> Result("success", 1, TRUE)
    [] scenarioValue = "stale_revision" -> Result("stale_revision", 2, FALSE)
    [] scenarioValue = "read_failure" -> Result("read_error", 0, FALSE)
    [] scenarioValue = "staged_write_failure" -> Result("write_error", 1, FALSE)
    [] OTHER -> Result("replace_error", 1, FALSE)

ExpectedTrace(scenarioValue) ==
  CASE scenarioValue = "create_success" -> <<"read_missing", "stage_write", "replace">>
    [] scenarioValue = "valid_update" -> <<"read_found", "stage_write", "replace">>
    [] scenarioValue = "idempotent_retry" -> <<"read_found">>
    [] scenarioValue = "stale_revision" -> <<"read_found">>
    [] scenarioValue = "read_failure" -> <<"read_error">>
    [] scenarioValue = "staged_write_failure" -> <<"read_found", "stage_write_error">>
    [] OTHER -> <<"read_found", "stage_write", "replace_error", "delete_stage">>

=============================================================================
