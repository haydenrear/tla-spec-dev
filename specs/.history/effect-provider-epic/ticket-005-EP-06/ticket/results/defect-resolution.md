# EP-06 validation defects resolved

The repeatable runs preserved failures instead of overwriting them, then fixed
only evidence-confirmed causes:

1. Atomic `agent-ep06-atomic-v1` recorded sandbox denial of TLC's local
   listener. The unchanged model/code passed once the required local listener
   was permitted; this is an environment limitation, not a product defect.
2. HTTP v1 exposed a commit-relative clean-worktree audit that treated another
   agent's pre-existing test as a rescue edit. The project now snapshots
   forbidden framework bytes at validation start and proves the campaign
   changes none of them.
3. HTTP v2 passed behaviorally but its result digest preceded the final usage
   descriptor edit. v3 reran after the descriptor was final and passed the
   common digest gate.
4. Reminder v1 passed TLC, controls, mutants, replay, and cleanup but capability
   enforcement rejected `channel: process`. The adapter drives a CLI child
   process, so all seven external mappings now honestly declare `channel: cli`.
5. EP-05 signature preflight rejected reminder methods using `_command: Any`.
   All four bindings now use the exact generated parameter names, generated
   command annotations, and return annotations; a focused test walks every
   generated Protocol method.
6. The first central aggregate run reproduced the same commit-relative audit
   defect in atomic because the new common contract test was intentionally
   untracked before commit. Captured logs proved TLC, generation, campaigns,
   replay, cleanup, interpreter, and descriptors were green. Atomic now uses
   the validation-start byte snapshot with a regression test; the unchanged
   aggregate command passed as v2.

No blocking defect remains and no new domain helper was introduced.
