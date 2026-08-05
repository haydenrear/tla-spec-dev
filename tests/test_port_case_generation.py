"""PA-03: ports in the manifest, and cases generated PER PORT.

The two senses of "adapter" become one object here. The prompt already makes an
agent declare ports in the DOMAIN'S vocabulary; these tests cover the half that
makes a port the agent invented into a port the TOOLCHAIN knows about -- read
out of the manifest in the same shape the effect ports already use, turned into
a case set of its own, and CHECKED AGAINST BEHAVIOUR rather than believed.

That last clause is the plan's `declaration_executability_rule`, and it is here
because a declaration nothing executes drifted five times in five consecutive
attempts by three authors, plus once through a test that passed vacuously by
reading the wrong key. So:

* every consumer reads the declaration through the SHIPPED builder
  (``load_port_catalog``), never by re-parsing YAML in a test;
* the prompt's own worked example is fed through that builder, so a rename in
  either the prompt or the reader fails a test rather than silently teaching a
  shape nothing reads;
* the generated port cases are EXECUTED against a real adapter and its fake,
  with a fault seeded in each, so "a port case drives a port" is a measured
  claim and not a sentence.
"""

from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generate_cases_from_tlc_dump import (  # noqa: E402
    NEGATIVE_LABEL,
    PORT_EMITTED_LABEL,
    PORT_SILENT_LABEL,
    Edge,
    PortCatalog,
    load_port_catalog,
    port_cases_for_corpus,
    port_regions,
    prepare_cases,
    render_python_package,
    _signatures_for_regions,
)
from scripts.infer_action_params import build_recipes  # noqa: E402
from scripts.run_generated_case_adapters import assert_case_result_per_field  # noqa: E402

AB_MANIFEST = ROOT / "examples/validation/ab/model/spec_manifest.yaml"
HEXAGONAL_PROMPT = ROOT / "prompts/hexagonal_implementation.md"


# ---------------------------------------------------------------------------
# A tiny model with ONE durable side, so a port has something to be behind.
# ---------------------------------------------------------------------------

TINY_MODULE = """---- MODULE Tiny ----
EXTENDS Naturals, Sequences

CONSTANTS Items

VARIABLES held, journal, outcome

vars == << held, journal, outcome >>

Init ==
  /\\ held = {}
  /\\ journal = << >>
  /\\ outcome = "init"

Take(i) ==
  /\\ i \\notin held
  /\\ held' = held \\cup {i}
  /\\ outcome' = "taken"
  /\\ UNCHANGED << journal >>

Commit(i) ==
  /\\ i \\in held
  /\\ held' = held \\ {i}
  /\\ journal' = Append(journal, i)
  /\\ outcome' = "committed"

RefuseTake(i) ==
  /\\ i \\in held
  /\\ outcome' = "refused"
  /\\ UNCHANGED << held, journal >>

Next ==
  \\/ \\E i \\in Items : Take(i)
  \\/ \\E i \\in Items : Commit(i)
  \\/ \\E i \\in Items : RefuseTake(i)

====
"""

TINY_CFG = """SPECIFICATION Spec
CONSTANTS
  Items = {a, b}
"""

TINY_MANIFEST = """module: Tiny
package: tiny_cases
effects:
  components:
    store:
      ports:
        JournalPort:
          kind: durable_write
          asserts_content: true
  actions:
    Commit: [JournalPort]
    Take: []
"""


def tiny_states() -> dict[str, dict[str, Any]]:
    return {
        "1": {"held": frozenset(), "journal": (), "outcome": "init"},
        "2": {"held": frozenset({"a"}), "journal": (), "outcome": "taken"},
        "3": {"held": frozenset(), "journal": ("a",), "outcome": "committed"},
    }


def tiny_edges() -> list[Edge]:
    return [
        Edge(source="1", target="2", action="Take"),
        Edge(source="2", target="3", action="Commit"),
    ]


def tiny_catalog(tmp_path: Path) -> PortCatalog:
    path = tmp_path / "spec_manifest.yaml"
    path.write_text(TINY_MANIFEST, encoding="utf-8")
    return load_port_catalog(path)


def tiny_regions(catalog: PortCatalog):
    return port_regions(catalog, *_signatures_for_regions(TINY_MODULE, TINY_CFG))


def tiny_port_cases(tmp_path: Path, dedupe: str = "region"):
    catalog = tiny_catalog(tmp_path)
    regions, skipped = tiny_regions(catalog)
    source = prepare_cases(
        states=tiny_states(),
        edges=tiny_edges(),
        view="internal",
        action_metadata={},
        labelers=[],
        state_projector=None,
        output_projector=None,
        dedupe="none",
        param_recipes=build_recipes(TINY_MODULE),
    )
    return port_cases_for_corpus(
        source_cases=source,
        catalog=catalog,
        regions=regions,
        skipped=skipped,
        dedupe=dedupe,
        start_index=1,
    )


# ---------------------------------------------------------------------------
# The manifest, read through the shipped builder
# ---------------------------------------------------------------------------


def test_a_port_declared_in_the_manifest_is_read_in_the_effect_port_shape() -> None:
    """The shape the ticket asks an agent to declare into, read by the toolchain."""
    catalog = load_port_catalog(AB_MANIFEST)
    assert [port.qualified for port in catalog.ports] == ["ledger.LedgerAppendPort"]
    port = catalog.ports[0]
    assert port.component == "ledger"
    assert port.actions == ("CloseTenant", "Commit")
    # Attributes travel as data: this fixture speaks `kind`/`asserts_content`
    # and this repository's own manifest speaks `type`/`target`, and neither
    # vocabulary is privileged by the reader.
    assert port.attributes["kind"] == "durable_write"
    assert port.attributes["asserts_content"] is True


def test_absent_and_empty_are_different_claims() -> None:
    """"We checked, there are none" is not "nobody looked"."""
    catalog = load_port_catalog(AB_MANIFEST)
    assert catalog.is_mapped("Reserve") and catalog.ports_for("Reserve") == ()
    assert not catalog.is_mapped("RefuseCommitUnknown")


def test_this_repositorys_own_manifest_declares_no_orphan_port_name() -> None:
    """Every name in `effects.actions` resolves to a port under `components`."""
    catalog = load_port_catalog(ROOT / "specs/current/spec_manifest.yaml")
    declared = {port.name for port in catalog.ports}
    assert declared, "the repository's own manifest declares effect ports"
    for action, qualified in catalog.mapped_actions.items():
        for entry in qualified:
            assert entry.split(".", 1)[1] in declared, f"{action} names an undeclared port"


def test_a_missing_manifest_yields_an_empty_catalogue_rather_than_raising(tmp_path: Path) -> None:
    catalog = load_port_catalog(tmp_path / "nope.yaml")
    assert catalog.ports == () and catalog.mapped_actions == {}
    assert "missing" in catalog.source


# ---------------------------------------------------------------------------
# The region, derived from the model rather than named by hand
# ---------------------------------------------------------------------------


def test_the_port_region_is_derived_from_the_models_own_write_sets(tmp_path: Path) -> None:
    catalog = tiny_catalog(tmp_path)
    regions, skipped = tiny_regions(catalog)
    # `journal` is written only by the action that declares the port. `held` and
    # `outcome` are written by `Take` too, so they are shared and nothing behind
    # the boundary.
    assert regions["store.JournalPort"] == frozenset({"journal"})
    assert skipped == {}


def test_the_ab_fixtures_port_region_is_the_ledger_aspect_derived() -> None:
    """The hand-authored aspect slice, obtained from the declaration alone."""
    catalog = load_port_catalog(AB_MANIFEST)
    tla = (ROOT / "examples/validation/ab/model/QuotaLedger.tla").read_text(encoding="utf-8")
    cfg = (ROOT / "examples/validation/ab/model/QuotaLedger.cfg").read_text(encoding="utf-8")
    regions, _ = port_regions(catalog, *_signatures_for_regions(tla, cfg))
    assert regions["ledger.LedgerAppendPort"] == frozenset({"committed", "ledger", "closed"})


def test_a_port_no_action_declares_is_reported_dead_and_never_refused(tmp_path: Path) -> None:
    path = tmp_path / "spec_manifest.yaml"
    path.write_text(
        TINY_MANIFEST.replace("    Commit: [JournalPort]\n", "    Commit: []\n"),
        encoding="utf-8",
    )
    catalog = load_port_catalog(path)
    assert catalog.dead_ports == ("store.JournalPort",)
    regions, skipped = port_regions(catalog, *_signatures_for_regions(TINY_MODULE, TINY_CFG))
    assert regions["store.JournalPort"] == frozenset()
    assert "DEAD declared surface" in skipped["store.JournalPort"]


def test_an_unmapped_action_narrows_no_region(tmp_path: Path) -> None:
    """Silence must not shrink a region: an unmapped action has not been checked."""
    path = tmp_path / "spec_manifest.yaml"
    path.write_text(TINY_MANIFEST.replace("    Take: []\n", ""), encoding="utf-8")
    catalog = load_port_catalog(path)
    regions, _ = port_regions(catalog, *_signatures_for_regions(TINY_MODULE, TINY_CFG))
    # With `Take` unmapped, `held` and `outcome` are no longer subtracted.
    assert regions["store.JournalPort"] == frozenset({"held", "journal", "outcome"})


# ---------------------------------------------------------------------------
# The case set, per port
# ---------------------------------------------------------------------------


def test_a_declared_port_produces_its_own_case_set_and_the_count_is_reported(
    tmp_path: Path,
) -> None:
    cases, report = tiny_port_cases(tmp_path)
    block = report.per_port["store.JournalPort"]
    assert block["cases"] == len(cases) == 2
    assert block["emitted"] == 1 and block["silent"] == 1
    assert block["per_action"] == {"Commit": 1, "Take": 1}
    assert block["region"] == ["journal"]


def test_a_port_case_asserts_the_ports_region_and_keeps_the_whole_before(
    tmp_path: Path,
) -> None:
    cases, _ = tiny_port_cases(tmp_path)
    commit = next(case for case in cases if case.edge.action == "Commit")
    assert PORT_EMITTED_LABEL in commit.labels
    assert "port:store.JournalPort" in commit.labels
    # Narrowed AFTER, whole BEFORE: an adapter has to be able to build the state
    # at all, and the assertion is what the boundary owns.
    assert set(commit.after) == {"journal"}
    assert set(commit.before) == {"held", "journal", "outcome"}


def test_an_action_the_manifest_maps_without_the_port_is_asserted_silent(
    tmp_path: Path,
) -> None:
    cases, _ = tiny_port_cases(tmp_path)
    take = next(case for case in cases if case.edge.action == "Take")
    assert PORT_SILENT_LABEL in take.labels
    assert take.before["journal"] == take.after["journal"]


def test_an_unmapped_action_gets_no_port_case_and_is_named(tmp_path: Path) -> None:
    catalog = tiny_catalog(tmp_path)
    regions, skipped = tiny_regions(catalog)
    source = prepare_cases(
        states={**tiny_states(), "4": {"held": frozenset({"a"}), "journal": (), "outcome": "refused"}},
        edges=tiny_edges() + [Edge(source="2", target="4", action="RefuseTake")],
        view="internal",
        action_metadata={},
        labelers=[],
        state_projector=None,
        output_projector=None,
        dedupe="none",
        param_recipes=build_recipes(TINY_MODULE),
    )
    cases, report = port_cases_for_corpus(
        source_cases=source,
        catalog=catalog,
        regions=regions,
        skipped=skipped,
        dedupe="region",
        start_index=1,
    )
    assert report.unmapped_actions == ("RefuseTake",)
    assert all(case.edge.action != "RefuseTake" for case in cases)


def test_the_declaration_is_checked_against_the_models_write_behaviour(
    tmp_path: Path,
) -> None:
    """The declaration and the model disagreeing is REPORTED, in both directions.

    Reported, and nothing else: the plan's `no_new_gates_rule` means this pass
    refuses nothing. The value is that a disagreement is visible in the run
    output instead of surviving another epic.

    The region is supplied here rather than derived, and that is the point. With
    a region derived by ``port_regions`` the "wrote a region it does not
    declare" counter is STRUCTURALLY ZERO -- the subtraction removes every
    variable a non-declaring mapped action writes, so no case can move one. It
    is kept because it is a self-check on the DERIVATION: it can only fire when
    the static write-set analysis under-approximates, which is exactly the
    failure a derived region would otherwise hide.
    """
    path = tmp_path / "spec_manifest.yaml"
    path.write_text(
        TINY_MANIFEST.replace("    Commit: [JournalPort]\n    Take: []\n",
                              "    Commit: []\n    Take: [JournalPort]\n"),
        encoding="utf-8",
    )
    catalog = load_port_catalog(path)
    source = prepare_cases(
        states=tiny_states(), edges=tiny_edges(), view="internal", action_metadata={},
        labelers=[], state_projector=None, output_projector=None, dedupe="none",
        param_recipes=build_recipes(TINY_MODULE),
    )
    _, report = port_cases_for_corpus(
        source_cases=source,
        catalog=catalog,
        regions={"store.JournalPort": frozenset({"journal"})},
        skipped={},
        dedupe="region",
        start_index=1,
    )
    # `Take` declares the port and never touches `journal`.
    assert report.declared_but_inert == {"Take -> store.JournalPort": 1}
    # `Commit` is mapped WITHOUT the port and appends to `journal` anyway.
    assert report.undeclared_region_writes == {"Commit -> store.JournalPort": 1}
    assert report.pair_cases == {"Take -> store.JournalPort": 1, "Commit -> store.JournalPort": 1}


def test_a_derived_region_makes_the_undeclared_write_counter_unreachable(
    tmp_path: Path,
) -> None:
    """Stated as a test so the claim above is checked rather than asserted."""
    catalog = tiny_catalog(tmp_path)
    regions, skipped = tiny_regions(catalog)
    source = prepare_cases(
        states=tiny_states(), edges=tiny_edges(), view="internal", action_metadata={},
        labelers=[], state_projector=None, output_projector=None, dedupe="none",
        param_recipes=build_recipes(TINY_MODULE),
    )
    _, report = port_cases_for_corpus(
        source_cases=source, catalog=catalog, regions=regions, skipped=skipped,
        dedupe="region", start_index=1,
    )
    assert report.undeclared_region_writes == {}


def test_the_dedupe_is_never_a_trim(tmp_path: Path) -> None:
    exact_cases, exact = tiny_port_cases(tmp_path, dedupe="none")
    collapsed_cases, collapsed = tiny_port_cases(tmp_path, dedupe="region")
    assert exact.deduped_from == 0
    assert collapsed.emitted + collapsed.deduped_from == len(exact_cases)
    assert len(collapsed_cases) <= len(exact_cases)


def test_port_generation_is_deterministic(tmp_path: Path) -> None:
    first, _ = tiny_port_cases(tmp_path)
    second, _ = tiny_port_cases(tmp_path)
    assert [case.name for case in first] == [case.name for case in second]
    assert [case.output_expression for case in first] == [case.output_expression for case in second]
    assert [sorted(case.after) for case in first] == [sorted(case.after) for case in second]


# ---------------------------------------------------------------------------
# Composition with the negative corpus -- inherited, never rebuilt
# ---------------------------------------------------------------------------


def test_the_port_pass_composes_with_the_negative_corpus(tmp_path: Path) -> None:
    """`with-positive` leaves every negative case exactly where it was.

    The negative corpus took guard relaxation from 0 of 3 to 3 of 3. The port
    pass is a FUNCTION OF the corpus the other passes produced, so it cannot
    regress them: this asserts the emitted prefix is unchanged, case for case.
    """
    negative_only = render_python_package(
        module="Tiny", states=tiny_states(), edges=tiny_edges(),
        package_dir=tmp_path / "neg", negative="with-positive", negative_dedupe="none",
        tla_source=TINY_MODULE, cfg_text=TINY_CFG,
    )
    catalog = tiny_catalog(tmp_path)
    both = render_python_package(
        module="Tiny", states=tiny_states(), edges=tiny_edges(),
        package_dir=tmp_path / "both", negative="with-positive", negative_dedupe="none",
        tla_source=TINY_MODULE, cfg_text=TINY_CFG,
        ports="with-positive", port_catalog=catalog,
    )
    prefix = both[: len(negative_only)]
    assert [case.name for case in prefix] == [case.name for case in negative_only]
    assert [case.output_expression for case in prefix] == [
        case.output_expression for case in negative_only
    ]
    assert len(both) > len(negative_only)


def test_a_port_case_from_a_refused_call_stays_a_refusal(tmp_path: Path) -> None:
    """The label an adapter routes on survives the port pass."""
    catalog = tiny_catalog(tmp_path)
    reports: list = []
    cases = render_python_package(
        module="Tiny", states=tiny_states(), edges=tiny_edges(),
        package_dir=tmp_path / "portneg", negative="only", negative_dedupe="none",
        tla_source=TINY_MODULE, cfg_text=TINY_CFG,
        ports="only", port_catalog=catalog, port_report_out=reports,
    )
    assert cases, "the port's own refusal case set is not empty"
    assert all(NEGATIVE_LABEL in case.labels for case in cases)
    assert all("StateGraphRejection" in case.output_expression for case in cases)
    # A refused call leaving the port alone is what a refusal IS, never a
    # disagreement between the declaration and the model.
    assert reports[0].declared_but_inert == {}


def test_port_mode_off_changes_nothing(tmp_path: Path) -> None:
    without = render_python_package(
        module="Tiny", states=tiny_states(), edges=tiny_edges(),
        package_dir=tmp_path / "a", negative="with-positive",
        tla_source=TINY_MODULE, cfg_text=TINY_CFG,
    )
    off = render_python_package(
        module="Tiny", states=tiny_states(), edges=tiny_edges(),
        package_dir=tmp_path / "b", negative="with-positive",
        tla_source=TINY_MODULE, cfg_text=TINY_CFG, ports="off",
        port_catalog=tiny_catalog(tmp_path),
    )
    assert [case.name for case in without] == [case.name for case in off]
    assert (tmp_path / "a" / "cases.py").read_text() == (tmp_path / "b" / "cases.py").read_text()


def test_only_mode_writes_a_package_of_port_cases(tmp_path: Path) -> None:
    reports: list = []
    cases = render_python_package(
        module="Tiny", states=tiny_states(), edges=tiny_edges(),
        package_dir=tmp_path / "port", tla_source=TINY_MODULE, cfg_text=TINY_CFG,
        ports="only", port_catalog=tiny_catalog(tmp_path), port_report_out=reports,
    )
    assert cases and all("port:store.JournalPort" in case.labels for case in cases)
    docs = (tmp_path / "port" / "docs.md").read_text()
    assert "Port corpus: `only`" in docs
    assert "`store.JournalPort`" in docs
    assert reports[0].emitted == len(cases)


# ---------------------------------------------------------------------------
# The declaration, checked against BEHAVIOUR
# ---------------------------------------------------------------------------


class _RealJournal:
    """The durable side. Appends, and reads its own writes back."""

    def __init__(self) -> None:
        self._lines: list[str] = []

    def append(self, item: str) -> None:
        self._lines.append(item)

    def read(self) -> tuple[str, ...]:
        return tuple(self._lines)


class _FakeJournal:
    """The in-memory stand-in an agent writes so the domain can be tested."""

    def __init__(self) -> None:
        self._lines: tuple[str, ...] = ()

    def append(self, item: str) -> None:
        self._lines = self._lines + (item,)

    def read(self) -> tuple[str, ...]:
        return self._lines


class _Store:
    """The domain, holding its durable side behind the declared port."""

    def __init__(self, journal: Any, held: frozenset[str]) -> None:
        self.journal = journal
        self.held = set(held)

    def take(self, item: str) -> None:
        self.held.add(item)

    def commit(self, item: str) -> None:
        self.held.discard(item)
        self.journal.append(item)


class _PortResult:
    def __init__(self, after: dict[str, Any]) -> None:
        self.output = None
        self.after = after
        self.semantic_output = {"unobservable": []}


def _drive_port_case(case: Any, journal: Any) -> _PortResult:
    """Run one generated port case against a store wired to `journal`."""
    store = _Store(journal, case.before["held"])
    for existing in case.before["journal"]:
        journal.append(existing)
    action = case.input.action
    item = case.input.params["i"]
    if action == "Take":
        store.take(item)
    elif action == "Commit":
        store.commit(item)
    else:  # pragma: no cover - the manifest maps no other action
        raise AssertionError(f"no binding for {action}")
    return _PortResult({"journal": journal.read()})


@pytest.mark.parametrize("journal_factory", [_RealJournal, _FakeJournal])
def test_generated_port_cases_pass_against_the_real_adapter_and_its_fake(
    tmp_path: Path, journal_factory: Any
) -> None:
    """A generated port case DRIVES a port, and the same list runs on both sides."""
    cases, _ = tiny_port_cases(tmp_path)
    package = tmp_path / "exec"
    render_python_package(
        module="Tiny", states=tiny_states(), edges=tiny_edges(), package_dir=package,
        tla_source=TINY_MODULE, cfg_text=TINY_CFG, ports="only",
        port_catalog=tiny_catalog(tmp_path), param_recipes=build_recipes(TINY_MODULE),
    )
    for case in _load_cases(package):
        assert_case_result_per_field(case=case, result=_drive_port_case(case, journal_factory()))


@pytest.mark.parametrize("broken", ["real", "fake"])
def test_a_fault_on_either_side_of_the_port_dies(tmp_path: Path, broken: str) -> None:
    """The half PA-04 turns into the instrument, proved possible here.

    A fault seeded in the REAL adapter and the same fault seeded in the FAKE are
    the same semantic on two sides of one boundary. PA-01 measured that under
    the only wiring the predecessor had, one dies and the other is untouchable.
    Against a case list scoped to the port, both die.
    """

    class _BrokenReal(_RealJournal):
        """PA-M11's semantic: the real adapter loses what it was given."""

        def append(self, item: str) -> None:
            return None

    class _BrokenFake(_FakeJournal):
        """PA-M12: the SAME semantic, on the other side of the same port."""

        def append(self, item: str) -> None:
            return None

    package = tmp_path / "kill"
    render_python_package(
        module="Tiny", states=tiny_states(), edges=tiny_edges(), package_dir=package,
        tla_source=TINY_MODULE, cfg_text=TINY_CFG, ports="only",
        port_catalog=tiny_catalog(tmp_path), param_recipes=build_recipes(TINY_MODULE),
    )
    factory = _BrokenReal if broken == "real" else _BrokenFake
    cases = _load_cases(package)
    assert cases
    failures = 0
    for case in cases:
        try:
            assert_case_result_per_field(case=case, result=_drive_port_case(case, factory()))
        except AssertionError:
            failures += 1
    assert failures, f"the {broken}-side fault survived every port case"


def _load_cases(package: Path) -> list[Any]:
    """Import a generated package the way the shipped corpus runner does."""
    parent = str(package.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    module = importlib.import_module(f"{package.name}.cases")
    module = importlib.reload(module)
    return list(module.CASES)


# ---------------------------------------------------------------------------
# The PROMPT teaches the shape the reader reads
# ---------------------------------------------------------------------------


def test_the_prompt_declares_ports_in_the_shape_the_shipped_builder_reads(
    tmp_path: Path,
) -> None:
    """The anti-drift check for the guidance itself.

    The prompt asks an agent to declare its ports in the manifest. If it teaches
    a shape `load_port_catalog` does not read, the agent's declaration is a file
    nothing looks at -- the exact defect the plan's
    `declaration_executability_rule` was written for. So the prompt's own worked
    example is fed through the shipped builder, and a rename on either side
    fails here instead of silently orphaning the declaration.
    """
    text = HEXAGONAL_PROMPT.read_text(encoding="utf-8")
    blocks = re.findall(r"```yaml\n(.*?)```", text, flags=re.DOTALL)
    manifest_blocks = [block for block in blocks if "effects:" in block and "ports:" in block]
    assert manifest_blocks, "the prompt shows no manifest port declaration"
    path = tmp_path / "spec_manifest.yaml"
    path.write_text(manifest_blocks[0], encoding="utf-8")
    catalog = load_port_catalog(path)
    assert catalog.ports, "the shipped builder reads no port out of the prompt's own example"
    for port in catalog.ports:
        assert port.actions, f"{port.qualified} is declared by no action in the prompt's example"
