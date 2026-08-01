"""Path helpers for spec-relative scripts."""

from __future__ import annotations

from pathlib import Path


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def resolve_existing_from_cwd(path: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (Path.cwd() / path).resolve()


def resolve_spec_dir(tla_path: Path) -> Path:
    resolved = resolve_existing_from_cwd(tla_path)
    if not resolved.exists():
        raise SystemExit(f"ERROR: spec not found: {resolved}")
    return resolved.parent.resolve()


def resolve_existing_spec_input(path: Path, spec_dir: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    cwd_candidate = (Path.cwd() / path).resolve()
    if cwd_candidate.exists():
        return cwd_candidate
    spec_candidate = (spec_dir / path).resolve()
    if spec_candidate.exists():
        return spec_candidate
    return cwd_candidate


def resolve_spec_relative_path(path: Path, spec_dir: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    spec_dir = spec_dir.resolve()
    cwd_candidate = (Path.cwd() / path).resolve()
    if is_relative_to(cwd_candidate, spec_dir):
        return cwd_candidate
    return (spec_dir / path).resolve()


#: The directory name every declared evidence write must land under. The
#: `evidence_report` port declares `target: "**/results/**"`, so a write that
#: lands anywhere else is an UNDECLARED effect no matter how truthful the
#: report inside it is.
EVIDENCE_DIR_NAME = "results"


class EvidencePathError(ValueError):
    """An `--out` path that the `evidence_report` port does not cover.

    RC-01 (MF-026 G-2/G-3). `analyze complexity --out`, `analyze architecture
    --out` and `architecture_reflexion --out` each took a BARE STRING and did
    `out_path.parent.mkdir(parents=True); out_path.write_text(...)`, so an
    evidence write could land anywhere on the filesystem while the only port
    that could have covered it targets `**/results/**`. The audit's remediation
    was "declare the port and constrain the path, or drop --out". The path is
    constrained HERE, in one place, so the declaration in spec_manifest.yaml is
    true of every caller rather than true of the documented one.

    Deliberately a REFUSAL and not a silent relocation: rewriting the operator's
    path would make the flag lie about where the file went, which is the same
    honest-in-prose / misleading-in-artifact defect RP-02 was opened for.
    """


def resolve_evidence_out(value: str | Path) -> Path:
    """Resolve an `--out` evidence path, refusing anything outside `results/`.

    The check is on the RESOLVED path, so `..` cannot walk out of the tree, and
    it is a containment check on a path COMPONENT rather than a prefix match, so
    any `results/` directory in the repository qualifies -- ticket results,
    project results, a temp dir the caller made. That is exactly the surface
    `**/results/**` declares.
    """
    resolved = Path(value).expanduser()
    resolved = resolved.resolve() if resolved.is_absolute() else (Path.cwd() / resolved).resolve()
    if EVIDENCE_DIR_NAME not in resolved.parts[:-1]:
        raise EvidencePathError(
            f"--out must write under a `{EVIDENCE_DIR_NAME}/` directory; got {resolved}. "
            f"The `evidence_report` effect port declares target `**/{EVIDENCE_DIR_NAME}/**`, "
            "so a write anywhere else is an undeclared effect. Pass a path under the "
            f"ticket's {EVIDENCE_DIR_NAME}/ directory, or drop --out and redirect stdout."
        )
    return resolved
