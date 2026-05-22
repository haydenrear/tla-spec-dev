---------------------------- MODULE Subscription ----------------------------
EXTENDS Naturals, FiniteSets, Sequences, TLC

\* Partial example:
\* A subscription has lifecycle states such as trialing, active, paused,
\* and canceled. Only certain transitions are allowed. Some transitions
\* preserve billing period data. Some reject if invoices are unpaid.

CONSTANTS
  Subscriptions,
  Statuses,
  Trialing,
  Active,
  Paused,
  Canceled,
  Paid,
  Unpaid,
  NoReason

VARIABLES
  status,
  invoice_state,
  billing_period,
  result

vars == << status, invoice_state, billing_period, result >>

Init ==
  /\ status = [s \in Subscriptions |-> Trialing]
  /\ invoice_state = [s \in Subscriptions |-> Paid]
  /\ billing_period = [s \in Subscriptions |-> 0]
  /\ result = [accepted |-> TRUE, reason |-> NoReason]

\* @command ActivateSubscription
Activate(s) ==
  IF /\ status[s] \in {Trialing, Paused}
     /\ invoice_state[s] = Paid
  THEN
    /\ status' = [status EXCEPT ![s] = Active]
    /\ UNCHANGED << invoice_state, billing_period >>
    /\ result' = [accepted |-> TRUE, reason |-> NoReason]
  ELSE
    /\ result' = [accepted |-> FALSE, reason |-> "ACTIVATION_REJECTED"]
    /\ UNCHANGED << status, invoice_state, billing_period >>

\* @command PauseSubscription
Pause(s) ==
  IF status[s] = Active
  THEN
    /\ status' = [status EXCEPT ![s] = Paused]
    /\ UNCHANGED << invoice_state, billing_period >>
    /\ result' = [accepted |-> TRUE, reason |-> NoReason]
  ELSE
    /\ result' = [accepted |-> FALSE, reason |-> "PAUSE_REJECTED"]
    /\ UNCHANGED << status, invoice_state, billing_period >>

\* @command CancelSubscription
Cancel(s) ==
  IF status[s] # Canceled
  THEN
    /\ status' = [status EXCEPT ![s] = Canceled]
    /\ UNCHANGED << invoice_state, billing_period >>
    /\ result' = [accepted |-> TRUE, reason |-> NoReason]
  ELSE
    /\ result' = [accepted |-> FALSE, reason |-> "ALREADY_CANCELED"]
    /\ UNCHANGED << status, invoice_state, billing_period >>

Next ==
  \E s \in Subscriptions:
    \/ Activate(s)
    \/ Pause(s)
    \/ Cancel(s)

\* @invariant CanceledNotActiveInvariant
CanceledNotActiveInvariant ==
  \A s \in Subscriptions:
    ~(status[s] = Canceled /\ status[s] = Active)

Spec ==
  Init /\ [][Next]_vars

=============================================================================
