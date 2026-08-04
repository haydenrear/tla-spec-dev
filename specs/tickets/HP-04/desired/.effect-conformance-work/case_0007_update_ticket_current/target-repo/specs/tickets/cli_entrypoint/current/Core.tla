------------------------------- MODULE Core -------------------------------
\* Shared constants and helper operators for the whole-program model.
\* Internal.tla and External.tla both EXTEND this module, so anything both
\* views need to agree on belongs here.
\*
\* SCAFFOLD: replace the placeholder domain below with this repository's real
\* resources. Completion target: examples/distributed_history/specs/program_model/
EXTENDS Naturals, Sequences, FiniteSets

CONSTANTS
  Actors,
  Records

RecordStatus == {"none", "accepted"}
ProjectionStatus == {"none", "published"}

SeqToSet(seq) == {seq[i] : i \in 1..Len(seq)}

=============================================================================
\* tla-spec-dev-adapter: CURRENT-READY
