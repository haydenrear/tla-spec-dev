#!/usr/bin/env python3
"""Blind dispatch: run a judge without the operator's conclusions, and refuse
a round whose judge received them anyway.

CA-01, GOAL-blind-dispatch. Two subcommands:

  cell    build a neutral working directory for one dispatched agent
  check   REFUSE a judge self-report that shows the operator's conclusions
          were in its context before it read anything

`check` is the instrument. Its needles are derived AT RUN TIME from the
operator's live auto-memory index and the repository's own recent commit
subjects -- never a hand-written list of expected answers. Fitting a detector
to a known answer is MF-020, and this project has refused it three times.

R1: this ships with a demonstrated failing input on a real subject. See
specs/results/scorecards/cut-the-apparatus/CA-01/ -- `check` refuses the
transcripts of real agents dispatched the ordinary way, and passes the ones
dispatched through `cell`.

What this does NOT do, measured rather than assumed: it does not remove the
`<env>` block, the scratchpad path or the skill listing, all of which identify
the repository and its toolchain. See references/blind_dispatch.md.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

MEMORY_ROOT = pathlib.Path.home() / ".claude" / "projects"
# HAND-WRITTEN LITERALS, and they must be described as such. These four are the
# harness's own block LABELS -- names of injected blocks, not conclusions about
# any subject -- which is why they are not the MF-020 hazard that a hand-written
# list of expected ANSWERS would be. But they are not "derived from live data",
# and the other two needle classes are; see `check`'s output, which reports the
# three classes separately for exactly this reason.
HARNESS_MARKERS = (
    "# claudeMd",
    "user's auto-memory",
    "gitStatus:",
    "Recent commits:",
)

# A subject that is not a self-report cannot be judged. No needles found in an
# empty file is absence of EVIDENCE, not evidence of absence, and returning PASS
# for it is a FALSE PASS in an instrument whose entire job is refusing. Found by
# review of this instrument as shipped: an empty file and a failed dispatch
# (`Error: Invalid API key`) both returned PASS, exit 0.
#
# The floor sits far below any honest answer to a four-part probe and far above
# any single-line dispatch failure, so it separates those two cases without
# being tuned to the particular transcripts this ticket happens to hold.
MIN_REPORT_BYTES = 200
DISPATCH_FAILURE_SIGNATURES = (
    "Invalid API key",
    "Please run /login",
    "Credit balance is too low",
    "command not found",
    "Traceback (most recent call last)",
    "usage: claude",
    "error: unknown option",
)


def memory_path_for(cwd: pathlib.Path) -> pathlib.Path:
    """Auto-memory is keyed by a slug of the session's working directory."""
    return MEMORY_ROOT / str(cwd.resolve()).replace("/", "-") / "memory" / "MEMORY.md"


def memory_needles(mem: pathlib.Path) -> list[str]:
    """Bullet titles from the live memory index, e.g. '[Ports-as-adapters epic]'."""
    if not mem.is_file():
        return []
    titles = re.findall(r"^-\s*\[([^\]]+)\]", mem.read_text(errors="replace"), re.M)
    return [t.strip() for t in titles if len(t.strip()) > 8]


def commit_needles(repo: pathlib.Path, count: int) -> list[str]:
    """Subject lines the harness hands every agent in the gitStatus block."""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "log", f"-{count}", "--format=%s"],
            capture_output=True, text=True, timeout=30, check=True,
        ).stdout
    except (subprocess.SubprocessError, OSError):
        return []
    return [s.strip() for s in out.splitlines() if len(s.strip()) > 20]


def cmd_check(args: argparse.Namespace) -> int:
    report = pathlib.Path(args.report).read_text(errors="replace")
    repo = pathlib.Path(args.repo).resolve()
    # The memory belongs to the DISPATCHING SESSION's cwd, which is not the
    # same directory as the repository under test. A ticket worktree has no
    # memory slug of its own while the primary checkout it was branched from
    # has the whole index -- so pointing --repo at a worktree silently derives
    # zero memory needles. Found by running this instrument on a real subject.
    mem = pathlib.Path(args.memory) if args.memory else memory_path_for(repo)

    # PRECONDITION, before any needle is counted: is this a self-report at all?
    stripped = report.strip()
    unusable = None
    if not stripped:
        unusable = "the subject is empty"
    elif len(stripped) < MIN_REPORT_BYTES:
        unusable = (f"the subject is {len(stripped)} bytes, below the "
                    f"{MIN_REPORT_BYTES}-byte floor for an honest answer to the probe")
    else:
        for sig in DISPATCH_FAILURE_SIGNATURES:
            if sig in stripped[:2000]:
                unusable = f"the subject looks like a failed dispatch ({sig!r})"
                break
    if unusable is not None:
        print(f"subject      {args.report}")
        print(f"\nUNDECIDED: {unusable}.")
        print("A subject that is not an agent's self-report cannot be judged. "
              "Finding no leak in it is absence of EVIDENCE, not evidence of "
              "absence.\nThis is NOT a pass. Re-dispatch and re-run.")
        return 2

    groups = {
        "harness block label": list(HARNESS_MARKERS),
        "operator memory entry": memory_needles(mem),
        "repository commit subject": commit_needles(repo, args.commits),
    }

    hits: list[tuple[str, str]] = []
    for kind, needles in groups.items():
        for needle in needles:
            if needle in report:
                hits.append((kind, needle))

    print(f"subject      {args.report}")
    print(f"repository   {repo}")
    print(f"auto-memory  {mem if mem.is_file() else str(mem) + '  (absent)'}")
    for kind, needles in groups.items():
        print(f"needles      {len(needles):>3}  {kind}")

    if not any(groups.values()):
        print("\nUNDECIDED: no needles could be derived. Not a pass.")
        return 2

    # A pass carried only by literal block labels is a weak pass, and saying so
    # is cheaper than discovering later that the strongest needle class was
    # never in play.
    weak = not groups["operator memory entry"]
    if weak:
        print(f"\nWARNING: 0 memory needles. {mem} holds no index, so the "
              "strongest needle class was unavailable.\n         Pass --memory "
              "with the DISPATCHING SESSION's memory file to strengthen this.")

    if hits:
        print(f"\nREFUSED: {len(hits)} leak indicator(s) present in the judge's "
              f"own report of its pre-read context.\n")
        for kind, needle in hits:
            print(f"  [{kind}] {needle}")
        print("\nThis round is not blind. Do not label it blind; print the "
              "contamination note beside every number it produced.")
        return 1

    print("\nWEAK PASS." if weak else "\nPASS.", end=" ")
    print("None of the operator's conclusions appear in this report.")
    print("Scope: silence about these needles only. It is NOT a claim that the "
          "agent knew nothing of this project -- the <env> block, the scratchpad "
          "path, the SessionStart hook output and the skill listing still name "
          "its toolchain. Measured, not assumed: see references/blind_dispatch.md.")
    return 0


def cmd_cell(args: argparse.Namespace) -> int:
    """A working directory carrying no memory slug and no git history."""
    cell = pathlib.Path(args.path).resolve()
    if cell.exists() and any(cell.iterdir()):
        print(f"refusing: {cell} exists and is not empty", file=sys.stderr)
        return 2
    cell.mkdir(parents=True, exist_ok=True)

    problems = []
    if memory_path_for(cell).exists():
        problems.append(f"a memory file already exists at {memory_path_for(cell)}")
    probe = subprocess.run(["git", "-C", str(cell), "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True)
    if probe.returncode == 0:
        problems.append(f"inside a git repository ({probe.stdout.strip()}) -- "
                        "the gitStatus block will be injected")
    for part in cell.parts:
        if "tla-spec" in part or "spec-dev" in part:
            problems.append(f"path component {part!r} names the project under test")

    print(f"cell         {cell}")
    print(f"memory slug  {memory_path_for(cell).parent.parent.name}  (no memory dir)")
    for p in problems:
        print(f"PROBLEM      {p}")
    if problems:
        return 1
    print("\nReady. Dispatch with:  cd " + str(cell) + " && claude -p \"<prompt>\"")
    print("Then run `check` on the agent's reply before believing any number.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="refuse a self-report that shows a leak")
    c.add_argument("report", help="file holding the agent's verbatim self-report")
    c.add_argument("--repo", default=".", help="repository whose conclusions must not leak")
    c.add_argument("--commits", type=int, default=5,
                   help="how many commit subjects the harness injects (default 5)")
    c.add_argument("--memory", default=None,
                   help="the DISPATCHING SESSION's MEMORY.md; defaults to the "
                        "slug of --repo, which is wrong when they differ")
    c.set_defaults(func=cmd_check)

    n = sub.add_parser("cell", help="build a neutral working directory")
    n.add_argument("path", help="where to build it -- outside any git repository")
    n.set_defaults(func=cmd_cell)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
