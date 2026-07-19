"""MF-015: external channel enforcement.

The central test in this file is
``test_illegal_production_import_from_testgraph_adapter_is_caught``: it writes a
Test Graph adapter that imports the production package in-process -- the exact
degeneracy the ticket exists to stop -- and asserts the gate refuses it with the
adapter, the offending import, and the remediation. That test is the
deliverable's proof, not a nice-to-have.
"""

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.testgraph_channels import (  # noqa: E402
    BASE_CHANNELS,
    ChannelEnforcementError,
    enforce_external_bindings,
    imported_modules,
    production_imports_for_module,
)
import ast  # noqa: E402


PRODUCTION_PACKAGE = "shipping_service"


def _spec_dir(tmp_path: Path) -> Path:
    """A minimal spec directory with a production package beside the adapters."""
    spec = tmp_path / "program_model"
    spec.mkdir(parents=True)
    package = tmp_path / PRODUCTION_PACKAGE
    package.mkdir()
    (package / "__init__.py").write_text("VALUE = 1\n", encoding="utf-8")
    return spec


def _bindings(
    spec: Path,
    *,
    actions: str,
    production_package: str = PRODUCTION_PACKAGE,
    port_bindings: str = "    ShippingPort: real\n    ClockPort: double\n",
    extra_external: str = "",
) -> Path:
    path = spec / "testgraph_bindings.yml"
    path.write_text(
        "external:\n"
        f"  production_package: {production_package}\n"
        "  port_bindings:\n"
        f"{port_bindings}"
        f"{extra_external}"
        "actions:\n"
        f"{actions}",
        encoding="utf-8",
    )
    return path


def _legal_adapter(spec: Path, name: str = "adapters") -> None:
    """A Test Graph adapter that drives HTTP and touches no production code."""
    (spec / f"{name}.py").write_text(
        "import json\n"
        "import urllib.request\n"
        "\n"
        "class ShipHttpAdapter:\n"
        "    def run(self, case, work_dir=None):\n"
        "        urllib.request.urlopen('http://localhost:8080/ship')\n"
        "        return {'ok': True}\n",
        encoding="utf-8",
    )


def _binding_block(adapter: str = "adapters:ShipHttpAdapter", channel: str | None = "http") -> str:
    channel_line = f"    channel: {channel}\n" if channel is not None else ""
    return (
        "  SubmitShip:\n"
        "    view: external\n"
        f"{channel_line}"
        "    layer: external\n"
        "    controllability: e2e_direct\n"
        f"    adapter: {adapter}\n"
    )


# ---------------------------------------------------------------------------
# The deliverable's proof: an illegal production import is caught.
# ---------------------------------------------------------------------------


def test_illegal_production_import_from_testgraph_adapter_is_caught(tmp_path: Path) -> None:
    spec = _spec_dir(tmp_path)
    # An adapter that reaches into the program under test instead of driving it.
    (spec / "adapters.py").write_text(
        "import json\n"
        f"from {PRODUCTION_PACKAGE} import VALUE\n"
        "\n"
        "class ShipHttpAdapter:\n"
        "    def run(self, case, work_dir=None):\n"
        "        return {'ok': VALUE}\n",
        encoding="utf-8",
    )
    path = _bindings(spec, actions=_binding_block())

    with pytest.raises(ChannelEnforcementError) as excinfo:
        enforce_external_bindings(path, import_roots=[tmp_path])

    error = excinfo.value
    assert len(error.violations) == 1
    violation = error.violations[0]
    assert violation.action == "SubmitShip"
    # reports the adapter ...
    assert violation.adapter == "adapters:ShipHttpAdapter"
    # ... the offending import ...
    assert PRODUCTION_PACKAGE in violation.problem
    assert "in-process" in violation.problem
    # ... and the remediation.
    assert "rebind this action as a spec-unit adapter" in violation.remediation
    assert "drive the declared channel" in violation.remediation


def test_illegal_import_laundered_through_a_helper_is_still_caught(tmp_path: Path) -> None:
    """Transitivity: hiding the import one module away must not evade the gate."""
    spec = _spec_dir(tmp_path)
    (spec / "helper.py").write_text(
        f"import {PRODUCTION_PACKAGE}\n\ndef value():\n    return {PRODUCTION_PACKAGE}.VALUE\n",
        encoding="utf-8",
    )
    (spec / "adapters.py").write_text(
        "import helper\n"
        "\n"
        "class ShipHttpAdapter:\n"
        "    def run(self, case, work_dir=None):\n"
        "        return {'ok': helper.value()}\n",
        encoding="utf-8",
    )
    path = _bindings(spec, actions=_binding_block())

    with pytest.raises(ChannelEnforcementError) as excinfo:
        enforce_external_bindings(path, import_roots=[tmp_path, spec])

    problem = excinfo.value.violations[0].problem
    assert PRODUCTION_PACKAGE in problem
    assert "via helper" in problem


def test_dynamic_import_of_production_package_is_caught(tmp_path: Path) -> None:
    spec = _spec_dir(tmp_path)
    (spec / "adapters.py").write_text(
        "import importlib\n"
        "\n"
        "class ShipHttpAdapter:\n"
        "    def run(self, case, work_dir=None):\n"
        f"        mod = importlib.import_module('{PRODUCTION_PACKAGE}')\n"
        "        return {'ok': mod.VALUE}\n",
        encoding="utf-8",
    )
    path = _bindings(spec, actions=_binding_block())

    with pytest.raises(ChannelEnforcementError) as excinfo:
        enforce_external_bindings(path, import_roots=[tmp_path])
    assert PRODUCTION_PACKAGE in excinfo.value.violations[0].problem


def test_production_import_in_projector_is_caught(tmp_path: Path) -> None:
    """All four adapter roles run in the harness, so all four are isolated."""
    spec = _spec_dir(tmp_path)
    _legal_adapter(spec)
    (spec / "projectors.py").write_text(
        f"import {PRODUCTION_PACKAGE}\n\nclass StateProjector:\n    def observe(self, ctx):\n        return {{}}\n",
        encoding="utf-8",
    )
    path = _bindings(
        spec,
        actions=_binding_block() + "    projector: projectors:StateProjector\n",
    )

    with pytest.raises(ChannelEnforcementError) as excinfo:
        enforce_external_bindings(path, import_roots=[tmp_path, spec])
    assert "projector module projectors imports production package" in (
        excinfo.value.violations[0].problem
    )


def test_clean_external_binding_passes(tmp_path: Path) -> None:
    spec = _spec_dir(tmp_path)
    _legal_adapter(spec)
    path = _bindings(spec, actions=_binding_block())

    contract = enforce_external_bindings(path, import_roots=[tmp_path, spec])
    assert contract.production_package == PRODUCTION_PACKAGE
    assert contract.real_ports == ("ShippingPort",)
    assert contract.double_ports == ("ClockPort",)
    assert contract.rung() == "ShippingPort"


# ---------------------------------------------------------------------------
# Channel field
# ---------------------------------------------------------------------------


def test_binding_without_channel_is_rejected_with_remediation(tmp_path: Path) -> None:
    spec = _spec_dir(tmp_path)
    _legal_adapter(spec)
    path = _bindings(spec, actions=_binding_block(channel=None))

    with pytest.raises(ChannelEnforcementError) as excinfo:
        enforce_external_bindings(path, import_roots=[tmp_path, spec])

    violation = excinfo.value.violations[0]
    assert violation.problem == "binding declares no channel"
    assert "declare channel" in violation.remediation
    for channel in BASE_CHANNELS:
        assert channel in violation.remediation


@pytest.mark.parametrize("channel", sorted(BASE_CHANNELS))
def test_each_base_channel_is_accepted(tmp_path: Path, channel: str) -> None:
    spec = _spec_dir(tmp_path)
    _legal_adapter(spec)
    path = _bindings(spec, actions=_binding_block(channel=channel))
    assert enforce_external_bindings(path, import_roots=[tmp_path, spec])


def test_unknown_channel_is_rejected(tmp_path: Path) -> None:
    spec = _spec_dir(tmp_path)
    _legal_adapter(spec)
    path = _bindings(spec, actions=_binding_block(channel="carrier-pigeon"))

    with pytest.raises(ChannelEnforcementError) as excinfo:
        enforce_external_bindings(path, import_roots=[tmp_path, spec])
    assert "is not a declared channel" in excinfo.value.violations[0].problem


def test_additional_channels_extend_the_set_explicitly(tmp_path: Path) -> None:
    """Extensibility is a visible per-program declaration, not an override."""
    spec = _spec_dir(tmp_path)
    _legal_adapter(spec)
    path = _bindings(
        spec,
        actions=_binding_block(channel="grpc"),
        extra_external="  additional_channels: [grpc]\n",
    )
    assert enforce_external_bindings(path, import_roots=[tmp_path, spec])


def test_additional_channels_cannot_excuse_a_missing_channel(tmp_path: Path) -> None:
    """Widening the accepted set never makes the field optional."""
    spec = _spec_dir(tmp_path)
    _legal_adapter(spec)
    path = _bindings(
        spec,
        actions=_binding_block(channel=None),
        extra_external="  additional_channels: [grpc]\n",
    )
    with pytest.raises(ChannelEnforcementError) as excinfo:
        enforce_external_bindings(path, import_roots=[tmp_path, spec])
    assert excinfo.value.violations[0].problem == "binding declares no channel"


# ---------------------------------------------------------------------------
# Port binding configuration (double|real) -- integration-ladder rungs
# ---------------------------------------------------------------------------


def test_all_doubles_configuration_is_rejected(tmp_path: Path) -> None:
    spec = _spec_dir(tmp_path)
    _legal_adapter(spec)
    path = _bindings(
        spec,
        actions=_binding_block(),
        port_bindings="    ShippingPort: double\n    ClockPort: double\n",
    )

    with pytest.raises(ChannelEnforcementError) as excinfo:
        enforce_external_bindings(path, import_roots=[tmp_path, spec])
    problems = [v.problem for v in excinfo.value.violations]
    assert any("all-doubles configuration is not a Test Graph rung" in p for p in problems)


def test_port_binding_must_be_double_or_real(tmp_path: Path) -> None:
    spec = _spec_dir(tmp_path)
    _legal_adapter(spec)
    path = _bindings(
        spec,
        actions=_binding_block(),
        port_bindings="    ShippingPort: real\n    ClockPort: maybe\n",
    )

    with pytest.raises(ChannelEnforcementError) as excinfo:
        enforce_external_bindings(path, import_roots=[tmp_path, spec])
    assert any("is not double or real" in v.problem for v in excinfo.value.violations)


def test_rung_names_the_real_ports(tmp_path: Path) -> None:
    spec = _spec_dir(tmp_path)
    _legal_adapter(spec)
    path = _bindings(
        spec,
        actions=_binding_block(),
        port_bindings="    ShippingPort: real\n    LedgerPort: real\n    ClockPort: double\n",
    )
    contract = enforce_external_bindings(path, import_roots=[tmp_path, spec])
    assert contract.rung() == "LedgerPort+ShippingPort"


def test_missing_port_bindings_is_rejected(tmp_path: Path) -> None:
    spec = _spec_dir(tmp_path)
    _legal_adapter(spec)
    path = spec / "testgraph_bindings.yml"
    path.write_text(
        f"external:\n  production_package: {PRODUCTION_PACKAGE}\nactions:\n" + _binding_block(),
        encoding="utf-8",
    )
    with pytest.raises(ChannelEnforcementError) as excinfo:
        enforce_external_bindings(path, import_roots=[tmp_path, spec])
    assert any("port_bindings is not declared" in v.problem for v in excinfo.value.violations)


# ---------------------------------------------------------------------------
# No degenerate escapes: absent declarations FAIL, they never skip the check
# ---------------------------------------------------------------------------


def test_missing_external_block_fails_rather_than_skipping(tmp_path: Path) -> None:
    spec = _spec_dir(tmp_path)
    _legal_adapter(spec)
    path = spec / "testgraph_bindings.yml"
    path.write_text("actions:\n" + _binding_block(), encoding="utf-8")

    with pytest.raises(ChannelEnforcementError) as excinfo:
        enforce_external_bindings(path, import_roots=[tmp_path, spec])
    assert "no external: block" in excinfo.value.violations[0].problem


def test_missing_production_package_fails_rather_than_skipping(tmp_path: Path) -> None:
    """A gate that silently disables itself when its input is absent is the
    degeneracy references/architecture_tractability.md forbids."""
    spec = _spec_dir(tmp_path)
    _legal_adapter(spec)
    path = spec / "testgraph_bindings.yml"
    path.write_text(
        "external:\n  port_bindings:\n    ShippingPort: real\nactions:\n" + _binding_block(),
        encoding="utf-8",
    )
    with pytest.raises(ChannelEnforcementError) as excinfo:
        enforce_external_bindings(path, import_roots=[tmp_path, spec])
    assert any("production_package is not declared" in v.problem for v in excinfo.value.violations)


def test_every_violation_is_reported_not_just_the_first(tmp_path: Path) -> None:
    """Evidence is never truncated: all violations are reported together."""
    spec = _spec_dir(tmp_path)
    (spec / "adapters.py").write_text(
        f"import {PRODUCTION_PACKAGE}\n\nclass ShipHttpAdapter:\n    pass\n",
        encoding="utf-8",
    )
    actions = (
        "  SubmitShip:\n"
        "    view: external\n"
        "    adapter: adapters:ShipHttpAdapter\n"
        "  SubmitCancel:\n"
        "    view: external\n"
        "    adapter: adapters:ShipHttpAdapter\n"
    )
    path = _bindings(spec, actions=actions)

    with pytest.raises(ChannelEnforcementError) as excinfo:
        enforce_external_bindings(path, import_roots=[tmp_path, spec])
    actions_reported = {v.action for v in excinfo.value.violations}
    assert actions_reported == {"SubmitShip", "SubmitCancel"}
    # each action contributes both a missing-channel and an import violation
    assert len(excinfo.value.violations) == 4


def test_no_override_or_skip_parameter_exists() -> None:
    """The gate must expose no way to pass while failing."""
    import inspect

    params = set(inspect.signature(enforce_external_bindings).parameters)
    assert params == {"bindings_path", "import_roots", "actions"}
    for forbidden in ("allow", "override", "skip", "force", "ignore"):
        assert not any(forbidden in name for name in params)


# ---------------------------------------------------------------------------
# Import analysis units
# ---------------------------------------------------------------------------


def test_imported_modules_covers_static_and_dynamic_forms() -> None:
    tree = ast.parse(
        "import a.b\n"
        "from c import d\n"
        "from . import sibling\n"
        "import importlib\n"
        "importlib.import_module('e.f')\n"
        "__import__('g')\n"
    )
    assert {"a.b", "c", "importlib", "e.f", "g"} <= imported_modules(tree)


def test_unresolvable_third_party_import_is_not_followed(tmp_path: Path) -> None:
    """Only first-party modules are walked; stdlib/third-party are left alone."""
    spec = _spec_dir(tmp_path)
    (spec / "adapters.py").write_text("import json\nimport urllib.request\n", encoding="utf-8")
    assert (
        production_imports_for_module(
            "adapters", package=PRODUCTION_PACKAGE, roots=[spec, tmp_path]
        )
        == []
    )


def test_spec_unit_adapters_may_import_production(tmp_path: Path) -> None:
    """Internal bindings are in-process by contract; the gate must not touch them."""
    spec = _spec_dir(tmp_path)
    (spec / "adapters.py").write_text(
        f"import {PRODUCTION_PACKAGE}\n\nclass UnitAdapter:\n    pass\n", encoding="utf-8"
    )
    path = _bindings(spec, actions=_binding_block())
    # Restricting `actions` to an empty set checks nothing external; the
    # spec-unit path never calls this gate at all.
    contract = enforce_external_bindings(path, import_roots=[tmp_path, spec], actions=set())
    assert contract.production_package == PRODUCTION_PACKAGE


# ---------------------------------------------------------------------------
# Wiring: both entry points enforce, end to end
# ---------------------------------------------------------------------------


def _external_case_package(tmp_path: Path) -> Path:
    from scripts.generate_cases_from_tlc_dump import (
        ActionMetadata,
        Edge,
        render_python_package,
    )

    package_dir = tmp_path / "external_cases"
    render_python_package(
        module="Program",
        states={"0": {"status": "pending"}, "1": {"status": "done"}},
        edges=[Edge("0", "1", "Submit")],
        package_dir=package_dir,
        view="external",
        action_metadata={
            "Submit": ActionMetadata("Submit", "external", "e2e_direct", ("testgraph",))
        },
    )
    return package_dir


def _offending_bindings(tmp_path: Path, *, channel: str | None = "http") -> Path:
    package = tmp_path / PRODUCTION_PACKAGE
    package.mkdir(exist_ok=True)
    (package / "__init__.py").write_text("VALUE = 1\n", encoding="utf-8")
    (tmp_path / "wired_adapters.py").write_text(
        f"from {PRODUCTION_PACKAGE} import VALUE\n"
        "\n"
        "class SubmitAdapter:\n"
        "    def run(self, case, work_dir=None):\n"
        "        return {'ok': VALUE}\n",
        encoding="utf-8",
    )
    channel_line = f"    channel: {channel}\n" if channel else ""
    path = tmp_path / "testgraph_bindings.yml"
    path.write_text(
        "external:\n"
        f"  production_package: {PRODUCTION_PACKAGE}\n"
        "  port_bindings:\n"
        "    RequestPort: real\n"
        "actions:\n"
        "  Submit:\n"
        "    view: external\n"
        f"{channel_line}"
        "    adapter: wired_adapters:SubmitAdapter\n",
        encoding="utf-8",
    )
    return path


def _run_adapters(package_dir: Path, bindings: Path, tmp_path: Path, *view: str):
    import subprocess

    return subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "run_generated_case_adapters.py"),
            str(package_dir),
            "--mapping",
            str(bindings),
            "--work-dir",
            str(tmp_path / "work"),
            "--import-root",
            str(tmp_path),
            *view,
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def test_runner_refuses_an_adapter_that_imports_the_production_package(tmp_path: Path) -> None:
    package_dir = _external_case_package(tmp_path)
    bindings = _offending_bindings(tmp_path)

    result = _run_adapters(package_dir, bindings, tmp_path, "--view", "external")

    output = result.stdout + result.stderr
    assert result.returncode != 0, output
    assert "external channel enforcement failed" in output
    assert PRODUCTION_PACKAGE in output
    assert "rebind this action as a spec-unit adapter" in output


def test_runner_enforces_without_the_view_flag(tmp_path: Path) -> None:
    """The gate keys on the CASE's view, so omitting --view cannot bypass it."""
    package_dir = _external_case_package(tmp_path)
    bindings = _offending_bindings(tmp_path)

    result = _run_adapters(package_dir, bindings, tmp_path)

    output = result.stdout + result.stderr
    assert result.returncode != 0, output
    assert "external channel enforcement failed" in output


def test_runner_refuses_a_binding_without_a_channel(tmp_path: Path) -> None:
    package_dir = _external_case_package(tmp_path)
    # legal adapter, but the binding never says how the program is driven
    (tmp_path / "wired_adapters.py").write_text(
        "class SubmitAdapter:\n"
        "    def run(self, case, work_dir=None):\n"
        "        return {'ok': True}\n",
        encoding="utf-8",
    )
    bindings = _offending_bindings(tmp_path, channel=None)
    (tmp_path / "wired_adapters.py").write_text(
        "class SubmitAdapter:\n"
        "    def run(self, case, work_dir=None):\n"
        "        return {'ok': True}\n",
        encoding="utf-8",
    )

    result = _run_adapters(package_dir, bindings, tmp_path, "--view", "external")

    output = result.stdout + result.stderr
    assert result.returncode != 0, output
    assert "binding declares no channel" in output


def test_exporter_refuses_an_adapter_that_imports_the_production_package(tmp_path: Path) -> None:
    import subprocess

    package_dir = _external_case_package(tmp_path)
    bindings = _offending_bindings(tmp_path)
    manifest = tmp_path / "spec_manifest.yaml"
    manifest.write_text(
        "module: Program\nbudgets:\n  max_external_cases_per_action: 50\n", encoding="utf-8"
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "export_testgraph_cases.py"),
            str(package_dir),
            "--out",
            str(tmp_path / "traces"),
            "--manifest",
            str(manifest),
            "--bindings",
            str(bindings),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    output = result.stdout + result.stderr
    assert result.returncode != 0, output
    assert "external channel enforcement failed" in output
    assert not (tmp_path / "traces").exists(), "export proceeded despite a failing gate"


def test_exporter_requires_bindings_at_all() -> None:
    """There is no way to export Test Graph traces with unchecked bindings."""
    import subprocess

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "export_testgraph_cases.py"), "--help"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert "--bindings" in result.stdout
    text = (ROOT / "scripts" / "export_testgraph_cases.py").read_text(encoding="utf-8")
    assert "required=True" in text
    for flag in ("--skip-channel", "--allow-in-process", "--no-channel-check"):
        assert flag not in text, f"export offers {flag}; a gate with a bypass is not a gate"
