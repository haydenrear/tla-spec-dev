"""Ticket-local adapters for the shipped tla-spec-dev CLI entrypoint."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "skill-manager.toml").is_file() and (parent / "scripts" / "tla_spec_dev.py").is_file():
            return parent
    raise RuntimeError("could not locate tla-spec-dev repository root")


# ---------------------------------------------------------------------------
# MF-028 SPIKE: the case-execution seam.
#
# `run_generated_case_adapters.py` calls `run(case, work_dir=...)`; every
# adapter here implements `apply(target_repo, ...)`. The two never met. This
# block is the measured minimum needed to cross that seam for ONE adapter, and
# it is deliberately small so the cost of the remaining fifteen can be read off
# it. It is NOT a finished framework.
#
# A generated case is (before-state, action, after-state) over the nine model
# variables. `run()` therefore has three obligations, and each has a different
# cost profile:
#
#   1. MATERIALIZE `case.before` as a real repository.
#   2. EXECUTE the action against it.
#   3. PROJECT the resulting repository back into the nine variables.
#
# What the spike found about each is recorded at the helper that implements it.
# ---------------------------------------------------------------------------

#: The setup pipeline as the model orders it. `setup_phase` is an ORDINAL over
#: this list, which is the single most important fact for costing this work:
#: the before-state of the setup segment is not arbitrary filesystem content,
#: it is a PREFIX of this sequence. Materializing "setup_phase = N" therefore
#: means replaying elements [0:N] -- an operation that is shared across every
#: adapter in the segment rather than adapter-specific.
SETUP_PIPELINE = [
    "BuildSkillCli",       # phase 0 -> 1
    "InstallLocalCli",     # phase 1 -> 2
    "ScaffoldProject",     # phase 2 -> 3
    "RecordBudgets",       # phase 3 -> 4
    "ScaffoldWorkflow",    # phase 4 -> 5
]

#: Variables that NO filesystem inspection can recover. `lastCommand` and
#: `result` describe the last CLI invocation, not the repository: two different
#: command histories can leave byte-identical trees. The complexity analyzer
#: independently flagged exactly this pair ("no configured invariant reads
#: [lastCommand, result]").
#:
#: They are still checked here, but from the CLI invocation the adapter
#: actually performed -- the command it ran and that command's exit status --
#: never by copying them out of `case.after`. `result.next` is the one field
#: that is genuinely unobservable: the CLI prints a prose "next:" block, not
#: the model's token, so comparing it would require re-encoding the spec inside
#: the adapter. The spike declines to do that and reports the field as
#: unprojectable instead of faking agreement.
UNPROJECTABLE_FIELDS = ("result.next",)


class BeforeStateUnreachable(RuntimeError):
    """Raised when `case.before` cannot be built by replaying the CLI.

    This is the honest failure mode for case execution and it is raised, never
    swallowed: an adapter that quietly ran against the wrong before-state would
    report a conformance result about a repository the case never described.
    """


def materialize_before(case: object, work_dir: Path) -> tuple[Path, str, list[dict[str, object]]]:
    """Build a repository in `case.before` by replaying the CLI prefix.

    Returns (target_repo, spec_root, replay records).

    COST NOTE (the number this spike exists to produce): for the setup segment
    this is ~15 lines and is entirely SHARED -- no adapter contributes anything
    adapter-specific to it. That is because phases 0..2 concern the tla-spec-dev
    source repo, which is already built in any checkout, so they materialize to
    an EMPTY DIRECTORY and cost nothing; and phases 3..5 are exactly the CLI's
    own scaffold commands, which the adapters were already calling by hand.
    The ticket segment (`ticket_state`) is a second, per-ticket ordinal replayed
    the same way. The expensive-sounding phrase in the ticket -- "constructing a
    repository already in that state" -- turns out to be "replay a prefix",
    because this model has no free-form state.
    """
    before = dict(getattr(case, "before"))
    phase = int(before["setup_phase"])
    if not 0 <= phase <= 5:
        raise BeforeStateUnreachable(f"setup_phase {phase} is outside the modelled pipeline")

    spec_root_token = str(before.get("spec_root", "NoRoot"))
    # The model's SpecRoots are symbolic constants; the repository directory
    # they denote is a binding decision, not a model fact. `default_specs` is
    # the conventional "specs" tree.
    spec_root = "specs" if spec_root_token in ("NoRoot", "default_specs") else str(spec_root_token)

    target_repo = Path(work_dir) / "target-repo"
    target_repo.mkdir(parents=True, exist_ok=True)

    root = repo_root()
    replay: list[dict[str, object]] = []
    for step in SETUP_PIPELINE[:phase]:
        if step in ("BuildSkillCli", "InstallLocalCli"):
            # Concern the tla-spec-dev checkout itself, which is already built
            # and importable. Nothing to construct in the target repo.
            replay.append({"step": step, "action": "no-op (source repo already built)"})
            continue
        if step == "ScaffoldProject":
            record = run_cli(root, target_repo, "--spec-root", spec_root, "scaffold", "project", "--name", "CliProject")
        elif step == "RecordBudgets":
            # The model has RecordBudgets as its own transition; the shipped CLI
            # emits the budgets block as part of `scaffold project` and expects
            # the agent to negotiate the values. Replaying it is therefore an
            # in-place manifest edit, not a command. This is the first place the
            # replay stops being a pure command sequence.
            record = _negotiate_budgets(target_repo, spec_root)
        elif step == "ScaffoldWorkflow":
            record = run_cli(
                root, target_repo, "--spec-root", spec_root, "scaffold", "workflow", "CLI-028", "MF-028 spike replay"
            )
        else:  # pragma: no cover - SETUP_PIPELINE is closed
            raise BeforeStateUnreachable(f"no replay defined for {step}")
        replay.append(
            {
                "step": step,
                "exit_code": getattr(record, "returncode", 0),
                "stderr": getattr(record, "stderr", "")[-400:],
            }
        )
        if getattr(record, "returncode", 0) != 0:
            raise BeforeStateUnreachable(
                f"replaying {step} to reach setup_phase={phase} failed: {getattr(record, 'stderr', '')[-600:]}"
            )

    ticket_state = before.get("ticket_state") or {}
    if any(int(value) != 0 for value in dict(ticket_state).values()):
        # Deliberately NOT implemented by this spike. The ticket segment is a
        # second ordinal and would replay the same way, but proving that is a
        # separate measurement and the spike refuses to imply coverage it does
        # not have.
        raise BeforeStateUnreachable(
            f"ticket_state {dict(ticket_state)!r} is non-initial; MF-028 measured the setup segment only"
        )

    return target_repo, spec_root, replay


def _negotiate_budgets(target_repo: Path, spec_root: str):
    """Mark the scaffolded budgets block as negotiated, as RecordBudgets means."""
    manifest = target_repo / spec_root / "program_model" / "spec_manifest.yaml"
    if not manifest.exists():
        raise BeforeStateUnreachable(f"cannot record budgets before scaffold project: {manifest} missing")
    text = manifest.read_text(encoding="utf-8")
    if "source: negotiated" not in text:
        text = text.replace("source: default", "source: negotiated", 1)
        manifest.write_text(text, encoding="utf-8")
    return subprocess.CompletedProcess(args=["<record-budgets>"], returncode=0, stdout="", stderr="")


def project_state(
    target_repo: Path,
    spec_root: str,
    *,
    prior: dict[str, object],
    last_command: str,
    accepted: bool,
) -> dict[str, object]:
    """Project a real repository back into the nine model variables.

    COST NOTE: this is the half of the seam that does NOT come for free, and it
    is where the remaining adapters will diverge. `setup_phase` and `spec_root`
    are read from directory evidence below in ~10 lines. The four gate variables
    (complexity_gate, corpus_gate, effect_conformance, kill_test) are read from
    results artifacts and are only meaningful once the corresponding oracle has
    run -- for setup-segment actions they are carried from `prior` because the
    action provably cannot change them (the TLA+ action lists them UNCHANGED).
    Carrying an UNCHANGED variable through is sound; carrying a CHANGED one
    would be the exact self-deception this epic keeps catching, so the caller
    asserts the changed-set instead.
    """
    state = dict(prior)

    specs = Path(target_repo) / spec_root
    program_model = specs / "program_model"
    manifest = program_model / "spec_manifest.yaml"

    phase = 2  # source repo built + CLI importable; both true in any checkout
    if program_model.is_dir() and any(program_model.glob("*.tla")):
        phase = 3
        if manifest.exists() and "source: negotiated" in manifest.read_text(encoding="utf-8"):
            phase = 4
            if (specs / "current").is_dir() and (specs / "desired_program_model").is_dir():
                phase = 5
    state["setup_phase"] = phase

    # spec_root is observable only once a root has actually been written.
    if phase >= 3:
        state["spec_root"] = "default_specs" if spec_root == "specs" else spec_root
    else:
        state["spec_root"] = "NoRoot"

    # Observed from the invocation the adapter actually performed.
    state["lastCommand"] = last_command
    prior_result = dict(prior.get("result") or {})
    state["result"] = {
        "accepted": bool(accepted),
        "reason": prior_result.get("reason", "NoReason"),
        # NOT observable -- see UNPROJECTABLE_FIELDS. Carried so the dict shape
        # matches; the comparison below excludes it by name rather than
        # pretending it was checked.
        "next": prior_result.get("next"),
    }
    return state


def compare_projection(
    *,
    case: object,
    projected: dict[str, object],
    unobservable: tuple[str, ...] = (),
) -> dict[str, object]:
    """Compare a projected after-state to `case.after`, field by field.

    Reports agreements, disagreements and explicitly-unchecked fields
    separately. A field that could not be observed is reported as UNCHECKED --
    never as agreement.
    """
    expected = dict(getattr(case, "after"))
    agreements: list[str] = []
    disagreements: list[dict[str, object]] = []
    unchecked: list[str] = []

    for field in sorted(set(expected) | set(projected)):
        want = expected.get(field)
        got = projected.get(field)
        if field == "result":
            want_r, got_r = dict(want or {}), dict(got or {})
            for key in sorted(set(want_r) | set(got_r)):
                dotted = f"result.{key}"
                if dotted in UNPROJECTABLE_FIELDS or dotted in unobservable:
                    unchecked.append(dotted)
                elif want_r.get(key) == got_r.get(key):
                    agreements.append(dotted)
                else:
                    disagreements.append({"field": dotted, "expected": want_r.get(key), "actual": got_r.get(key)})
            continue
        if field in unobservable:
            unchecked.append(field)
        elif want == got:
            agreements.append(field)
        else:
            disagreements.append({"field": field, "expected": want, "actual": got})

    return {
        "agreements": agreements,
        "disagreements": disagreements,
        "unchecked": unchecked,
        "conformant": not disagreements,
    }


def enforce_projection(case: object, comparison: dict[str, object]) -> None:
    """Fail the run when the projected after-state disagrees with the case.

    The runner's built-in `assert_case_result` compares `result.after` to
    `case.after` with `==` over the WHOLE dict, which cannot express "this field
    is not observable". Returning a whole-dict `after` would therefore force a
    choice between failing on `result.next` forever or copying it out of the
    case to make it agree -- and the second is fabrication. So the adapter owns
    the comparison and raises here, and reports the unchecked field by name
    instead of hiding it. Costing note: this is a REAL gap in the runner, and it
    is shared by all fifteen remaining adapters.
    """
    disagreements = comparison.get("disagreements") or []
    if disagreements:
        detail = "; ".join(
            f"{item['field']}: expected {item['expected']!r}, observed {item['actual']!r}" for item in disagreements
        )
        raise AssertionError(f"{getattr(case, 'name')}: projected after-state disagrees with the model -- {detail}")


class _UnimplementedActionAdapter:
    """MF-028 spike scaffolding. Binds a modelled action that has NO adapter.

    The spike found two model actions -- `UpdateTicketDesired` and
    `UpdateTicketCurrent` -- with no adapter class anywhere in the repository.
    They are not "adapters missing run()"; they are actions the production
    adapter set never covered at all, and no gate had noticed because nothing
    ever drove the corpus.

    Binding them was necessary only to get past the runner's whole-corpus
    coverage gate. `run()` REFUSES rather than returning a passing result: a
    stub that returned success would manufacture exactly the false conformance
    signal this ticket was opened to eliminate.
    """

    action_name = "Unimplemented"

    def run(self, case: object, work_dir: Path | None = None):
        raise NotImplementedError(
            f"{getattr(case, 'name')}: action {getattr(case, 'input').action} has no production adapter "
            "(MF-028 finding; not implemented by this spike)"
        )


class UpdateTicketDesiredAdapter(_UnimplementedActionAdapter):
    action_name = "UpdateTicketDesired"


class UpdateTicketCurrentAdapter(_UnimplementedActionAdapter):
    action_name = "UpdateTicketCurrent"


class StutterAdapter:
    """MF-028 spike scaffolding, NOT a deliverable of this ticket.

    The runner's coverage gate is WHOLE-CORPUS: it refuses before executing
    anything unless every label in the corpus has a binding. Running a single
    ScaffoldProject case therefore required binding `Stutter` too, and no
    Stutter adapter exists at the epic tip.

    This is a finding about ordering, not a fix. MF-023's stuttering work and
    its `case_adapters.toml` bindings are on open PR #50; this class exists only
    so the spike could reach its measurement, and it should be DELETED in favour
    of PR #50's version rather than merged alongside it.
    """

    action_name = "Stutter"

    def run(self, case: object, work_dir: Path | None = None):
        before, after = dict(getattr(case, "before")), dict(getattr(case, "after"))
        if before != after:
            raise AssertionError(f"{getattr(case, 'name')}: stutter changed state")
        return {"output": None, "after": None, "semantic_output": {"stutter": True}}


class BuildSkillCliAdapter:
    action_name = "BuildSkillCli"

    def apply(self) -> dict[str, object]:
        root = repo_root()
        entrypoint = root / "scripts" / "tla_spec_dev.py"
        installer = root / "skill-scripts" / "install-tla-spec-dev.sh"
        return {
            "accepted": entrypoint.is_file() and installer.is_file(),
            "entrypoint": str(entrypoint),
            "installer": str(installer),
        }

    # MF-028: the FLOOR case. Included because it is the cheapest possible
    # `run()` in the repository and therefore calibrates the bottom of the
    # difficulty scale -- not because it is representative. Its before-state is
    # setup_phase=0, which materializes to an empty directory, so it exercises
    # execution and projection but NOT before-state construction. Read the
    # ScaffoldProject run() below for the first honest measurement.
    def can_run(self, case: object) -> tuple[bool, str | None]:
        if getattr(case, "input").action != self.action_name:
            return False, f"case action {getattr(case, 'input').action} is not {self.action_name}"
        if int(dict(getattr(case, "before"))["setup_phase"]) != 0:
            return False, "BuildSkillCli is enabled only at setup_phase = 0"
        return True, None

    def run(self, case: object, work_dir: Path | None = None):
        work_dir = Path(work_dir or Path.cwd())
        target_repo, spec_root, replay = materialize_before(case, work_dir)
        applied = self.apply()
        projected = project_state(
            target_repo,
            spec_root,
            prior=dict(getattr(case, "before")),
            last_command="BuildSkillCli",
            accepted=bool(applied["accepted"]),
        )
        # BuildSkillCli advances the pipeline but writes nothing into the target
        # repo, so filesystem evidence cannot distinguish phase 0 from phase 1.
        # The adapter reports the phase it actually achieved: the entrypoint and
        # installer it just verified ARE the postcondition of BuildSkillCli.
        projected["setup_phase"] = 1 if applied["accepted"] else 0
        projected["spec_root"] = "NoRoot"
        comparison = compare_projection(case=case, projected=projected)
        enforce_projection(case, comparison)
        return {
            "output": None,
            "after": None,  # reported through semantic_output; see enforce_projection
            "semantic_output": {
                "case": getattr(case, "name"),
                "adapter": type(self).__name__,
                "replay": replay,
                "projected": projected,
                "comparison": comparison,
            },
        }


class InstallLocalCliAdapter:
    action_name = "InstallLocalCli"

    def apply(self, bin_dir: Path, cache_dir: Path) -> dict[str, object]:
        root = repo_root()
        env = {
            **os.environ,
            "SKILL_MANAGER_BIN_DIR": str(bin_dir),
            "SKILL_MANAGER_CACHE_DIR": str(cache_dir),
            "SKILL_DIR": str(root),
            "SKILL_NAME": "spec-double-compiler",
        }
        install = subprocess.run(
            ["bash", str(root / "skill-scripts" / "install-tla-spec-dev.sh")],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        wrapper = bin_dir / "tla-spec-dev"
        version = subprocess.run(
            [str(wrapper), "--version"],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        ) if wrapper.exists() else None
        return {
            "accepted": install.returncode == 0 and version is not None and version.returncode == 0,
            "install_exit_code": install.returncode,
            "version_exit_code": None if version is None else version.returncode,
            "version": "" if version is None else version.stdout.strip(),
            "wrapper": str(wrapper),
        }


class ScaffoldProjectAdapter:
    action_name = "ScaffoldProject"

    def apply(self, target_repo: Path, *, spec_root: str = "specs", name: str = "CliProject") -> dict[str, object]:
        root = repo_root()
        result = subprocess.run(
            [
                sys.executable,
                str(root / "scripts" / "tla_spec_dev.py"),
                "--spec-root",
                spec_root,
                "scaffold",
                "project",
                "--name",
                name,
            ],
            cwd=target_repo,
            text=True,
            capture_output=True,
            check=False,
        )
        return {
            "accepted": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "program_model": str(target_repo / spec_root / "program_model" / f"{name}.tla"),
        }

    # MF-028: THE MEASURED CASE. ScaffoldProject is the simplest adapter whose
    # before-state is non-vacuous AND whose action mutates persistent state:
    #
    #   * before-state setup_phase=2 is a real prefix (built + installed), so
    #     materialization is actually exercised rather than skipped;
    #   * the action writes a program_model tree, so the after-state is
    #     recoverable from the filesystem instead of being asserted on stdout;
    #   * it changes exactly two observable variables (setup_phase, spec_root),
    #     so a mismatch localizes instead of producing a wall of diffs.
    #
    # Everything cheaper than this (BuildSkillCli, InstallLocalCli,
    # ValidateTestGraphCli) has an empty before-state and no persistent effect,
    # and so cannot measure the thing the ticket asked about.
    def can_run(self, case: object) -> tuple[bool, str | None]:
        if getattr(case, "input").action != self.action_name:
            return False, f"case action {getattr(case, 'input').action} is not {self.action_name}"
        if int(dict(getattr(case, "before"))["setup_phase"]) != 2:
            return False, "ScaffoldProject is enabled only at setup_phase = 2"
        return True, None

    def run(self, case: object, work_dir: Path | None = None):
        work_dir = Path(work_dir or Path.cwd())
        target_repo, spec_root, replay = materialize_before(case, work_dir)

        # MF-028 HEADLINE FINDING, caught by this spike's own negative control.
        #
        # ScaffoldProject(root) is PARAMETERIZED, but the generated case carries
        # `params={}` -- and so does every one of the 57,617 cases in the
        # corpus. The generator recovers action arguments from a
        # `lastInternalAction` marker variable; this model declares no such
        # variable, so every argument to every parameterized action is lost.
        #
        # The adapter therefore cannot know which root the model chose. The
        # first draft of this method defaulted to `case.after["spec_root"]`,
        # which made the `spec_root` check a TAUTOLOGY: it read the expected
        # answer out of the case and echoed it back as an observation. A
        # deliberately corrupted after-state still passed. That is exactly the
        # false signal MF-016 caught in the kill rate.
        #
        # So: the adapter picks its own root, and `spec_root` is declared
        # UNCHECKED rather than compared. An unverifiable field is reported
        # unverifiable.
        params = dict(getattr(case, "input").params or {})
        root_token = str(params["root"]) if "root" in params else None
        chosen = "specs" if root_token in (None, "default_specs") else str(root_token)

        applied = self.apply(target_repo, spec_root=chosen)
        projected = project_state(
            target_repo,
            chosen,
            prior=dict(getattr(case, "before")),
            last_command="tla-spec-dev scaffold project",
            accepted=bool(applied["accepted"]),
        )
        # Map the concrete directory back to a symbolic token where one was
        # actually supplied. With no params in the corpus this stays None, and
        # spec_root is declared unobservable below rather than compared.
        projected["spec_root"] = root_token if root_token is not None else f"<unparameterized:{chosen}>"
        unobservable = () if root_token is not None else ("spec_root",)
        comparison = compare_projection(case=case, projected=projected, unobservable=unobservable)
        enforce_projection(case, comparison)
        return {
            "output": None,
            "after": None,  # reported through semantic_output; see enforce_projection
            "semantic_output": {
                "case": getattr(case, "name"),
                "adapter": type(self).__name__,
                "replay": replay,
                "exit_code": applied["exit_code"],
                "projected": projected,
                "comparison": comparison,
            },
        }


class ScaffoldWorkflowAdapter:
    action_name = "ScaffoldWorkflow"

    def apply(
        self,
        target_repo: Path,
        *,
        spec_root: str = "specs",
        ticket_id: str = "CLI-123",
        title: str = "CLI scaffold ticket",
    ) -> dict[str, object]:
        root = repo_root()
        result = subprocess.run(
            [
                sys.executable,
                str(root / "scripts" / "tla_spec_dev.py"),
                "--spec-root",
                spec_root,
                "scaffold",
                "workflow",
                ticket_id,
                title,
            ],
            cwd=target_repo,
            text=True,
            capture_output=True,
            check=False,
        )
        return {
            "accepted": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "current": str(target_repo / spec_root / "current"),
            "desired": str(target_repo / spec_root / "desired_program_model"),
        }


def run_cli(root: Path, target_repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts" / "tla_spec_dev.py"), *args],
        cwd=target_repo,
        text=True,
        capture_output=True,
        check=False,
    )


def prepare_ticket_workflow(
    root: Path,
    target_repo: Path,
    *,
    spec_root: str,
    ticket_id: str,
    title: str,
) -> list[subprocess.CompletedProcess[str]]:
    return [
        run_cli(root, target_repo, "--spec-root", spec_root, "scaffold", "project", "--name", "CliProject"),
        run_cli(root, target_repo, "--spec-root", spec_root, "scaffold", "workflow", ticket_id, title),
    ]


# MF-019: closing a ticket requires a filled-in complexity ledger input. `open
# ticket` scaffolds it with TODO sentinels that fail the gate on purpose, so
# every adapter that drives a real close fills it first. There is deliberately
# no bypass flag -- the standing objective is a required close-out step, so the
# adapters go through the real gate rather than around it.
PASSING_COMPLEXITY_LEDGER = """\
retention:
  kill_rate:
    status: "pass"
    evidence: "results/kill-test.json"
  effect_conformance:
    status: "clean"
    evidence: "results/effect-conformance.txt"
  external_coverage:
    status: "pass"
    evidence: "results/external-coverage.txt"
justification: "Adapter fixture close; no model growth claimed."
refinement:
  searched: true
  outcome: "none"
refinement_note: "searched, found none"
narrative: "Adapter fixture ledger narrative."
"""


def fill_complexity_ledger(target_repo: Path, spec_root: str, ticket_id: str) -> Path:
    """Fill the scaffolded per-ticket complexity ledger input before a close."""
    path = target_repo / spec_root / "tickets" / ticket_id / "results" / "complexity_ledger.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(PASSING_COMPLEXITY_LEDGER, encoding="utf-8")
    return path

#: A fixture model with three state variables, used to establish a measurable
#: baseline so that a later one-variable model is a genuine DECREASE. Variable
#: count is one of the direction metrics, so this works without depending on
#: the analyzer inferring domain cardinality for a throwaway module.
BASELINE_FIXTURE_MODEL = "---- MODULE Fixture ----\nVARIABLES a, b, c\n====\n"
SHRUNK_FIXTURE_MODEL = "---- MODULE Fixture ----\nVARIABLES a\n====\n"


def set_ticket_model(target_repo: Path, spec_root: str, ticket_id: str, text: str) -> None:
    """Write a fixture model into BOTH ticket trees.

    Both trees, because ticket current and desired must stay equal -- otherwise
    the close is refused by the equality gate and a test asserting on the
    ledger's refusal would be asserting against the wrong one.
    """
    for tree in ("current", "desired"):
        model_dir = target_repo / spec_root / "tickets" / ticket_id / tree
        for tla in model_dir.glob("*.tla"):
            if not tla.name.startswith("MC"):
                tla.write_text(text, encoding="utf-8")



class OpenTicketAdapter:
    action_name = "OpenTicket"

    def apply(
        self,
        target_repo: Path,
        *,
        spec_root: str = "specs",
        ticket_id: str = "CLI-124",
        title: str = "CLI ticket lifecycle",
    ) -> dict[str, object]:
        root = repo_root()
        setup = prepare_ticket_workflow(root, target_repo, spec_root=spec_root, ticket_id=ticket_id, title=title)
        result = run_cli(root, target_repo, "--spec-root", spec_root, "open", "ticket", ticket_id)
        ticket_dir = target_repo / spec_root / "tickets" / ticket_id
        return {
            "accepted": all(record.returncode == 0 for record in setup)
            and result.returncode == 0
            and (ticket_dir / "desired" / "Internal.tla").is_file()
            and (ticket_dir / "current" / "Internal.tla").is_file()
            and "Edit" in result.stdout
            and "desired" in result.stdout,
            "setup_exit_codes": [record.returncode for record in setup],
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "ticket_dir": str(ticket_dir),
        }


class CloseTicketAdapter:
    action_name = "CloseTicket"

    def apply(
        self,
        target_repo: Path,
        *,
        spec_root: str = "specs",
        ticket_id: str = "CLI-125",
        title: str = "CLI close ticket lifecycle",
    ) -> dict[str, object]:
        root = repo_root()
        setup = prepare_ticket_workflow(root, target_repo, spec_root=spec_root, ticket_id=ticket_id, title=title)
        opened = run_cli(root, target_repo, "--spec-root", spec_root, "open", "ticket", ticket_id)
        plan_path = target_repo / spec_root / "desired_program_model" / "ticket_plan.yaml"
        if plan_path.exists():
            plan_path.write_text(plan_path.read_text(encoding="utf-8").replace("status: next", "status: done", 1), encoding="utf-8")
        fill_complexity_ledger(target_repo, spec_root, ticket_id)
        result = run_cli(
            root,
            target_repo,
            "--spec-root",
            spec_root,
            "close",
            "ticket",
            ticket_id,
            "--summary",
            "closed from ticket lifecycle adapter",
        )
        ticket_dir = target_repo / spec_root / "tickets" / ticket_id
        history_dir = target_repo / spec_root / ".history" / "desired-ticket-workflow" / f"ticket-000-{ticket_id}"
        return {
            "accepted": all(record.returncode == 0 for record in setup)
            and opened.returncode == 0
            and result.returncode == 0
            and not ticket_dir.exists()
            and (history_dir / "manifest.json").is_file()
            and (target_repo / spec_root / "current" / "Internal.tla").is_file(),
            "setup_exit_codes": [record.returncode for record in setup],
            "open_exit_code": opened.returncode,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "history_dir": str(history_dir),
        }


class ClosePromotionPreservesCurrentAdapter:
    """MF-021: drive the shipped CLI and prove promotion does not destroy specs/current.

    Runs the real ``scaffold -> open ticket -> close ticket`` lifecycle against
    a throwaway repository. Between ``open`` and ``close`` it writes two kinds
    of path into project ``specs/current``:

    * ``unseeded_only.py`` -- created after the workspace was seeded, and
      ``probe-dir/note.txt`` inside a current-only directory. Neither was ever
      offered to the ticket, so promotion must preserve both. This is the exact
      shape of the loss that destroyed MF-012's budgets retention test and
      MF-020's ``refinement-probe/`` directory.
    * the project workflow test, which ``open ticket`` excludes from the ticket
      workspace by design and which promotion therefore must never delete.

    It also asserts the close output *enumerates* what it preserved: a silent
    survival would still leave the next regression undetectable.
    """

    action_name = "CloseTicket"

    def apply(
        self,
        target_repo: Path,
        *,
        spec_root: str = "specs",
        ticket_id: str = "CLI-127",
        title: str = "CLI close promotion preserves current",
    ) -> dict[str, object]:
        root = repo_root()
        setup = prepare_ticket_workflow(root, target_repo, spec_root=spec_root, ticket_id=ticket_id, title=title)
        opened = run_cli(root, target_repo, "--spec-root", spec_root, "open", "ticket", ticket_id)

        specs_current = target_repo / spec_root / "current"
        unseeded = specs_current / "unseeded_only.py"
        unseeded.write_text("MUST_SURVIVE_PROMOTION = True\n", encoding="utf-8")
        probe = specs_current / "probe-dir" / "note.txt"
        probe.parent.mkdir(parents=True, exist_ok=True)
        probe.write_text("current-only directory\n", encoding="utf-8")
        workflow_test = specs_current / "tests" / "test_current_ticket_workflow.py"
        workflow_test_existed = workflow_test.is_file()

        plan_path = target_repo / spec_root / "desired_program_model" / "ticket_plan.yaml"
        if plan_path.exists():
            plan_path.write_text(plan_path.read_text(encoding="utf-8").replace("status: next", "status: done", 1), encoding="utf-8")
        fill_complexity_ledger(target_repo, spec_root, ticket_id)
        result = run_cli(
            root,
            target_repo,
            "--spec-root",
            spec_root,
            "close",
            "ticket",
            ticket_id,
            "--summary",
            "closed from promotion-preservation adapter",
        )

        survived = unseeded.is_file() and probe.is_file()
        workflow_test_survived = (not workflow_test_existed) or workflow_test.is_file()
        enumerated = "unseeded_only.py" in result.stdout and "preserved" in result.stdout

        return {
            "accepted": all(record.returncode == 0 for record in setup)
            and opened.returncode == 0
            and result.returncode == 0
            and survived
            and workflow_test_survived
            and enumerated,
            "setup_exit_codes": [record.returncode for record in setup],
            "open_exit_code": opened.returncode,
            "exit_code": result.returncode,
            "current_only_file_survived": unseeded.is_file(),
            "current_only_directory_survived": probe.is_file(),
            "project_workflow_test_seeded": workflow_test_existed,
            "project_workflow_test_survived": workflow_test_survived,
            "preservation_enumerated_in_output": enumerated,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }


class SkillFeedbackCloseOutAdapter:
    """MF-017: drive the shipped CLI and prove close-out runs the Phase 6 retro.

    Closes a fixture workflow twice against a throwaway repository and asserts:

    * the first close emits ``<spec-root>/results/skill_feedback.md`` carrying
      all four prompt sections and the instruction to file each item as a
      ticket or PR against spec-double-compiler;
    * the history manifest records the filing status -- ``feedback_filed``
      false while the retro is unreviewed;
    * a finding filled in between the two closes survives the second close
      (the document accumulates; it is never regenerated over real content),
      and the second history entry records ``feedback_filed`` true together
      with *where* it was filed.
    """

    action_name = "CloseTicket"

    #: A real finding from this epic (GitHub #22): ticket-close promotion
    #: destroyed regression tests unique to specs/current.
    FINDING = (
        "\n### SF-001 — ticket-close promotion destroyed files unique to specs/current\n"
        "- category: profile-schema-cli\n"
        "- target: scripts/spec_evolution.py::replace_tree\n"
        "- observed_on: tla-spec-dev @ MF-012, MF-020, MF-021\n"
        "- evidence: tests/test_promotion_preserves_current.py\n"
        "- severity: silent-data-loss\n"
        "- root_cause: tool\n"
        "- surface: tla-spec-dev close ticket\n"
        "- forced_workaround: restore deleted regression tests from git history\n"
        "- data_loss: yes\n"
        "- recommendation: ticket https://github.com/haydenrear/tla-spec-dev/issues/22\n"
        "- status: filed\n"
    )

    def apply(
        self,
        target_repo: Path,
        *,
        spec_root: str = "specs",
        ticket_id: str = "CLI-129",
        title: str = "CLI close-out skill feedback",
    ) -> dict[str, object]:
        import json

        root = repo_root()
        setup = prepare_ticket_workflow(root, target_repo, spec_root=spec_root, ticket_id=ticket_id, title=title)
        plan_path = target_repo / spec_root / "desired_program_model" / "ticket_plan.yaml"

        def close(ticket: str) -> object:
            run_cli(root, target_repo, "--spec-root", spec_root, "open", "ticket", ticket)
            if plan_path.exists():
                plan_path.write_text(
                    plan_path.read_text(encoding="utf-8").replace("status: next", "status: done", 1),
                    encoding="utf-8",
                )
            fill_complexity_ledger(target_repo, spec_root, ticket)
            return run_cli(
                root, target_repo, "--spec-root", spec_root,
                "close", "ticket", ticket, "--summary", "closed from skill-feedback adapter",
            )

        first = close(ticket_id)

        feedback = target_repo / spec_root / "results" / "skill_feedback.md"
        emitted = feedback.is_file()
        text = feedback.read_text(encoding="utf-8") if emitted else ""
        sections = ["surviving-mutants", "unmodelable-effects", "budget-and-metric", "profile-schema-cli"]
        has_sections = all(section in text for section in sections)
        instructs_filing = "spec-double-compiler" in text and "ticket or PR" in text

        history_root = target_repo / spec_root / ".history" / "desired-ticket-workflow"
        first_manifest_path = history_root / f"ticket-000-{ticket_id}" / "manifest.json"
        first_manifest = json.loads(first_manifest_path.read_text(encoding="utf-8")) if first_manifest_path.is_file() else {}

        # A second close proves the document accumulates rather than being
        # regenerated, so the fixture plan needs a second ticket entry.
        second_ticket = f"{ticket_id}-B"
        if plan_path.exists():
            plan_path.write_text(
                plan_path.read_text(encoding="utf-8")
                + f'  - id: {second_ticket}\n    title: "second close"\n    status: next\n    depends_on: []\n',
                encoding="utf-8",
            )

        # Fill in a real finding, then close that second ticket.
        if emitted:
            feedback.write_text(
                text.replace("- feedback_status: unreviewed", "- feedback_status: items-recorded", 1) + self.FINDING,
                encoding="utf-8",
            )
        second = close(second_ticket)

        after = feedback.read_text(encoding="utf-8") if feedback.is_file() else ""
        finding_survived = "SF-001" in after and "issues/22" in after
        second_manifest_path = history_root / f"ticket-000-{second_ticket}" / "manifest.json"
        if not second_manifest_path.is_file():
            candidates = sorted(history_root.glob(f"ticket-*-{second_ticket}/manifest.json"))
            second_manifest_path = candidates[0] if candidates else second_manifest_path
        second_manifest = json.loads(second_manifest_path.read_text(encoding="utf-8")) if second_manifest_path.is_file() else {}

        first_filed = first_manifest.get("feedback_filed")
        second_filed = second_manifest.get("feedback_filed")
        filed_where = second_manifest.get("feedback_filed_where", [])

        return {
            "accepted": all(record.returncode == 0 for record in setup)
            and first.returncode == 0
            and second.returncode == 0
            and emitted
            and has_sections
            and instructs_filing
            and first_filed is False
            and finding_survived
            and second_filed is True
            and filed_where == ["https://github.com/haydenrear/tla-spec-dev/issues/22"],
            "setup_exit_codes": [record.returncode for record in setup],
            "exit_code": first.returncode,
            "second_exit_code": second.returncode,
            "template_emitted": emitted,
            "feedback_path": str(feedback),
            "prompt_sections_present": has_sections,
            "instructs_filing_against_skill_repo": instructs_filing,
            "first_close_feedback_filed": first_filed,
            "finding_survived_second_close": finding_survived,
            "second_close_feedback_filed": second_filed,
            "feedback_filed_where": filed_where,
            "stdout": first.stdout,
            "second_stdout": second.stdout,
            "stderr": first.stderr,
        }


class RunSpecUnitTestsAdapter:
    action_name = "RunSpecUnitTests"

    def apply(
        self,
        target_repo: Path,
        *,
        spec_root: str = "specs",
        ticket_id: str = "CLI-126",
        title: str = "CLI run spec-unit tests",
    ) -> dict[str, object]:
        root = repo_root()
        setup = prepare_ticket_workflow(root, target_repo, spec_root=spec_root, ticket_id=ticket_id, title=title)
        opened = run_cli(root, target_repo, "--spec-root", spec_root, "open", "ticket", ticket_id)
        ticket_current = target_repo / spec_root / "tickets" / ticket_id / "current"
        test_path = ticket_current / "tests" / "test_spec_unit_cli.py"
        test_path.parent.mkdir(parents=True, exist_ok=True)
        test_path.write_text("def test_spec_unit_cli():\n    assert True\n", encoding="utf-8")
        result = run_cli(root, target_repo, "--spec-root", spec_root, "run", "spec-unit-tests")
        return {
            "accepted": all(record.returncode == 0 for record in setup)
            and opened.returncode == 0
            and result.returncode == 0
            and str(ticket_current) in result.stdout
            and "spec-unit validation passed" in result.stdout,
            "setup_exit_codes": [record.returncode for record in setup],
            "open_exit_code": opened.returncode,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "ticket_current": str(ticket_current),
        }


class TestGraphCliAdapter:
    action_name = "ValidateTestGraphCli"

    def apply(self) -> dict[str, object]:
        root = repo_root()
        build = root / "test_graph" / "build.gradle.kts"
        readme = root / "test_graph" / "README.md"
        required_sources = [
            root / "test_graph" / "sources" / "tla_spec_dev_cli_install.py",
            root / "test_graph" / "sources" / "spec_workflow_create_repo.py",
            root / "test_graph" / "sources" / "spec_workflow_start_ticket.py",
            root / "test_graph" / "sources" / "spec_workflow_complete_ticket.py",
            root / "test_graph" / "sources" / "spec_workflow_spec_units.py",
            root / "test_graph" / "sources" / "spec_workflow_close_ticket.py",
            root / "test_graph" / "sources" / "spec_workflow_failure_cleanup_probe.py",
            root / "test_graph" / "sources" / "spec_workflow_cleanup.py",
        ]
        build_text = build.read_text(encoding="utf-8") if build.exists() else ""
        readme_text = readme.read_text(encoding="utf-8") if readme.exists() else ""
        required_fragments = [
            "testGraph(\"specWorkflow\")",
            "sources/tla_spec_dev_cli_install.py",
            "sources/spec_workflow_start_ticket.py",
            "sources/spec_workflow_spec_units.py",
            "sources/spec_workflow_close_ticket.py",
            "sources/spec_workflow_failure_cleanup_probe.py",
            "sources/spec_workflow_cleanup.py",
        ]
        return {
            "accepted": all(path.is_file() for path in required_sources)
            and all(fragment in build_text for fragment in required_fragments)
            and "tla-spec-dev --spec-root specs run spec-unit-tests" in readme_text
            and "cleanup after both passing and failing" in readme_text,
            "build": str(build),
            "readme": str(readme),
            "required_sources": [str(path) for path in required_sources],
            "missing_sources": [str(path) for path in required_sources if not path.is_file()],
        }


class RecordBudgetsAdapter:
    """Scaffolding establishes per-program budgets before any generation action.

    Runs the real scaffold into a temp dir and asserts the emitted manifest
    carries the budgets block with the documented defaults, and that the
    scaffold output instructs the agent to negotiate them with the user.
    """

    action_name = "RecordBudgets"

    def apply(self, target_repo: Path, *, spec_root: str = "specs", name: str = "BudgetProg") -> dict[str, object]:
        root = repo_root()
        sys.path.insert(0, str(root))
        from scripts.budgets import DEFAULT_BUDGETS, load_budgets

        result = subprocess.run(
            [
                sys.executable,
                str(root / "scripts" / "tla_spec_dev.py"),
                "--spec-root",
                spec_root,
                "scaffold",
                "project",
                "--name",
                name,
            ],
            cwd=target_repo,
            text=True,
            capture_output=True,
            check=False,
        )

        manifest = Path(target_repo) / spec_root / "program_model" / "spec_manifest.yaml"
        manifest_text = manifest.read_text() if manifest.is_file() else ""
        recorded = load_budgets(manifest, warn=False) if manifest.is_file() else {}
        stdout = result.stdout

        prompt_phrases = (
            "Propose these defaults to the user",
            "Ask which to adjust for this program",
            "one-line rationale",
        )

        return {
            "accepted": (
                result.returncode == 0
                and "budgets:" in manifest_text
                and recorded == DEFAULT_BUDGETS
                and all(phrase in stdout for phrase in prompt_phrases)
            ),
            "exit_code": result.returncode,
            "budgets_block_emitted": "budgets:" in manifest_text,
            "budgets": recorded,
            "defaults_match": recorded == DEFAULT_BUDGETS,
            "prompts_user": all(phrase in stdout for phrase in prompt_phrases),
            "manifest": str(manifest),
            "stderr": result.stderr,
        }


UNDER_BUDGET_TLA = """---------------------------- MODULE UnderBudget ----------------------------
EXTENDS Naturals

CONSTANTS Slots

VARIABLES armed, fired

vars == << armed, fired >>

Init ==
  /\\ armed = FALSE
  /\\ fired = FALSE

Arm ==
  /\\ ~armed
  /\\ armed' = TRUE
  /\\ UNCHANGED << fired >>

Fire ==
  /\\ armed
  /\\ ~fired
  /\\ fired' = TRUE
  /\\ UNCHANGED << armed >>

Next == Arm \\/ Fire

TypeInvariant ==
  /\\ armed \\in BOOLEAN
  /\\ fired \\in BOOLEAN

Spec == Init /\\ [][Next]_vars
=============================================================================
"""

UNDER_BUDGET_CFG = """SPECIFICATION Spec

CONSTANTS
  Slots = {s1, s2}

INVARIANTS
  TypeInvariant
"""

OVER_BUDGET_TLA = """---------------------------- MODULE OverBudget ----------------------------
EXTENDS Naturals

CONSTANTS Nodes

VARIABLES a, b, c, d

vars == << a, b, c, d >>

Init ==
  /\\ a = [n \\in Nodes |-> 0]
  /\\ b = [n \\in Nodes |-> 0]
  /\\ c = {}
  /\\ d = {}

BumpA ==
  /\\ \\E n \\in Nodes: a' = [a EXCEPT ![n] = 1]
  /\\ UNCHANGED << b, c, d >>

BumpB ==
  /\\ \\E n \\in Nodes: b' = [b EXCEPT ![n] = 1]
  /\\ UNCHANGED << a, c, d >>

AddC ==
  /\\ \\E n \\in Nodes: c' = c \\cup {n}
  /\\ UNCHANGED << a, b, d >>

AddD ==
  /\\ \\E n \\in Nodes: d' = d \\cup {n}
  /\\ UNCHANGED << a, b, c >>

Next == BumpA \\/ BumpB \\/ AddC \\/ AddD

TypeInvariant ==
  /\\ a \\in [Nodes -> 0..9]
  /\\ b \\in [Nodes -> 0..9]
  /\\ c \\subseteq Nodes
  /\\ d \\subseteq Nodes

Spec == Init /\\ [][Next]_vars
=============================================================================
"""

OVER_BUDGET_CFG = """SPECIFICATION Spec

CONSTANTS
  Nodes = {n1, n2, n3, n4, n5, n6}

INVARIANTS
  TypeInvariant
"""

BUDGET_MANIFEST = """module: Fixture
budgets:
  max_distinct_states: 50000
  max_component_variables: 6
  max_component_actions: 8
"""

# Deliberately unmeetable budgets applied to the *small* fixture. This is how
# the generation refusal and its override are exercised: the gate must fail,
# but TLC must still finish instantly when the override lets it through. Using
# the genuinely huge OverBudget fixture here would hang forever -- which is
# precisely the failure this command exists to prevent.
TIGHT_MANIFEST = """module: Fixture
budgets:
  max_distinct_states: 2
  max_component_variables: 1
  max_component_actions: 1
"""


def _write_fixture(
    directory: Path, module: str, tla: str, cfg: str, manifest: str = BUDGET_MANIFEST
) -> tuple[Path, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    tla_path = directory / f"{module}.tla"
    cfg_path = directory / "MC.cfg"
    tla_path.write_text(tla, encoding="utf-8")
    cfg_path.write_text(cfg, encoding="utf-8")
    (directory / "spec_manifest.yaml").write_text(manifest, encoding="utf-8")
    return tla_path, cfg_path


class AnalyzeComplexityAdapter:
    """`tla-spec-dev analyze complexity` ADVISES a model against its thresholds.

    MF-036: complexity is a scanner, not a gate
    (references/architecture_tractability.md, "Advisory, Not Blocking"). Runs the
    REAL command against two fixture specs -- one comfortably under threshold,
    one far over it -- and asserts the table output, that BOTH sides exit 0 (a
    complex model is a finding, not a failure), that the over-threshold side
    emits a WARNING with a recommendation, and that case generation ADVISES but
    never refuses.

    The over-threshold fixture is 6 nodes x two 0..9 functions x two powersets:
    10^6 * 10^6 * 2^6 * 2^6, far above the default threshold. It produces a
    warning-bearing REPORT (exit 0), never a promotion failure.
    """

    action_name = "AnalyzeComplexity"

    def apply(self, target_repo: Path, *, spec_root: str = "specs") -> dict[str, object]:
        root = repo_root()
        target_repo = Path(target_repo)

        under_tla, under_cfg = _write_fixture(
            target_repo / "under", "UnderBudget", UNDER_BUDGET_TLA, UNDER_BUDGET_CFG
        )
        over_tla, over_cfg = _write_fixture(
            target_repo / "over", "OverBudget", OVER_BUDGET_TLA, OVER_BUDGET_CFG
        )

        def cli(*args: str) -> subprocess.CompletedProcess:
            return subprocess.run(
                [sys.executable, str(root / "scripts" / "tla_spec_dev.py"),
                 "--spec-root", spec_root, "analyze", "complexity", *args],
                cwd=target_repo, text=True, capture_output=True, check=False,
            )

        under = cli(str(under_tla), str(under_cfg))
        over = cli(str(over_tla), str(over_cfg))

        # Case generation must ADVISE above the threshold and proceed anyway --
        # never refuse. Exercised against a SMALL model carrying unmeetable
        # thresholds, so the advisory path is reached but generation completes.
        tight_tla, tight_cfg = _write_fixture(
            target_repo / "tight", "UnderBudget", UNDER_BUDGET_TLA, UNDER_BUDGET_CFG,
            manifest=TIGHT_MANIFEST,
        )

        def generate(*extra: str) -> subprocess.CompletedProcess:
            return subprocess.run(
                [sys.executable, str(root / "scripts" / "generate_cases_from_tlc_dump.py"),
                 str(tight_tla), str(tight_cfg), "--out", str(target_repo / "generated"), *extra],
                cwd=target_repo, text=True, capture_output=True, check=False,
                timeout=180,
            )

        advised = generate()

        table_phrases = ("Dimension table", "State-space upper bound",
                         "read/write matrix", "SUGGESTED MOVE")
        under_has_table = all(phrase in under.stdout for phrase in table_phrases)
        recommendation_labeled = (
            "RECOMMENDATION -- REQUIRES USER APPROVAL, NOT AUTO-APPLIED" in under.stdout
        )
        measured_projected_split = "[MEASURED]" in under.stdout and "[PROJECTED]" in under.stdout
        over_names_dimensions = "dominant dimensions" in over.stdout.lower()
        # The over-threshold model produces a warning-bearing REPORT, not a
        # failure: a WARNING that names the target and RECOMMENDS a concrete move.
        over_warns_and_recommends = (
            "WARNING:" in over.stdout and "recommendation:" in over.stdout
        )

        # Generation advises (prints the warnings) and proceeds -- it never
        # refuses, and there is no over-budget override flag to honor.
        advisory_ok = (
            "ADVISORY WARNINGS" in advised.stderr
            and "recommendation:" in advised.stderr
            and "Proceeding with case generation" in advised.stderr
            and "REFUSING to generate cases" not in advised.stderr
        )

        return {
            "accepted": (
                under.returncode == 0
                and over.returncode == 0
                and under_has_table
                and recommendation_labeled
                and measured_projected_split
                and over_names_dimensions
                and over_warns_and_recommends
                and advisory_ok
            ),
            "under_budget_exit_code": under.returncode,
            "over_budget_exit_code": over.returncode,
            "prints_dimension_table": under_has_table,
            "suggested_move_labeled_recommendation": recommendation_labeled,
            "separates_measured_from_projected": measured_projected_split,
            "over_budget_names_dominant_dimensions": over_names_dimensions,
            "over_budget_warns_and_recommends": over_warns_and_recommends,
            "generation_advises_not_refused": advisory_ok,
            "stderr": under.stderr + over.stderr,
        }


# --------------------------------------------------------------------------
# MF-014: corpus diagnostics and hard case caps
# --------------------------------------------------------------------------

CORPUS_FIXTURE_CASES = '''
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class StateGraphInput:
    action: str
    source_node: str
    target_node: str
    params: dict = field(default_factory=dict)


@dataclass(frozen=True)
class StateGraphCase:
    name: str
    before: dict
    input: StateGraphInput
    output: Any
    after: dict
    labels: frozenset
    view: str = "external"
    layer: str = "external"


SOURCE_MODULE = "Fixture"
SOURCE_VIEW = "external"

CASES = [
    StateGraphCase(
        name="case_%04d_SubmitDuplicate" % i,
        before={"n": i % 7, "seen": True},
        input=StateGraphInput("SubmitDuplicate", str(1000 + i), str(2000 + i), {"client": "c%d" % i}),
        output={},
        after={"n": i % 7, "seen": True},
        labels=frozenset({"SubmitDuplicate", "duplicate_submission"}),
    )
    for i in range(__COUNT__)
] + [
    StateGraphCase(
        name="case_regression_promoted",
        before={"n": 0},
        input=StateGraphInput("SubmitOnce", "1", "2", {}),
        output={},
        after={"n": 1},
        labels=frozenset({"SubmitOnce", "regression:issue-41"}),
    )
]

CASES_BY_NAME = {c.name: c for c in CASES}
'''


def _write_corpus_fixture(target: Path, count: int, cap: int) -> tuple[Path, Path]:
    """A generated-package-shaped corpus with `count` cases of one action."""
    package = target / "generated" / "fixture_cases"
    package.mkdir(parents=True, exist_ok=True)
    (package / "__init__.py").write_text(
        "from .cases import CASES, CASES_BY_NAME, SOURCE_MODULE, SOURCE_VIEW\n", encoding="utf-8"
    )
    (package / "cases.py").write_text(
        CORPUS_FIXTURE_CASES.replace("__COUNT__", str(count)), encoding="utf-8"
    )
    manifest = target / "spec_manifest.yaml"
    manifest.write_text(
        f"module: Fixture\nbudgets:\n  max_external_cases_per_action: {cap}\n", encoding="utf-8"
    )
    return package, manifest


class AnalyzeCorpusAdapter:
    """`tla-spec-dev analyze corpus` gates a generated corpus against its caps.

    Runs the REAL command on both sides of the cap and asserts the model's
    central claim: over cap it REPORTS AND REFUSES, and the corpus is exactly
    as large afterwards as it was before. Nothing is dropped, filtered,
    sampled, or truncated to fit the budget -- so the same fixture that fails
    at cap 50 passes unchanged at cap 500, with every case still present.
    """

    action_name = "AnalyzeCorpus"

    def apply(self, target_repo: Path, *, spec_root: str = "specs") -> dict[str, object]:
        root = repo_root()
        target_repo = Path(target_repo)

        over_pkg, over_manifest = _write_corpus_fixture(target_repo / "over", count=200, cap=50)
        under_pkg, under_manifest = _write_corpus_fixture(target_repo / "under", count=200, cap=500)

        def cli(pkg: Path, manifest: Path) -> subprocess.CompletedProcess:
            return subprocess.run(
                [sys.executable, str(root / "scripts" / "tla_spec_dev.py"),
                 "--spec-root", spec_root, "analyze", "corpus", str(pkg),
                 "--view", "external", "--manifest", str(manifest)],
                cwd=target_repo, text=True, capture_output=True, check=False, timeout=180,
            )

        over = cli(over_pkg, over_manifest)
        under = cli(under_pkg, under_manifest)

        def case_count(pkg: Path) -> int:
            import re
            return len(re.findall(r"StateGraphCase\(", (pkg / "cases.py").read_text(encoding="utf-8")))

        # The same 201-case corpus, before and after a FAILING gate run.
        corpus_intact = case_count(over_pkg) == case_count(under_pkg)

        reports_distribution = "Distribution per (action, label class)" in over.stdout
        reports_dominant = "Strata that DOMINATE the corpus" in over.stdout
        reports_starved = "Strata that are STARVED" in over.stdout
        reports_variance = "What VARIES across the redundant group" in over.stdout
        names_cause = "Likely cause:" in over.stdout
        recommendation_labeled = (
            "RECOMMENDATION REQUIRING USER APPROVAL -- not applied automatically." in over.stdout
        )
        accept_path = (
            "ACCEPT PATH" in over.stdout
            and "source: negotiated" in over.stdout
            and "rationale:" in over.stdout
        )
        never_trims = (
            "Nothing was" in over.stdout
            and "trimmed" in over.stdout
            and "dropped, filtered, sampled, or truncated" in over.stdout
        )
        regression_retained = (
            "Named regression traces (always retained)" in over.stdout
            and "Named regression traces (always retained)" in under.stdout
        )
        no_trim_offered = "--distill" not in over.stdout and "--trim" not in over.stdout

        return {
            "accepted": (
                over.returncode == 1
                and under.returncode == 0
                and corpus_intact
                and reports_distribution
                and reports_dominant
                and reports_starved
                and reports_variance
                and names_cause
                and recommendation_labeled
                and accept_path
                and never_trims
                and regression_retained
                and no_trim_offered
            ),
            "over_cap_exit_code": over.returncode,
            "raised_cap_exit_code": under.returncode,
            "corpus_unchanged_by_failing_gate": corpus_intact,
            "reports_count_per_action_and_label_class": reports_distribution,
            "reports_dominant_strata": reports_dominant,
            "reports_starved_strata": reports_starved,
            "reports_what_varies_across_redundant_group": reports_variance,
            "names_representation_cause": names_cause,
            "remediation_labeled_recommendation": recommendation_labeled,
            "cap_raise_accept_path_offered": accept_path,
            "never_offers_to_trim": never_trims and no_trim_offered,
            "regression_traces_retained": regression_retained,
            "stdout": over.stdout,
            "stderr": over.stderr + under.stderr,
        }


class RunEffectConformanceAdapter:
    """`tla-spec-dev run effect-conformance` diffs observed vs declared effects.

    Runs the REAL command over three fixture spec directories and asserts the
    model's central claim: an undeclared observed effect FAILS, and NOTHING
    suppresses that failure.

    The load-bearing assertion is
    `justification_does_not_change_the_verdict`: two fixtures identical except
    that one carries a recorded justification produce byte-identical verdicts.
    That is the inverse test the 2026-07-18 degeneracy audit required -- there
    is deliberately no fixture proving suppression works, because out-of-
    contract justifications are withdrawn and suppression no longer exists.
    """

    action_name = "RunEffectConformance"

    _DECLARED = """module: Demo
effects:
  components:
    C:
      ports:
        workspace:
          type: filesystem.write
          target: "**/workspace/**"
  actions:
    Act: [workspace]
"""

    def apply(self, target_repo: Path, *, spec_root: str = "specs") -> dict[str, object]:
        root = repo_root()
        target_repo = Path(target_repo)

        def fixture(name: str, body: str) -> Path:
            spec_dir = target_repo / name
            spec_dir.mkdir(parents=True, exist_ok=True)
            (spec_dir / "spec_manifest.yaml").write_text(body, encoding="utf-8")
            return spec_dir

        plain = fixture("plain", self._DECLARED)
        justified = fixture(
            "justified",
            self._DECLARED + "  justification: 'accepted by review; ports are aspirational'\n",
        )
        undeclared = fixture("undeclared", "module: Demo\n")

        def cli(spec_dir: Path, out: Path) -> subprocess.CompletedProcess:
            return subprocess.run(
                [sys.executable, str(root / "scripts" / "tla_spec_dev.py"),
                 "--spec-root", spec_root, "run", "effect-conformance",
                 "--target", str(spec_dir), "--out", str(out)],
                cwd=target_repo, text=True, capture_output=True, check=False, timeout=180,
            )

        plain_out = target_repo / "plain.json"
        justified_out = target_repo / "justified.json"
        plain_run = cli(plain, plain_out)
        justified_run = cli(justified, justified_out)
        undeclared_run = cli(undeclared, target_repo / "undeclared.json")

        plain_report = json.loads(plain_out.read_text(encoding="utf-8"))
        justified_report = json.loads(justified_out.read_text(encoding="utf-8"))

        # The inverse test: identical outcome with and without a justification.
        same_verdict = (
            plain_report["verdict"] == justified_report["verdict"]
            and plain_report["ok"] == justified_report["ok"] is False
            and plain_run.returncode == justified_run.returncode == 1
        )
        # ...and the ignored key is surfaced rather than silently dropped.
        suppression_reported = justified_report["ignored_suppression_keys"] == ["effects.justification"]
        policy_recorded = "withdrawn" in plain_report["suppression_policy"]

        return {
            "accepted": bool(
                same_verdict
                and suppression_reported
                and policy_recorded
                and undeclared_run.returncode == 2
            ),
            "findings_exit_code": plain_run.returncode,
            "justified_exit_code": justified_run.returncode,
            "no_declarations_exit_code": undeclared_run.returncode,
            "justification_does_not_change_the_verdict": same_verdict,
            "suppression_attempt_reported_not_honored": suppression_reported,
            "suppression_policy_recorded_in_report": policy_recorded,
            "report_written_as_evidence": plain_out.is_file() and justified_out.is_file(),
            "stdout": plain_run.stdout + justified_run.stdout,
            "stderr": plain_run.stderr + justified_run.stderr + undeclared_run.stderr,
        }


class RunKillTestAdapter:
    """`tla-spec-dev run kill-test` -- oracle 4, the mutation kill test.

    Runs the REAL command over fixture spec directories and asserts the
    model's central claims. Three of them are load-bearing:

    1. `below_floor_fails` -- a kill rate under `kill_rate_floor` exits
       nonzero. The floor is the VALUE floor that keeps every cost cap in the
       toolchain honest, so if this ever passes silently, every budget in the
       epic becomes gameable by shrinking the model toward nothing.
    2. `uncovered_boundary_refuses_and_computes_no_rate` -- a declared port
       with no seeded fault yields `incomplete_catalog` and NO kill rate,
       rather than a flattering 1.0 over the mutants that happen to exist.
       Same discipline MF-027 applied to `unobservable`.
    3. `waiver_does_not_change_the_verdict` -- two catalogs identical except
       that one carries `waiver`/`expected_to_survive` keys produce
       byte-identical verdicts. There is deliberately NO fixture proving a
       waiver works, because no waiver exists.

    The fixture programs are trivial on purpose: a real corpus run is deferred
    epic-wide to MF-023, so what is proved here is the GATE, not this
    repository's actual kill rate.
    """

    action_name = "RunKillTest"

    _MANIFEST = """module: Demo
budgets:
  kill_rate_floor: 0.8
effects:
  components:
    DemoPort:
      ports:
        alpha:
          type: filesystem.write
          target: "**/a/**"
  actions:
    Act: [alpha]
"""

    _CFG = """SPECIFICATION Spec

CONSTANTS
  Xs = {x}

INVARIANTS
  TypeInvariant
"""

    @staticmethod
    def _catalog(entries: str) -> str:
        return entries

    def _fixture(self, directory: Path, *, catalog: str, source: str) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "spec_manifest.yaml").write_text(self._MANIFEST, encoding="utf-8")
        (directory / "MC.cfg").write_text(self._CFG, encoding="utf-8")
        (directory / "kill_mutants.toml").write_text(catalog, encoding="utf-8")
        (directory / "src.py").write_text(source, encoding="utf-8")
        return directory

    @staticmethod
    def _mutant(ident: str, kind: str, ref: str, find: str, replace: str, **extra: str) -> str:
        block = [
            "[[mutants]]",
            f'id = "{ident}"',
            f'boundary_kind = "{kind}"',
            f'boundary_ref = "{ref}"',
            'path = "src.py"',
            f'find = "{find}"',
            f'replace = "{replace}"',
            f'description = "fault at {ref}"',
            'refine_variable = "demo_var"',
            'refine_action = "DemoAction"',
        ]
        block.extend(f'{key} = "{value}"' for key, value in extra.items())
        return "\n".join(block) + "\n"

    def apply(self, target_repo: Path) -> dict[str, object]:
        root = repo_root()
        target_repo = Path(target_repo)
        script = str(root / "scripts" / "run_kill_test.py")

        def run(spec_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
            # --root is the tree the mutant `path` fields are relative to.
            # Each fixture owns its own source file, so seeding never touches
            # this repository's real code.
            return subprocess.run(
                [sys.executable, script, "--target", str(spec_dir), "--root", str(spec_dir), *args],
                cwd=target_repo,
                text=True,
                capture_output=True,
                check=False,
                timeout=180,
            )

        # A corpus command that kills a mutant iff the seeded file no longer
        # contains the correct marker. Killing is therefore genuinely a
        # function of the seeded fault, not of the runner -- a runner that
        # returned a fixed answer would prove nothing about the gate.
        # Markers are disjoint strings, never substrings of one another: a
        # marker that contains another silently makes a mutant look dead.
        detector = target_repo / "detect.py"
        detector.write_text(
            "import pathlib, sys\n"
            "text = pathlib.Path(sys.argv[1]).read_text()\n"
            "missing = [m for m in sys.argv[2:] if m not in text]\n"
            "sys.exit(1 if missing else 0)\n",
            encoding="utf-8",
        )

        # --- fixture 1: complete catalog, every mutant killed -------------
        complete = self._fixture(
            target_repo / "kt_complete",
            catalog=(
                self._mutant("m-alpha", "port", "alpha", "MARKONE", "BROKENONE")
                + self._mutant("m-type", "invariant", "TypeInvariant", "MARKTWO", "BROKENTWO")
            ),
            source="a = 'MARKONE'\nb = 'MARKTWO'\n",
        )
        cmd = f"{sys.executable} {detector} {complete / 'src.py'} MARKONE MARKTWO"
        pass_out = target_repo / "results" / "pass.json"
        pass_run = run(complete, "--corpus-command", cmd, "--out", str(pass_out))
        pass_payload = json.loads(pass_out.read_text(encoding="utf-8")) if pass_out.is_file() else {}

        # --- fixture 2: complete catalog, one mutant survives -------------
        # The second mutant edits a line the detector never reads, so the
        # corpus cannot tell the broken program from the correct one.
        surviving = self._fixture(
            target_repo / "kt_survivor",
            catalog=(
                self._mutant("m-alpha", "port", "alpha", "MARKONE", "BROKENONE")
                + self._mutant("m-type", "invariant", "TypeInvariant", "UNWATCHED", "MUTATED")
            ),
            source="a = 'MARKONE'\nb = 'UNWATCHED'\n",
        )
        surv_cmd = f"{sys.executable} {detector} {surviving / 'src.py'} MARKONE"
        surv_out = target_repo / "results" / "below.json"
        surv_run = run(surviving, "--corpus-command", surv_cmd, "--out", str(surv_out))
        surv_payload = json.loads(surv_out.read_text(encoding="utf-8")) if surv_out.is_file() else {}

        # --- fixture 3: a declared port with NO seeded fault --------------
        uncovered = self._fixture(
            target_repo / "kt_uncovered",
            catalog=self._mutant("m-alpha", "port", "alpha", "MARKONE", "BROKENONE"),
            source="a = 'MARKONE'\n",
        )
        unc_cmd = f"{sys.executable} {detector} {uncovered / 'src.py'} MARKONE"
        unc_out = target_repo / "results" / "uncovered.json"
        unc_run = run(uncovered, "--corpus-command", unc_cmd, "--out", str(unc_out))
        unc_payload = json.loads(unc_out.read_text(encoding="utf-8")) if unc_out.is_file() else {}

        # --- fixture 4: the survivor catalog PLUS waiver keys -------------
        waived = self._fixture(
            target_repo / "kt_waived",
            catalog=(
                self._mutant("m-alpha", "port", "alpha", "MARKONE", "BROKENONE")
                + self._mutant(
                    "m-type",
                    "invariant",
                    "TypeInvariant",
                    "UNWATCHED",
                    "MUTATED",
                    waiver="the owner accepted this survivor",
                    expected_to_survive="yes",
                )
            ),
            source="a = 'MARKONE'\nb = 'UNWATCHED'\n",
        )
        waived_cmd = f"{sys.executable} {detector} {waived / 'src.py'} MARKONE"
        waived_out = target_repo / "results" / "waived.json"
        waived_run = run(waived, "--corpus-command", waived_cmd, "--out", str(waived_out))
        waived_payload = (
            json.loads(waived_out.read_text(encoding="utf-8")) if waived_out.is_file() else {}
        )

        survivors = surv_payload.get("surviving_mutants", [])
        pointer = survivors[0] if survivors else {}

        return {
            "accepted": pass_run.returncode == 0,
            # 1. the floor gate
            "pass_verdict": pass_payload.get("verdict"),
            "pass_exit_code": pass_run.returncode,
            "pass_kill_rate": pass_payload.get("kill_rate"),
            "below_floor_verdict": surv_payload.get("verdict"),
            "below_floor_exit_code": surv_run.returncode,
            "below_floor_kill_rate": surv_payload.get("kill_rate"),
            "below_floor_fails": surv_run.returncode == 1,
            # 2. a partial experiment yields no number
            "uncovered_verdict": unc_payload.get("verdict"),
            "uncovered_exit_code": unc_run.returncode,
            "uncovered_kill_rate_is_absent": unc_payload.get("kill_rate") is None,
            "uncovered_boundaries": unc_payload.get("uncovered_boundaries", []),
            # 3. no waiver
            "waived_verdict": waived_payload.get("verdict"),
            "waived_exit_code": waived_run.returncode,
            "waiver_does_not_change_the_verdict": (
                waived_payload.get("verdict") == surv_payload.get("verdict")
                and waived_payload.get("kill_rate") == surv_payload.get("kill_rate")
                and waived_run.returncode == surv_run.returncode
            ),
            "waiver_reported_not_honored": bool(
                waived_payload.get("ignored_suppression_keys")
            ),
            # 4. a survivor is a pointer
            "survivor_names_variable": pointer.get("refine_variable"),
            "survivor_names_action": pointer.get("refine_action"),
            "survivor_names_boundary": pointer.get("boundary_ref"),
            # 5. evidence layout
            "report_written_as_evidence": all(
                path.is_file() for path in (pass_out, surv_out, unc_out, waived_out)
            ),
            "kill_matrix_rows": len(surv_payload.get("kill_matrix", [])),
            "stdout": pass_run.stdout + surv_run.stdout,
            "stderr": pass_run.stderr + surv_run.stderr + unc_run.stderr,
        }


class ComplexityLedgerCloseOutAdapter:
    """MF-019: prove the standing objective is a GATE on the shipped close path.

    Drives the real CLI (`scaffold -> open ticket -> close ticket`) against a
    throwaway repository, four times, and asserts the close-time behavior that
    eleven tickets of this epic performed by hand:

    * a filled ledger input closes, and the history entry records the complexity
      delta JOINTLY with its retention evidence and the refinement record;
    * an UNFILLED scaffolded template refuses the close -- the standing
      objective is a required step, not an optional one;
    * a complexity DECREASE with degraded retention evidence is REJECTED, which
      is the anti-gaming rule (MF-016 and MF-027 both applied it by hand);
    * `unobservable` effect conformance does NOT count as `clean` (MF-027).
    """

    action_name = "CloseTicket"

    def apply(
        self,
        target_repo: Path,
        *,
        spec_root: str = "specs",
        ticket_id: str = "CLI-140",
        title: str = "CLI complexity ledger close-out",
    ) -> dict[str, object]:
        import json

        root = repo_root()
        setup = prepare_ticket_workflow(root, target_repo, spec_root=spec_root, ticket_id=ticket_id, title=title)
        plan_path = target_repo / spec_root / "desired_program_model" / "ticket_plan.yaml"

        def open_ticket(ticket: str) -> Path:
            if ticket != ticket_id and plan_path.exists():
                plan_path.write_text(
                    plan_path.read_text(encoding="utf-8")
                    + f'  - id: {ticket}\n    title: "ledger case"\n    status: next\n    depends_on: []\n',
                    encoding="utf-8",
                )
            run_cli(root, target_repo, "--spec-root", spec_root, "open", "ticket", ticket)
            return target_repo / spec_root / "tickets" / ticket / "results" / "complexity_ledger.yaml"

        def close(ticket: str):
            if plan_path.exists():
                plan_path.write_text(
                    plan_path.read_text(encoding="utf-8").replace("status: next", "status: done", 1),
                    encoding="utf-8",
                )
            return run_cli(
                root, target_repo, "--spec-root", spec_root,
                "close", "ticket", ticket, "--summary", "closed from complexity-ledger adapter",
            )

        # 1. Filled ledger input -> the close is recorded.
        ledger_input = open_ticket(ticket_id)
        template_scaffolded = ledger_input.is_file() and "TODO" in ledger_input.read_text(encoding="utf-8")
        set_ticket_model(target_repo, spec_root, ticket_id, BASELINE_FIXTURE_MODEL)
        fill_complexity_ledger(target_repo, spec_root, ticket_id)
        good = close(ticket_id)

        history_root = target_repo / spec_root / ".history" / "desired-ticket-workflow"
        manifest_path = history_root / f"ticket-000-{ticket_id}" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
        ledger_file = target_repo / spec_root / "results" / "complexity_ledger.json"

        # 2. The scaffolded template, left unfilled, must REFUSE the close.
        unfilled_ticket = f"{ticket_id}-UNFILLED"
        open_ticket(unfilled_ticket)
        unfilled = close(unfilled_ticket)

        # 3. A decrease with a degraded kill rate must be REJECTED.
        degraded_ticket = f"{ticket_id}-DEGRADED"
        degraded_input = open_ticket(degraded_ticket)
        degraded_input.write_text(
            PASSING_COMPLEXITY_LEDGER.replace('status: "pass"', 'status: "below_floor"', 1),
            encoding="utf-8",
        )
        # Shrink the model so the delta is a genuine decrease. Both trees, so
        # the current==desired equality gate still passes and the refusal under
        # test is the ledger's, not an earlier gate's.
        set_ticket_model(target_repo, spec_root, degraded_ticket, SHRUNK_FIXTURE_MODEL)
        degraded = close(degraded_ticket)

        # 4. `unobservable` is not `clean`.
        unobs_ticket = f"{ticket_id}-UNOBSERVABLE"
        unobs_input = open_ticket(unobs_ticket)
        unobs_input.write_text(
            PASSING_COMPLEXITY_LEDGER.replace('status: "clean"', 'status: "unobservable"', 1),
            encoding="utf-8",
        )
        set_ticket_model(target_repo, spec_root, unobs_ticket, SHRUNK_FIXTURE_MODEL)
        unobservable = close(unobs_ticket)

        return {
            "accepted": all(record.returncode == 0 for record in setup)
            and good.returncode == 0
            and template_scaffolded
            and unfilled.returncode != 0
            and degraded.returncode != 0
            and unobservable.returncode != 0,
            # 1. recorded, jointly
            "close_recorded": good.returncode == 0,
            "ledger_file_written": ledger_file.is_file(),
            "delta_recorded": manifest.get("complexity_delta") is not None,
            "retention_recorded": manifest.get("retention_evidence") is not None,
            "refinement_recorded": (manifest.get("refinement_record") or {}).get("outcome"),
            "delta_and_retention_in_same_entry": bool(
                manifest.get("complexity_delta") is not None
                and manifest.get("retention_evidence") is not None
            ),
            # 2. the template is a gate, not a suggestion
            "template_scaffolded_with_sentinels": template_scaffolded,
            "unfilled_template_refuses_close": unfilled.returncode != 0,
            "unfilled_names_refinement_and_narrative": (
                "refinement" in unfilled.stdout + unfilled.stderr
                and "narrative" in unfilled.stdout + unfilled.stderr
            ),
            # 3. anti-gaming
            "degraded_decrease_rejected": degraded.returncode != 0,
            "degraded_message_says_rejected": "REJECTED" in degraded.stdout + degraded.stderr,
            # 4. MF-027
            "unobservable_rejected": unobservable.returncode != 0,
            "unobservable_is_not_clean": "unobservable" in unobservable.stdout + unobservable.stderr,
            "stdout": good.stdout + unfilled.stdout + degraded.stdout,
            "stderr": good.stderr + unfilled.stderr + degraded.stderr,
        }
