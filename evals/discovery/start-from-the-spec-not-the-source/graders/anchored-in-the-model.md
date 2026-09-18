---
type: file_exists
path: ".eval/grounded"
weight: 2
---

Written by the `Stop` hook only after `checks/discovery_map.py` reads the
workspace's own `specs/program_model/*.tla`, extracts the identifiers those
modules define, and finds at least three of them in `DISCOVERY.md` -- one of
them a name the model's `.cfg` files actually assert.

Those names are the model's, not the domain's. A capable account of an
ecommerce backend written without opening `specs/` does not contain
`AccountsAreUnique`; an account that starts from the map does.

The agent cannot write this path: `verify.sh` deletes `.eval/` before it looks,
and the check runs under a profile that denies it every filesystem write, so it
signals through its exit status and the hook records the verdict.

**What it does not decide.** It reads a document, not a behaviour. It can tell
that the account is anchored in the model; it cannot tell you the account is
correct, or that the agent would have found the same names without the skill.
