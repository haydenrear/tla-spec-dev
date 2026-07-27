------------------------------- MODULE Pipeline -------------------------------
\* EV-01 decomposable fixture.
\*
\* Derived from the epic owner's probe model (specs/results/Pipeline.tla), which
\* proved AC-01's three decomposition criteria satisfiable at Q = 0.219. One
\* variable and one action are added here, and the reason is stated in the
\* fixture README: a TWO-component partition has exactly one component pair,
\* that pair is ported, and `unfalsifiable_coherence` therefore fires on every
\* reflexion run over it -- no code edge could ever have diverged. A fixture
\* that cannot produce a divergence cannot be the positive test for a
\* divergence check. Three components give one UNPORTED pair (ingest <-> ledger)
\* and that pair is where the divergent twin's answer key lives.
\*
\* The owner's noted property is preserved on purpose: Deliver writes on BOTH
\* sides of the ingest/dispatch boundary, so it is simultaneously the port and a
\* single-writer violation. That is the honest atomicity-fidelity signal -- a
\* handoff mutating both sides in one step has no explicit commit point -- and
\* the answer key expects it. A report that names it is CORRECT, not a false
\* positive.
EXTENDS Naturals, FiniteSets

CONSTANTS Items

VARIABLES inbox, accepted, queue, delivered, failed, ledger

vars == << inbox, accepted, queue, delivered, failed, ledger >>

TypeInvariant ==
  /\ inbox \subseteq Items
  /\ accepted \subseteq Items
  /\ queue \subseteq Items
  /\ delivered \subseteq Items
  /\ failed \subseteq Items
  /\ ledger \subseteq Items

\* A delivered item is never simultaneously failed.
DeliveryExclusive == delivered \cap failed = {}

\* Nothing reaches the ledger that was not delivered at some point.
LedgerIsDownstream == ledger \subseteq (delivered \cup failed)

Init ==
  /\ inbox = Items
  /\ accepted = {}
  /\ queue = {}
  /\ delivered = {}
  /\ failed = {}
  /\ ledger = {}

\* ---- ingest ---------------------------------------------------------------

Accept(i) ==
  /\ i \in inbox
  /\ inbox' = inbox \ {i}
  /\ accepted' = accepted \cup {i}
  /\ UNCHANGED << queue, delivered, failed, ledger >>

Enqueue(i) ==
  /\ i \in accepted
  /\ i \notin queue
  /\ queue' = queue \cup {i}
  /\ UNCHANGED << inbox, accepted, delivered, failed, ledger >>

\* ---- the ingest <-> dispatch handoff --------------------------------------
\* Writes queue (ingest) and delivered (dispatch) in one step. Port AND
\* single-writer violation, by construction.

Deliver(i) ==
  /\ i \in queue
  /\ i \notin failed
  /\ queue' = queue \ {i}
  /\ delivered' = delivered \cup {i}
  /\ UNCHANGED << inbox, accepted, failed, ledger >>

\* ---- dispatch -------------------------------------------------------------

Fail(i) ==
  /\ i \in delivered
  /\ i \notin failed
  /\ delivered' = delivered \ {i}
  /\ failed' = failed \cup {i}
  /\ UNCHANGED << inbox, accepted, queue, ledger >>

\* ---- the dispatch <-> ledger port -----------------------------------------
\* Reads delivered (dispatch), writes ledger (ledger). Crossing, not spanning:
\* its write set lands in one component.

Record(i) ==
  /\ i \in delivered
  /\ i \notin ledger
  /\ ledger' = ledger \cup {i}
  /\ UNCHANGED << inbox, accepted, queue, delivered, failed >>

Next ==
  \/ \E i \in Items : Accept(i)
  \/ \E i \in Items : Enqueue(i)
  \/ \E i \in Items : Deliver(i)
  \/ \E i \in Items : Fail(i)
  \/ \E i \in Items : Record(i)

Spec == Init /\ [][Next]_vars
=============================================================================
