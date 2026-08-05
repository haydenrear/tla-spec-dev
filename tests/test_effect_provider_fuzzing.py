from __future__ import annotations

from contextlib import contextmanager
from dataclasses import FrozenInstanceError
import json
import os
from pathlib import Path
import shlex
from types import SimpleNamespace
import subprocess
import sys
from typing import Any
import venv

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.run_generated_case_adapters import (  # noqa: E402
    AdapterMapping,
    execute_cases_in_batch,
    load_effect_provider_plan,
)
from spec_double_compiler.runtime import EffectProviderContext  # noqa: E402


def make_case(name: str, *, action: str = "Publish", view: str = "internal") -> SimpleNamespace:
    return SimpleNamespace(
        name=name,
        before={"state": 0},
        input=SimpleNamespace(action=action),
        output={"ok": True},
        after={"state": 1},
        labels=frozenset({action}),
        view=view,
        controllability="unit_direct" if view == "internal" else "e2e_direct",
        generates=frozenset({"spec_unit" if view == "internal" else "testgraph"}),
    )


def write_contract(tmp_path: Path, *, module: str, provider_tables: str) -> tuple[Path, Path]:
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
        """actions:
  Publish:
    layer: internal
    effect_ports: [FilesystemPort, PatchPort]
""",
        encoding="utf-8",
    )
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


def test_execution_point_is_immutable_and_keeps_the_original_case() -> None:
    from scripts.run_generated_case_adapters import ExecutionPoint

    case = make_case("original")
    point = ExecutionPoint(case=case, iteration=3)

    assert point.case is case
    assert point.iteration == 3
    with pytest.raises(FrozenInstanceError):
        point.iteration = 4  # type: ignore[misc]


def test_seed_protocol_has_a_fixed_unicode_vector_and_is_order_independent() -> None:
    from spec_double_compiler.effects import EFFECT_SEED_VERSION, derive_effect_seed

    assert EFFECT_SEED_VERSION == "tla-spec-dev/effect-seed/v1"
    assert derive_effect_seed(91, "case / Δ value", 7, "Filesystem Port") == (
        309256555147443017393012616679821206188
    )

    selected = derive_effect_seed(17, "selected case", 2, "PatchPort")
    reordered = [
        derive_effect_seed(17, case_name, iteration, port)
        for case_name, iteration, port in [
            ("other", 9, "FilesystemPort"),
            ("selected case", 2, "PatchPort"),
            ("first", 0, "ClockPort"),
        ]
    ]
    filtered = derive_effect_seed(17, "selected case", 2, "PatchPort")
    assert reordered[1] == selected == filtered


def test_seed_protocol_is_stable_across_python_hash_seeds() -> None:
    code = (
        "from spec_double_compiler.effects import derive_effect_seed; "
        "print(derive_effect_seed(91, 'case / Δ value', 7, 'Filesystem Port'))"
    )
    outputs: list[str] = []
    for hash_seed in ("1", "987654"):
        env = os.environ.copy()
        env["PYTHONHASHSEED"] = hash_seed
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        outputs.append(result.stdout.strip())

    assert outputs == [
        "309256555147443017393012616679821206188",
        "309256555147443017393012616679821206188",
    ]


def write_campaign_fixture(tmp_path: Path) -> None:
    sys.modules.pop("fuzz_campaign_fixture", None)
    (tmp_path / "fuzz_campaign_fixture.py").write_text(
        """from spec_double_compiler.runtime import CaseRunResult

CONTEXTS = []
SCOPES = []
EFFECT_MAPS = []
SHARED_MAPS = []
BATCH_CASE_NAMES = []
BATCH_WORK_DIRS = []
BATCH_SAW_SENTINEL = []
WORK_DIRS = []
CASE_OBJECT_IDS = []
ADAPTERS = []


class Binding:
    def write(self, value: str) -> None:
        pass

    def request(self) -> str:
        return "ok"


class Scope:
    def __init__(self, context):
        self.context = context
        SCOPES.append(self)

    def __enter__(self):
        return Binding()

    def __exit__(self, exc_type, exc, traceback):
        return False


class Provider:
    def bind(self, context):
        CONTEXTS.append(context)
        return Scope(context)


filesystem_provider = Provider()
patch_provider = Provider()


class Adapter:
    def __init__(self):
        ADAPTERS.append(self)

    def setup_all(self, context):
        SHARED_MAPS.append(context.shared)
        BATCH_CASE_NAMES.append(tuple(case.name for case in context.cases))
        BATCH_WORK_DIRS.append(context.work_dir)
        sentinel = context.work_dir / "setup-all-sentinel"
        BATCH_SAW_SENTINEL.append(sentinel.exists())
        sentinel.write_text(context.cases[0].name, encoding="utf-8")

    def setup(self, context):
        EFFECT_MAPS.append(context.effects)
        WORK_DIRS.append(context.work_dir)
        CASE_OBJECT_IDS.append(id(context.case))

    def run(self, case, work_dir=None):
        return CaseRunResult(output=case.output, after=case.after)
""",
        encoding="utf-8",
    )


def test_campaign_uses_fresh_point_resources_without_copying_cases(tmp_path: Path) -> None:
    from spec_double_compiler.effects import derive_effect_seed

    write_campaign_fixture(tmp_path)
    spec_dir, mapping_path = write_contract(
        tmp_path,
        module="fuzz_campaign_fixture",
        provider_tables="""[effect_providers.FilesystemPort]
provider = "fuzz_campaign_fixture:filesystem_provider"

[effect_providers.PatchPort]
provider = "fuzz_campaign_fixture:patch_provider"
""",
    )
    cases = [make_case("case one"), make_case("case-δ")]
    plan = load_effect_provider_plan(
        spec_dir=spec_dir,
        mapping_path=mapping_path,
        cases=cases,
        import_roots=[tmp_path],
    )

    execute_cases_in_batch(
        cases=cases,
        mappings={"Publish": AdapterMapping("Publish", "fuzz_campaign_fixture:Adapter", kind="publisher")},
        work_dir=tmp_path / "work",
        import_roots=[tmp_path],
        effect_provider_plan=plan,
        fuzz_runs=2,
        root_seed=73,
        replay_command_factory=lambda point: f"/absolute/runner --case {point.case.name!r} --fuzz-iteration {point.iteration}",
    )

    import fuzz_campaign_fixture as fixture

    assert [(ctx.case.name, ctx.iteration, ctx.port_name) for ctx in fixture.CONTEXTS] == [
        ("case one", 0, "FilesystemPort"),
        ("case one", 0, "PatchPort"),
        ("case-δ", 0, "FilesystemPort"),
        ("case-δ", 0, "PatchPort"),
        ("case one", 1, "FilesystemPort"),
        ("case one", 1, "PatchPort"),
        ("case-δ", 1, "FilesystemPort"),
        ("case-δ", 1, "PatchPort"),
    ]
    for context in fixture.CONTEXTS:
        assert context.root_seed == 73
        assert context.seed_version == "tla-spec-dev/effect-seed/v1"
        assert context.derived_seed == derive_effect_seed(
            73,
            context.case.name,
            context.iteration,
            context.port_name,
        )

    # Provider-bearing hooks/caches are point-isolated so the replay command
    # recreates the exact setup_all/teardown_all input as well as the case.
    assert len(fixture.ADAPTERS) == 4
    assert len(fixture.SHARED_MAPS) == 4
    assert len({id(shared) for shared in fixture.SHARED_MAPS}) == 4
    assert fixture.BATCH_CASE_NAMES == [
        ("case one",),
        ("case-δ",),
        ("case one",),
        ("case-δ",),
    ]
    assert len(set(fixture.BATCH_WORK_DIRS)) == 4
    assert fixture.BATCH_SAW_SENTINEL == [False, False, False, False]
    assert len(fixture.SCOPES) == 8
    assert len({id(scope) for scope in fixture.SCOPES}) == 8
    assert len(fixture.EFFECT_MAPS) == 4
    assert len({id(effects) for effects in fixture.EFFECT_MAPS}) == 4
    assert len(fixture.WORK_DIRS) == 4
    assert len(set(fixture.WORK_DIRS)) == 4
    assert all("iteration-" in str(path) for path in fixture.WORK_DIRS)
    assert fixture.CASE_OBJECT_IDS == [id(cases[0]), id(cases[1]), id(cases[0]), id(cases[1])]


def test_seed_only_campaign_uses_an_iteration_qualified_work_path(tmp_path: Path) -> None:
    from scripts.run_generated_case_adapters import _opaque_path_component

    write_campaign_fixture(tmp_path)
    spec_dir, mapping_path = write_contract(
        tmp_path,
        module="fuzz_campaign_fixture",
        provider_tables="""[effect_providers.FilesystemPort]
provider = "fuzz_campaign_fixture:filesystem_provider"

[effect_providers.PatchPort]
provider = "fuzz_campaign_fixture:patch_provider"
""",
    )
    case = make_case("seed-only")
    plan = load_effect_provider_plan(
        spec_dir=spec_dir,
        mapping_path=mapping_path,
        cases=[case],
        import_roots=[tmp_path],
    )

    execute_cases_in_batch(
        cases=[case],
        mappings={
            "Publish": AdapterMapping(
                "Publish",
                "fuzz_campaign_fixture:Adapter",
                kind="publisher",
            )
        },
        work_dir=tmp_path / "work",
        import_roots=[tmp_path],
        effect_provider_plan=plan,
        root_seed=73,
    )

    import fuzz_campaign_fixture as fixture

    assert fixture.WORK_DIRS == [
        tmp_path
        / "work"
        / "case-work"
        / _opaque_path_component("case", "seed-only")
        / "iteration-000000"
    ]


def test_case_and_kind_work_paths_use_opaque_collision_resistant_components(
    tmp_path: Path,
) -> None:
    from scripts.run_generated_case_adapters import (
        _opaque_path_component,
        generate_programs,
    )

    write_campaign_fixture(tmp_path)
    spec_dir, mapping_path = write_contract(
        tmp_path,
        module="fuzz_campaign_fixture",
        provider_tables="""[effect_providers.FilesystemPort]
provider = "fuzz_campaign_fixture:filesystem_provider"

[effect_providers.PatchPort]
provider = "fuzz_campaign_fixture:patch_provider"
""",
    )
    names = [
        "../../escaped-point",
        str(tmp_path / "absolute-point"),
        "alias/point",
        "alias:point",
        r"alias\point",
        "..",
        "x" * 300,
    ]
    cases = [make_case(name) for name in names]
    plan = load_effect_provider_plan(
        spec_dir=spec_dir,
        mapping_path=mapping_path,
        cases=cases,
        import_roots=[tmp_path],
    )
    dangerous_kind = "../../kind/../alias:kind\\portable"
    work_root = tmp_path / "work"

    execute_cases_in_batch(
        cases=cases,
        mappings={
            "Publish": AdapterMapping(
                "Publish",
                "fuzz_campaign_fixture:Adapter",
                kind=dangerous_kind,
            )
        },
        work_dir=work_root,
        import_roots=[tmp_path],
        effect_provider_plan=plan,
        root_seed=73,
    )

    import fuzz_campaign_fixture as fixture

    expected_case_components = {
        _opaque_path_component("case", name) for name in names
    }
    assert len(expected_case_components) == len(names)
    assert {
        path.parent.name for path in fixture.WORK_DIRS
    } == expected_case_components
    assert {
        path.name for path in fixture.BATCH_WORK_DIRS
    } == {_opaque_path_component("kind", dangerous_kind)}
    for path in [*fixture.WORK_DIRS, *fixture.BATCH_WORK_DIRS]:
        assert path.resolve().is_relative_to(work_root.resolve())
    for role, values in {
        "case": names,
        "kind": ["a/b", "a:b", r"a\b", "..", "/absolute"],
    }.items():
        components = [_opaque_path_component(role, value) for value in values]
        assert len(set(components)) == len(values)
        assert all(component.startswith(f"{role}-") for component in components)
        assert all(
            set(component.removeprefix(f"{role}-")) <= set("0123456789abcdef")
            for component in components
        )

    generated_work = tmp_path / "generated-work"
    programs = generate_programs(
        cases=cases,
        mappings={
            "Publish": AdapterMapping(
                "Publish",
                "fuzz_campaign_fixture:Adapter",
                kind=dangerous_kind,
            )
        },
        cases_dir=tmp_path / "generated_contract",
        work_dir=generated_work,
        import_roots=[tmp_path],
    )
    assert {program.stem for program in programs} == expected_case_components
    assert {
        path.name for path in (generated_work / "case-work").iterdir()
    } == expected_case_components
    assert all(program.resolve().is_relative_to(generated_work.resolve()) for program in programs)


def test_point_isolated_providers_preserve_corpus_level_passive_effect_diff(
    tmp_path: Path,
) -> None:
    from scripts.effect_conformance import load_effect_declarations

    write_campaign_fixture(tmp_path)
    spec_dir, mapping_path = write_contract(
        tmp_path,
        module="passive_provider_fixture",
        provider_tables="",
    )
    (tmp_path / "actions.yml").write_text(
        """actions:
  PublishA:
    layer: internal
    effect_ports: [FilesystemPort, PatchPort]
  PublishB:
    layer: internal
    effect_ports: [FilesystemPort, PatchPort]
""",
        encoding="utf-8",
    )
    (tmp_path / "passive_provider_fixture.py").write_text(
        """from pathlib import Path
from spec_double_compiler.runtime import CaseRunResult

class Adapter:
    def run(self, case, work_dir=None):
        target = Path(work_dir) / "sandbox" / (case.input.action + ".txt")
        target.write_text(case.name, encoding="utf-8")
        return CaseRunResult(output=case.output, after=case.after)
""",
        encoding="utf-8",
    )
    mapping_path.write_text(
        """[adapters.PublishA]
adapter = "passive_provider_fixture:Adapter"
kind = "publisher"

[adapters.PublishB]
adapter = "passive_provider_fixture:Adapter"
kind = "publisher"

[effect_providers.FilesystemPort]
provider = "fuzz_campaign_fixture:filesystem_provider"

[effect_providers.PatchPort]
provider = "fuzz_campaign_fixture:patch_provider"
""",
        encoding="utf-8",
    )
    cases = [
        make_case("case-a", action="PublishA"),
        make_case("case-b", action="PublishB"),
    ]
    plan = load_effect_provider_plan(
        spec_dir=spec_dir,
        mapping_path=mapping_path,
        cases=cases,
        import_roots=[tmp_path],
    )
    declarations = load_effect_declarations(
        {
            "effects": {
                "components": {
                    "Fixture": {
                        "ports": {
                            "publish_a_file": {
                                "type": "filesystem.write",
                                "target": "**/sandbox/PublishA.txt",
                            },
                            "publish_b_file": {
                                "type": "filesystem.write",
                                "target": "**/sandbox/PublishB.txt",
                            },
                        }
                    }
                },
                "actions": {
                    "PublishA": ["publish_a_file"],
                    "PublishB": ["publish_b_file"],
                },
            }
        }
    )
    report_path = tmp_path / "effect-report.json"

    execute_cases_in_batch(
        cases=cases,
        mappings={
            action: AdapterMapping(
                action,
                "passive_provider_fixture:Adapter",
                kind="publisher",
            )
            for action in ("PublishA", "PublishB")
        },
        work_dir=tmp_path / "work",
        import_roots=[tmp_path],
        declarations=declarations,
        effect_report_path=report_path,
        effect_provider_plan=plan,
    )

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["ok"] is True
    assert report["verdict"] == "clean"
    assert report["cases"] == ["case-a", "case-b"]
    assert set(report["declared_ports"]) == {
        "Fixture.publish_a_file",
        "Fixture.publish_b_file",
    }


def test_temporary_root_provider_lifecycle_is_not_an_application_effect(
    tmp_path: Path,
) -> None:
    from scripts.effect_conformance import load_effect_declarations

    spec_dir, mapping_path = write_contract(
        tmp_path,
        module="temporary_root_effect_fixture",
        provider_tables="""[effect_providers.FilesystemPort]
provider = "temporary_root_effect_fixture:filesystem_provider"
""",
    )
    (tmp_path / "actions.yml").write_text(
        """actions:
  Publish:
    layer: internal
    effect_ports: [FilesystemPort]
""",
        encoding="utf-8",
    )
    (tmp_path / "temporary_root_effect_fixture.py").write_text(
        """from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from spec_double_compiler.runtime import CaseRunResult

class Binding:
    def __init__(self, root: Path):
        self.root = root

    def write(self, value: str) -> None:
        (self.root / "payload.txt").write_text(value, encoding="utf-8")

class Provider:
    @contextmanager
    def bind(self, context):
        with TemporaryDirectory(prefix="effect-root-", dir=context.work_dir) as root:
            yield Binding(Path(root))

filesystem_provider = Provider()

class Adapter:
    def setup(self, context):
        self.filesystem = context.effects["FilesystemPort"]

    def run(self, case, work_dir=None):
        self.filesystem.write(case.name)
        return CaseRunResult(output=case.output, after=case.after)
""",
        encoding="utf-8",
    )
    case = make_case("temporary-root-case")
    plan = load_effect_provider_plan(
        spec_dir=spec_dir,
        mapping_path=mapping_path,
        cases=[case],
        import_roots=[tmp_path],
    )
    declarations = load_effect_declarations(
        {
            "effects": {
                "components": {
                    "Fixture": {
                        "ports": {
                            "payload": {
                                "type": "filesystem.write",
                                "target": "**/effect-root-*/payload.txt",
                            }
                        }
                    }
                },
                "actions": {"Publish": ["payload"]},
            }
        }
    )
    report_path = tmp_path / "temporary-root-report.json"

    execute_cases_in_batch(
        cases=[case],
        mappings={
            "Publish": AdapterMapping(
                "Publish",
                "temporary_root_effect_fixture:Adapter",
                kind="publisher",
            )
        },
        work_dir=tmp_path / "work",
        import_roots=[tmp_path],
        declarations=declarations,
        effect_report_path=report_path,
        effect_provider_plan=plan,
    )

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["ok"] is True
    assert report["gaps"] == []
    # Compared as CROSSINGS, not as raw records. One boundary crossing trips
    # every patch layer it passes through -- `Path.mkdir` calls `os.mkdir`,
    # `shutil.copy` calls `open`, and since HP-04 patched `Path.open` (so that
    # `path.open("a")` is no longer an invisible durable append),
    # `Path.write_text` trips two. `diff_effects` already collapses the same way
    # for gaps.
    crossings = {(effect["type"], effect["target"]) for effect in report["observed_effects"]}
    assert {effect_type for effect_type, _ in crossings} == {"filesystem.write"}
    assert len(crossings) == 1
    assert next(iter(crossings))[1].endswith("/payload.txt")


def test_self_installed_patch_remains_effective_inside_passive_observation(
    tmp_path: Path,
) -> None:
    from scripts.effect_conformance import load_effect_declarations

    spec_dir, mapping_path = write_contract(
        tmp_path,
        module="patch_effect_fixture",
        provider_tables="""[effect_providers.PatchPort]
provider = "patch_effect_fixture:patch_provider"
""",
    )
    (tmp_path / "actions.yml").write_text(
        """actions:
  Publish:
    layer: internal
    effect_ports: [PatchPort]
""",
        encoding="utf-8",
    )
    (tmp_path / "patch_effect_fixture.py").write_text(
        """from contextlib import contextmanager
from pathlib import Path
from spec_double_compiler.runtime import CaseRunResult

def request(target):
    raise AssertionError("provider patch was not installed")

@contextmanager
def installed_request_patch():
    global request
    original = request
    request = lambda target: Path(target).write_text("patched", encoding="utf-8")
    try:
        yield
    finally:
        request = original

class Provider:
    @contextmanager
    def bind(self, context):
        with installed_request_patch():
            yield None

patch_provider = Provider()

class Adapter:
    def run(self, case, work_dir=None):
        request(Path(work_dir) / "sandbox" / "patched.txt")
        return CaseRunResult(output=case.output, after=case.after)
""",
        encoding="utf-8",
    )
    case = make_case("patch-case")
    plan = load_effect_provider_plan(
        spec_dir=spec_dir,
        mapping_path=mapping_path,
        cases=[case],
        import_roots=[tmp_path],
    )
    declarations = load_effect_declarations(
        {
            "effects": {
                "components": {
                    "Fixture": {
                        "ports": {
                            "patched_request": {
                                "type": "filesystem.write",
                                "target": "**/sandbox/patched.txt",
                            }
                        }
                    }
                },
                "actions": {"Publish": ["patched_request"]},
            }
        }
    )
    report_path = tmp_path / "patch-report.json"

    execute_cases_in_batch(
        cases=[case],
        mappings={
            "Publish": AdapterMapping(
                "Publish",
                "patch_effect_fixture:Adapter",
                kind="publisher",
            )
        },
        work_dir=tmp_path / "work",
        import_roots=[tmp_path],
        declarations=declarations,
        effect_report_path=report_path,
        effect_provider_plan=plan,
    )

    import patch_effect_fixture

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["ok"] is True
    assert report["gaps"] == []
    # One crossing; see the crossings-not-records note above.
    assert len({(e["type"], e["target"]) for e in report["observed_effects"]}) == 1
    with pytest.raises(AssertionError, match="provider patch was not installed"):
        patch_effect_fixture.request(tmp_path / "after-cleanup.txt")


def effect_context(tmp_path: Path) -> EffectProviderContext:
    return EffectProviderContext(
        port_name="FilesystemPort",
        action="Publish",
        case=make_case("helper case"),
        work_dir=tmp_path,
        iteration=4,
        root_seed=8,
        derived_seed=9,
        seed_version="tla-spec-dev/effect-seed/v1",
    )


def test_repository_provider_uses_only_the_standard_context_manager_contract(
    tmp_path: Path,
) -> None:
    entered: list[int] = []
    exited: list[int] = []

    @contextmanager
    def binding(context: EffectProviderContext):
        entered.append(context.derived_seed)
        try:
            yield {"representative": context.derived_seed}
        finally:
            exited.append(context.derived_seed)

    class Provider:
        def bind(self, context: EffectProviderContext):
            return binding(context)

    provider = Provider()
    first = provider.bind(effect_context(tmp_path))
    second = provider.bind(effect_context(tmp_path))
    assert entered == []

    with first as value:
        assert value == {"representative": 9}
        assert entered == [9]
        assert exited == []

    with second:
        assert entered == [9, 9]

    assert exited == [9, 9]


def write_phase_fixture(tmp_path: Path) -> None:
    sys.modules.pop("fuzz_phase_fixture", None)
    (tmp_path / "fuzz_phase_fixture.py").write_text(
        """from spec_double_compiler.runtime import CaseRunResult

FAIL_PHASE = None
FAIL_CASE = None
EVENTS = []


class Binding:
    def write(self, value: str) -> None:
        pass

    def request(self) -> str:
        return "ok"


class Scope:
    def __init__(self, context):
        self.context = context

    def __enter__(self):
        if FAIL_PHASE == "enter" and self.context.port_name == "FilesystemPort":
            raise RuntimeError("enter failed")
        if FAIL_PHASE == "invalid_binding" and self.context.port_name == "FilesystemPort":
            return object()
        return Binding()

    def __exit__(self, exc_type, exc, traceback):
        if FAIL_PHASE == "exit:" + self.context.port_name:
            raise RuntimeError("exit failed for " + self.context.port_name)
        return False


class Provider:
    def bind(self, context):
        EVENTS.append(("bind", context.case.name, context.port_name))
        if (
            FAIL_PHASE == "bind"
            and context.port_name == "FilesystemPort"
            and (FAIL_CASE is None or context.case.name == FAIL_CASE)
        ):
            raise RuntimeError("bind failed")
        return Scope(context)


filesystem_provider = Provider()
patch_provider = Provider()


class Adapter:
    def __init__(self):
        if FAIL_PHASE == "adapter_instantiate":
            raise RuntimeError("adapter instantiate failed")

    def setup_all(self, context):
        EVENTS.append(("setup_all", tuple(case.name for case in context.cases)))
        if FAIL_PHASE == "setup_all":
            raise RuntimeError("setup_all failed")

    def setup(self, context):
        EVENTS.append(("setup", context.case.name))
        if FAIL_PHASE == "setup":
            raise RuntimeError("setup failed")

    def run(self, case, work_dir=None):
        EVENTS.append(("run", case.name))
        if FAIL_PHASE == "run":
            raise RuntimeError("run failed")
        output = {"ok": False} if FAIL_PHASE == "output_assert" else case.output
        return CaseRunResult(output=output, after=case.after)

    def teardown(self, context):
        if FAIL_PHASE == "teardown":
            raise RuntimeError("teardown failed")

    def teardown_all(self, context):
        EVENTS.append(("teardown_all", tuple(case.name for case in context.cases)))
        if FAIL_PHASE == "teardown_all":
            raise RuntimeError("teardown_all failed")


class Projector:
    def observe(self, context):
        return {"state": 0}
""",
        encoding="utf-8",
    )


def structured_failures(message: str) -> list[dict[str, Any]]:
    prefix = "EFFECT_FUZZ_FAILURE "
    return [json.loads(line[len(prefix) :]) for line in message.splitlines() if line.startswith(prefix)]


def test_later_point_bind_failure_prevents_every_application_hook(tmp_path: Path) -> None:
    write_phase_fixture(tmp_path)
    spec_dir, mapping_path = write_contract(
        tmp_path,
        module="fuzz_phase_fixture",
        provider_tables="""[effect_providers.FilesystemPort]
provider = "fuzz_phase_fixture:filesystem_provider"

[effect_providers.PatchPort]
provider = "fuzz_phase_fixture:patch_provider"
""",
    )
    cases = [make_case("first"), make_case("later")]
    plan = load_effect_provider_plan(
        spec_dir=spec_dir,
        mapping_path=mapping_path,
        cases=cases,
        import_roots=[tmp_path],
    )
    import fuzz_phase_fixture as fixture

    fixture.FAIL_PHASE = "bind"
    fixture.FAIL_CASE = "later"
    with pytest.raises(SystemExit) as raised:
        execute_cases_in_batch(
            cases=cases,
            mappings={
                "Publish": AdapterMapping(
                    "Publish",
                    "fuzz_phase_fixture:Adapter",
                    kind="publisher",
                )
            },
            work_dir=tmp_path / "work",
            import_roots=[tmp_path],
            effect_provider_plan=plan,
            replay_command_factory=lambda point: f"runner --case {point.case.name}",
        )

    diagnostic = next(item for item in structured_failures(str(raised.value)) if item["phase"] == "bind")
    assert diagnostic["case"] == "later"
    assert all(event[0] == "bind" for event in fixture.EVENTS)


@pytest.mark.parametrize(
    ("failure", "expected_phase", "specific_port"),
    [
        ("bind", "bind", "FilesystemPort"),
        ("adapter_load", "adapter_load", None),
        ("adapter_instantiate", "adapter_instantiate", None),
        ("output_projection_load", "output_projection_load", None),
        ("setup_all", "setup_all", None),
        ("enter", "enter", "FilesystemPort"),
        ("invalid_binding", "invalid_binding", "FilesystemPort"),
        ("setup", "setup", None),
        ("run", "run", None),
        ("output_assert", "output_assert", None),
        ("projected_assert", "projected_assert", None),
        ("teardown", "teardown", None),
        ("teardown_all", "teardown_all", None),
        ("exit:PatchPort", "exit", "PatchPort"),
        ("exit:FilesystemPort", "exit", "FilesystemPort"),
    ],
)
def test_failure_diagnostics_attribute_every_phase(
    tmp_path: Path,
    failure: str,
    expected_phase: str,
    specific_port: str | None,
) -> None:
    write_phase_fixture(tmp_path)
    spec_dir, mapping_path = write_contract(
        tmp_path,
        module="fuzz_phase_fixture",
        provider_tables="""[effect_providers.FilesystemPort]
provider = "fuzz_phase_fixture:filesystem_provider"

[effect_providers.PatchPort]
provider = "fuzz_phase_fixture:patch_provider"
""",
    )
    case = make_case("phase case", view="external" if failure == "projected_assert" else "internal")
    plan = load_effect_provider_plan(
        spec_dir=spec_dir,
        mapping_path=mapping_path,
        cases=[case],
        import_roots=[tmp_path],
    )
    import fuzz_phase_fixture as fixture

    fixture.FAIL_PHASE = failure
    adapter_reference = (
        "missing_effect_adapter:Adapter"
        if failure == "adapter_load"
        else "fuzz_phase_fixture:Adapter"
    )
    mapping = AdapterMapping(
        "Publish",
        adapter_reference,
        output_projection=(
            "missing_effect_projection:project"
            if failure == "output_projection_load"
            else None
        ),
        kind="publisher",
        projector="fuzz_phase_fixture:Projector" if failure == "projected_assert" else None,
    )
    with pytest.raises(SystemExit) as raised:
        execute_cases_in_batch(
            cases=[case],
            mappings={"Publish": mapping},
            work_dir=tmp_path / "work",
            import_roots=[tmp_path],
            effect_provider_plan=plan,
            fuzz_runs=8,
            root_seed=123,
            fuzz_iteration=5,
            replay_command_factory=lambda point: (
                f"{sys.executable} /absolute/runner.py --case {shlex.quote(point.case.name)} "
                f"--seed 123 --fuzz-iteration {point.iteration}"
            ),
        )

    failures = structured_failures(str(raised.value))
    diagnostic = next(item for item in failures if item["phase"] == expected_phase)
    assert diagnostic["case"] == "phase case"
    assert diagnostic["iteration"] == 5
    assert diagnostic["root_seed"] == 123
    assert diagnostic["seed_version"] == "tla-spec-dev/effect-seed/v1"
    assert diagnostic["replay"].startswith(sys.executable)
    assert [provider["port"] for provider in diagnostic["providers"]] == ["FilesystemPort", "PatchPort"]
    assert all(isinstance(provider["derived_seed"], int) for provider in diagnostic["providers"])
    if specific_port is None:
        assert "provider" not in diagnostic
    else:
        assert diagnostic["provider"]["port"] == specific_port


def write_case_package(package: Path, names: list[str]) -> None:
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("from .cases import CASES\n", encoding="utf-8")
    (package / "cases.py").write_text(
        """from dataclasses import dataclass

@dataclass(frozen=True)
class Input:
    action: str

@dataclass(frozen=True)
class Case:
    name: str
    before: dict
    input: Input
    output: dict
    after: dict
    labels: frozenset
    view: str = "internal"
    controllability: str = "unit_direct"
    generates: frozenset = frozenset({"spec_unit"})

CASES = [
"""
        + "\n".join(
            f"    Case({name!r}, {{}}, Input('Publish'), {{'ok': True}}, {{}}, frozenset({{'Publish'}})),"
            for name in names
        )
        + "\n]\n",
        encoding="utf-8",
    )


@pytest.mark.parametrize("failure_phase", ["run", "setup_all", "teardown_all"])
def test_cli_reexec_and_absolute_shell_safe_replay_run_exactly_one_point(
    tmp_path: Path,
    failure_phase: str,
) -> None:
    project = tmp_path / "project with spaces [and] quotes"
    environment = tmp_path / "dependency environment"
    venv.EnvBuilder(with_pip=False).create(environment)
    environment_python = environment / "bin" / "python"
    site_packages_result = subprocess.run(
        [
            str(environment_python),
            "-c",
            "import site; print(site.getsitepackages()[0])",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    site_packages = Path(site_packages_result.stdout.strip())
    (site_packages / "effect_replay_dependency.py").write_text(
        'TOKEN = "dependency-bearing-environment"\n',
        encoding="utf-8",
    )
    spec_dir = project / "spec files"
    cases_dir = project / "case package"
    spec_dir.mkdir(parents=True)
    weird_case = "case $dollar 'quote' [x]"
    write_case_package(cases_dir, ["ordinary case", weird_case])

    generated = spec_dir / "generated" / "replay_contract"
    generated.mkdir(parents=True)
    (generated / "__init__.py").write_text("", encoding="utf-8")
    (generated / "ports.py").write_text(
        """from typing import Protocol, runtime_checkable
@runtime_checkable
class FilesystemPort(Protocol):
    def write(self, value: str) -> None: ...
""",
        encoding="utf-8",
    )
    (spec_dir / "spec_manifest.yaml").write_text(
        """module: Replay
package: replay_contract
ports:
  FilesystemPort:
    role: effect
    methods:
      write:
        result: None
""",
        encoding="utf-8",
    )
    (spec_dir / "actions.yml").write_text(
        """actions:
  Publish:
    layer: internal
    effect_ports: [FilesystemPort]
""",
        encoding="utf-8",
    )
    event_log = project / "events with spaces.jsonl"
    (project / "replay_provider.py").write_text(
        f"""import hashlib
import json
import os
from pathlib import Path
import random
import effect_replay_dependency
from spec_double_compiler.runtime import CaseRunResult

assert effect_replay_dependency.TOKEN == "dependency-bearing-environment"
ACTIVE = None
LOG = Path(os.environ["EFFECT_REPLAY_EVENT_LOG"])
FAIL_PHASE = os.environ["EFFECT_REPLAY_FAILURE_PHASE"]

def record(event, scope, batch_cases=None):
    payload = {{
        "event": event,
        "case": scope.context.case.name,
        "iteration": scope.context.iteration,
        "choice": scope.choice,
        "response": scope.response,
        "transcript_digest": scope.transcript_digest,
    }}
    if batch_cases is not None:
        payload["batch_cases"] = list(batch_cases)
    with LOG.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(payload, sort_keys=True) + "\\n")

def record_hook(event, context):
    payload = {{
        "event": event,
        "case": context.cases[0].name,
        "iteration": context.iteration,
        "batch_cases": [case.name for case in context.cases],
    }}
    with LOG.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(payload, sort_keys=True) + "\\n")

class Binding:
    def __init__(self, scope):
        self.scope = scope

    def write(self, value: str) -> None:
        record("effect", self.scope)

class Scope:
    def __init__(self, context):
        self.context = context
        rng = random.Random(context.derived_seed)
        self.choice = f"artifact-{{rng.randrange(1_000_000)}}.json"
        self.response = {{
            "status": rng.choice(["accepted", "stored", "committed"]),
            "token": rng.getrandbits(48),
        }}
        transcript = json.dumps(
            {{
                "case": context.case.name,
                "iteration": context.iteration,
                "derived_seed": context.derived_seed,
                "choice": self.choice,
                "response": self.response,
            }},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.transcript_digest = hashlib.sha256(transcript).hexdigest()

    def __enter__(self):
        global ACTIVE
        ACTIVE = self
        record("enter", self)
        return Binding(self)

    def __exit__(self, exc_type, exc, traceback):
        global ACTIVE
        record("exit", self)
        ACTIVE = None
        return False

class Provider:
    def bind(self, context):
        scope = Scope(context)
        record("bind", scope)
        return scope

filesystem_provider = Provider()

def should_fail(scope, phase):
    return (
        FAIL_PHASE == phase
        and scope.context.iteration == 2
        and scope.context.case.name == {weird_case!r}
    )

def hook_should_fail(context, phase):
    return (
        FAIL_PHASE == phase
        and context.iteration == 2
        and context.cases[0].name == {weird_case!r}
    )

class Adapter:
    def setup_all(self, context):
        record_hook("setup_all", context)
        if hook_should_fail(context, "setup_all"):
            raise RuntimeError("deterministic setup_all replay failure")

    def setup(self, context):
        self.binding = context.effects["FilesystemPort"]
        record("setup", ACTIVE)

    def run(self, case, work_dir=None):
        record("run", ACTIVE)
        self.binding.write(case.name)
        if should_fail(ACTIVE, "run"):
            raise RuntimeError("deterministic run replay failure")
        return CaseRunResult(output=case.output, after=case.after)

    def teardown(self, context):
        record("teardown", ACTIVE)

    def teardown_all(self, context):
        record_hook("teardown_all", context)
        if hook_should_fail(context, "teardown_all"):
            raise RuntimeError("deterministic teardown_all replay failure")
""",
        encoding="utf-8",
    )
    mapping = project / "mapping with spaces.toml"
    mapping.write_text(
        """[adapters.Publish]
adapter = "replay_provider:Adapter"

[effect_providers.FilesystemPort]
provider = "replay_provider:filesystem_provider"
""",
        encoding="utf-8",
    )

    command = [
        str(environment_python),
        str(ROOT / "scripts" / "run_generated_case_adapters.py"),
        str(cases_dir),
        "--mapping",
        str(mapping),
        "--spec-dir",
        str(spec_dir),
        "--import-root",
        str(project),
        "--batch",
        "--fuzz-runs",
        "3",
        "--seed",
        "444",
        "--python",
        str(environment_python),
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(ROOT), env.get("PYTHONPATH", "")]
    ).rstrip(os.pathsep)
    env["EFFECT_REPLAY_EVENT_LOG"] = str(event_log)
    env["EFFECT_REPLAY_FAILURE_PHASE"] = failure_phase

    def run_campaign() -> tuple[subprocess.CompletedProcess[str], list[dict[str, Any]], list[dict[str, Any]]]:
        if event_log.exists():
            event_log.unlink()
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        events = [json.loads(line) for line in event_log.read_text(encoding="utf-8").splitlines()]
        diagnostics = structured_failures(completed.stdout + completed.stderr)
        return completed, events, diagnostics

    campaign, first_events, first_diagnostics = run_campaign()
    repeated, repeated_events, repeated_diagnostics = run_campaign()

    assert campaign.returncode != 0
    assert repeated.returncode != 0
    failure = next(item for item in first_diagnostics if item["phase"] == failure_phase)
    repeated_failure = next(item for item in repeated_diagnostics if item["phase"] == failure_phase)
    assert repeated_failure == failure
    assert repeated_events == first_events
    assert failure["case"] == weird_case
    assert failure["iteration"] == 2
    assert failure["root_seed"] == 444
    replay = failure["replay"]
    replay_argv = shlex.split(replay)
    assert replay_argv[0] == str(environment_python)
    assert Path(replay_argv[0]).is_absolute()
    assert Path(replay_argv[1]).is_absolute()
    assert replay_argv[replay_argv.index("--case") + 1] == weird_case
    assert replay_argv[replay_argv.index("--fuzz-iteration") + 1] == "2"

    failing_events = [
        event
        for event in first_events
        if event["case"] == weird_case and event["iteration"] == 2
    ]
    concrete_transcript = {
        (
            event["choice"],
            json.dumps(event["response"], sort_keys=True),
            event["transcript_digest"],
        )
        for event in failing_events
        if "choice" in event
    }
    assert len(concrete_transcript) == 1

    event_log.unlink()
    replayed = subprocess.run(replay_argv, cwd=tmp_path, env=env, text=True, capture_output=True, check=False)
    assert replayed.returncode != 0
    replay_events = [json.loads(line) for line in event_log.read_text(encoding="utf-8").splitlines()]
    assert replay_events == failing_events
    assert {event["case"] for event in replay_events} == {weird_case}
    assert {event["iteration"] for event in replay_events} == {2}


def test_tla_spec_dev_forwards_fuzz_and_replay_flags_to_case_runner(tmp_path: Path, monkeypatch: Any) -> None:
    from scripts import tla_spec_dev

    current = tmp_path / "specs" / "current"
    current.mkdir(parents=True)
    (current / "case_adapters.toml").write_text(
        '[adapters.Publish]\nadapter = "provider:Adapter"\n',
        encoding="utf-8",
    )
    cases_dir = tmp_path / "cases"
    write_case_package(cases_dir, ["selected"])
    commands: list[list[str]] = []

    def fake_run(command: list[str], **_kwargs: Any) -> SimpleNamespace:
        commands.append(command)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(tla_spec_dev.subprocess, "run", fake_run)
    args = SimpleNamespace(
        repo_root=tmp_path,
        spec_root="specs",
        target=None,
        scope="project",
        ticket=None,
        tests_dir=None,
        cases_dir=[str(cases_dir)],
        mapping=None,
        work_dir=None,
        label=[],
        case=["selected"],
        limit=None,
        validate_only=False,
        validate_capabilities=False,
        no_batch=False,
        pytest_arg=["-q"],
        fuzz_runs=9,
        seed=2468,
        fuzz_iteration=7,
    )

    assert tla_spec_dev.run_spec_unit_tests(args) == 0
    adapter_command = next(command for command in commands if "run_generated_case_adapters.py" in command[1])
    assert adapter_command[adapter_command.index("--fuzz-runs") + 1] == "9"
    assert adapter_command[adapter_command.index("--seed") + 1] == "2468"
    assert adapter_command[adapter_command.index("--fuzz-iteration") + 1] == "7"
    assert adapter_command[adapter_command.index("--case") + 1] == "selected"


def test_cli_scaffolded_project_selects_a_custom_project_provider_without_framework_edits(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "tla_spec_dev.py"),
            "--spec-root",
            "specs",
            "scaffold",
            "project",
            "--name",
            "CliProject",
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    program_model = tmp_path / "specs" / "program_model"
    providers_path = program_model / "providers.py"
    assert providers_path.is_file()
    providers_path.write_text(
        """from contextlib import contextmanager

class Binding:
    def ping(self):
        return "pong"

class Provider:
    @contextmanager
    def bind(self, context):
        yield Binding()

custom_provider = Provider()
""",
        encoding="utf-8",
    )

    actions_path = program_model / "actions.yml"
    actions = actions_path.read_text(encoding="utf-8")
    original_actions = actions
    actions = actions.replace(
        "  RegisterActor:\n    layer: internal\n    controllability: unit_direct\n    generates:\n      - spec_unit\n    effect_ports: []",
        "  RegisterActor:\n    layer: internal\n    controllability: unit_direct\n    generates:\n      - spec_unit\n    effect_ports: [ExampleEffectPort]",
        1,
    )
    assert actions != original_actions, "scaffold must make effect_ports explicit on RegisterActor"
    actions_path.write_text(actions, encoding="utf-8")
    manifest_path = program_model / "spec_manifest.yaml"
    manifest = manifest_path.read_text(encoding="utf-8").replace(
        "ports:\n",
        """ports:
  ExampleEffectPort:
    role: effect
    methods:
      ping:
        result: str
""",
        1,
    )
    manifest_path.write_text(manifest, encoding="utf-8")
    with (program_model / "case_adapters.toml").open("a", encoding="utf-8") as stream:
        stream.write(
            """
[effect_providers.ExampleEffectPort]
provider = "specs.program_model.providers:custom_provider"
"""
        )

    generated = program_model / "generated" / "cliproject_program_cases"
    generated.mkdir(parents=True)
    (generated / "__init__.py").write_text("", encoding="utf-8")
    (generated / "ports.py").write_text(
        """from typing import Protocol, runtime_checkable
@runtime_checkable
class ExampleEffectPort(Protocol):
    def ping(self) -> str: ...
""",
        encoding="utf-8",
    )
    case = make_case("cli scaffold", action="RegisterActor")
    plan = load_effect_provider_plan(
        spec_dir=program_model,
        mapping_path=program_model / "case_adapters.toml",
        cases=[case],
        import_roots=[tmp_path],
    )

    resolved = plan.for_case(case)
    assert [binding.port_name for binding in resolved] == ["ExampleEffectPort"]
    assert resolved[0].provider_reference == "specs.program_model.providers:custom_provider"


def test_effect_provider_docs_state_the_unvalidated_boundary_honestly() -> None:
    reference = (ROOT / "references" / "effect_providers.md").read_text(encoding="utf-8")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")

    for text in (
        "The framework ships one effect extension point",
        "TLA+ selects the semantic outcome",
        "repository provider owns concrete representatives",
        "Callable-only factories are not providers",
        "effect_provider_usage.yaml",
        "does not ship domain implementations",
        "exact replay",
        "EP-03",
        "twelve concrete gaps",
        "not a reusable provider library",
        "Python-native",
    ):
        assert text in reference
    assert "references/effect_providers.md" in skill
