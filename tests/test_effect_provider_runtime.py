from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.effect_conformance import load_effect_declarations
from scripts.generate_cases_from_tlc_dump import Edge, render_python_package
from scripts.generate_python import generate, render_ports
from scripts.run_generated_case_adapters import (
    AdapterMapping,
    EffectProviderConfigurationError,
    execute_cases_in_batch,
    load_effect_provider_plan,
    parse_simple_mapping_toml,
    validate_effect_provider_execution_mode,
)


@dataclass(frozen=True)
class Output:
    changed: dict


def make_case(name: str = "case_1", action: str = "Publish") -> SimpleNamespace:
    return SimpleNamespace(
        name=name,
        before={},
        input=SimpleNamespace(action=action),
        output=Output({}),
        after={},
        labels=frozenset({action}),
        view="internal",
        controllability="unit_direct",
        generates=frozenset({"spec_unit"}),
    )


def write_effect_project(
    tmp_path: Path,
    *,
    action_ports: str = "[FilesystemPort, PatchPort]",
    providers: str | None = None,
    provider_module: str | None = None,
) -> tuple[Path, Path]:
    sys.modules.pop("generated_contract", None)
    sys.modules.pop("generated_contract.ports", None)
    package = tmp_path / "generated_contract"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "ports.py").write_text(
        """from typing import Protocol, runtime_checkable

@runtime_checkable
class FilesystemPort(Protocol):
    def write(self, value: str) -> None: ...

@runtime_checkable
class PatchPort(Protocol):
    def request(self) -> str: ...
""",
        encoding="utf-8",
    )
    (tmp_path / "spec_manifest.yaml").write_text(
        """module: Example
package: generated_contract
state: {}
commands: {}
results: {}
ports:
  FilesystemPort:
    role: effect
    methods:
      write:
        result: None
  PatchPort:
    role: effect
    methods:
      request:
        result: str
""",
        encoding="utf-8",
    )
    (tmp_path / "actions.yml").write_text(
        f"""actions:
  Publish:
    layer: internal
    effect_ports: {action_ports}
""",
        encoding="utf-8",
    )
    module = provider_module or "effect_provider_fixture"
    provider_tables = providers
    if provider_tables is None:
        provider_tables = f"""[effect_providers.FilesystemPort]
provider = \"{module}:filesystem_provider\"

[effect_providers.PatchPort]
provider = \"{module}:patch_provider\"
"""
    mapping_path = tmp_path / "case_adapters.toml"
    mapping_path.write_text(
        f"""[adapters.Publish]
adapter = \"{module}:Adapter\"
kind = \"publisher\"

{provider_tables}
""",
        encoding="utf-8",
    )
    return tmp_path, mapping_path


def write_provider_fixture(tmp_path: Path) -> None:
    sys.modules.pop("effect_provider_fixture", None)
    (tmp_path / "effect_provider_fixture.py").write_text(
        """from contextlib import contextmanager

EVENTS = []
EFFECT_MAPS = []
PATCHED = False
FAIL_SETUP = False
FAIL_RUN = False
FAIL_TEARDOWN = False
FAIL_EXIT = False
SUPPRESS = False


class FilesystemBinding:
    def write(self, value: str) -> None:
        EVENTS.append((\"write\", value))


@contextmanager
def filesystem_binding(context):
    EVENTS.append((\"enter\", context.port_name, context.action, context.case.name))
    try:
        yield FilesystemBinding()
    finally:
        EVENTS.append((\"exit\", context.port_name))


class PatchScope:
    def __init__(self, context):
        self.context = context

    def __enter__(self):
        global PATCHED
        PATCHED = True
        EVENTS.append((\"enter\", self.context.port_name, self.context.action, self.context.case.name))
        return None

    def __exit__(self, exc_type, exc, traceback):
        global PATCHED
        EVENTS.append((\"exit\", self.context.port_name))
        PATCHED = False
        if FAIL_EXIT:
            raise RuntimeError(\"provider exit failed\")
        return SUPPRESS


class Provider:
    def __init__(self, factory):
        self.factory = factory

    def bind(self, context):
        return self.factory(context)


filesystem_provider = Provider(filesystem_binding)
patch_provider = Provider(PatchScope)


def callable_only_provider(context):
    return PatchScope(context)


class Adapter:
    def setup(self, context):
        EFFECT_MAPS.append(context.effects)
        EVENTS.append((\"setup\", tuple(context.effects), PATCHED))
        if FAIL_SETUP:
            raise RuntimeError(\"adapter setup failed\")
        context.effects[\"FilesystemPort\"].write(\"setup\")
        try:
            context.effects[\"other\"] = object()
        except TypeError:
            EVENTS.append((\"effects-immutable\",))

    def run(self, case, work_dir=None):
        EVENTS.append((\"run\", case.name, PATCHED))
        if FAIL_RUN:
            raise RuntimeError(\"adapter run failed\")

    def teardown(self, context):
        EVENTS.append((\"teardown\", context.case.name, PATCHED, context.error is None))
        if FAIL_TEARDOWN:
            raise RuntimeError(\"adapter teardown failed\")
""",
        encoding="utf-8",
    )


def load_plan(tmp_path: Path, *, action_ports: str = "[FilesystemPort, PatchPort]", providers: str | None = None):
    write_provider_fixture(tmp_path)
    spec_dir, mapping_path = write_effect_project(tmp_path, action_ports=action_ports, providers=providers)
    case = make_case()
    plan = load_effect_provider_plan(
        spec_dir=spec_dir,
        mapping_path=mapping_path,
        cases=[case],
        import_roots=[tmp_path],
    )
    return case, mapping_path, plan


def load_suppressing_outer_plan(tmp_path: Path, *, inner_provider: str):
    write_provider_fixture(tmp_path)
    fixture_path = tmp_path / "effect_provider_fixture.py"
    fixture_path.write_text(
        fixture_path.read_text(encoding="utf-8")
        + """
class SuppressingFilesystemScope:
    def __init__(self, context):
        self.context = context

    def __enter__(self):
        EVENTS.append(("enter-suppressor", self.context.port_name))
        return FilesystemBinding()

    def __exit__(self, exc_type, exc, tb):
        EVENTS.append(("exit-suppressor", None if exc_type is None else exc_type.__name__))
        return True


suppressing_filesystem_provider = Provider(SuppressingFilesystemScope)


@contextmanager
def invalid_patch_binding(context):
    EVENTS.append(("enter-invalid-inner", context.port_name))
    try:
        yield object()
    finally:
        EVENTS.append(("exit-invalid-inner", context.port_name))


invalid_patch_provider = Provider(invalid_patch_binding)


class InnerEnterFailureScope:
    def __enter__(self):
        EVENTS.append(("enter-failure-inner",))
        raise RuntimeError("inner provider enter failed")

    def __exit__(self, exc_type, exc, tb):
        EVENTS.append(("unexpected-inner-exit",))


inner_enter_failure_provider = Provider(lambda context: InnerEnterFailureScope())


class InnerExitFailureScope:
    def __enter__(self):
        EVENTS.append(("enter-exit-failure-inner",))
        return None

    def __exit__(self, exc_type, exc, tb):
        EVENTS.append(("exit-failure-inner",))
        raise RuntimeError("inner provider exit failed")


inner_exit_failure_provider = Provider(lambda context: InnerExitFailureScope())
""",
        encoding="utf-8",
    )
    providers = f"""[effect_providers.FilesystemPort]
provider = "effect_provider_fixture:suppressing_filesystem_provider"

[effect_providers.PatchPort]
provider = "effect_provider_fixture:{inner_provider}"
"""
    spec_dir, mapping_path = write_effect_project(tmp_path, providers=providers)
    case = make_case()
    plan = load_effect_provider_plan(
        spec_dir=spec_dir,
        mapping_path=mapping_path,
        cases=[case],
        import_roots=[tmp_path],
    )
    return case, plan


def test_generated_effect_ports_are_runtime_checkable() -> None:
    rendered = render_ports(
        {
            "module": "Example",
            "types": {},
            "state": {},
            "commands": {},
            "results": {},
            "ports": {"FilesystemPort": {"role": "effect", "methods": {"write": {"result": "None"}}}},
        },
        Path("spec_manifest.yaml"),
    )

    assert "from typing import Protocol, runtime_checkable" in rendered
    assert "@runtime_checkable\nclass FilesystemPort(Protocol):" in rendered


def test_effect_providers_wrap_setup_run_assertion_teardown_and_exit_in_reverse_order(tmp_path: Path) -> None:
    case, _mapping_path, plan = load_plan(tmp_path)

    execute_cases_in_batch(
        cases=[case],
        mappings={"Publish": AdapterMapping("Publish", "effect_provider_fixture:Adapter", kind="publisher")},
        work_dir=tmp_path / "work",
        import_roots=[tmp_path],
        effect_provider_plan=plan,
    )

    import effect_provider_fixture

    assert effect_provider_fixture.EVENTS == [
        ("enter", "FilesystemPort", "Publish", "case_1"),
        ("enter", "PatchPort", "Publish", "case_1"),
        ("setup", ("FilesystemPort", "PatchPort"), True),
        ("write", "setup"),
        ("effects-immutable",),
        ("run", "case_1", True),
        ("teardown", "case_1", True, True),
        ("exit", "PatchPort"),
        ("exit", "FilesystemPort"),
    ]
    assert effect_provider_fixture.PATCHED is False


def test_case_action_not_adapter_label_selects_effect_ports(tmp_path: Path) -> None:
    write_provider_fixture(tmp_path)
    spec_dir, mapping_path = write_effect_project(tmp_path)
    case = make_case()
    case.labels = frozenset({"FineGrainedAdapterLabel"})

    plan = load_effect_provider_plan(
        spec_dir=spec_dir,
        mapping_path=mapping_path,
        cases=[case],
        import_roots=[tmp_path],
    )

    assert [binding.port_name for binding in plan.for_case(case)] == ["FilesystemPort", "PatchPort"]


def test_each_case_gets_a_fresh_immutable_effect_map_including_none_patch_binding(tmp_path: Path) -> None:
    write_provider_fixture(tmp_path)
    spec_dir, mapping_path = write_effect_project(tmp_path)
    cases = [make_case("case_1"), make_case("case_2")]
    plan = load_effect_provider_plan(
        spec_dir=spec_dir,
        mapping_path=mapping_path,
        cases=cases,
        import_roots=[tmp_path],
    )

    execute_cases_in_batch(
        cases=cases,
        mappings={"Publish": AdapterMapping("Publish", "effect_provider_fixture:Adapter", kind="publisher")},
        work_dir=tmp_path / "work",
        import_roots=[tmp_path],
        effect_provider_plan=plan,
    )

    import effect_provider_fixture

    first, second = effect_provider_fixture.EFFECT_MAPS
    assert first is not second
    assert first["PatchPort"] is None and second["PatchPort"] is None
    with pytest.raises(TypeError):
        first["FilesystemPort"] = object()


def test_provider_bind_receives_an_existing_case_work_directory(tmp_path: Path) -> None:
    write_provider_fixture(tmp_path)
    fixture_path = tmp_path / "effect_provider_fixture.py"
    fixture_path.write_text(
        fixture_path.read_text(encoding="utf-8")
        + """
from contextlib import contextmanager as _work_dir_contextmanager

@_work_dir_contextmanager
def work_dir_binding(context):
    EVENTS.append(("bind-work-dir", context.work_dir.is_dir()))
    yield FilesystemBinding()


work_dir_provider = Provider(work_dir_binding)
""",
        encoding="utf-8",
    )
    providers = """[effect_providers.FilesystemPort]
provider = "effect_provider_fixture:work_dir_provider"

[effect_providers.PatchPort]
provider = "effect_provider_fixture:patch_provider"
"""
    spec_dir, mapping_path = write_effect_project(
        tmp_path,
        providers=providers,
    )
    case = make_case()
    plan = load_effect_provider_plan(
        spec_dir=spec_dir,
        mapping_path=mapping_path,
        cases=[case],
        import_roots=[tmp_path],
    )

    execute_cases_in_batch(
        cases=[case],
        mappings={"Publish": AdapterMapping("Publish", "effect_provider_fixture:Adapter")},
        work_dir=tmp_path / "work",
        import_roots=[tmp_path],
        effect_provider_plan=plan,
    )

    import effect_provider_fixture

    assert ("bind-work-dir", True) in effect_provider_fixture.EVENTS


def test_provider_cannot_mutate_nested_generated_case_oracle_during_bind(tmp_path: Path) -> None:
    write_provider_fixture(tmp_path)
    fixture_path = tmp_path / "effect_provider_fixture.py"
    fixture_path.write_text(
        fixture_path.read_text(encoding="utf-8")
        + """
def mutating_binding(context):
    context.case.before["rewritten"] = True
    return filesystem_provider.bind(context)


mutating_provider = Provider(mutating_binding)
""",
        encoding="utf-8",
    )
    providers = """[effect_providers.FilesystemPort]
provider = "effect_provider_fixture:mutating_provider"
"""
    spec_dir, mapping_path = write_effect_project(
        tmp_path,
        action_ports="[FilesystemPort]",
        providers=providers,
    )
    case = make_case()
    plan = load_effect_provider_plan(
        spec_dir=spec_dir,
        mapping_path=mapping_path,
        cases=[case],
        import_roots=[tmp_path],
    )

    with pytest.raises(SystemExit, match="must not rewrite the test oracle"):
        execute_cases_in_batch(
            cases=[case],
            mappings={"Publish": AdapterMapping("Publish", "effect_provider_fixture:Adapter")},
            work_dir=tmp_path / "work",
            import_roots=[tmp_path],
            effect_provider_plan=plan,
        )

    import effect_provider_fixture

    assert not any(event[0] == "setup" for event in effect_provider_fixture.EVENTS)


def test_simple_toml_fallback_rejects_duplicate_keys_and_adapter_tables() -> None:
    with pytest.raises(ValueError, match="duplicate key 'provider'"):
        parse_simple_mapping_toml(
            """[effect_providers.FilesystemPort]
provider = "one:provider"
provider = "two:provider"
"""
        )

    with pytest.raises(ValueError, match=r"duplicate \[adapters.Publish\] table"):
        parse_simple_mapping_toml(
            """[adapters.Publish]
adapter = "one:Adapter"
[adapters.Publish]
adapter = "two:Adapter"
"""
        )


@pytest.mark.parametrize(
    ("flag", "message", "expected_absent"),
    [
        ("FAIL_SETUP", "adapter setup failed", "run"),
        ("FAIL_TEARDOWN", "adapter teardown failed", "never"),
        ("FAIL_EXIT", "provider exit failed", "never"),
    ],
)
def test_lifecycle_failures_keep_all_cleanup_active(
    tmp_path: Path,
    flag: str,
    message: str,
    expected_absent: str,
) -> None:
    case, _mapping_path, plan = load_plan(tmp_path)
    import effect_provider_fixture

    setattr(effect_provider_fixture, flag, True)
    with pytest.raises(SystemExit, match=message):
        execute_cases_in_batch(
            cases=[case],
            mappings={"Publish": AdapterMapping("Publish", "effect_provider_fixture:Adapter", kind="publisher")},
            work_dir=tmp_path / "work",
            import_roots=[tmp_path],
            effect_provider_plan=plan,
        )

    event_names = [event[0] for event in effect_provider_fixture.EVENTS]
    if expected_absent != "never":
        assert expected_absent not in event_names
    assert event_names[-2:] == ["exit", "exit"]
    assert effect_provider_fixture.EVENTS[-2:] == [("exit", "PatchPort"), ("exit", "FilesystemPort")]
    assert effect_provider_fixture.PATCHED is False


def test_primary_and_provider_cleanup_failures_are_both_reported_and_all_cleanup_runs(tmp_path: Path) -> None:
    case, _mapping_path, plan = load_plan(tmp_path)
    import effect_provider_fixture

    effect_provider_fixture.FAIL_RUN = True
    effect_provider_fixture.FAIL_EXIT = True
    with pytest.raises(SystemExit) as excinfo:
        execute_cases_in_batch(
            cases=[case],
            mappings={"Publish": AdapterMapping("Publish", "effect_provider_fixture:Adapter", kind="publisher")},
            work_dir=tmp_path / "work",
            import_roots=[tmp_path],
            effect_provider_plan=plan,
        )

    message = str(excinfo.value)
    assert "adapter run failed" in message
    assert "provider exit failed" in message
    assert effect_provider_fixture.EVENTS[-2:] == [("exit", "PatchPort"), ("exit", "FilesystemPort")]
    assert effect_provider_fixture.PATCHED is False


def test_provider_exit_cannot_suppress_primary_adapter_failure(tmp_path: Path) -> None:
    case, _mapping_path, plan = load_plan(tmp_path)
    import effect_provider_fixture

    effect_provider_fixture.FAIL_RUN = True
    effect_provider_fixture.SUPPRESS = True
    with pytest.raises(SystemExit, match="adapter run failed"):
        execute_cases_in_batch(
            cases=[case],
            mappings={"Publish": AdapterMapping("Publish", "effect_provider_fixture:Adapter", kind="publisher")},
            work_dir=tmp_path / "work",
            import_roots=[tmp_path],
            effect_provider_plan=plan,
        )

    assert effect_provider_fixture.EVENTS[-2:] == [("exit", "PatchPort"), ("exit", "FilesystemPort")]


def test_outer_provider_cannot_suppress_invalid_inner_binding(tmp_path: Path) -> None:
    case, plan = load_suppressing_outer_plan(tmp_path, inner_provider="invalid_patch_provider")

    with pytest.raises(SystemExit, match="does not implement generated port PatchPort"):
        execute_cases_in_batch(
            cases=[case],
            mappings={"Publish": AdapterMapping("Publish", "effect_provider_fixture:Adapter")},
            work_dir=tmp_path / "work",
            import_roots=[tmp_path],
            effect_provider_plan=plan,
        )

    import effect_provider_fixture

    assert effect_provider_fixture.EVENTS == [
        ("enter-suppressor", "FilesystemPort"),
        ("enter-invalid-inner", "PatchPort"),
        ("exit-invalid-inner", "PatchPort"),
        ("exit-suppressor", "TypeError"),
    ]


def test_outer_provider_cannot_suppress_inner_enter_failure(tmp_path: Path) -> None:
    case, plan = load_suppressing_outer_plan(tmp_path, inner_provider="inner_enter_failure_provider")

    with pytest.raises(SystemExit, match="inner provider enter failed"):
        execute_cases_in_batch(
            cases=[case],
            mappings={"Publish": AdapterMapping("Publish", "effect_provider_fixture:Adapter")},
            work_dir=tmp_path / "work",
            import_roots=[tmp_path],
            effect_provider_plan=plan,
        )

    import effect_provider_fixture

    assert effect_provider_fixture.EVENTS == [
        ("enter-suppressor", "FilesystemPort"),
        ("enter-failure-inner",),
        ("exit-suppressor", "RuntimeError"),
    ]


def test_outer_provider_cannot_suppress_inner_exit_failure(tmp_path: Path) -> None:
    case, plan = load_suppressing_outer_plan(tmp_path, inner_provider="inner_exit_failure_provider")

    with pytest.raises(SystemExit, match="inner provider exit failed"):
        execute_cases_in_batch(
            cases=[case],
            mappings={"Publish": AdapterMapping("Publish", "effect_provider_fixture:Adapter")},
            work_dir=tmp_path / "work",
            import_roots=[tmp_path],
            effect_provider_plan=plan,
        )

    import effect_provider_fixture

    assert effect_provider_fixture.EVENTS[-2:] == [
        ("exit-failure-inner",),
        ("exit-suppressor", "RuntimeError"),
    ]


def test_teardown_and_provider_cleanup_failures_are_both_reported(tmp_path: Path) -> None:
    case, _mapping_path, plan = load_plan(tmp_path)
    import effect_provider_fixture

    effect_provider_fixture.FAIL_TEARDOWN = True
    effect_provider_fixture.FAIL_EXIT = True
    with pytest.raises(SystemExit) as excinfo:
        execute_cases_in_batch(
            cases=[case],
            mappings={"Publish": AdapterMapping("Publish", "effect_provider_fixture:Adapter")},
            work_dir=tmp_path / "work",
            import_roots=[tmp_path],
            effect_provider_plan=plan,
        )

    message = str(excinfo.value)
    assert "adapter teardown failed" in message
    assert "provider exit failed" in message
    assert effect_provider_fixture.EVENTS[-2:] == [("exit", "PatchPort"), ("exit", "FilesystemPort")]
    assert effect_provider_fixture.PATCHED is False


def test_assertion_failure_reaches_teardown_and_provider_cleanup(tmp_path: Path) -> None:
    write_provider_fixture(tmp_path)
    fixture_path = tmp_path / "effect_provider_fixture.py"
    fixture_path.write_text(
        fixture_path.read_text(encoding="utf-8").replace(
            'EVENTS.append(("run", case.name, PATCHED))',
            'EVENTS.append(("run", case.name, PATCHED))\n        return {"output": "wrong"}',
        ),
        encoding="utf-8",
    )
    spec_dir, mapping_path = write_effect_project(tmp_path)
    case = make_case()
    plan = load_effect_provider_plan(
        spec_dir=spec_dir,
        mapping_path=mapping_path,
        cases=[case],
        import_roots=[tmp_path],
    )

    with pytest.raises(SystemExit, match="adapter output mismatch"):
        execute_cases_in_batch(
            cases=[case],
            mappings={"Publish": AdapterMapping("Publish", "effect_provider_fixture:Adapter", kind="publisher")},
            work_dir=tmp_path / "work",
            import_roots=[tmp_path],
            effect_provider_plan=plan,
        )

    import effect_provider_fixture

    assert ("teardown", "case_1", True, False) in effect_provider_fixture.EVENTS
    assert effect_provider_fixture.EVENTS[-2:] == [("exit", "PatchPort"), ("exit", "FilesystemPort")]
    assert effect_provider_fixture.PATCHED is False


@pytest.mark.parametrize(
    ("action_ports", "providers", "message"),
    [
        ("[UnknownPort]", None, "unknown semantic effect port UnknownPort"),
        ("[FilesystemPort, FilesystemPort]", None, "duplicate semantic effect port FilesystemPort"),
        (
            "[FilesystemPort, PatchPort]",
            '[effect_providers.FilesystemPort]\nprovider = "effect_provider_fixture:filesystem_provider"\n',
            "missing provider for semantic effect port PatchPort",
        ),
        (
            "[FilesystemPort]",
            '[effect_providers.UnknownPort]\nprovider = "effect_provider_fixture:filesystem_provider"\n',
            "provider configured for unknown semantic effect port UnknownPort",
        ),
        (
            "[FilesystemPort]",
            '[effect_providers.FilesystemPort]\nprovider = "missing_module:nope"\n',
            "could not load provider",
        ),
        (
            "[FilesystemPort]",
            '[effect_providers.FilesystemPort]\nprovider = "effect_provider_fixture:callable_only_provider"\n',
            "must implement EffectProvider.bind",
        ),
        (
            "FilesystemPort",
            '[effect_providers.FilesystemPort]\nprovider = "effect_provider_fixture:filesystem_provider"\n',
            "effect_ports must be a list",
        ),
        (
            "{}",
            '[effect_providers.FilesystemPort]\nprovider = "effect_provider_fixture:filesystem_provider"\n',
            "effect_ports must be a list",
        ),
        (
            "null",
            '[effect_providers.FilesystemPort]\nprovider = "effect_provider_fixture:filesystem_provider"\n',
            "effect_ports must be a list",
        ),
        (
            '[" FilesystemPort"]',
            '[effect_providers.FilesystemPort]\nprovider = "effect_provider_fixture:filesystem_provider"\n',
            "effect_ports must be a list",
        ),
        # The orphan-provider configuration that used to sit here -- a provider
        # bound for a port no selected case requires -- is deliberately NOT a
        # refusal any more. HP-04 (CM-F5 / EV-03-DF-02) made it a report,
        # because it is the normal shape of a case-module SLICE and the refusal
        # left the shipped ex4 fixture with zero working configurations for its
        # own slice. The same configuration is asserted, with the opposite
        # outcome, by `test_an_orphaned_provider_is_reported_not_refused`.
    ],
)
def test_effect_provider_configuration_fails_closed_before_execution(
    tmp_path: Path,
    action_ports: str,
    providers: str | None,
    message: str,
) -> None:
    write_provider_fixture(tmp_path)
    spec_dir, mapping_path = write_effect_project(tmp_path, action_ports=action_ports, providers=providers)

    with pytest.raises(EffectProviderConfigurationError, match=message):
        load_effect_provider_plan(
            spec_dir=spec_dir,
            mapping_path=mapping_path,
            cases=[make_case()],
            import_roots=[tmp_path],
        )


def test_an_orphaned_provider_is_reported_not_refused(tmp_path: Path) -> None:
    """CM-F5 / EV-03-DF-02: a slice narrower than its view still runs.

    A case module in `slice` form enters fewer actions than the view it
    extends, so the view's providers for the actions it does not enter are
    orphaned. That used to raise, which meant EVERY mapping the ex4 fixture
    ships refused the fixture's own slice: zero working configurations, and the
    documented workaround needed a third mapping file that existed nowhere.

    The two halves asserted here are the two halves of the fix. The plan is
    produced (no refusal), AND it says out loud which oracle the run does not
    carry -- because the blind agent that hit the refusal wrote its own third
    mapping and observed it was a strictly weaker instrument, so a green run
    under it over-reads. Documentation cannot reach a reader at that moment; the
    run's own output can.
    """
    write_provider_fixture(tmp_path)
    spec_dir, mapping_path = write_effect_project(tmp_path, action_ports="[FilesystemPort]", providers=None)

    plan = load_effect_provider_plan(
        spec_dir=spec_dir,
        mapping_path=mapping_path,
        cases=[make_case()],
        import_roots=[tmp_path],
    )

    assert plan.orphan_ports == ("PatchPort",)
    assert set(plan.carried) == {"FilesystemPort"}
    assert plan.configured is True
    # The bindings the run DOES carry are unaffected: reporting the orphan must
    # not quietly drop the providers the corpus actually requires.
    assert [binding.port_name for binding in plan.for_case(make_case())] == ["FilesystemPort"]

    rendered = plan.render_oracle_coverage()
    assert "**NOT** CARRIED" in rendered
    assert "PatchPort" in rendered
    assert "FLOOR" in rendered
    assert "FilesystemPort" in rendered


def test_non_effect_manifest_port_cannot_be_bound_as_semantic_effect(tmp_path: Path) -> None:
    write_provider_fixture(tmp_path)
    providers = """[effect_providers.PatchPort]
provider = "effect_provider_fixture:patch_provider"
"""
    spec_dir, mapping_path = write_effect_project(tmp_path, action_ports="[PatchPort]", providers=providers)
    manifest = spec_dir / "spec_manifest.yaml"
    manifest.write_text(
        manifest.read_text(encoding="utf-8").replace("  PatchPort:\n    role: effect", "  PatchPort:\n    role: application"),
        encoding="utf-8",
    )

    with pytest.raises(EffectProviderConfigurationError, match="unknown semantic effect port PatchPort"):
        load_effect_provider_plan(
            spec_dir=spec_dir,
            mapping_path=mapping_path,
            cases=[make_case()],
            import_roots=[tmp_path],
        )


def test_duplicate_provider_table_is_rejected(tmp_path: Path) -> None:
    write_provider_fixture(tmp_path)
    providers = """[effect_providers.FilesystemPort]
provider = "effect_provider_fixture:filesystem_provider"

[effect_providers.FilesystemPort]
provider = "effect_provider_fixture:filesystem_provider"
"""
    spec_dir, mapping_path = write_effect_project(tmp_path, action_ports="[FilesystemPort]", providers=providers)

    with pytest.raises(EffectProviderConfigurationError, match="invalid provider mapping"):
        load_effect_provider_plan(
            spec_dir=spec_dir,
            mapping_path=mapping_path,
            cases=[make_case()],
            import_roots=[tmp_path],
        )


def test_provider_table_rejects_unknown_keys(tmp_path: Path) -> None:
    write_provider_fixture(tmp_path)
    providers = """[effect_providers.FilesystemPort]
provider = "effect_provider_fixture:filesystem_provider"
response_plan = "not-framework-owned"
"""
    spec_dir, mapping_path = write_effect_project(tmp_path, action_ports="[FilesystemPort]", providers=providers)

    with pytest.raises(EffectProviderConfigurationError, match="unknown key.*response_plan"):
        load_effect_provider_plan(
            spec_dir=spec_dir,
            mapping_path=mapping_path,
            cases=[make_case()],
            import_roots=[tmp_path],
        )


def test_all_case_effect_declarations_preflight_before_any_adapter_hook(tmp_path: Path) -> None:
    write_provider_fixture(tmp_path)
    spec_dir, mapping_path = write_effect_project(tmp_path)
    (spec_dir / "actions.yml").write_text(
        """actions:
  Publish:
    effect_ports: [FilesystemPort, PatchPort]
  Broken:
    effect_ports: [UnknownPort]
""",
        encoding="utf-8",
    )

    with pytest.raises(EffectProviderConfigurationError, match="UnknownPort"):
        load_effect_provider_plan(
            spec_dir=spec_dir,
            mapping_path=mapping_path,
            cases=[make_case("good", "Publish"), make_case("bad", "Broken")],
            import_roots=[tmp_path],
        )

    import effect_provider_fixture

    assert effect_provider_fixture.EVENTS == []


@pytest.mark.parametrize(
    ("invalid_action", "action_document", "message"),
    [
        (
            "Missing",
            """actions:
  Publish:
    effect_ports: [FilesystemPort, PatchPort]
""",
            "case bad action Missing is not declared in actions.yml",
        ),
        (
            "NullAction",
            """actions:
  Publish:
    effect_ports: [FilesystemPort, PatchPort]
  NullAction:
""",
            "actions.yml action NullAction must be a mapping",
        ),
        (
            "NoPorts",
            """actions:
  Publish:
    effect_ports: [FilesystemPort, PatchPort]
  NoPorts:
    layer: internal
""",
            "actions.yml action NoPorts must declare effect_ports",
        ),
    ],
)
def test_configured_semantic_schema_requires_every_case_action_mapping(
    tmp_path: Path,
    invalid_action: str,
    action_document: str,
    message: str,
) -> None:
    write_provider_fixture(tmp_path)
    spec_dir, mapping_path = write_effect_project(tmp_path)
    (spec_dir / "actions.yml").write_text(action_document, encoding="utf-8")

    with pytest.raises(EffectProviderConfigurationError, match=message):
        load_effect_provider_plan(
            spec_dir=spec_dir,
            mapping_path=mapping_path,
            cases=[make_case("good", "Publish"), make_case("bad", invalid_action)],
            import_roots=[tmp_path],
        )

    import effect_provider_fixture

    assert effect_provider_fixture.EVENTS == []


def test_invalid_explicit_binding_fails_before_adapter_setup(tmp_path: Path) -> None:
    write_provider_fixture(tmp_path)
    with (tmp_path / "effect_provider_fixture.py").open("a", encoding="utf-8") as fixture:
        fixture.write(
            """
from contextlib import contextmanager as _contextmanager

@_contextmanager
def invalid_binding(context):
    EVENTS.append(("enter-invalid", context.port_name))
    try:
        yield object()
    finally:
        EVENTS.append(("exit-invalid", context.port_name))


invalid_provider = Provider(invalid_binding)
"""
        )
    providers = """[effect_providers.FilesystemPort]
provider = "effect_provider_fixture:invalid_provider"
"""
    spec_dir, mapping_path = write_effect_project(tmp_path, action_ports="[FilesystemPort]", providers=providers)
    case = make_case()
    plan = load_effect_provider_plan(
        spec_dir=spec_dir,
        mapping_path=mapping_path,
        cases=[case],
        import_roots=[tmp_path],
    )

    with pytest.raises(SystemExit, match="does not implement generated port FilesystemPort"):
        execute_cases_in_batch(
            cases=[case],
            mappings={"Publish": AdapterMapping("Publish", "effect_provider_fixture:Adapter", kind="publisher")},
            work_dir=tmp_path / "work",
            import_roots=[tmp_path],
            effect_provider_plan=plan,
        )

    import effect_provider_fixture

    assert not any(event[0] in {"setup", "run", "teardown"} for event in effect_provider_fixture.EVENTS)
    assert effect_provider_fixture.EVENTS == [
        ("enter-invalid", "FilesystemPort"),
        ("exit-invalid", "FilesystemPort"),
    ]


@pytest.mark.parametrize(
    ("method_source", "message"),
    [
        (
            "def write(self, value: str, extra: str) -> None:\n        pass",
            "FilesystemPort.write has incompatible parameters",
        ),
        (
            "def write(self, value: bytes) -> None:\n        pass",
            "FilesystemPort.write parameter 'value' annotation mismatch",
        ),
        (
            "def write(self, value: str) -> str:\n        return value",
            "FilesystemPort.write return annotation mismatch",
        ),
    ],
)
def test_generated_port_signature_mismatch_fails_before_application_execution(
    tmp_path: Path,
    method_source: str,
    message: str,
) -> None:
    write_provider_fixture(tmp_path)
    with (tmp_path / "effect_provider_fixture.py").open("a", encoding="utf-8") as fixture:
        fixture.write(
            f"""
class WrongSignatureBinding:
    {method_source}


@contextmanager
def wrong_signature_scope(context):
    EVENTS.append(("enter-wrong-signature", context.port_name))
    try:
        yield WrongSignatureBinding()
    finally:
        EVENTS.append(("exit-wrong-signature", context.port_name))


wrong_signature_provider = Provider(wrong_signature_scope)
"""
        )
    providers = """[effect_providers.FilesystemPort]
provider = "effect_provider_fixture:wrong_signature_provider"
"""
    spec_dir, mapping_path = write_effect_project(
        tmp_path,
        action_ports="[FilesystemPort]",
        providers=providers,
    )
    case = make_case()
    plan = load_effect_provider_plan(
        spec_dir=spec_dir,
        mapping_path=mapping_path,
        cases=[case],
        import_roots=[tmp_path],
    )

    with pytest.raises(SystemExit, match=message):
        execute_cases_in_batch(
            cases=[case],
            mappings={"Publish": AdapterMapping("Publish", "effect_provider_fixture:Adapter")},
            work_dir=tmp_path / "work",
            import_roots=[tmp_path],
            effect_provider_plan=plan,
        )

    import effect_provider_fixture

    assert not any(event[0] in {"setup", "run", "teardown"} for event in effect_provider_fixture.EVENTS)
    assert effect_provider_fixture.EVENTS == [
        ("enter-wrong-signature", "FilesystemPort"),
        ("exit-wrong-signature", "FilesystemPort"),
    ]


def test_provider_enter_failure_cleans_already_entered_provider_without_running_adapter(tmp_path: Path) -> None:
    write_provider_fixture(tmp_path)
    with (tmp_path / "effect_provider_fixture.py").open("a", encoding="utf-8") as fixture:
        fixture.write(
            """
class EnterFailure:
    def __enter__(self):
        EVENTS.append(("enter-failure",))
        raise RuntimeError("provider enter failed")

    def __exit__(self, exc_type, exc, tb):
        EVENTS.append(("unexpected-exit",))


enter_failure_provider = Provider(lambda context: EnterFailure())
"""
        )
    providers = """[effect_providers.FilesystemPort]
provider = "effect_provider_fixture:filesystem_provider"

[effect_providers.PatchPort]
provider = "effect_provider_fixture:enter_failure_provider"
"""
    spec_dir, mapping_path = write_effect_project(tmp_path, providers=providers)
    case = make_case()
    plan = load_effect_provider_plan(
        spec_dir=spec_dir,
        mapping_path=mapping_path,
        cases=[case],
        import_roots=[tmp_path],
    )

    with pytest.raises(SystemExit, match="provider enter failed"):
        execute_cases_in_batch(
            cases=[case],
            mappings={"Publish": AdapterMapping("Publish", "effect_provider_fixture:Adapter", kind="publisher")},
            work_dir=tmp_path / "work",
            import_roots=[tmp_path],
            effect_provider_plan=plan,
        )

    import effect_provider_fixture

    assert effect_provider_fixture.EVENTS == [
        ("enter", "FilesystemPort", "Publish", "case_1"),
        ("enter-failure",),
        ("exit", "FilesystemPort"),
    ]


def test_provider_bearing_non_batch_execution_is_rejected() -> None:
    plan = SimpleNamespace(configured=True)

    with pytest.raises(SystemExit, match="semantic effect providers require --batch"):
        validate_effect_provider_execution_mode(plan, batch=False, validate_only=False)

    validate_effect_provider_execution_mode(plan, batch=True, validate_only=False)
    validate_effect_provider_execution_mode(plan, batch=False, validate_only=True)


def test_semantic_providers_coexist_with_passive_effect_sandbox(tmp_path: Path) -> None:
    case, _mapping_path, plan = load_plan(tmp_path)
    declarations = load_effect_declarations(
        {
            "effects": {
                "components": {
                    "Fixture": {
                        "ports": {
                            "case_sandbox": {
                                "type": "filesystem.write",
                                "target": "**/sandbox/**",
                            }
                        }
                    }
                },
                "actions": {"Publish": ["case_sandbox"]},
            }
        }
    )

    execute_cases_in_batch(
        cases=[case],
        mappings={
            "Publish": AdapterMapping(
                "Publish",
                "tests.effect_adapter_fixtures:DeclaredEffectAdapter",
                kind="passive-and-semantic",
            )
        },
        work_dir=tmp_path / "work",
        import_roots=[ROOT, tmp_path],
        declarations=declarations,
        effect_provider_plan=plan,
    )

    import effect_provider_fixture

    assert effect_provider_fixture.EVENTS == [
        ("enter", "FilesystemPort", "Publish", "case_1"),
        ("enter", "PatchPort", "Publish", "case_1"),
        ("exit", "PatchPort"),
        ("exit", "FilesystemPort"),
    ]


def test_legacy_passive_effect_case_with_no_input_needs_no_semantic_action(tmp_path: Path) -> None:
    case = SimpleNamespace(
        name="legacy_case",
        labels=frozenset({"Act"}),
        before={},
        input=None,
        output=None,
        after=None,
    )
    declarations = load_effect_declarations(
        {
            "effects": {
                "components": {
                    "Fixture": {
                        "ports": {
                            "case_sandbox": {
                                "type": "filesystem.write",
                                "target": "**/sandbox/**",
                            }
                        }
                    }
                },
                "actions": {"Act": ["case_sandbox"]},
            }
        }
    )

    execute_cases_in_batch(
        cases=[case],
        mappings={
            "Act": AdapterMapping(
                "Act",
                "tests.effect_adapter_fixtures:DeclaredEffectAdapter",
            )
        },
        work_dir=tmp_path / "work",
        import_roots=[ROOT],
        declarations=declarations,
    )


def test_real_batch_cli_resolves_generated_port_from_spec_generated_package_not_case_package(tmp_path: Path) -> None:
    spec_dir = tmp_path / "spec"
    spec_dir.mkdir()
    (spec_dir / "Example.tla").write_text(
        """----------------------------- MODULE Example -----------------------------
VARIABLE status
Init == status = "start"
Next == status' = "done"
=============================================================================
""",
        encoding="utf-8",
    )
    manifest_path = spec_dir / "spec_manifest.yaml"
    manifest_path.write_text(
        """module: Example
package: generated_contract
state:
  ExampleState:
    fields:
      status:
        type: str
        tla: status
types: {}
commands: {}
results: {}
ports:
  FilesystemPort:
    role: effect
    methods:
      write:
        result: None
invariants: []
finite_model: {}
generators: {}
fake:
  class: ExampleSpecDouble
  actions: {}
""",
        encoding="utf-8",
    )
    generated_root = spec_dir / "generated"
    generated_contract = generate(manifest_path, generated_root)
    # Keep cases and mapping outside the spec tree.  The outer CLI invocation
    # below re-execs for ``--python``; the child can find the generated port
    # package only if the explicit --spec-dir survives that re-exec.
    cases_dir = tmp_path / "case-package" / "example_cases"
    render_python_package(
        module="Example",
        states={
            "0": {"status": "start"},
            "1": {"status": "done"},
            "2": {"status": "broken"},
        },
        edges=[Edge("0", "1", "Publish"), Edge("0", "2", "Broken")],
        package_dir=cases_dir,
    )
    assert not (cases_dir / "ports.py").exists()
    assert (generated_contract / "ports.py").is_file()

    actions_path = spec_dir / "actions.yml"
    actions_path.write_text(
        """actions:
  Publish:
    layer: internal
    controllability: unit_direct
    generates: [spec_unit]
    effect_ports: [FilesystemPort]
  Broken:
    layer: internal
    controllability: unit_direct
    generates: [spec_unit]
    effect_ports: [UnknownPort]
""",
        encoding="utf-8",
    )
    (spec_dir / "provider_app.py").write_text(
        """from contextlib import contextmanager
from pathlib import Path

EVENTS = Path(__file__).with_name("events.txt")

def event(value):
    with EVENTS.open("a", encoding="utf-8") as handle:
        handle.write(value + "\\n")

class FilesystemBinding:
    def write(self) -> None:
        event("write")

@contextmanager
def filesystem_binding(context):
    event("enter:" + context.port_name)
    try:
        yield FilesystemBinding()
    finally:
        event("exit:" + context.port_name)

class Provider:
    def bind(self, context):
        return filesystem_binding(context)

filesystem_provider = Provider()

class Adapter:
    def setup(self, context):
        event("setup:" + ",".join(context.effects))
        context.effects["FilesystemPort"].write()

    def run(self, case, work_dir=None):
        event("run:" + case.input.action)
        return {"output": case.output, "after": case.after}

    def teardown(self, context):
        event("teardown:" + str("FilesystemPort" in context.effects))
""",
        encoding="utf-8",
    )
    mapping_path = tmp_path / "case_adapters.toml"
    mapping_path.write_text(
        """[adapters.Publish]
adapter = "provider_app:Adapter"

[adapters.Broken]
adapter = "provider_app:Adapter"

[effect_providers.FilesystemPort]
provider = "provider_app:filesystem_provider"
""",
        encoding="utf-8",
    )

    command = [
        sys.executable,
        str(ROOT / "scripts" / "run_generated_case_adapters.py"),
        str(cases_dir),
        "--mapping",
        str(mapping_path),
        "--spec-dir",
        str(spec_dir),
        "--batch",
        "--label",
        "Publish",
        "--python",
        sys.executable,
        "--work-dir",
        str(tmp_path / "work"),
    ]

    # Provider preflight is coverage-wide, not weakened by the runnable-case
    # label filter.  No provider or adapter code runs for this malformed
    # unselected case.
    invalid = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert invalid.returncode != 0
    assert "UnknownPort" in invalid.stdout + invalid.stderr
    assert not (spec_dir / "events.txt").exists()

    actions_path.write_text(
        """actions:
  Publish:
    layer: internal
    controllability: unit_direct
    generates: [spec_unit]
    effect_ports: [FilesystemPort]
  Broken:
    layer: internal
    controllability: unit_direct
    generates: [spec_unit]
    effect_ports: []
""",
        encoding="utf-8",
    )
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert (spec_dir / "events.txt").read_text(encoding="utf-8").splitlines() == [
        "enter:FilesystemPort",
        "setup:FilesystemPort",
        "write",
        "run:Publish",
        "teardown:True",
        "exit:FilesystemPort",
    ]

    (spec_dir / "events.txt").unlink()
    non_batch_work = tmp_path / "non-batch-work"
    non_batch_command = [part for part in command if part != "--batch"]
    non_batch_command[non_batch_command.index(str(tmp_path / "work"))] = str(non_batch_work)
    non_batch = subprocess.run(
        non_batch_command,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert non_batch.returncode != 0
    assert "semantic effect providers require --batch" in non_batch.stdout + non_batch.stderr
    assert not (spec_dir / "events.txt").exists(), "provider and adapter code must not run in unsupported mode"
    assert not non_batch_work.exists(), "non-batch refusal must precede program/work-directory generation"


def test_no_effect_plan_preserves_legacy_batch_execution(tmp_path: Path) -> None:
    (tmp_path / "legacy_adapter.py").write_text(
        """EVENTS = []
class Adapter:
    def run(self, case, work_dir=None):
        EVENTS.append(case.name)
""",
        encoding="utf-8",
    )
    execute_cases_in_batch(
        cases=[make_case()],
        mappings={"Publish": AdapterMapping("Publish", "legacy_adapter:Adapter", kind="legacy")},
        work_dir=tmp_path / "work",
        import_roots=[tmp_path],
    )

    import legacy_adapter

    assert legacy_adapter.EVENTS == ["case_1"]


def test_empty_semantic_schema_plan_does_not_require_legacy_input_action(tmp_path: Path) -> None:
    (tmp_path / "spec_manifest.yaml").write_text(
        """module: Example
package: generated_contract
state: {}
commands: {}
results: {}
ports: {}
""",
        encoding="utf-8",
    )
    (tmp_path / "actions.yml").write_text(
        """actions:
  Act:
    effect_ports: []
""",
        encoding="utf-8",
    )
    mapping_path = tmp_path / "case_adapters.toml"
    mapping_path.write_text(
        """[adapters.Act]
adapter = "tests.effect_adapter_fixtures:DeclaredEffectAdapter"
""",
        encoding="utf-8",
    )
    legacy_case = SimpleNamespace(name="legacy", input=None, labels=frozenset({"Act"}))

    plan = load_effect_provider_plan(
        spec_dir=tmp_path,
        mapping_path=mapping_path,
        cases=[legacy_case],
        import_roots=[ROOT],
    )

    assert plan.configured is False
    assert plan.for_case(legacy_case) == ()
