"""State and output projections for this repository's own CLI model.

WHY THIS FILE EXISTS. `generate cases` on `MCsmall.cfg` -- the config that
exists SO THAT a corpus is tractable -- produced 3,678,217 cases and a 7.4 GB
`cases.py` CPython cannot import: 18,391x this manifest's own cap of 200
internal cases per component. RC-02-DF-04 and MF026-R4-F-01 both filed it, and
this model was the only one in the repository with no `tlc_projection.py` while
every worked example had one. A corpus nobody can import is not a mechanism,
and a negative corpus nobody can import is not one either.

WHAT IS PROJECTED, AND WHY IT IS NOT A TRIM. Nothing is dropped. Two kinds of
variable move from the STATE to the OUTPUT, where they are still asserted:

  `lastCommand`, `result`
      Pure outputs. Every action writes them, no guard reads them. They belong
      to what a command RETURNS, not to the state a later command is enabled
      from -- and while they sit in the state, every case's before-state
      records which command happened to run before it, so the corpus enumerates
      one case per predecessor command. Measured: removing `lastCommand` alone
      takes 3,678,217 transitions to 2,964,421.

  the recorded verdicts
      `complexity_gate`, `corpus_gate`, `effect_conformance`, `kill_test`.
      Each is a fact a scanner RECORDED. They form an independent product that
      every action carries through unchanged, so the corpus enumerates each
      command once per combination of the verdicts it never reads and never
      writes. The output projection below carries back exactly the verdicts the
      action ITSELF changed, so what a command records is still checked case by
      case; what it merely coexisted with is not.

      There were SIX until 2026-08-04, when `architecture_scan` and
      `architecture_delta` were removed with the static architecture scanners.
      The measured figures below predate that removal and are left as measured
      -- they are what justified this file, and re-stating them from a later
      model would be quoting a number nobody ran. The projection is
      unaffected in kind: two dimensions left the ambient product, so the
      collapse this file performs is smaller than it was and no less
      necessary.

  Measured on MCsmall: 3,678,217 -> 76 transitions, with every recorded verdict
  and every result field still asserted.

WHAT THIS COSTS, STATED RATHER THAN OMITTED. A fault whose symptom is that a
command wrongly PRESERVES a verdict it should not have touched is no longer
visible: the projection cannot distinguish "left it alone" from "was never
there". Two of the model's invariants are about exactly that relationship --
`SpecUnitTestsRequireMeasuredCorpus` and `WeakenedClosesCertifyNothing` -- and
they are checked by TLC on the unprojected model, which is where that
obligation belongs. This is the MF-020 trap said out loud: a count that
improved because an edge was deleted is not an improvement, so the edges are
here, moved rather than deleted, and the one thing genuinely lost is named.
"""

from __future__ import annotations

from typing import Any

#: Verdicts a scanner records. Read by no guard in the module; every action
#: either writes one or leaves them all alone.
#:
#: `architecture_scan` and `architecture_delta` were REMOVED here on 2026-08-04
#: with the model variables they named. Leaving them would have been a
#: declaration with nothing behind it -- the exact class
#: references/architecture_advice.md rule 4 is about -- and it would have
#: passed silently, because the comprehensions below guard with `if name in
#: after`. A name that can never match is not a filter.
RECORDED_VERDICTS = (
    "complexity_gate",
    "corpus_gate",
    "effect_conformance",
    "kill_test",
)

#: What a command returns rather than what it leaves behind.
COMMAND_OUTPUTS = ("lastCommand", "result")

#: What actually enables the next command: the lifecycle position, the spec
#: root a command must match, and each ticket's stage.
CONTROL_STATE = ("setup_phase", "spec_root", "ticket_state")


def project_visible_state(state: dict[str, Any]) -> dict[str, Any]:
    """The state a later command is enabled from, and nothing else."""
    return {name: state[name] for name in CONTROL_STATE if name in state}


def project_adapter_output(
    *,
    before: dict[str, Any],
    after: dict[str, Any],
    action: str,
    params: dict[str, Any],
    changed: dict[str, dict[str, Any]],
    **_kwargs: Any,
) -> dict[str, Any]:
    """What the command returned, plus every verdict it actually recorded.

    A verdict the action left unchanged is deliberately absent rather than
    present-and-equal: including it would put the ambient five back into the
    dedupe key and undo the collapse without checking anything new.
    """
    recorded = {
        name: after[name]
        for name in RECORDED_VERDICTS
        if name in after and before.get(name) != after.get(name)
    }
    return {
        "action": action,
        "lastCommand": after.get("lastCommand"),
        "result": after.get("result"),
        "recorded": recorded,
        "changed": {
            name: value for name, value in changed.items() if name in CONTROL_STATE
        },
    }
