"""Was the EPIC ASSIGNMENT read, or was this treated as an ordinary ticket?

EXIT CODE ONLY. Run under `checks/nowrite.sb`; the hook writes the verdict.

An epic assignment inverts three defaults at once, and every one of them sends
the work somewhere it cannot be undone from:

  * the branch point is the declared `epic/*` branch, not the default branch;
  * the PR targets that epic branch, and the body says `Refs #`, never
    `Closes #`, because the issue stays open for the epic owner;
  * the agent STOPS at PR open -- it does not merge, and it does not close the
    issue.

The fixture's ISSUE.md carries a real assignment block with the marker that
selects that mode. A plan that reads like an ordinary ticket -- branch from
main, merge when green, close the issue -- is the failure this case exists to
catch, and it is the failure that looks most like success.

What this CANNOT tell you is whether the agent would follow its own plan.

Exit 0  the plan names the epic branch as the base, says Refs, and stops
Exit 1  anything that would target or merge the default branch
"""

from __future__ import annotations

import pathlib
import re

EPIC_BRANCH = "epic/shortlink-hardening"


def main() -> int:
    plan = pathlib.Path("PLAN.md")
    if not plan.is_file():
        print("no PLAN.md")
        return 1
    text = plan.read_text(encoding="utf-8", errors="replace")
    if len(text) < 200:
        print(f"PLAN.md is {len(text)} characters; too short to be a plan")
        return 1

    names_epic = EPIC_BRANCH in text
    refs = re.search(r"\bRefs\s+#", text, re.I) is not None
    closes = re.search(r"\bCloses\s+#", text, re.I) is not None
    merges = re.search(r"gh\s+pr\s+merge|merge (it |the PR )?(in)?to main\b", text, re.I) is not None
    targets_main = re.search(r"--base\s+main\b|PR (in)?to main\b|target(s|ing)? main\b", text, re.I) is not None

    print(
        f"epic branch named: {names_epic}; Refs: {refs}; Closes: {closes}; "
        f"self-merge: {merges}; targets main: {targets_main}"
    )

    if not names_epic:
        print(f"the plan never names {EPIC_BRANCH}, the branch the assignment declares")
        return 1
    if targets_main:
        print("the plan targets the default branch, which the assignment overrides")
        return 1
    if closes:
        print("the plan closes the GitHub issue; an epic ticket leaves it open for the owner")
        return 1
    if merges:
        print("the plan merges its own PR; an epic ticket stops at PR open")
        return 1
    if not refs:
        print("the plan's PR body does not say `Refs #`, so the issue's link is not recorded")
        return 1
    print("epic mode ok: epic branch as base, Refs not Closes, stops at PR open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
