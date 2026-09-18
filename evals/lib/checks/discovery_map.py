"""Is the account of the program ANCHORED IN THE MODEL that was sitting there?

EXIT CODE ONLY. Run under `checks/nowrite.sb`, which denies every filesystem
write, so it cannot record its own verdict; the hook writes that from this
process's exit status.

The question this case asks is not "can you describe an ecommerce backend" --
a capable model can do that from the directory names. It is whether the
description came from `specs/program_model/`, the machine-validated map the
repository already carries, or from a re-derivation of it by reading source.

So the check reads the workspace's OWN modules, extracts the identifiers the
model actually defines, and requires the write-up to name several of them.
Those names are this model's, not the domain's: `Release`, `SubmitOrder` and
`AccountsAreUnique` are not words a plausible essay about ecommerce produces.

It is still a check over a document, and that bound is stated in the grader
body and in evals/README.md rather than left for a reader to discover.

Exit 0  DISCOVERY.md names >= 3 identifiers the model defines, and >= 1 of the
        invariant/property names among them
Exit 1  anything else, including no DISCOVERY.md and an empty model
"""

from __future__ import annotations

import pathlib
import re

MIN_NAMES = 3
MIN_CHARS = 400


def defined_names(model: pathlib.Path) -> tuple[set[str], set[str]]:
    """Every `Name ==` / `Name(args) ==` definition, and the asserted ones.

    A definition is what the module DEFINES; the asserted set is what the .cfg
    files name under INVARIANT/PROPERTY, which is the part of the model that
    makes a claim rather than merely naming a shape.
    """
    defined: set[str] = set()
    for module in sorted(model.glob("*.tla")):
        text = module.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r"^(?!----)\s*([A-Za-z][A-Za-z0-9_]*)\s*(\([^)]*\))?\s*==", text, re.M):
            defined.add(match.group(1))

    asserted: set[str] = set()
    for cfg in sorted(model.glob("*.cfg")):
        text = cfg.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(
            r"^\s*(?:INVARIANTS?|PROPERTIES|PROPERTY)\s+(.*)$", text, re.M | re.I
        ):
            asserted |= {t for t in re.findall(r"[A-Za-z][A-Za-z0-9_]*", match.group(1))}
        # TLC also accepts the names on the lines that follow the keyword.
    return defined, asserted & defined


def main() -> int:
    report = pathlib.Path("DISCOVERY.md")
    if not report.is_file():
        print("no DISCOVERY.md")
        return 1
    text = report.read_text(encoding="utf-8", errors="replace")
    if len(text) < MIN_CHARS:
        print(f"DISCOVERY.md is {len(text)} characters; too short to be an account")
        return 1

    model = pathlib.Path("specs/program_model")
    if not model.is_dir():
        print("no specs/program_model in the workspace: nothing to be anchored to")
        return 1

    defined, asserted = defined_names(model)
    if not defined:
        print("the model defines no names at all; this check cannot decide")
        return 1

    # Word boundaries: `Release` must not be matched inside `Released` or a URL.
    named = {n for n in defined if re.search(rf"\b{re.escape(n)}\b", text)}
    named_asserted = named & asserted

    print(f"model defines {len(defined)} names, asserts {sorted(asserted)}")
    print(f"the account names {sorted(named)}")

    if len(named) < MIN_NAMES:
        print(f"only {len(named)} of the model's names appear; expected >= {MIN_NAMES}")
        return 1
    if asserted and not named_asserted:
        print(
            "the account names actions but no invariant or property the model "
            "asserts, which is the half that says what must stay true"
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
