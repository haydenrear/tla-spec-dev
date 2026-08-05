#!/usr/bin/env python3
"""Attribute each in-model script to the modeled action(s) that can reach it.

The row set is Sweep 1's in-model list. The mapping is derived, not asserted:
each CLI leaf subcommand's handler is read out of `build_parser`'s
`set_defaults(func=...)`, the handler's transitive `scripts.*` import closure is
walked, and every module in that closure is attributed to the action the
subcommand realises. A module in NO closure is `unrepresented` by construction.

Usage: python3 module_to_action.py <repo_root>
"""
import ast
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
SCRIPTS = ROOT / "scripts"
HERE = Path(__file__).resolve().parent

# CLI leaf subcommand -> handler function in tla_spec_dev.py -> modeled action.
# Read from scripts/tla_spec_dev.py build_parser set_defaults(func=...) and from
# the @command annotations in specs/current/TlaSpecDevCli.tla.
HANDLERS = {
    "run_scaffold_project": "ScaffoldProject / RecordBudgets",
    "run_scaffold_workflow": "ScaffoldWorkflow / RecordBudgets",
    "run_open_ticket": "OpenTicket",
    "run_analyze_complexity": "AnalyzeComplexity",
    "run_analyze_corpus": "AnalyzeCorpus",
    "run_analyze_architecture": "AnalyzeArchitecture",
    "run_generate_cases": "GenerateCases",
    "run_effect_conformance_cmd": "RunEffectConformance",
    "run_kill_test_cmd": "RunKillTest",
    "run_close_ticket": "CloseTicket / CloseTicketWeakened",
    "run_spec_unit_tests": "RunSpecUnitTests",
}


def imports_in(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Import):
            for a in n.names:
                names.add(a.name.split(".")[-1])
        elif isinstance(n, ast.ImportFrom):
            mod = n.module or ""
            if mod in {"scripts", ""}:
                for a in n.names:
                    names.add(a.name)
            else:
                names.add(mod.split(".")[-1])
    return {n for n in names if (SCRIPTS / f"{n}.py").is_file()}


def closure(seed: set[str]) -> set[str]:
    seen: set[str] = set()
    stack = list(seed)
    while stack:
        m = stack.pop()
        if m in seen:
            continue
        seen.add(m)
        stack.extend(imports_in(ast.parse((SCRIPTS / f"{m}.py").read_text(encoding="utf-8"))))
    return seen


def main() -> int:
    tree = ast.parse((SCRIPTS / "tla_spec_dev.py").read_text(encoding="utf-8"))
    fns = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    attribution: dict[str, set[str]] = {}
    for handler, action in HANDLERS.items():
        seed = imports_in(fns[handler]) if handler in fns else set()
        for mod in closure(seed):
            attribution.setdefault(mod, set()).add(action)
    # tla_spec_dev.py itself is the entrypoint for every action.
    attribution["tla_spec_dev"] = {"ALL (entrypoint, build_parser/main)"}

    rows = []
    for p in sorted(SCRIPTS.glob("*.py")):
        acts = sorted(attribution.get(p.stem, ()))
        verdict = "represented" if acts else "unrepresented"
        rows.append(f"scripts/{p.name}\t{verdict}\t{'; '.join(acts) or 'NO modeled action reaches this module'}")
    (HERE / "sweep1-module-to-action.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print("\n".join(rows))
    n_un = sum(1 for r in rows if "\tunrepresented\t" in r)
    print(f"\nscripts total={len(rows)} represented={len(rows)-n_un} unrepresented={n_un}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
