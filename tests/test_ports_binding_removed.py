"""SM-02: the `[ports.*]` binding machinery is GONE, and the corpus is NOT.

This file replaces `tests/test_port_adapter_binding.py`, which existed to prove
the machinery worked. It did work. It was measured, and what it bought was zero:

* zero unique kills across 28 tables, and absent from every blind-authored one;
* `suite-fake` -- four lines of `quota_ledger_fake.py`, no binding table, no
  wiring flag -- strictly dominates `corpus-port-swap:fake`;
* `SM-01`'s `SM-GM-P3` (the fake is silently a second REAL adapter) **survived
  all six of the machinery's own columns at 1543 executed cases each** while the
  positive control died on those same six in the same run. The swap cannot
  detect that its own fake is not a fake.

TWO CLAIMS, NOT ONE. Defunding `[ports.*]` is supported; defunding the CORPUS is
not, and the second half of this file exists so a later reader cannot quietly
widen the first into the second. The generated corpus reaches guard relaxation
0 -> 3 of 3, a class nothing else has ever reached, and per-port generation
reaches 83.2% executable against the whole-view corpus's 8.66%. `--port-cases`,
`PortDeclaration` and `load_port_catalog` are KEPT and asserted here.

NOT A GATE. Nothing below refuses anything at run time; these are regression
tests over the shape of the shipped API and the behaviour of the runner. The
epic's `no_new_gates_rule` is intact: SM-02 removed a mechanism and added no
refusal, and a mapping that still carries a `[ports.*]` table is IGNORED rather
than rejected. That silence is a residue of the cut and it is FILED as
`SM-02-DF-01`, not fixed here.
"""

from __future__ import annotations

import dataclasses
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "scripts/run_generated_case_adapters.py"
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import run_generated_case_adapters as runner_module  # noqa: E402
from run_generated_case_adapters import (  # noqa: E402
    AdapterMapping,
    EffectProviderPlan,
    adapter_for_case,
    load_mappings,
    parse_simple_mapping_toml,
    render_oracle_statement,
)

PORT = "ledger.LedgerAppendPort"


@dataclass(frozen=True)
class _Case:
    name: str
    labels: frozenset[str]


def _write(tmp_path: Path, body: str, name: str = "case_adapters.toml") -> Path:
    path = tmp_path / name
    path.write_text(textwrap.dedent(body), encoding="utf-8")
    return path


def _empty_plan() -> EffectProviderPlan:
    return EffectProviderPlan(by_case={})


# -- 1. the table no longer binds anything ----------------------------------


def test_a_ports_only_mapping_now_declares_no_binding_at_all(tmp_path):
    """The centrepiece of the ports-as-adapters epic, exercised as it was.

    Before SM-02 this produced exactly one binding, labelled `port:ledger.
    LedgerAppendPort`, and drove every generated port case. It now produces
    none, and the runner reports the mapping as empty through the error it has
    always had for an empty mapping -- no new refusal was written for this.
    """
    mapping = _write(tmp_path, f'''
        [ports."{PORT}"]
        adapter = "m:Real"
        fake = "m:Fake"
    ''')
    with pytest.raises(ValueError, match="no adapter mappings found"):
        load_mappings(mapping)


def test_a_port_case_binds_to_its_ACTION_now_that_the_port_table_is_gone(tmp_path):
    """A generated port case carries BOTH labels. The action one is what is left.

    This is the `corpus-action-bound` column of every table PA-04 ever printed --
    the pre-PA-04 world, restored on evidence. Before SM-02 the port table won
    this by an explicit precedence rule keyed on `mapping.binds`.
    """
    mapping = _write(tmp_path, f'''
        [actions.Commit]
        adapter = "m:Action"

        [ports."{PORT}"]
        adapter = "m:Real"
        fake = "m:Fake"
    ''')
    mappings = load_mappings(mapping)
    assert sorted(mappings) == ["Commit"]
    case = _Case(name="c0", labels=frozenset({"Commit", f"port:{PORT}"}))
    chosen = adapter_for_case(case, mappings)
    assert chosen is not None and chosen.adapter == "m:Action"


def test_the_fallback_toml_parser_no_longer_knows_what_a_ports_table_is(tmp_path):
    """The second reader had its own `[ports.` branch. Both are gone.

    Two parsers is how a mechanism half-survives a removal: `tomllib` is absent
    below Python 3.11 and this branch is what runs there.
    """
    with pytest.raises(ValueError):
        parse_simple_mapping_toml(f'[ports."{PORT}"]\nadapter = "m:Real"\n')
    assert "ports" not in parse_simple_mapping_toml(
        '[actions.Commit]\nadapter = "m:Action"\n'
    )


def test_a_binding_carries_no_port_no_fake_and_no_binds_discriminator():
    """The three fields the swap was built on, read off the shipped dataclass."""
    names = {field.name for field in dataclasses.fields(AdapterMapping)}
    assert not names & {"binds", "port", "fake"}
    # ...and the per-case programs the runner emits cannot mention them either,
    # since the template interpolates from this same object.
    assert "binds={mapping.binds!r}" not in RUNNER.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "name",
    ["apply_wiring", "port_bindings", "render_port_binding_report",
     "port_case_label", "load_declared_ports", "_port_declaration_type"],
)
def test_the_machinery_exports_nothing_a_caller_can_still_reach(name):
    assert not hasattr(runner_module, name)


# -- 2. the run no longer claims an oracle it does not carry -----------------


def test_the_oracle_statement_neither_carries_nor_misses_a_port_swap(tmp_path):
    """R2's shape, applied to the removal itself.

    A run that kept printing `port-fake-real-swap: no [ports."Component.Name"]
    binding in this mapping` would be advertising an oracle the toolchain can no
    longer carry under any mapping -- a standing invitation to go and configure
    it. The line is gone from BOTH halves, not moved from one to the other.
    """
    mapping = _write(tmp_path, '''
        [[adapter]]
        labels = ["Commit"]
        adapter = "m:Action"
    ''')
    statement = render_oracle_statement(
        mappings=load_mappings(mapping), plan=_empty_plan()
    )
    # what survives, unchanged -- HP-04's widening is kept
    assert "ORACLES CARRIED BY THIS MAPPING:" in statement
    assert "ORACLES **NOT** CARRIED:" in statement
    assert "NO DURABLE-WRITE ORACLE" in statement
    assert "mutation-kill-test: never carried by this runner" in statement
    # what went
    assert "port-fake-real-swap" not in statement
    assert 'no [ports."Component.Name"] binding' not in statement


def test_the_runner_has_no_wiring_flag_and_no_port_manifest_flag():
    """Both halves of PA-04's command line, checked by running it."""
    helped = subprocess.run(
        [sys.executable, str(RUNNER), "--help"],
        capture_output=True, text=True, check=True,
    )
    assert "--wiring" not in helped.stdout
    assert "--port-manifest" not in helped.stdout

    rejected = subprocess.run(
        [sys.executable, str(RUNNER), "cases", "--mapping", "m.toml", "--wiring", "fake"],
        capture_output=True, text=True,
    )
    assert rejected.returncode != 0
    assert "unrecognized arguments: --wiring" in rejected.stderr


# -- 3. THE CUT DID NOT WIDEN: the corpus is untouched ----------------------
#
# "Defund [ports.*]" is supported. "Defund the corpus" is NOT. Everything below
# is the second claim, asserted so it cannot be taken by drift.


def test_the_generator_still_declares_ports_and_still_builds_port_labels():
    from generate_cases_from_tlc_dump import PortDeclaration, load_port_catalog

    catalog = load_port_catalog(REPO_ROOT / "examples/validation/ab/model/spec_manifest.yaml")
    qualified = {port.qualified for port in catalog.ports}
    assert PORT in qualified, "the manifest's declared ports are corpus input, not binding input"

    declaration = PortDeclaration(component="ledger", name="LedgerAppendPort",
                                  attributes={}, actions=())
    assert declaration.label == f"port:{PORT}"


def test_the_port_corpus_generation_flag_survives_the_cut():
    """`--port-cases` reaches 83.2% executable against the whole view's 8.66%.

    It is generation, not binding, and SM-02 does not touch it.
    """
    helped = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts/generate_cases_from_tlc_dump.py"), "--help"],
        capture_output=True, text=True, check=True,
    )
    assert "--port-cases" in helped.stdout
    assert "--negative-cases" in helped.stdout, "the negative corpus owns guard relaxation 3 of 3"
