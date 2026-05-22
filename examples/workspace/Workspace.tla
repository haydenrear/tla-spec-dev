----------------------------- MODULE Workspace -----------------------------
EXTENDS Naturals, FiniteSets, Sequences, TLC

\* Product narrative:
\* Users own workspaces. Each user has a workspace limit. Creating a
\* workspace succeeds only while the user is below the limit.

CONSTANTS
  Users,
  Workspaces,
  LimitOneUsers,
  LimitTwoUsers,
  NoReason

VARIABLES
  owned,
  limits,
  result

vars == << owned, limits, result >>

Init ==
  /\ owned = [u \in Users |-> {}]
  /\ limits = [
      u \in Users |->
        IF u \in LimitOneUsers THEN 1
        ELSE IF u \in LimitTwoUsers THEN 2
        ELSE 0
    ]
  /\ result = [accepted |-> TRUE, reason |-> NoReason]

\* @command CreateWorkspace
\* @result CreateWorkspaceResult
\* @port WorkspacePort.create_workspace
Create(u, w) ==
  IF Cardinality(owned[u]) >= limits[u]
  THEN
    /\ result' = [
        accepted |-> FALSE,
        reason |-> "WORKSPACE_LIMIT_REACHED"
      ]
    /\ UNCHANGED << owned, limits >>
  ELSE
    /\ owned' = [owned EXCEPT ![u] = @ \cup {w}]
    /\ result' = [accepted |-> TRUE, reason |-> NoReason]
    /\ UNCHANGED limits

Next ==
  \E u \in Users, w \in Workspaces:
    Create(u, w)

\* @invariant WorkspaceLimitInvariant
WorkspaceLimitInvariant ==
  \A u \in Users:
    Cardinality(owned[u]) <= limits[u]

Spec ==
  Init /\ [][Next]_vars

=============================================================================
