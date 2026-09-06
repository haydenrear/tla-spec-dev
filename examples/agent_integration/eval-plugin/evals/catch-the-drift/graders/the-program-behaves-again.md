---
type: file_exists
path: ".eval/behaviour"
weight: 2
---

Written by the `Stop` hook only after it imports the workspace's own
`EcommerceStore`, calls `create_account`, and finds the account in
`snapshot()`. THE REAL OBJECT, THE REAL STORE.

The seeded fault is not invented for this case: it is mutant
`store-account_store` from the example's own `kill_mutants.toml` -- *"creating
an account returns 201 but writes nothing to the account store"*. Using the
project's declared fault rather than a fresh one keeps the case from being a
recogniser fitted to an answer (`MF-020`).

Weight 2, because this is the case. Verified three ways before shipping: fault
present, no verdict; fault repaired, verdict; and the verifier's own first
version withheld the verdict for its own import bug, which is how the false
negative gets caught before it is charged to an agent.
