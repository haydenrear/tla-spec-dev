#!/usr/bin/env python3
"""MF-026 re-verification at 0a05eed: do the two NEW kill mutants apply and revert?

Non-destructive. Reads each mutant's `find`/`replace` out of kill_mutants.toml
and checks, in memory:
  * the `find` string occurs in the named file,
  * it occurs EXACTLY once (an ambiguous seed patches an arbitrary site),
  * `replace` differs from `find`,
  * applying then reversing the substitution restores the original file byte for
    byte -- which is what "reverts" means for the shipped `seeded()` finally
    branch at kill_test.py:548/551.

Also cross-checks every port mutant against the manifest's `justification`
table, which `analyze complexity` reads to flag unlinked model elements.

Usage: python3 reverify_mutants.py <repo_root>
"""
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
NEW = {"port-case_work_dir_delete", "port-case_program_process"}


def main() -> int:
    ok = True
    for tree in ("current", "program_model", "desired_program_model"):
        cat = tomllib.loads((ROOT / "specs" / tree / "kill_mutants.toml").read_text(encoding="utf-8"))
        mutants = cat["mutants"]
        print(f"\n=== specs/{tree}/kill_mutants.toml -- {len(mutants)} mutants ===")
        for m in mutants:
            if m["id"] not in NEW:
                continue
            path = ROOT / m["path"]
            text = path.read_text(encoding="utf-8")
            find, repl = m["find"], m["replace"]
            n = text.count(find)
            applied = text.replace(find, repl, 1) if n else text
            reverted = applied.replace(repl, find, 1) if n else text
            line = text[: text.index(find)].count("\n") + 1 if n else None
            print(f"  {m['id']}")
            print(f"    path            {m['path']}")
            print(f"    find occurrences {n}   {'OK' if n == 1 else 'PROBLEM'}"
                  + (f"   (line {line})" if line else ""))
            print(f"    replace differs  {repl != find}")
            print(f"    applies          {applied != text if n else False}")
            print(f"    reverts byte-for-byte {reverted == text if n else False}")
            print(f"    refine_variable  {m.get('refine_variable')!r}   refine_action {m.get('refine_action')!r}")
            if n != 1 or applied == text or reverted != text:
                ok = False

    # Every port mutant vs the manifest justification table.
    man = (ROOT / "specs" / "current" / "spec_manifest.yaml").read_text(encoding="utf-8")
    just = man[man.index("\njustification:"):]
    cat = tomllib.loads((ROOT / "specs" / "current" / "kill_mutants.toml").read_text(encoding="utf-8"))
    port_mutants = sorted(m["id"] for m in cat["mutants"] if m.get("boundary_kind") == "port")
    print(f"\n=== port mutants vs specs/current/spec_manifest.yaml `justification` ===")
    linked, unlinked = [], []
    for mid in port_mutants:
        (linked if re.search(rf"\b{re.escape(mid)}\b", just) else unlinked).append(mid)
    print(f"  linked in a variable's kill_tests ({len(linked)}): {linked}")
    print(f"  NOT linked ({len(unlinked)}): {unlinked}")

    # Declared ports vs mutant coverage.
    ports = re.findall(r"^        ([a-z_]+):\n\s+type:", man, re.M)
    print(f"\n=== declared ports ({len(ports)}) vs port mutants ({len(port_mutants)}) ===")
    missing = [p for p in ports if f"port-{p}" not in port_mutants]
    print(f"  ports with no seeded mutant: {missing or 'NONE'}")
    print(f"\nRESULT: {'all new mutants apply and revert cleanly' if ok else 'PROBLEM -- see above'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
