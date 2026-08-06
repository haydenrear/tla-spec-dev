"""HP-05: content assertion is the default, and the alternative is loud.

The measured claim this file guards: content-asserting effect providers caught
2 of 6 seeded faults nothing else caught, reproduced across two rounds, and a
blind agent replicated the split at 3 of 3 durable-write mutants under the
checking mapping against 0 of 3 under the silent one. Before this ticket the
scaffold shipped a `raise NotImplementedError` provider stub and a COMMENTED
OUT binding, so 30% of the instrument's yield depended on an author writing an
assertion nobody asked them for.

These tests assert the DEFAULT and the ANNOUNCEMENT. None of them asserts that
anything refuses: `no_new_gates_rule` -- a run that names its mapping is a
report, a run that will not proceed without one is a gate.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.extract_spec_manifest import load_manifest
from scripts.generate_python import (
    ANNOUNCE_PREFIX,
    NO_ORACLE_SENTENCE,
    bind_default_providers,
    effect_ports,
    generate,
    mapping_audit,
    port_content_spec,
)

ROOT = Path(__file__).resolve().parents[1]

MODULE_TLA = """\
---- MODULE Ledger ----
EXTENDS Naturals

VARIABLES committed, ledger

Commit == committed' = committed
====
"""

MANIFEST = """\
module: Ledger
package: ledger_contract

types:
  Tenant:
    python: str

state:
  LedgerState:
    fields:
      committed:
        type: dict

commands:
  AppendLine:
    fields:
      tenant:
        type: Tenant
      total:
        type: int

results:
  AppendResult:
    fields:
      path:
        type: str

ports:
  LedgerAppendPort:
    role: effect
    kind: durable_write
    methods:
      append:
        command: AppendLine
        result: str
    content:
      append:
        total: "committed[tenant]"
"""

#: The same port declared the way the passive `effects:` observer reads it, and
#: the way HP-01's A/B fixture actually declares it: no methods, so no Protocol,
#: so no provider can be bound. A boundary nobody can bind is exactly the case
#: the audit exists to be loud about.
MANIFEST_UNBINDABLE_BOUNDARY = MANIFEST.replace(
    """\
ports:
  LedgerAppendPort:
    role: effect
    kind: durable_write
    methods:
      append:
        command: AppendLine
        result: str
    content:
      append:
        total: "committed[tenant]"
""",
    """\
ports:
  ReadPort:
    role: query
    methods:
      read:
        command: AppendLine
        result: str

effects:
  components:
    ledger:
      ports:
        LedgerAppendPort:
          kind: durable_write
          asserts_content: true
  actions:
    Commit: [LedgerAppendPort]
""",
)


def write_spec(tmp_path: Path, manifest_text: str = MANIFEST) -> Path:
    spec_dir = tmp_path / "spec"
    spec_dir.mkdir()
    (spec_dir / "Ledger.tla").write_text(MODULE_TLA, encoding="utf-8")
    manifest_path = spec_dir / "spec_manifest.yaml"
    manifest_path.write_text(manifest_text, encoding="utf-8")
    return manifest_path


def load_generated(tmp_path: Path, package_dir: Path):
    sys.path.insert(0, str(package_dir.parent))
    try:
        import importlib

        for name in list(sys.modules):
            if name.startswith(package_dir.name):
                del sys.modules[name]
        return importlib.import_module(f"{package_dir.name}.effect_providers")
    finally:
        sys.path.remove(str(package_dir.parent))


class _Case:
    def __init__(self, after: dict, name: str = "case_0001_commit") -> None:
        self.after = after
        self.name = name


class _Context:
    def __init__(self, case: _Case) -> None:
        self.case = case
        self.action = "Commit"
        self.port_name = "LedgerAppendPort"


# --- the default -----------------------------------------------------------


def test_codegen_emits_a_provider_module_for_every_semantic_effect_port(tmp_path: Path) -> None:
    manifest_path = write_spec(tmp_path)
    package_dir = generate(manifest_path, tmp_path / "out")

    module = load_generated(tmp_path, package_dir)

    assert module.DEFAULT_PROVIDERS == {
        "LedgerAppendPort": "ledger_contract.effect_providers:ledger_append_port_provider"
    }
    assert module.ledger_append_port_provider.asserts_content is True
    assert module.silent_ledger_append_port_provider.asserts_content is False


def test_the_default_provider_asserts_content_and_the_silent_one_does_not(tmp_path: Path) -> None:
    """The 30% cell. Same crossing, same case, two providers, two verdicts."""
    manifest_path = write_spec(tmp_path)
    package_dir = generate(manifest_path, tmp_path / "out")
    module = load_generated(tmp_path, package_dir)
    types = sys.modules[f"{package_dir.name}.types"]

    # The in-memory model says the running total is 2; the durable write says 1.
    # This is M04's shape exactly: nothing but the bytes is wrong.
    case = _Case(after={"committed": {"t1": 2}})
    context = _Context(case)

    with pytest.raises(AssertionError) as failure:
        with module.ledger_append_port_provider.bind(context) as port:
            port.append(types.AppendLine(tenant="t1", total=1))
    assert "DETECTOR[provider_content_assertion]" in str(failure.value)
    assert "committed[tenant]" in str(failure.value)

    # The silent provider sees the identical crossing and says nothing.
    with module.silent_ledger_append_port_provider.bind(context) as port:
        port.append(types.AppendLine(tenant="t1", total=1))


def test_the_default_provider_passes_a_write_that_agrees_with_the_model(tmp_path: Path) -> None:
    manifest_path = write_spec(tmp_path)
    package_dir = generate(manifest_path, tmp_path / "out")
    module = load_generated(tmp_path, package_dir)
    types = sys.modules[f"{package_dir.name}.types"]

    context = _Context(_Case(after={"committed": {"t1": 2}}))
    with module.ledger_append_port_provider.bind(context) as port:
        port.append(types.AppendLine(tenant="t1", total=2))


def test_codegen_binds_the_content_asserting_provider_with_nobody_configuring_it(
    tmp_path: Path,
) -> None:
    manifest_path = write_spec(tmp_path)
    mapping = manifest_path.parent / "case_adapters.toml"
    mapping.write_text(
        '[adapters.Commit]\nadapter = "adapters:CommitAdapter"\nkind = "internal"\n',
        encoding="utf-8",
    )
    generate(manifest_path, tmp_path / "out")

    bound = bind_default_providers(load_manifest(manifest_path), mapping)

    assert bound == ["LedgerAppendPort"]
    text = mapping.read_text(encoding="utf-8")
    assert "[effect_providers.LedgerAppendPort]" in text
    assert 'provider = "ledger_contract.effect_providers:ledger_append_port_provider"' in text
    # Additive only: it never touches what somebody else wrote.
    assert '[adapters.Commit]\nadapter = "adapters:CommitAdapter"' in text


def test_binding_defaults_is_idempotent_and_never_overwrites_a_deliberate_choice(
    tmp_path: Path,
) -> None:
    manifest_path = write_spec(tmp_path)
    mapping = manifest_path.parent / "case_adapters.toml"
    mapping.write_text(
        "[effect_providers.LedgerAppendPort]\n"
        'provider = "ledger_contract.effect_providers:silent_ledger_append_port_provider"\n',
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_path)

    assert bind_default_providers(manifest, mapping) == []
    assert "silent_ledger_append_port_provider" in mapping.read_text(encoding="utf-8")
    assert bind_default_providers(manifest, mapping) == []


# --- the announcement ------------------------------------------------------


def test_a_run_under_the_default_mapping_names_it_unprompted(tmp_path: Path) -> None:
    manifest_path = write_spec(tmp_path)
    package_dir = generate(manifest_path, tmp_path / "out")
    module = load_generated(tmp_path, package_dir)
    types = sys.modules[f"{package_dir.name}.types"]

    lines = module.describe_binding(
        "LedgerAppendPort",
        "ledger_contract.effect_providers:ContentAssertingLedgerAppendPortProvider",
        "specs/program_model/case_adapters.toml",
        asserts_content=True,
    )

    assert len(lines) == 1
    assert "DURABLE-WRITE ORACLE ACTIVE" in lines[0]
    assert "specs/program_model/case_adapters.toml" in lines[0]
    assert "append.total == committed[tenant]" in lines[0]
    assert types is not None


def test_a_run_with_no_durable_write_oracle_says_so_in_its_output(tmp_path: Path, capsys) -> None:
    """Assertion 3, and it must be in the RUN, not only in documentation."""
    manifest_path = write_spec(tmp_path)
    package_dir = generate(manifest_path, tmp_path / "out")
    module = load_generated(tmp_path, package_dir)
    types = sys.modules[f"{package_dir.name}.types"]

    context = _Context(_Case(after={"committed": {"t1": 2}}))
    with module.silent_ledger_append_port_provider.bind(context) as port:
        port.append(types.AppendLine(tenant="t1", total=1))

    printed = capsys.readouterr().out
    assert "NO DURABLE-WRITE ORACLE" in printed
    assert NO_ORACLE_SENTENCE in printed
    assert "FLOOR" in printed


def test_a_port_with_no_content_declaration_announces_that_it_checks_nothing(
    tmp_path: Path,
) -> None:
    manifest_path = write_spec(tmp_path, MANIFEST.replace(
        '    content:\n      append:\n        total: "committed[tenant]"\n', ""
    ))
    package_dir = generate(manifest_path, tmp_path / "out")
    module = load_generated(tmp_path, package_dir)

    lines = module.describe_binding(
        "LedgerAppendPort", "pkg:Provider", "m.toml", asserts_content=True
    )

    assert "NO DURABLE-WRITE ORACLE" in lines[0]
    assert "declares no `content:` block" in lines[0]


def test_the_announcement_is_advisory_and_does_not_refuse(tmp_path: Path, capsys) -> None:
    """`no_new_gates_rule`: a silent mapping is loud, and it still runs."""
    manifest_path = write_spec(tmp_path)
    package_dir = generate(manifest_path, tmp_path / "out")
    module = load_generated(tmp_path, package_dir)
    types = sys.modules[f"{package_dir.name}.types"]

    with module.silent_ledger_append_port_provider.bind(_Context(_Case(after={}))) as port:
        result = port.append(types.AppendLine(tenant="t1", total=99))

    assert result == ""
    assert "NO DURABLE-WRITE ORACLE" in capsys.readouterr().out


# --- the audit -------------------------------------------------------------


def test_the_audit_reports_an_unbound_effect_port(tmp_path: Path) -> None:
    manifest_path = write_spec(tmp_path)
    mapping = manifest_path.parent / "case_adapters.toml"
    mapping.write_text('[adapters.Commit]\nadapter = "a:B"\n', encoding="utf-8")

    report = mapping_audit(load_manifest(manifest_path), mapping)

    assert any("binds no provider to it" in line for line in report)
    assert all(line.startswith(ANNOUNCE_PREFIX) for line in report)


def test_the_audit_reports_a_declared_boundary_no_provider_can_reach(tmp_path: Path) -> None:
    """HP-01's fixture shape: `effects:` says durable_write, and nothing can bind it."""
    manifest_path = write_spec(tmp_path, MANIFEST_UNBINDABLE_BOUNDARY)
    mapping = manifest_path.parent / "case_adapters.toml"
    mapping.write_text('[adapters.Commit]\nadapter = "a:B"\n', encoding="utf-8")

    report = mapping_audit(load_manifest(manifest_path), mapping)

    assert any(
        "LedgerAppendPort" in line and "no provider can be bound to it" in line for line in report
    )


def test_the_audit_names_the_active_oracle_and_what_it_compares(tmp_path: Path) -> None:
    manifest_path = write_spec(tmp_path)
    mapping = manifest_path.parent / "case_adapters.toml"
    mapping.write_text("", encoding="utf-8")
    bind_default_providers(load_manifest(manifest_path), mapping)

    report = mapping_audit(load_manifest(manifest_path), mapping)

    assert any(
        "DURABLE-WRITE ORACLE ACTIVE" in line and "append.total == committed[tenant]" in line
        for line in report
    )


def test_the_cli_prints_the_audit_unprompted(tmp_path: Path) -> None:
    manifest_path = write_spec(tmp_path)
    (manifest_path.parent / "case_adapters.toml").write_text("", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "generate_python.py"),
            str(manifest_path),
            "--out",
            str(tmp_path / "out"),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "DURABLE-WRITE ORACLE ACTIVE" in completed.stdout
    assert "bound LedgerAppendPort to its generated content-asserting provider" in completed.stdout


# --- the declaration -------------------------------------------------------


def test_content_spec_reads_the_manifest_declaration(tmp_path: Path) -> None:
    manifest = load_manifest(write_spec(tmp_path))
    port = effect_ports(manifest)["LedgerAppendPort"]

    assert port_content_spec(port) == {"append": {"total": "committed[tenant]"}}


def test_a_project_with_no_effect_ports_gets_no_provider_module(tmp_path: Path) -> None:
    manifest_path = write_spec(
        tmp_path, MANIFEST.replace("    role: effect\n", "    role: query\n")
    )
    package_dir = generate(manifest_path, tmp_path / "out")

    assert not (package_dir / "effect_providers.py").exists()
