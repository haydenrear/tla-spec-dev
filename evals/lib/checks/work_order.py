"""Is the issue a WORK ORDER, or a wish? EXIT CODE ONLY.

Run under `checks/nowrite.sb`; the hook writes the verdict from the exit status.

`git-issue`'s whole claim is that an issue it produces can be picked up and
implemented without re-discovering the repository: it carries the discovery
already done, points the implementer at a worktree and branch, names the
measurable outcome and the instrument that decides it, decides whether a spec
workflow is needed, and lists what closes it out.

Those are five properties of a document, and each is mechanically detectable,
which is why this is a program and not a judge. What it CANNOT tell you is
whether the references are the right ones or the metric is a good metric -- it
reads structure, not quality. That bound is in the grader body too.

Exit 0  ISSUE.md carries all five
Exit 1  anything else
"""

from __future__ import annotations

import pathlib
import re

# A FLOOR AGAINST A STUB, NOT A LENGTH REQUIREMENT.
#
# This was 600, and a known-GOOD control fixture -- five well-formed sections,
# every property present, naming the program -- was 483 characters and got
# refused with "too short to be a work order". That is a false negative in the
# verifier, which is the direction that matters: it charges the agent for the
# checker's opinion about length.
#
# Found by running the verifier against a known-good and a known-bad workspace
# before trusting a score from it, which is the cheapest rule in the reference
# and the only reason this was caught before it billed a run rather than after.
#
# The five properties below plus the program-name check are what decide. This
# number now only excludes an empty file or a one-line token.
MIN_CHARS = 200

# Each property is a list of alternative spellings: an issue may say "measurable
# outcome" or "goal" or "metric", and pinning one wording would grade phrasing.
PROPERTIES = {
    "references the implementer starts from": [
        r"^#{1,4}\s*References\b",
        r"\bReferences\s*:",
    ],
    "a measurable goal": [
        r"\bGoal\b", r"\bmetric\b", r"\bmeasurable\b", r"\bbaseline\b",
    ],
    "the instrument that decides it": [
        r"\binstrument\b", r"\bdecided by\b", r"\bharness\b",
        r"\bpytest\b", r"\btest[_ -]graph\b", r"\bspec-unit\b",
    ],
    "a worktree or branch to work in": [
        r"\bworktree\b", r"\bfeature/", r"\bbranch\b",
    ],
    "what closes it out": [
        r"\bRegression\b", r"\bvalidation\b", r"\bclose[- ]out\b",
        r"\bAcceptance\b", r"\bchecklist\b",
    ],
}


def main() -> int:
    issue = None
    for candidate in ("ISSUE.md", "issue.md"):
        path = pathlib.Path(candidate)
        if path.is_file():
            issue = path
            break
    if issue is None:
        print("no ISSUE.md")
        return 1

    text = issue.read_text(encoding="utf-8", errors="replace")
    if len(text) < MIN_CHARS:
        print(f"{issue} is {len(text)} characters; too short to be a work order")
        return 1

    missing = [
        name
        for name, patterns in PROPERTIES.items()
        if not any(re.search(p, text, re.M | re.I) for p in patterns)
    ]
    if missing:
        print(f"the issue does not carry: {missing}")
        return 1

    # A work order names the program. An issue that never mentions the thing it
    # is about was written without opening the repository.
    if not re.search(r"\b(reserve|release|resolve|shortlink|slug)\b", text, re.I):
        print("the issue never names anything in the program it is about")
        return 1

    print("work order ok: all five properties present, and it names the program")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
