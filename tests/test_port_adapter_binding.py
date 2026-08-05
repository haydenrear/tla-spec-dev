"""PA-04: an adapter binds to a declared PORT, and the fake/real swap is an instrument.

Every test here checks BEHAVIOUR, using the shipped builders, so a rename fails
a test instead of silently orphaning the binding. The plan's
``declaration_executability_rule`` exists because five declarations in five
consecutive attempts by three authors drifted from the code they described, in
both directions, plus a test for the class that passed vacuously by reading the
wrong key -- so nothing below asserts that a string appears in a file.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from generate_cases_from_tlc_dump import PortDeclaration, load_port_catalog  # noqa: E402
from run_generated_case_adapters import (  # noqa: E402
    adapter_for_case,
    apply_wiring,
    load_mappings,
    port_bindings,
    port_case_label,
    render_oracle_statement,
    render_port_binding_report,
    EffectProviderPlan,
)

AB_MANIFEST = REPO_ROOT / "examples/validation/ab/model/spec_manifest.yaml"
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


# -- the label, from the shipped builder ------------------------------------


def test_the_port_label_a_binding_resolves_is_the_one_the_generator_emits():
    """The binding and the corpus must agree on the label, by construction.

    Not `assert port_case_label(x) == "port:" + x`. That would pass while the
    generator moved to a different prefix, which is the exact drift the rule is
    about. The right-hand side here is produced by the generator's own
    declaration type.
    """
    declaration = PortDeclaration(
        component="ledger", name="LedgerAppendPort", attributes={}, actions=()
    )
    assert port_case_label(PORT) == declaration.label


def test_the_label_resolves_for_every_port_the_shipped_builder_reads():
    catalogue = load_port_catalog(AB_MANIFEST)
    assert catalogue.ports, "the A/B manifest declares at least one port"
    for port in catalogue.ports:
        assert port_case_label(port.qualified) == port.label


@pytest.mark.parametrize("bad", ["LedgerAppendPort", "", "ledger.", ".Port"])
def test_a_port_binding_must_name_a_qualified_port(bad):
    with pytest.raises(ValueError, match="Component.Name"):
        port_case_label(bad)


# -- the binding is READ, not inferred --------------------------------------


def test_a_ports_table_binds_the_generated_port_case(tmp_path):
    mapping = _write(tmp_path, f'''
        [ports."{PORT}"]
        adapter = "m:Real"
        fake = "m:Fake"
    ''')
    mappings = load_mappings(mapping)
    bound = port_bindings(mappings)
    assert bound[PORT].adapter == "m:Real"
    assert bound[PORT].fake == "m:Fake"
    assert bound[PORT].binds == "port"
    assert bound[PORT].label == port_case_label(PORT)

    case = _Case("case_0001_commit__port_ledger_ledgerappendport",
                 frozenset({"Commit", port_case_label(PORT), "port-expect:emitted"}))
    assert adapter_for_case(case, mappings).port == PORT


def test_a_port_binding_wins_over_an_action_binding_however_the_file_is_ordered(tmp_path):
    """The precedence is declared, not positional.

    Before PA-04 `adapter_for_case` broke a tie on insertion order, so which of
    two matching bindings drove a port case depended on which table a human had
    typed first. A port case carries BOTH labels, so that ordering silently
    decided every result in this ticket.
    """
    action_first = _write(tmp_path, f'''
        [[adapter]]
        labels = ["Commit"]
        adapter = "m:Action"

        [ports."{PORT}"]
        adapter = "m:Port"
    ''', "action_first.toml")
    port_first = _write(tmp_path, f'''
        [ports."{PORT}"]
        adapter = "m:Port"

        [[adapter]]
        labels = ["Commit"]
        adapter = "m:Action"
    ''', "port_first.toml")
    case = _Case("c", frozenset({"Commit", port_case_label(PORT)}))
    for path in (action_first, port_first):
        chosen = adapter_for_case(case, load_mappings(path))
        assert chosen.adapter == "m:Port", path.name
        assert chosen.binds == "port"


def test_a_case_with_no_port_label_still_binds_to_its_action(tmp_path):
    mapping = _write(tmp_path, f'''
        [ports."{PORT}"]
        adapter = "m:Port"

        [[adapter]]
        labels = ["Commit"]
        adapter = "m:Action"
    ''')
    case = _Case("c", frozenset({"Commit"}))
    assert adapter_for_case(case, load_mappings(mapping)).adapter == "m:Action"


def test_the_fallback_toml_parser_reads_a_ports_table_too(tmp_path):
    """The no-tomllib path is only reachable on Python < 3.11 and still ships.

    A table header added to `load_mappings` alone passes on this machine and
    raises `unsupported TOML line` there.
    """
    from run_generated_case_adapters import parse_simple_mapping_toml

    loaded = parse_simple_mapping_toml(f'[ports."{PORT}"]\nadapter = "m:Real"\nfake = "m:Fake"\n')
    assert loaded["ports"][PORT] == {"adapter": "m:Real", "fake": "m:Fake"}


# -- the swap ----------------------------------------------------------------


def test_wiring_fake_swaps_the_adapter_and_leaves_everything_else_alone(tmp_path):
    mapping = _write(tmp_path, f'''
        [ports."{PORT}"]
        adapter = "m:Real"
        fake = "m:Fake"

        [[adapter]]
        labels = ["Commit"]
        adapter = "m:Action"
    ''')
    mappings = load_mappings(mapping)
    real, real_notes = apply_wiring(mappings, "real")
    fake, fake_notes = apply_wiring(mappings, "fake")

    assert port_bindings(real)[PORT].adapter == "m:Real"
    assert port_bindings(fake)[PORT].adapter == "m:Fake"
    # The fake side still remembers what it stands in for.
    assert port_bindings(fake)[PORT].fake == "m:Fake"
    # An action binding is untouched by a wiring choice.
    assert real["Commit"].adapter == fake["Commit"].adapter == "m:Action"
    assert real_notes == []
    assert any("wiring=fake" in note for note in fake_notes)


def test_a_port_with_no_fake_is_reported_and_never_refused(tmp_path):
    """no_new_gates_rule. A codebase with one implementation is a fact.

    This is arm A: a flat module, no declared port, nothing for a swap to swap.
    Refusing here would make `--wiring fake` a gate on how a codebase is shaped.
    """
    mapping = _write(tmp_path, f'''
        [ports."{PORT}"]
        adapter = "m:Real"
    ''')
    mappings, notes = apply_wiring(load_mappings(mapping), "fake")
    assert port_bindings(mappings)[PORT].adapter == "m:Real"
    assert any("NO FAKE DECLARED" in note for note in notes)


# -- the run says what it carries, every run ---------------------------------


def test_every_run_states_the_oracles_it_does_not_carry(tmp_path):
    mapping = _write(tmp_path, '''
        [[adapter]]
        labels = ["Commit"]
        adapter = "m:Action"
    ''')
    statement = render_oracle_statement(
        mappings=load_mappings(mapping), plan=_empty_plan(), wiring="real", wiring_notes=[],
    )
    assert "ORACLES CARRIED BY THIS MAPPING:" in statement
    assert "ORACLES **NOT** CARRIED:" in statement
    # HP-04 printed this only when providers were configured, so the runs
    # carrying the FEWEST oracles were the ones that said nothing.
    assert "NO DURABLE-WRITE ORACLE" in statement
    assert "mutation-kill-test: never carried by this runner" in statement
    assert 'no [ports."Component.Name"] binding' in statement


def test_a_swap_run_names_the_side_it_ran_and_refuses_to_speak_for_the_other(tmp_path):
    mapping = _write(tmp_path, f'''
        [ports."{PORT}"]
        adapter = "m:Real"
        fake = "m:Fake"
    ''')
    mappings, notes = apply_wiring(load_mappings(mapping), "fake")
    statement = render_oracle_statement(
        mappings=mappings, plan=_empty_plan(), wiring="fake", wiring_notes=notes,
    )
    assert "THIS RUN USED THE FAKE SIDE" in statement
    assert "must be read beside its opposite wiring or not at all" in statement


# -- the declaration is checked against the manifest, both directions --------


def test_a_bound_port_the_manifest_declares_is_reported_as_declared(tmp_path):
    mapping = _write(tmp_path, f'''
        [ports."{PORT}"]
        adapter = "m:Real"
        fake = "m:Fake"
    ''')
    report = "\n".join(
        render_port_binding_report(load_mappings(mapping), load_port_catalog(AB_MANIFEST), mapping)
    )
    assert f"{PORT} [declared]" in report
    assert "DECLARED BUT NOT BOUND" not in report
    assert "BOUND BUT NOT DECLARED" not in report


def test_renaming_the_port_in_the_manifest_orphans_the_binding_and_is_reported(tmp_path):
    """THE DRIFT TEST. A declaration nothing executes will drift.

    The manifest is copied and the port renamed -- exactly what a refactor does
    -- and the run must say, in the same output, that a bound port is no longer
    declared AND that a declared port is not bound. Neither is a refusal.
    """
    renamed = tmp_path / "spec_manifest.yaml"
    renamed.write_text(
        AB_MANIFEST.read_text(encoding="utf-8").replace("LedgerAppendPort", "JournalWritePort"),
        encoding="utf-8",
    )
    mapping = _write(tmp_path, f'''
        [ports."{PORT}"]
        adapter = "m:Real"
    ''')
    report = "\n".join(
        render_port_binding_report(load_mappings(mapping), load_port_catalog(renamed), mapping)
    )
    assert f"{PORT} [NOT DECLARED by the manifest]" in report
    assert "DECLARED BUT NOT BOUND: ledger.JournalWritePort" in report
    assert f"BOUND BUT NOT DECLARED: {PORT}" in report


def test_the_binding_report_names_the_real_adapter_even_on_a_fake_run(tmp_path):
    """Found by RUNNING it, not by reading it.

    The first version of this reported the POST-SWAP mapping, so a `--wiring
    fake` run printed `real=...FakeJournalAdapter fake=...FakeJournalAdapter` --
    a run stating its own instrument incorrectly, which is the one thing this
    output exists to prevent. The report reads the mapping AS DECLARED.
    """
    mapping = _write(tmp_path, f'''
        [ports."{PORT}"]
        adapter = "m:Real"
        fake = "m:Fake"
    ''')
    declared = load_mappings(mapping)
    swapped, _ = apply_wiring(declared, "fake")
    assert port_bindings(swapped)[PORT].adapter == "m:Fake"
    report = "\n".join(
        render_port_binding_report(declared, load_port_catalog(AB_MANIFEST), mapping)
    )
    assert "real=m:Real fake=m:Fake" in report


# -- a fault on either side of the port dies ---------------------------------


_PORT_PAIR = '''\
class _Journal:
    def __init__(self):
        self._lines = []

    def append(self, line):
        self._lines.append(line)

    def lines(self):
        return [entry for entry in self._lines if entry]


class RealJournal(_Journal):
{real_body}


class FakeJournal(_Journal):
{fake_body}


class _Adapter:
    journal = RealJournal

    def can_run(self, case):
        return True

    def run(self, case, work_dir=None):
        journal = self.journal()
        for line in case.before["ledger"]:
            journal.append(line)
        journal.append(case.input.params["line"])
        return {{"after": {{"ledger": tuple(journal.lines())}}}}


class RealAdapter(_Adapter):
    journal = RealJournal


class FakeAdapter(_Adapter):
    journal = FakeJournal
'''

#: Both PA-M11 and PA-M12 are the SAME semantic -- "the read-back hides every
#: CLOSE line" -- seeded on opposite sides of one port. That is the whole design
#: of the catalogue pair: PA-M11 proves the fault is trivially visible, so
#: PA-M12's survival cannot be explained by the fault being subtle.
_UNMUTATED = "    pass"
_DROP_CLOSE = (
    "    def lines(self):\n"
    "        return [e for e in self._lines if e and not e.startswith('CLOSE')]"
)


def _pair_module(tmp_path: Path, real_body: str, fake_body: str) -> Path:
    path = tmp_path / "port_pair.py"
    path.write_text(
        _PORT_PAIR.format(real_body=real_body, fake_body=fake_body), encoding="utf-8"
    )
    # A mutant that does not apply scores as a survivor, which is how a broken
    # harness reads as a clean result. Prove the substitution landed.
    source = path.read_text(encoding="utf-8")
    assert source.count("startswith('CLOSE')") == (
        (real_body == _DROP_CLOSE) + (fake_body == _DROP_CLOSE)
    ), "the seeded fault did not land in the module under test"
    return path

_RUNNER = '''
import sys
sys.path.insert(0, {scripts!r})
sys.path.insert(0, {tmp!r})
from run_generated_case_adapters import adapter_for_case, apply_wiring, load_mappings

class Input:
    action = "CloseTenant"
    params = {{"line": "CLOSE acme 3"}}

class Case:
    name = "c"
    labels = frozenset({{"CloseTenant", {label!r}}})
    before = {{"ledger": ["COMMIT acme 3 3"]}}
    input = Input()
    after = {{"ledger": ("COMMIT acme 3 3", "CLOSE acme 3")}}

mappings, _ = apply_wiring(load_mappings(__import__("pathlib").Path({mapping!r})), {wiring!r})
mapping = adapter_for_case(Case(), mappings)
module, _, name = mapping.adapter.partition(":")
adapter = getattr(__import__(module), name)()
result = adapter.run(Case())
assert result["after"]["ledger"] == Case.after["ledger"], (
    f"port assertion failed: {{result['after']['ledger']}} != {{Case.after['ledger']}}"
)
print("OK")
'''


def _swap_verdict(tmp_path: Path, mapping: Path, wiring: str) -> str:
    """KILLED when the identical case list fails through this wiring."""
    script = tmp_path / f"drive_{wiring}.py"
    script.write_text(
        _RUNNER.format(
            scripts=str(REPO_ROOT / "scripts"), tmp=str(tmp_path), mapping=str(mapping),
            wiring=wiring, label=port_case_label(PORT),
        ),
        encoding="utf-8",
    )
    done = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    return "SURVIVED" if done.returncode == 0 else "KILLED"


@pytest.mark.parametrize(
    "real_body, fake_body, expected_real, expected_fake, why",
    [
        (_UNMUTATED, _UNMUTATED, "SURVIVED", "SURVIVED",
         "the control: unmutated code must pass BOTH wirings"),
        (_DROP_CLOSE, _UNMUTATED, "KILLED", "SURVIVED",
         "PA-M11's semantic: the fault is in the REAL adapter"),
        (_UNMUTATED, _DROP_CLOSE, "SURVIVED", "KILLED",
         "PA-M12's semantic: the fault is in the FAKE adapter"),
    ],
)
def test_a_fault_on_either_side_of_the_port_dies(
    tmp_path, real_body, fake_body, expected_real, expected_fake, why
):
    """THE TICKET, at unit scale, through the SHIPPED binder.

    `PA-M12` is `BA-B14` reproduced: a fault behind a port on the side no
    composition point wired. It survived five corpus instruments, the effect
    oracle and the hand-written suite for a whole epic -- not because it was
    subtle, but because nothing looked. Under one wiring one of these two rows
    is untouchable; the pair is what makes both reachable, and a run that
    reports only one side is reporting a floor.
    """
    _pair_module(tmp_path, real_body, fake_body)
    mapping = _write(tmp_path, f'''
        [ports."{PORT}"]
        adapter = "port_pair:RealAdapter"
        fake = "port_pair:FakeAdapter"
    ''')
    assert _swap_verdict(tmp_path, mapping, "real") == expected_real, why
    assert _swap_verdict(tmp_path, mapping, "fake") == expected_fake, why


def test_a_single_wiring_cannot_decide_both_sides(tmp_path):
    """State the floor as a test rather than as a sentence in a report.

    With only the real wiring available -- every mapping this project shipped
    before PA-04 -- the fake-side fault is not on the executed path and the
    column reads SURVIVED for a reason that is not about the fault.
    """
    _pair_module(tmp_path, _UNMUTATED, _DROP_CLOSE)
    mapping = _write(tmp_path, f'''
        [ports."{PORT}"]
        adapter = "port_pair:RealAdapter"
    ''')
    assert _swap_verdict(tmp_path, mapping, "real") == "SURVIVED"
    # And with no fake declared, asking for the fake side changes nothing.
    assert _swap_verdict(tmp_path, mapping, "fake") == "SURVIVED"
