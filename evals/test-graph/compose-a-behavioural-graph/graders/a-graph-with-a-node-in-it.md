---
type: file_exists
path: ".eval/graph"
weight: 2
---

Written by the `Stop` hook only after `checks/testgraph_scaffold.py` finds a
`test_graph/` project with a settings file, a build file that registers a graph
by name, at least one node file that describes itself, and a reference from the
registered graph to that node.

The last clause is the one that matters. A scaffold with an empty graph beside
an orphan node file is the cheap shape, and it satisfies every check except
"do they refer to each other".

**A red here is not always the work's, and this suite cannot say which.**
Running the graph would be better evidence and is deliberately not attempted:
the node runtime wants Gradle and a JBang or uv toolchain the eval sandbox does
not reliably carry, and a check that cannot run leaves the same absent path as
work that was never done. What was missing is printed into `.eval/verify.log`,
which is where to look before reading a 0 as the agent's.

The agent cannot write this path: `verify.sh` clears `.eval/` first, and the
check runs write-denied.
