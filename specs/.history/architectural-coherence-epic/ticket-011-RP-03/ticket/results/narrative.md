# RP-03 — narrative ledger

**Zero model delta.** Ticket `current` and `desired` are byte-identical, and both
equal `specs/current`. The complexity figures in this entry are RP-05's, carried
forward unchanged (`direction=zero`): nothing in the TLA+ moved. What changed is
`scripts/`, `tests/`, `references/` and `prompts/`.

## What this ticket was

Seven obstacles an outside-in eval run hit while trying to use case modules for
real. It authored one aspect for a service knowing only its public surface, and
succeeded — 60 authored lines, 38 cases, killing exactly what the 330-case
whole-view corpus killed — while hitting every one of them. Its report was the
specification.

## The one structural decision

**A case module could not generate from where the docs put it.** TLC runs with
cwd = the `.tla`'s directory, has no `-lib` flag, and does not search the current
directory — all three verified rather than assumed. SANY resolves `EXTENDS`
against the directory of the file it is handed plus the `TLA-Library` system
property, and nothing else. So a module in `specs/case_modules/` could not extend
a view in `specs/program_model/`, and the eval run had to copy the module beside
the view, generate, and delete the copy — which means the module checked into the
repository was not reproducible where it lived.

The alternatives considered:

- *move the modules beside the view* — makes the documented location wrong rather
  than making it work, and puts `Scenario_*.tla` into the accepted baseline
  directory, which CM-F1 already had to defend against;
- *stage into a temp directory and run TLC there* — the copy hack with the seam
  hidden inside the tool; every path TLC prints then points at a directory that
  does not exist afterwards;
- *set `TLA-Library`* — the mechanism TLA+ tooling actually provides. Taken.

It has one cost worth writing down: TLC's launcher is a shell script, so the
system property can only reach the JVM through `JAVA_TOOL_OPTIONS`, and the JVM
prints one `Picked up JAVA_TOOL_OPTIONS:` line to stderr when it does. That line
is unsuppressable. It is set **only** when something actually resolved outside
the module's own directory, so the ordinary single-directory run is unchanged.

The refinement that came out of it: the search path is resolved **once**, before
anything expensive runs, and the same path is handed to TLC, to the static
complexity/architecture scanner, and to the MF-029 parameter-recovery recipes.
Three lookups that could disagree about which file a case module extends became
one that cannot. The manifest is found along it too, because a case module has no
manifest of its own — the one that governs it belongs to the view.

## The defect the worked example found

Requirement (b) was to publish an internal-view worked example whose commands run
exactly as written. Running it end to end surfaced something the brief did not
list: **parameter recovery did not follow `EXTENDS`.** A case module declares no
actions, so recipes built from its own text alone recovered nothing — the view's
corpus carried 330/330 arguments while its two case modules carried 0/50 and 0/6,
and the adapters then refused those corpora case by case with ``no usable
argument for `i` ``. The manual-test-starter path produced a corpus that could be
generated and could not be executed, which is the whole value proposition
failing quietly. Fixed inside this ticket's own conflict key by building recipes
over the hierarchy, base modules first. Its blast radius on multi-module specs is
recorded in `deferred-and-negative-findings.txt` rather than left to be
discovered.

## Two things deliberately not mechanized

**Step 0's provenance requirement.** The brief allowed "checkable or honestly
labelled". It is not checkable. `Source` is free text; requiring it to be
non-empty, or rejecting `the model`/`derived`, are each one word of work for an
agent that wants to pass, and this epic has already shipped one guard that passed
vacuously. Both candidate checks are named and rejected *in the prompt*, at Step
0 where the requirement is made — not in the footnote at the bottom, which was
the previous state and is how the eval agent ended up having to flag its own
violation. The replacement is a contract, not a check: provenance is an
unverified claim, an authorless decomposition is labelled unreviewed, and a
consumer asks the named source directly.

**CM-F5.** A slice narrower than its view orphans the view's effect providers,
and `run_generated_case_adapters.py` treats an orphan provider as a configuration
error. On a whole view that is right; on a slice it is normal, and it means the
ex4 `Scenario_DeliveryPath` slice cannot run against the project's own
`case_adapters.toml` at all. The runner is not this ticket's file and the fix is
a decision about the runner. It is filed as CM-F5 and published *in the worked
example as a refusal* — the sixth command is expected to exit nonzero and says
so. Publishing a worked example that hides its one failing step would be the
honest-in-prose/misleading-in-artifact pattern this epic keeps finding.

## The deletion

`CFG_KEYWORDS` in `scripts/spec_evolution.py`, owner-authorized, dead since
RP-04 fixed the parser it worked around. Deleted with no reference remaining and
the three model-pair validator tests RP-04 measured as load-bearing on it green.

## One place the brief was wrong

"Step 1's `jq` pipeline assumes JSON-only stdout" did not reproduce: that command
writes 6,703 bytes to stdout and 0 to stderr, and every error path in
`analyze_architecture.py` prints to stderr. What did reproduce — `--spec-root`
not resolving the positional `.tla`/`.cfg`, and Step 1(b) requiring PyYAML, which
this toolchain deliberately does not depend on — is fixed. Recorded as a negative
finding rather than quietly dropped.
