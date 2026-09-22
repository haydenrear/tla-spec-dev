"""MATERIALISE THE PIN, VERIFY IT, AND WRITE DOWN WHAT RAN.

`evals/lib/toolchain.lock.toml` says which commit of each unit an eval run is
supposed to use. This turns that into a directory on disk and a record next to
the score.

Why materialising is the only shape available
---------------------------------------------
`claude plugin eval` has NO version pinning for plugin dependencies. A case's
`plugins:` field takes relative filesystem PATHS -- no git ref, no marketplace
constraint, no lockfile, no manifest-level plugin-depends-on-plugin. Measured on
2.1.276. So there is no field for a declared pin to live in, and the pin has to
become a path: fetch the commit, verify the checkout IS that commit, stage it
where a case can reach it.

What was measured, at $0.06 total, before this file was written
--------------------------------------------------------------
Three probes on Claude Code 2.1.276, because the two accounts available to me
disagreed and both turned out to be half right:

1. TOP-LEVEL `scaffold_script:` WITH INLINE BASH IS ACCEPTED AND SILENTLY
   IGNORED. A case whose body was `echo ... > marker` scored 1.00 and wrote no
   marker. This is the behaviour `evals/lib/place.sh` and
   `references/plugin_evals.md` recorded on 2.1.261, and it is still true.

2. `context.scaffold_script:` IS LIVE, BUT IT IS A PATH, NOT A SCRIPT BODY.
   Inline bash there is refused at case-LOAD time:
     case "...": path "echo "..." > /tmp/marker " does not exist

3. `context.scaffold_script: ./scaffold.sh` WITH `--scaffold` DOES EXECUTE, as
   the operator, outside the sandbox, with working network:
     scaffold: <abs path>/scaffold.sh
     FILED SCAFFOLD RAN pwd=/private/tmp/e-jS2iI9/home/cwd whoami=hayde
     HOME=/private/tmp/e-jS2iI9/home
     git ls-remote <unit remote> <branch> -> <sha>
   Note HOME is a SCRATCH home, not the operator's: a scaffold script cannot
   reach ~/.skill-manager, which is exactly the dependency this ticket removes.

So a per-case `context.scaffold_script` COULD clone. This file does the work
operator-side anyway, for three reasons, each of which is a defect if ignored:

  * `--scaffold` IS OFF BY DEFAULT. A suite whose fixture depends on it runs
    unscaffolded for anyone who forgets the flag -- and scores, silently. A
    silent default is the defect this ticket exists to close.
  * `plugins:` ENTRIES ARE VALIDATED AT CASE-LOAD TIME (measured: a missing
    entry fails the case file before any run). A directory a scaffold script
    creates during the run is not there when the loader looks.
  * ONE MATERIALISATION SERVES EVERY CASE. Per-case scaffolding clones N times.

Usage
-----
    python3 evals/lib/toolchain.py materialise [--ref <commitish>] [--check-drift]
    python3 evals/lib/toolchain.py print-ref [--unit <name>]
    python3 evals/lib/toolchain.py record --out <file.json>

`--ref` overrides the pinned commit for one unit, and the override is RECORDED
as an override; that is what makes "the runner asked and I answered something
else" visible afterwards instead of indistinguishable from the pin.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
LOCK = HERE / "toolchain.lock.toml"
# THE CACHE IS AT THE REPOSITORY ROOT, NOT UNDER `evals/`, AND THAT IS A BUG FIX.
# It lived at `evals/.toolchain` for one iteration, and the pytest sweep caught
# what that costs: `claude plugin eval` discovers cases with a recursive glob
# over the eval dir (`<eval dir>/**/case.yaml`), and the materialised
# skill-manager checkout carries **56 case.yaml files of its own** under
# `specs/evals/harness/evals/`. Every one of them would have been discovered as
# one of THIS suite's cases, scored, and billed, with nothing in the report
# marking them as somebody else's -- the hazard `plugin_evals.md` §3.5 names.
# Moving the cache out of the eval dir removes it at the source instead of
# relying on the staged view's exclude list to keep catching it.
DEFAULT_CACHE = REPO / ".toolchain"

HEX40 = re.compile(r"^[0-9a-f]{40}$")


# --------------------------------------------------------------- the lock
def _load_lock(path: pathlib.Path = LOCK) -> dict:
    """Read the lock. tomllib is stdlib from 3.11; fall back to a tiny reader.

    The fallback exists because this file runs from `run.sh` under whatever
    python3 the operator has, and a toolchain pin that cannot be read on 3.9 is
    a pin that silently stops being consulted.
    """
    text = path.read_text(encoding="utf-8")
    try:
        import tomllib

        return tomllib.loads(text)
    except ModuleNotFoundError:
        pass
    try:
        import tomli  # type: ignore

        return tomli.loads(text)
    except ModuleNotFoundError:
        pass
    return _parse_units_only(text)


def _parse_units_only(text: str) -> dict:
    """Enough TOML for THIS file's shape: [units.<name>] with scalar strings.

    Deliberately narrow. It understands `key = "value"` and `key = \"\"\"...\"\"\"`
    inside `[units.*]` tables and ignores everything else, so a malformed value
    shows up as a missing key (and then as an explicit refusal below) rather
    than as a wrong one.
    """
    units: dict[str, dict] = {}
    current: dict | None = None
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("[units."):
            name = stripped[len("[units.") :].rstrip("]").strip().strip('"')
            current = units.setdefault(name, {})
        elif stripped.startswith("[") and not stripped.startswith("[units."):
            current = None
        elif current is not None and "=" in stripped and not stripped.startswith("#"):
            key, _, value = stripped.partition("=")
            key, value = key.strip(), value.strip()
            if value.startswith('"""'):
                body = [value[3:]]
                while not body[-1].rstrip().endswith('"""'):
                    i += 1
                    if i >= len(lines):
                        break
                    body.append(lines[i])
                joined = "\n".join(body)
                current[key] = joined[: joined.rfind('"""')].strip()
            else:
                current[key] = value.strip().strip('"')
        i += 1
    return {"units": units}


def units(lock: dict | None = None) -> dict:
    lock = lock or _load_lock()
    found = lock.get("units") or {}
    # NON-VACUITY. An empty lock must not read as "everything is pinned".
    if not found:
        raise SystemExit(f"toolchain: {LOCK} declares no units -- refusing to "
                         "report a pinned toolchain when nothing is pinned")
    for name, spec in found.items():
        commit = (spec.get("commit") or "").strip()
        if not HEX40.match(commit):
            raise SystemExit(
                f"toolchain: unit '{name}' is pinned at {commit!r}, which is not a "
                "40-character commit sha. A branch is the thing the pin exists to "
                "stop depending on."
            )
        if not (spec.get("origin") or "").strip():
            raise SystemExit(f"toolchain: unit '{name}' declares no origin")
    return found


# -------------------------------------------------------------- the fetch
def _git(args: list[str], cwd: pathlib.Path, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(cwd), text=True, capture_output=True, check=check
    )


def _head(checkout: pathlib.Path) -> str | None:
    try:
        return _git(["rev-parse", "HEAD"], checkout).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None


def materialise_unit(name: str, spec: dict, cache: pathlib.Path, commit: str) -> dict:
    """Fetch `commit` of `spec['origin']` into `cache/name` and VERIFY it.

    Blobless + depth 1, fetching the commit sha directly. Measured 2026-09-19:
    skt is 504K of .git and 134 entries; skill-manager is 18M and 11,481 -- which
    is why skill-manager is never staged into the 20,000-entry-capped view.
    """
    checkout = cache / name
    checkout.mkdir(parents=True, exist_ok=True)

    if _head(checkout) == commit:
        return _verified(name, spec, checkout, commit, refetched=False)

    if not (checkout / ".git").exists():
        _git(["init", "-q", "."], checkout)
    existing = _git(["remote"], checkout, check=False).stdout.split()
    if "origin" in existing:
        _git(["remote", "set-url", "origin", spec["origin"]], checkout)
    else:
        _git(["remote", "add", "origin", spec["origin"]], checkout)

    try:
        _git(["fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", commit], checkout)
        _git(["checkout", "-q", "--detach", "FETCH_HEAD"], checkout)
    except subprocess.CalledProcessError as exc:
        # A commit a server will not serve by sha (some hosts disable it) still
        # has to be reachable, so fall back to fetching the ref and checking the
        # sha out of it -- and if THAT cannot produce the pinned commit, refuse.
        ref = (spec.get("ref_when_pinned") or "").strip()
        if not ref:
            raise SystemExit(
                f"toolchain: could not fetch {name} at {commit} from {spec['origin']}\n"
                f"{exc.stderr}"
            )
        _git(["fetch", "-q", "--filter=blob:none", "origin", ref], checkout)
        _git(["checkout", "-q", "--detach", commit], checkout)

    return _verified(name, spec, checkout, commit, refetched=True)


def _verified(name, spec, checkout, commit, refetched: bool) -> dict:
    """The check that makes this a pin rather than a hope."""
    head = _head(checkout)
    if head != commit:
        raise SystemExit(
            f"toolchain: {name} was materialised at {head}, but the lock pins "
            f"{commit}. Refusing to report a pinned toolchain for a checkout "
            "that is not it."
        )
    (checkout / ".si14-commit").write_text(commit + "\n", encoding="utf-8")

    record = {
        "unit": name,
        "origin": spec["origin"],
        "pinned_commit": commit,
        "verified_head": head,
        "path": str(checkout),
        "refetched": refetched,
        "materialised_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    # The CLI'S OWN account of which code ran, where it has one. skill-manager's
    # wrapper prints `0.28.1+g6ffacb88ff96` / `build: 6ffacb88ff96 (detached)`.
    self_report = (spec.get("self_report_command") or "").strip()
    wrapper = checkout / name
    if self_report and wrapper.is_file() and os.access(wrapper, os.X_OK):
        try:
            proc = subprocess.run(
                [str(wrapper), *self_report.split()],
                text=True, capture_output=True, timeout=600, cwd=str(checkout),
            )
            record["self_report"] = (proc.stdout or proc.stderr).strip()[:400]
        except (OSError, subprocess.SubprocessError) as exc:
            record["self_report"] = f"UNAVAILABLE: {exc}"
    return record


# ----------------------------------------------------------- what moved
def check_drift(name: str, spec: dict, cache: pathlib.Path) -> str:
    """Has the branch the pin was taken from moved since? Network; advisory."""
    ref = (spec.get("ref_when_pinned") or "").strip()
    if not ref:
        return f"{name}: no ref_when_pinned recorded; drift not checkable"
    try:
        proc = subprocess.run(
            ["git", "ls-remote", spec["origin"], ref],
            text=True, capture_output=True, timeout=120, check=False,
        )
        tip = (proc.stdout.split() or [""])[0]
    except (OSError, subprocess.SubprocessError) as exc:
        return f"{name}: drift not checked ({exc})"
    if not tip:
        return f"{name}: {ref} did not resolve on {spec['origin']}"
    if tip == spec["commit"]:
        return f"{name}: {ref} is still at the pinned commit"
    return (f"{name}: {ref} HAS MOVED to {tip[:12]} since the pin at "
            f"{spec['commit'][:12]} -- the pin is doing its job")


def home_says(name: str) -> str | None:
    """What the ambient home would have resolved, for comparison.

    This is the thing being replaced. Reading it is not using it.
    """
    for home in (REPO / ".skill-manager", pathlib.Path.home() / ".skill-manager"):
        record = home / "installed" / f"{name}.json"
        if record.is_file():
            try:
                data = json.loads(record.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            return (f"{home.name} at {home.parent}: gitRef {data.get('gitRef')} "
                    f"gitHash {(data.get('gitHash') or '')[:12]} "
                    f"installed {data.get('installedAt')}")
    return None


# ------------------------------------------------------------------ main
def _materialise_all(args) -> dict:
    cache = pathlib.Path(args.cache).resolve() if args.cache else DEFAULT_CACHE
    cache.mkdir(parents=True, exist_ok=True)
    spec_by_name = units()

    records, notes = [], []
    for name, spec in sorted(spec_by_name.items()):
        commit = spec["commit"]
        source = "pinned in evals/lib/toolchain.lock.toml"
        # SI-18: this read `name == "skt"`, and skt is not a pinned unit any
        # more — it is nested in this plugin, so the override could never
        # apply and `--ref` became a flag that accepted a value and did
        # nothing. It now targets the unit the operator names, defaulting to
        # the only one there is.
        if args.ref and name == (args.ref_unit or _sole_unit(spec_by_name)):
            resolved = _resolve_override(spec, cache, args.ref)
            if resolved != commit:
                source = f"OVERRIDE: operator asked for {args.ref!r}"
                commit = resolved
        rec = materialise_unit(name, spec, cache, commit)
        rec["ref_source"] = source
        rec["stage_into_view"] = spec.get("stage_into_view") or ""
        records.append(rec)
        if args.check_drift:
            notes.append(check_drift(name, spec, cache))

    if not records:
        raise SystemExit("toolchain: nothing was materialised")

    out = {
        "schema": "si14.toolchain-run-record.v1",
        "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "lock": str(LOCK.relative_to(REPO)),
        "cache": str(cache),
        "units": records,
        "drift": notes,
        "ambient_home_would_have_used": {
            n: home_says(n) for n in sorted(spec_by_name)
        },
    }
    return out


def _sole_unit(spec_by_name):
    """The only pinned unit's name, or None when there is more than one.

    `--ref` used to be hardcoded to "skt". Defaulting to the sole unit keeps
    the one-unit case ergonomic without silently picking one of several.
    """
    names = list(spec_by_name)
    return names[0] if len(names) == 1 else None


def _resolve_override(spec: dict, cache: pathlib.Path, ref: str) -> str:
    """Turn an operator's answer into a commit, or refuse."""
    if HEX40.match(ref.strip()):
        return ref.strip()
    proc = subprocess.run(
        ["git", "ls-remote", spec["origin"], ref],
        text=True, capture_output=True, timeout=120, check=False,
    )
    tip = (proc.stdout.split() or [""])[0]
    if not HEX40.match(tip or ""):
        raise SystemExit(
            f"toolchain: {ref!r} does not resolve on {spec['origin']}. "
            "Refusing to run against a toolchain nobody can name."
        )
    return tip


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("materialise", help="fetch and verify every pinned unit")
    m.add_argument("--cache", default=None)
    m.add_argument("--ref", default=None,
                   help="override a unit's pinned commit (recorded as an override)")
    m.add_argument("--ref-unit", default=None,
                   help="which unit --ref applies to; defaults to the only pinned unit")
    m.add_argument("--check-drift", action="store_true")
    m.add_argument("--record", default=None, help="write the run record here")
    m.add_argument("--stage-into", default=None, help="a staged view to copy stage_into_view units into")

    p = sub.add_parser("print-ref", help="print a unit's pinned commit")
    p.add_argument("--unit", default=None,
                   help="unit name; defaults to the only pinned unit")

    r = sub.add_parser("record", help="materialise and write the record only")
    r.add_argument("--out", required=True)
    r.add_argument("--cache", default=None)
    r.add_argument("--ref", default=None)
    r.add_argument("--check-drift", action="store_true")
    r.add_argument("--stage-into", default=None)

    args = parser.parse_args(argv)

    if args.cmd == "print-ref":
        all_units = units()
        unit = args.unit or _sole_unit(all_units)
        if unit is None:
            raise SystemExit("toolchain: several units are pinned; pass --unit")
        spec = all_units.get(unit)
        if not spec:
            raise SystemExit(f"toolchain: no unit {unit!r} in the lock")
        print(spec["commit"])
        return 0

    record = _materialise_all(args)

    stage_into = getattr(args, "stage_into", None)
    if stage_into:
        view = pathlib.Path(stage_into)
        for unit in record["units"]:
            rel = unit.get("stage_into_view")
            if not rel:
                continue
            dest = view / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                shutil.rmtree(dest)
            # WITHOUT .git: the view is counted against a 20,000-entry ceiling,
            # and a case only ever reads the unit's files.
            shutil.copytree(unit["path"], dest, ignore=shutil.ignore_patterns(".git"))
            unit["staged_at"] = str(dest)

    out_path = getattr(args, "record", None) or getattr(args, "out", None)
    if out_path:
        target = pathlib.Path(out_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    for unit in record["units"]:
        line = (f"  {unit['unit']}: {unit['pinned_commit'][:12]} "
                f"({unit['ref_source']})")
        if unit.get("staged_at"):
            line += f"\n      staged -> {unit['staged_at']}"
        if unit.get("self_report"):
            line += f"\n      the CLI says: {unit['self_report'].splitlines()[0]}"
        print(line)
    for note in record.get("drift") or []:
        print(f"  drift: {note}")
    if out_path:
        print(f"  record -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
