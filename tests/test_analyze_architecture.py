"""`analyze architecture` is a DESCRIPTOR of the structure the model implies.

The properties these tests hold, in order of how much damage their absence
would do:

1. **A refusal beats a false clean (MF-027).** A model whose interaction graph
   does not decompose must SAY SO. It must not receive a one-component
   partition in which every variable is trivially owned, no action is a port,
   and zero single-writer violations are reported -- that is a clean
   architecture report for a model with no architecture, and it is
   indistinguishable from the real thing.
2. **No suggested moves (CD-01).** No proposed cut, no refactor, no target
   shape, no next step. The chooser was removed for being confidently wrong on
   standard TLA+; it does not come back in a new costume.
3. **Advisory, never blocking.** Exit 0 whenever the model can be analyzed, no
   matter how incoherent it is. Nonzero ONLY for a model that cannot be
   analyzed (the MF-030 fail-closed) or a DECLARED partition that cannot be
   read.
4. **Declared, never inferred.** The tool measures a component partition the
   project declares. It never writes one -- an auditing tool that picks its own
   boundary can define every finding out of existence (the AC-02 rule, applied
   to the model side).
5. Every figure is labeled ``[MEASURED]``.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest  # noqa: E402

from scripts.analyze_architecture import (  # noqa: E402
    EXIT_ANALYSIS_ERROR,
    NEWMAN_SIGNIFICANT_Q,
    EXIT_PASS,
    EXIT_USAGE,
    SCHEMA,
    SCHEMA_VERSION,
    analyze,
    descriptor_payload,
    main,
    render_text,
)

# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

# Two genuinely separable components joined by one crossing action. This is
# what a model that DOES decompose looks like: `orders`/`stock` on one side,
# `outbox`/`shipped` on the other, and only `Dispatch` touching both.
DECOMPOSES_TLA = """---------------------------- MODULE Decomposes ----------------------------
EXTENDS Naturals

VARIABLES orders, stock, outbox, shipped

vars == << orders, stock, outbox, shipped >>

Init ==
  /\\ orders = 0
  /\\ stock = 0
  /\\ outbox = 0
  /\\ shipped = 0

PlaceOrder ==
  /\\ orders' = orders + 1
  /\\ UNCHANGED << stock, outbox, shipped >>

Restock ==
  /\\ stock' = stock + 1
  /\\ UNCHANGED << orders, outbox, shipped >>

Reserve ==
  /\\ stock > 0
  /\\ orders > 0
  /\\ stock' = stock - 1
  /\\ orders' = orders - 1
  /\\ UNCHANGED << outbox, shipped >>

Emit ==
  /\\ outbox' = outbox + 1
  /\\ UNCHANGED << orders, stock, shipped >>

Ship ==
  /\\ outbox > 0
  /\\ outbox' = outbox - 1
  /\\ shipped' = shipped + 1
  /\\ UNCHANGED << orders, stock >>

Dispatch ==
  /\\ orders > 0
  /\\ orders' = orders - 1
  /\\ outbox' = outbox + 1
  /\\ UNCHANGED << stock, shipped >>

Next == PlaceOrder \\/ Restock \\/ Reserve \\/ Emit \\/ Ship \\/ Dispatch

TypeInvariant ==
  /\\ orders \\in 0..3
  /\\ stock \\in 0..3
  /\\ outbox \\in 0..3
  /\\ shipped \\in 0..3

Spec == Init /\\ [][Next]_vars
=============================================================================
"""

DECOMPOSES_CFG = """SPECIFICATION Spec
INVARIANTS
  TypeInvariant
"""

# Every action touches every variable: a blob. Greedy modularity maximization
# collapses it to one community, and there is no cut to name.
BLOB_TLA = """---------------------------- MODULE Blob ----------------------------
EXTENDS Naturals

VARIABLES a, b, c

vars == << a, b, c >>

Init == a = 0 /\\ b = 0 /\\ c = 0

Step1 == a' = a + 1 /\\ b' = b + 1 /\\ c' = c + 1
Step2 == a' = a + 2 /\\ b' = b + 2 /\\ c' = c + 2

Next == Step1 \\/ Step2

TypeInvariant == a \\in 0..3 /\\ b \\in 0..3 /\\ c \\in 0..3

Spec == Init /\\ [][Next]_vars
=============================================================================
"""

BLOB_CFG = """SPECIFICATION Spec
INVARIANTS
  TypeInvariant
"""

UNRESOLVABLE_TLA = """---------------------------- MODULE Unresolvable ----------------------------
EXTENDS Naturals, NotAStandardModuleAndNotOnDisk

VARIABLES x

vars == << x >>

Init == x = 0
Bump == x' = x + 1
Next == Bump

TypeInvariant == x \\in 0..3

Spec == Init /\\ [][Next]_vars
=============================================================================
"""


def write_spec(directory: Path, name: str, tla: str, cfg: str) -> tuple[Path, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    tla_path = directory / f"{name}.tla"
    cfg_path = directory / f"{name}.cfg"
    tla_path.write_text(tla, encoding="utf-8")
    cfg_path.write_text(cfg, encoding="utf-8")
    return tla_path, cfg_path


@pytest.fixture()
def decomposes(tmp_path: Path) -> tuple[Path, Path]:
    return write_spec(tmp_path / "d", "Decomposes", DECOMPOSES_TLA, DECOMPOSES_CFG)


@pytest.fixture()
def blob(tmp_path: Path) -> tuple[Path, Path]:
    return write_spec(tmp_path / "b", "Blob", BLOB_TLA, BLOB_CFG)


def cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "tla_spec_dev.py"),
            "--spec-root",
            "specs",
            "analyze",
            "architecture",
            *args,
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


# --------------------------------------------------------------------------
# 1. The refusal: a model that does not decompose says so
# --------------------------------------------------------------------------


class TestAModelThatResistsClusteringSaysSo:
    """MF-027 applied to structure: a clean report on a model you could not cut
    is indistinguishable from a clean report on one you could."""

    def test_blob_is_reported_as_not_decomposing(self, blob: tuple[Path, Path]) -> None:
        descriptor = analyze(*blob)
        assert len(descriptor.components) == 1
        assert descriptor.decomposes is False
        assert descriptor.consumable_as_architecture is False

    def test_blob_does_not_report_zero_single_writer_violations(
        self, blob: tuple[Path, Path]
    ) -> None:
        """The false clean this whole ticket exists to avoid.

        With one component every variable is written 'inside its component', so
        a naive implementation reports zero violations -- a perfect
        single-writer architecture for a model that is one undifferentiated
        blob. The measurement is NOT DEFINED here and must say so.
        """
        descriptor = analyze(*blob)
        payload = descriptor_payload(descriptor)
        ownership = payload["measured"]["ownership"]
        assert ownership["single_writer_violations"] is None
        assert "NOT MEASURABLE" in ownership["single_writer_basis"]
        # AC-03-DF-01: `owns` is the same question one field over, and it used
        # to answer `[]` -- "owns nothing", a plausible architectural fact --
        # where the text renderer said NOT MEASURABLE. Undefined is `null` and
        # carries its reason, in the JSON exactly as in the text.
        assert descriptor.components[0].owns is None
        component = payload["measured"]["partition"]["components"][0]
        assert component["owns"] is None
        assert "NOT MEASURABLE" in component["owns_basis"]

    def test_blob_verdict_is_unmappable_not_coherent(self, blob: tuple[Path, Path]) -> None:
        payload = descriptor_payload(analyze(*blob))
        assert payload["verdict"]["architecture_scan"] == "unmappable"
        assert any("does not decompose" in r for r in payload["verdict"]["reasons"])

    def test_blob_text_names_the_criteria_that_failed(self, blob: tuple[Path, Path]) -> None:
        text = render_text(analyze(*blob))
        assert "DOES NOT DECOMPOSE" in text
        assert "component_count" in text
        assert "UNMAPPABLE" in text

    def test_blob_still_exits_zero(self, blob: tuple[Path, Path]) -> None:
        """A model with no architecture is a FINDING, not a failure."""
        assert main([str(blob[0]), str(blob[1])]) == EXIT_PASS

    def test_the_repositorys_own_model_flipped_out_of_the_blob_case(self) -> None:
        """Dogfood, recorded as a test so the finding cannot quietly reverse.

        THE FINDING REVERSED, AND THAT IS THE POINT OF RECORDING IT.

        Through AC-04 this repository's model did NOT decompose: `lastCommand`
        and `result` are written by every command, the interaction graph was
        effectively complete, and greedy modularity yielded one community at
        Q = 0. RC-01 added `architecture_delta` beside `architecture_scan` --
        one variable, written by the one action that already wrote its
        neighbour -- and the same measurement now reports TWO components and a
        partition that MEETS EVERY SHIPPED CRITERION, at
        Q = 0.0116.

        Nothing here was tuned to produce that. No criterion, threshold or
        clustering parameter changed in this ticket; the model grew to cover
        shipped surface and the scanner's answer inverted. Read it as a
        measurement of the SCANNER, not a promotion of this repository's
        architecture:

          * Q = 0.0116 is 26x below the Newman threshold of 0.3 the tool itself
            reports and does not apply. The `modularity_q` criterion is
            `Q > 0`, and 0.0116 clears it the same way 0.0 did not.
          * The cut it names is crossed by the god-variables it was supposed to
            expose: `lastCommand` and `result` are STILL single-writer
            violations across both components, and the descriptor says so on
            the same page it calls the partition a cut.
          * AC-03 measured 2 of 115,975 partitions of this model meeting all
            three criteria at Q = 0.0029. A verdict that one variable can flip
            is consistent with that measurement and is filed as RC-01-DF-01.

        Asserted here so the next reader meets the fragility rather than the
        headline.
        """
        spec = REPO_ROOT / "specs" / "current" / "TlaSpecDevCli.tla"
        cfg = REPO_ROOT / "specs" / "current" / "MC.cfg"
        descriptor = analyze(spec, cfg)
        assert descriptor.consumable_as_architecture is True
        assert len(descriptor.components) == 2
        # Barely above the criterion, and far below the significance threshold
        # the same report prints.
        assert 0.0 < descriptor.modularity_q < 0.05
        assert descriptor.modularity_q < NEWMAN_SIGNIFICANT_Q
        # The reason the flip is not an architecture: the two variables that
        # made the model a blob still cross the boundary it just drew.
        violations = {
            row["variable"]
            for row in descriptor_payload(descriptor)["measured"]["ownership"]["single_writer_violations"]
        }
        assert {"lastCommand", "result"} <= violations


# --------------------------------------------------------------------------
# 2. The positive case: a model that does decompose
# --------------------------------------------------------------------------


class TestAModelThatDecomposes:
    def test_components_ports_and_span_are_named(self, decomposes: tuple[Path, Path]) -> None:
        descriptor = analyze(*decomposes)
        assert descriptor.decomposes is True
        assert descriptor.consumable_as_architecture is True
        assert len(descriptor.components) == 2

        payload = descriptor_payload(descriptor)["measured"]
        members = {c["id"]: set(c["variables"]) for c in payload["partition"]["components"]}
        assert {frozenset(v) for v in members.values()} == {
            frozenset({"orders", "stock"}),
            frozenset({"outbox", "shipped"}),
        }

        # One port, crossed by the one action that touches both sides.
        assert len(payload["ports"]) == 1
        assert payload["ports"][0]["actions"] == ["Dispatch"]
        assert [row["action"] for row in payload["crossing_actions"]] == ["Dispatch"]
        # Dispatch WRITES on both sides, so it spans, not merely crosses.
        assert [row["action"] for row in payload["spanning_actions"]] == ["Dispatch"]

    def test_single_writer_violations_name_the_variables(
        self, decomposes: tuple[Path, Path]
    ) -> None:
        payload = descriptor_payload(analyze(*decomposes))["measured"]
        violations = {row["variable"] for row in payload["ownership"]["single_writer_violations"]}
        # Dispatch commits `orders` and `outbox` in one step, so neither is
        # confined to a single component. `stock` and `shipped` are.
        assert violations == {"orders", "outbox"}

    def test_per_variable_writers_are_reported(self, decomposes: tuple[Path, Path]) -> None:
        writers = descriptor_payload(analyze(*decomposes))["measured"]["ownership"]["writers"]
        assert writers["shipped"] == ["Ship"]
        assert set(writers["orders"]) == {"PlaceOrder", "Reserve", "Dispatch"}

    def test_verdict_is_still_unmappable_without_code(
        self, decomposes: tuple[Path, Path]
    ) -> None:
        """AC-01 measures only the model side.

        With no production code supplied there is nothing to be coherent WITH.
        An unobserved target reports `unmappable`, never `coherent` (MF-027).
        AC-02 supplies the code side via --code/--map.
        """
        payload = descriptor_payload(analyze(*decomposes))
        assert payload["verdict"]["architecture_scan"] == "unmappable"
        assert any("no production code" in r for r in payload["verdict"]["reasons"])


# --------------------------------------------------------------------------
# 3. Declared partitions: measured, never invented
# --------------------------------------------------------------------------


class TestTheToolMeasuresDeclaredPartitionsAndNeverWritesOne:
    def test_declared_partition_is_used_and_labeled_declared(
        self, blob: tuple[Path, Path], tmp_path: Path
    ) -> None:
        declared = tmp_path / "arch.yaml"
        declared.write_text(
            "architecture:\n"
            "  components:\n"
            "    - name: left\n"
            "      variables: [a]\n"
            "    - name: right\n"
            "      variables: [b, c]\n",
            encoding="utf-8",
        )
        descriptor = analyze(*blob, components_path=declared)
        assert descriptor.partition_source == "declared"
        assert [c.name for c in descriptor.components] == ["left", "right"]
        # A declared partition is consumable because the project named it, even
        # though this blob does not decompose on its own.
        assert descriptor.consumable_as_architecture is True
        assert descriptor.decomposes is False

    def test_declared_partition_measures_violations_against_the_declaration(
        self, blob: tuple[Path, Path], tmp_path: Path
    ) -> None:
        declared = tmp_path / "arch.yaml"
        declared.write_text(
            "architecture:\n"
            "  components:\n"
            "    - name: left\n"
            "      variables: [a]\n"
            "    - name: right\n"
            "      variables: [b, c]\n",
            encoding="utf-8",
        )
        payload = descriptor_payload(analyze(*blob, components_path=declared))["measured"]
        assert {row["variable"] for row in payload["ownership"]["single_writer_violations"]} == {
            "a",
            "b",
            "c",
        }
        assert payload["ownership"]["single_writer_basis"].startswith("the DECLARED partition")

    @pytest.mark.parametrize(
        "body, fragment",
        [
            ("architecture:\n  components: []\n", "non-empty"),
            (
                "architecture:\n  components:\n    - name: left\n      variables: [zzz]\n",
                "the model does not have",
            ),
            (
                "architecture:\n  components:\n"
                "    - name: left\n      variables: [a]\n"
                "    - name: right\n      variables: [a, b]\n",
                "must not overlap",
            ),
            (
                "architecture:\n  components:\n    - name: left\n",
                "declares no `variables:`",
            ),
        ],
    )
    def test_an_unreadable_declaration_is_refused_not_silently_replaced(
        self, blob: tuple[Path, Path], tmp_path: Path, body: str, fragment: str
    ) -> None:
        """Falling back to the emergent clustering would measure something else.

        The project asked for a specific partition to be measured. Quietly
        substituting the tool's own clustering would report facts about a
        boundary nobody declared, under the declaration's name.
        """
        declared = tmp_path / "arch.yaml"
        declared.write_text(body, encoding="utf-8")
        result = cli(str(blob[0]), str(blob[1]), "--components", str(declared))
        assert result.returncode == EXIT_USAGE
        assert fragment in result.stderr

    def test_no_declaration_means_the_tool_writes_none(
        self, blob: tuple[Path, Path], tmp_path: Path
    ) -> None:
        """The tool never emits a partition file, and never proposes one."""
        before = set(tmp_path.rglob("*"))
        text = render_text(analyze(*blob))
        assert set(tmp_path.rglob("*")) == before
        assert "DECLARE one" in text  # it points at the input, it does not fill it in


# --------------------------------------------------------------------------
# 4. CD-01: no suggested moves, [MEASURED] labels
# --------------------------------------------------------------------------


class TestTheDescriptorMakesNoSuggestions:
    BANNED = (
        "SUGGESTED MOVE",
        "RECOMMENDATION",
        "recommendation:",
        "[PROJECTED]",
        "you should",
        "consider extracting",
        "we recommend",
    )

    def test_no_suggestion_vocabulary_in_either_model(
        self, blob: tuple[Path, Path], decomposes: tuple[Path, Path]
    ) -> None:
        for spec in (blob, decomposes):
            text = render_text(analyze(*spec))
            for banned in self.BANNED:
                assert banned not in text, f"{banned!r} reappeared in the descriptor"

    def test_every_section_is_labeled_measured(self, decomposes: tuple[Path, Path]) -> None:
        text = render_text(analyze(*decomposes))
        for section in (
            "[MEASURED] Component partition",
            "[MEASURED] Does this partition decompose the model?",
            "[MEASURED] State ownership",
            "[MEASURED] Single-writer violations",
            "[MEASURED] Ports",
            "[MEASURED] Spanning actions",
        ):
            assert section in text

    def test_payload_declares_it_neither_blocks_nor_suggests(
        self, decomposes: tuple[Path, Path]
    ) -> None:
        payload = descriptor_payload(analyze(*decomposes))
        assert payload["advisory"]["blocks_promotion"] is False
        assert payload["advisory"]["suggests_moves"] is False
        assert payload["verdict"]["blocks_promotion"] is False


# --------------------------------------------------------------------------
# 5. Exit codes: advisory, with one fail-closed
# --------------------------------------------------------------------------


class TestExitCodes:
    def test_incoherent_model_exits_zero(self, blob: tuple[Path, Path]) -> None:
        assert cli(str(blob[0]), str(blob[1])).returncode == EXIT_PASS

    def test_coherent_model_exits_zero(self, decomposes: tuple[Path, Path]) -> None:
        assert cli(str(decomposes[0]), str(decomposes[1])).returncode == EXIT_PASS

    def test_unresolvable_hierarchy_fails_closed(self, tmp_path: Path) -> None:
        """MF-030: 'I could not measure this' is the one genuine error."""
        tla, cfg = write_spec(
            tmp_path / "u", "Unresolvable", UNRESOLVABLE_TLA, BLOB_CFG
        )
        result = cli(str(tla), str(cfg))
        assert result.returncode == EXIT_ANALYSIS_ERROR
        assert "could not be resolved" in result.stderr

    def test_missing_spec_is_a_usage_error(self, tmp_path: Path) -> None:
        assert cli(str(tmp_path / "nope.tla")).returncode == EXIT_USAGE


# --------------------------------------------------------------------------
# 6. The JSON contract AC-02 and AC-03 consume
# --------------------------------------------------------------------------


class TestTheMachineReadableContract:
    def test_json_output_is_valid_and_versioned(self, decomposes: tuple[Path, Path]) -> None:
        result = cli(str(decomposes[0]), str(decomposes[1]), "--format", "json")
        assert result.returncode == EXIT_PASS
        payload = json.loads(result.stdout)
        assert payload["schema"] == SCHEMA
        assert payload["schema_version"] == SCHEMA_VERSION

    def test_ac02_can_build_a_port_lookup_from_component_pairs(
        self, decomposes: tuple[Path, Path]
    ) -> None:
        """AC-02's convergence test is 'does a port exist between these two
        components' -- so ports are published keyed by the component PAIR, not
        only per crossing action."""
        payload = descriptor_payload(analyze(*decomposes))["measured"]
        pairs = {tuple(p["between"]) for p in payload["ports"]}
        component_ids = {c["id"] for c in payload["partition"]["components"]}
        assert len(pairs) == 1
        (left, right), = pairs
        assert {left, right} <= component_ids

    def test_ac03_can_render_a_brief_for_one_component(
        self, decomposes: tuple[Path, Path]
    ) -> None:
        """AC-03's brief needs, per component: the variables it owns, which
        components it may reach, and through which actions only."""
        payload = descriptor_payload(analyze(*decomposes))["measured"]
        for component in payload["partition"]["components"]:
            assert set(component) >= {
                "id",
                "name",
                "variables",
                "owns",
                "internal_actions",
                "crossing_actions",
                "reaches",
            }
            for reach in component["reaches"]:
                assert set(reach) == {"component", "name", "via_actions"}
                assert reach["via_actions"]

    def test_consumers_are_told_when_the_partition_is_not_usable(
        self, blob: tuple[Path, Path]
    ) -> None:
        """The single field AC-02 must branch on to avoid the false clean."""
        payload = descriptor_payload(analyze(*blob))
        assert payload["measured"]["partition"]["consumable_as_architecture"] is False
        assert payload["verdict"]["architecture_scan"] == "unmappable"

    def test_decomposition_criteria_publish_their_own_rule(
        self, decomposes: tuple[Path, Path]
    ) -> None:
        """The one judgment the tool makes ships with the rule that produced it."""
        criteria = descriptor_payload(analyze(*decomposes))["measured"]["partition"]["criteria"]
        assert {c["name"] for c in criteria} == {
            "component_count",
            "modularity_q",
            "crossing_action_fraction",
        }
        for criterion in criteria:
            assert set(criterion) == {"name", "measured", "rule", "met", "why"}

    def test_out_writes_the_evidence_file(
        self, decomposes: tuple[Path, Path], tmp_path: Path
    ) -> None:
        out = tmp_path / "results" / "architecture.json"
        result = cli(
            str(decomposes[0]), str(decomposes[1]), "--format", "json", "--out", str(out)
        )
        assert result.returncode == EXIT_PASS
        assert json.loads(out.read_text(encoding="utf-8"))["schema"] == SCHEMA


# --------------------------------------------------------------------------
# 7. It runs on the shipped example
# --------------------------------------------------------------------------


def test_runs_on_the_distributed_history_example() -> None:
    """The reference example's external view: two clusters, but 9 of 12 actions
    cross the boundary, so it does not decompose either. Recorded as evidence
    that the refusal is not a quirk of this repository's own model."""
    base = REPO_ROOT / "examples" / "distributed_history" / "specs" / "program_model"
    descriptor = analyze(base / "External.tla", base / "External.cfg")
    assert len(descriptor.components) == 2
    assert descriptor.decomposes is False
    failed = {c["name"] for c in descriptor.criteria if not c["met"]}
    assert failed == {"crossing_action_fraction"}
    # Every variable is written by some action that also writes into the other
    # component: the example has no single-writer state at all.
    assert all(component.owns == [] for component in descriptor.components)
