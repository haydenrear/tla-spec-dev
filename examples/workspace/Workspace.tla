----------------------------- MODULE Workspace -----------------------------
EXTENDS Naturals, FiniteSets, Sequences, TLC

\* Product narrative:
\* Users own workspaces. Each user has a workspace limit. Creating a
\* workspace succeeds only while the user is below the limit.

CONSTANTS
  Users,
  Workspaces,
  Limits,
  NoReason

VARIABLES
  owned,
  result

vars == << owned, result >>

Init ==
  /\ owned = [u \in Users |-> {}]
  /\ result = [accepted |-> TRUE, reason |-> NoReason]

\* @command CreateWorkspace
\* @result CreateWorkspaceResult
\* @port WorkspacePort.create_workspace
Create(u, w) ==
  IF Cardinality(owned[u]) >= Limits[u]
  THEN
    /\ result' = [
        accepted |-> FALSE,
        reason |-> "WORKSPACE_LIMIT_REACHED"
      ]
    /\ UNCHANGED owned
  ELSE
    /\ owned' = [owned EXCEPT ![u] = @ \cup {w}]
    /\ result' = [accepted |-> TRUE, reason |-> NoReason]

Next ==
  \E u \in Users, w \in Workspaces:
    Create(u, w)

\* @invariant WorkspaceLimitInvariant
WorkspaceLimitInvariant ==
  \A u \in Users:
    Cardinality(owned[u]) <= Limits[u]

Spec ==
  Init /\ [][Next]_vars

=============================================================================
