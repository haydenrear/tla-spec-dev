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
WORK_DIRS = []
CASE_OBJECT_IDS = []
ADAPTERS = []


class Binding:
    def write(self, value):
        pass

    def request(self):
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

    # One adapter/shared cache per iteration; provider scopes, effect maps and
    # case work directories are fresh for every point.
    assert len(fixture.ADAPTERS) == 2
    assert len(fixture.SHARED_MAPS) == 2
    assert fixture.SHARED_MAPS[0] is not fixture.SHARED_MAPS[1]
    assert len(fixture.SCOPES) == 8
    assert len({id(scope) for scope in fixture.SCOPES}) == 8
    assert len(fixture.EFFECT_MAPS) == 4
    assert len({id(effects) for effects in fixture.EFFECT_MAPS}) == 4
    assert len(fixture.WORK_DIRS) == 4
    assert len(set(fixture.WORK_DIRS)) == 4
    assert all("iteration-" in str(path) for path in fixture.WORK_DIRS)
    assert fixture.CASE_OBJECT_IDS == [id(cases[0]), id(cases[1]), id(cases[0]), id(cases[1])]


def test_seed_only_campaign_uses_an_iteration_qualified_work_path(tmp_path: Path) -> None:
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
        tmp_path / "work" / "case-work" / "seed-only" / "iteration-000000"
    ]


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


def test_temporary_root_provider_is_lazy_fresh_and_cleans_builder_failures(tmp_path: Path) -> None:
    from spec_double_compiler.effects import temporary_root_provider

    built: list[Path] = []

    class Value:
        def __init__(self, root: Path):
            self.root = root

    def builder(root: Path, _context: EffectProviderContext) -> Value:
        built.append(root)
        return Value(root)

    provider = temporary_root_provider(builder)
    first_binding = provider.bind(effect_context(tmp_path))
    second_binding = provider.bind(effect_context(tmp_path))
    assert built == []

    with first_binding as first:
        assert first.root.is_dir()
    assert not first.root.exists()

    with second_binding as second:
        assert second.root.is_dir()
        assert second.root != first.root
    assert not second.root.exists()

    failed_roots: list[Path] = []

    def failing_builder(root: Path, _context: EffectProviderContext) -> Any:
        failed_roots.append(root)
        raise RuntimeError("builder failed")

    failing_binding = temporary_root_provider(failing_builder).bind(effect_context(tmp_path))
    with pytest.raises(RuntimeError, match="builder failed"):
        failing_binding.__enter__()
    assert failed_roots and not failed_roots[0].exists()


def test_context_provider_acquires_lazily_restores_partial_nesting_and_never_suppresses(tmp_path: Path) -> None:
    from spec_double_compiler.effects import context_provider

    active: list[str] = []
    installs: list[int] = []

    @contextmanager
    def marked(name: str, *, fail: bool = False):
        active.append(name)
        try:
            if fail:
                raise RuntimeError(f"{name} enter failed")
            yield name
        finally:
            active.remove(name)

    def partial_installer(_context: EffectProviderContext, stack: Any) -> None:
        installs.append(1)
        stack.enter_context(marked("outer"))
        stack.enter_context(marked("inner", fail=True))

    provider = context_provider(partial_installer)
    binding = provider.bind(effect_context(tmp_path))
    assert installs == []
    with pytest.raises(RuntimeError, match="inner enter failed"):
        binding.__enter__()
    assert installs == [1]
    assert active == []

    class Suppressor:
        def __enter__(self) -> None:
            active.append("suppressor")

        def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> bool:
            active.remove("suppressor")
            return True

    def suppressing_installer(_context: EffectProviderContext, stack: Any) -> None:
        installs.append(2)
        stack.enter_context(Suppressor())

    suppressing_provider = context_provider(suppressing_installer)
    first = suppressing_provider.bind(effect_context(tmp_path))
    second = suppressing_provider.bind(effect_context(tmp_path))
    assert installs == [1]
    with pytest.raises(ValueError, match="primary"):
        with first:
            raise ValueError("primary")
    with second:
        assert active == ["suppressor"]
    assert installs == [1, 2, 2]
    assert active == []


def write_phase_fixture(tmp_path: Path) -> None:
    sys.modules.pop("fuzz_phase_fixture", None)
    (tmp_path / "fuzz_phase_fixture.py").write_text(
        """from spec_double_compiler.runtime import CaseRunResult

FAIL_PHASE = None


class Binding:
    def write(self, value):
        pass

    def request(self):
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
        if FAIL_PHASE == "bind" and context.port_name == "FilesystemPort":
            raise RuntimeError("bind failed")
        return Scope(context)


filesystem_provider = Provider()
patch_provider = Provider()


class Adapter:
    def setup(self, context):
        if FAIL_PHASE == "setup":
            raise RuntimeError("setup failed")

    def run(self, case, work_dir=None):
        if FAIL_PHASE == "run":
            raise RuntimeError("run failed")
        output = {"ok": False} if FAIL_PHASE == "output_assert" else case.output
        return CaseRunResult(output=output, after=case.after)

    def teardown(self, context):
        if FAIL_PHASE == "teardown":
            raise RuntimeError("teardown failed")


class Projector:
    def observe(self, context):
        return {"state": 0}
""",
        encoding="utf-8",
    )


def structured_failures(message: str) -> list[dict[str, Any]]:
    prefix = "EFFECT_FUZZ_FAILURE "
    return [json.loads(line[len(prefix) :]) for line in message.splitlines() if line.startswith(prefix)]


@pytest.mark.parametrize(
    ("failure", "expected_phase", "specific_port"),
    [
        ("bind", "bind", "FilesystemPort"),
        ("enter", "enter", "FilesystemPort"),
        ("invalid_binding", "invalid_binding", "FilesystemPort"),
        ("setup", "setup", None),
        ("run", "run", None),
        ("output_assert", "output_assert", None),
        ("projected_assert", "projected_assert", None),
        ("teardown", "teardown", None),
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
    mapping = AdapterMapping(
        "Publish",
        "fuzz_phase_fixture:Adapter",
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


def test_cli_reexec_and_absolute_shell_safe_replay_run_exactly_one_point(tmp_path: Path) -> None:
    project = tmp_path / "project with spaces [and] quotes"
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
        f"""import json
import os
from pathlib import Path
from spec_double_compiler.runtime import CaseRunResult

ACTIVE = None
LOG = Path(os.environ["EFFECT_REPLAY_EVENT_LOG"])

def record(event, context):
    with LOG.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({{"event": event, "case": context.case.name, "iteration": context.iteration}}) + "\\n")

class Binding:
    def write(self, value):
        pass

class Scope:
    def __init__(self, context):
        self.context = context

    def __enter__(self):
        global ACTIVE
        ACTIVE = self.context
        record("enter", self.context)
        return Binding()

    def __exit__(self, exc_type, exc, traceback):
        global ACTIVE
        record("exit", self.context)
        ACTIVE = None
        return False

class Provider:
    def bind(self, context):
        record("bind", context)
        return Scope(context)

filesystem_provider = Provider()

class Adapter:
    def setup(self, context):
        record("setup", ACTIVE)

    def run(self, case, work_dir=None):
        record("run", ACTIVE)
        if ACTIVE.iteration == 2 and case.name == {weird_case!r}:
            raise RuntimeError("deterministic replay failure")
        return CaseRunResult(output=case.output, after=case.after)

    def teardown(self, context):
        record("teardown", ACTIVE)
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
        sys.executable,
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
        sys.executable,
    ]
    env = os.environ.copy()
    env["EFFECT_REPLAY_EVENT_LOG"] = str(event_log)
    campaign = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True, check=False)

    assert campaign.returncode != 0
    diagnostics = structured_failures(campaign.stdout + campaign.stderr)
    failure = next(item for item in diagnostics if item["phase"] == "run")
    assert failure["case"] == weird_case
    assert failure["iteration"] == 2
    assert failure["root_seed"] == 444
    replay = failure["replay"]
    replay_argv = shlex.split(replay)
    assert Path(replay_argv[0]).is_absolute()
    assert Path(replay_argv[1]).is_absolute()
    assert replay_argv[replay_argv.index("--case") + 1] == weird_case
    assert replay_argv[replay_argv.index("--fuzz-iteration") + 1] == "2"

    event_log.unlink()
    replayed = subprocess.run(replay_argv, cwd=tmp_path, env=env, text=True, capture_output=True, check=False)
    assert replayed.returncode != 0
    replay_events = [json.loads(line) for line in event_log.read_text(encoding="utf-8").splitlines()]
    assert [event["event"] for event in replay_events] == [
        "bind",
        "enter",
        "setup",
        "run",
        "teardown",
        "exit",
    ]
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

@contextmanager
def custom_provider(context):
    yield Binding()
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
        "TLA+ selects the semantic outcome",
        "provider owns the concrete representatives",
        "MF-038",
        "0/9",
        "EP-03",
        "not yet validated",
        "universal interception",
        "Hypothesis shrinking",
        "provider-module globals",
    ):
        assert text in reference
    assert "references/effect_providers.md" in skill
