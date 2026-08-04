#!/usr/bin/env python3
"""`tla-spec-dev run effect-conformance` (MF-013).

The standalone reporting command. It resolves the spec directory, loads the
declared effect surface, executes the mapped adapters in the sandbox when a
generated case corpus is present, diffs observed against declared, writes the
report as ticket evidence, and exits nonzero on any finding.

Corresponds to the ``RunEffectConformance`` action in TlaSpecDevCli.tla. The
ENFORCING copy of the same measurement runs inside ``run spec-unit-tests``,
because a gate you have to remember to invoke is not a gate; this command
exists so the diff can be produced and inspected on its own.

Exit codes: 0 clean, 1 gaps, dead model surface, or an unobservable target,
2 malformed declarations. No flag changes that mapping.

MF-027: this command observes the in-process CPython runtime only. A target it
cannot observe -- a JVM adapter, a JBang/uv Test Graph node, an adapter that
delegates to a child process -- exits 1 with an ``unobservable`` verdict. It
never reports clean on a target it could not see, and there is no flag here
that changes that.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from effect_conformance import (  # noqa: E402
    CorpusExecution,
    EffectDeclarationError,
    EffectRecorder,
    diff_effects,
    execute_corpus,
    load_effect_declarations,
)
from extract_spec_manifest import load_manifest  # noqa: E402


def resolve_spec_dir(args: argparse.Namespace) -> Path:
    if getattr(args, "target", None):
        return Path(args.target)
    spec_root = Path(getattr(args, "spec_root", None) or "specs")
    ticket = getattr(args, "ticket", None)
    if ticket:
        return spec_root / "tickets" / ticket / "current"
    return spec_root / "current"


def load_declarations_for(spec_dir: Path):
    """Read ``effects:`` from actions.yml, else spec_manifest.yaml."""
    for candidate in ("actions.yml", "spec_manifest.yaml"):
        path = spec_dir / candidate
        if not path.exists():
            continue
        data = load_manifest(path)
        if isinstance(data, dict) and data.get("effects"):
            return load_effect_declarations(data), path
    return load_effect_declarations(None), None


def run(args: argparse.Namespace) -> int:
    spec_dir = resolve_spec_dir(args)
    if not spec_dir.exists():
        print(f"ERROR: spec directory not found: {spec_dir}", file=sys.stderr)
        return 2

    try:
        declarations, source = load_declarations_for(spec_dir)
    except EffectDeclarationError as exc:
        print(f"ERROR: malformed effect declarations: {exc}", file=sys.stderr)
        return 2

    if not declarations.ports:
        print(
            f"ERROR: no effect declarations found in {spec_dir}. "
            "Declare effects.components.<component>.ports and effects.actions "
            "in actions.yml or spec_manifest.yaml.",
            file=sys.stderr,
        )
        return 2

    print(f"effect declarations: {len(declarations.ports)} port(s) from {source}")

    recorder = EffectRecorder()
    execution = CorpusExecution()
    ran_corpus = False

    cases_dirs = [Path(d) for d in (getattr(args, "cases_dir", None) or [])]
    if cases_dirs:
        ran_corpus = True
        execution = _execute_corpus(args, spec_dir, cases_dirs, recorder)

    report = diff_effects(
        declarations,
        recorder.effects,
        cases=execution.cases,
        unobservable=recorder.unobservable,
        skipped=recorder.skipped,
        offered_actions=execution.offered_actions,
        executed_actions=execution.executed_actions,
        work_dir=str(execution.work_dir) if execution.work_dir else "",
        work_dir_reset=ran_corpus,
    )

    if getattr(args, "out", None):
        written = report.write(Path(args.out))
        print(f"wrote evidence: {written}")

    if getattr(args, "format", "text") == "json":
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        print(report.render())

    if not ran_corpus:
        # Be explicit rather than implying a clean bill of health from an
        # empty observation set. With no corpus every declared port is
        # trivially unexercised, so the dead-surface finding below is a
        # statement about THIS INVOCATION, not about the program.
        print(
            "\nNOTE: no --cases-dir supplied, so no adapter was executed and nothing was "
            "observed. The dead-surface finding above reflects an empty observation set. "
            "Supply --cases-dir to diff against a real corpus."
        )

    return 0 if report.ok else 1


def _execute_corpus(
    args: argparse.Namespace,
    spec_dir: Path,
    cases_dirs: list[Path],
    recorder: EffectRecorder,
) -> CorpusExecution:
    """Resolve this invocation's paths and hand the loop to the oracle.

    HP-04 moved the loop itself into ``effect_conformance.execute_corpus``. The
    three defects it carried -- no ``sys.path`` for the target project
    (RC-02-DF-02), an abort on the first ``apply()``-only adapter
    (RC-02-DF-03), and a work directory that survived between runs
    (MF026-R4-F-01) -- were all defects of the loop, and leaving it in the CLI
    shim is what let them be invisible to four rounds of reading the oracle's
    own module.
    """
    mapping_path = Path(getattr(args, "mapping", None) or spec_dir / "case_adapters.toml")
    work_dir = Path(getattr(args, "work_dir", None) or spec_dir / ".effect-conformance-work")
    return execute_corpus(
        spec_dir=spec_dir,
        cases_dirs=cases_dirs,
        mapping_path=mapping_path,
        work_dir=work_dir,
        recorder=recorder,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-root", default="specs")
    parser.add_argument("--ticket")
    parser.add_argument("--target", type=Path)
    parser.add_argument("--cases-dir", action="append")
    parser.add_argument("--mapping", type=Path)
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    return run(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
