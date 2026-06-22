------------------------------ MODULE Desired ------------------------------
EXTENDS External

Init == ExternalInit
Next == ExternalNext
Spec == Init /\ [][Next]_ExternalVars

Invariant == ExternalInvariant

=============================================================================
