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
    that could have covered it targets `**/results/**`. The last two were
    REMOVED 2026-08-04 with the architecture scanners; this refusal is
    unchanged and is exercised through `analyze complexity`. The audit's remediation
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


#: The directory name every declared case-generation write must land under. The
#: `spec_tree` and `spec_tree_delete` ports both declare `target: "**/specs/**"`,
#: and `fnmatch` -- which is what `effect_conformance.PortDeclaration.matches`
#: uses -- lets `*` cross separators, so that glob means exactly "somewhere
#: under a directory component named `specs`". This constant is that component.
SPEC_TREE_DIR_NAME = "specs"


class SpecTreePathError(ValueError):
    """A generation path the `spec_tree` / `spec_tree_delete` ports do not cover.

    RC-02 (MF-026 round-3 N-2). `generate cases` shipped in RC-01 with `--out`
    `required=True` and no location constraint, and `--dot` unconstrained
    beside it -- the SAME class RC-01 fixed for `analyze complexity`,
    `analyze architecture` and `architecture_reflexion` in the same commit
    (both since removed), reintroduced on the new command path. The writes it performs
    (`generate_cases_from_tlc_dump.render_python_package`'s package files, the
    per-action coverage record, the parameter-recovery audit) and, more
    seriously, the destructive `shutil.rmtree` of the TLC metadir in
    `run_tlc_dump`'s finally branch, all ran wherever the caller pointed, while
    the only ports that could cover them target `**/specs/**`.

    Constrained rather than declared, which is the disposition RC-01 itself
    chose for G-2/G-3. The alternative -- widening `spec_tree` and
    `spec_tree_delete` to `*` -- would weaken two ports that are currently
    precise and that `CloseTicket` also depends on, in order to legalise a
    destructive delete at a caller-chosen path.

    Deliberately a REFUSAL and not a silent relocation, for the same reason
    `EvidencePathError` is: rewriting the operator's path would make the flag
    lie about where the corpus went.
    """


def resolve_spec_tree_out(value: str | Path, spec_dir: Path, *, is_file: bool = False) -> Path:
    """Resolve a generation output path, refusing anything outside `specs/`.

    Resolution is unchanged -- it still goes through
    :func:`resolve_spec_relative_path`, so the documented behaviour of a
    relative path (resolved against the SPEC DIRECTORY unless it already points
    inside it) is exactly as before, and the only paths this can newly refuse
    are ones that resolve outside a `specs/` tree. In practice that is absolute
    paths: a relative `--out` already lands under the spec directory.

    ``is_file`` distinguishes a path that is itself written (``--dot``) from a
    root that is written INTO (``--out``). For the first the containing
    directory must carry the component; for the second the path itself may be
    the `specs` directory.
    """
    resolved = resolve_spec_relative_path(Path(value).expanduser(), spec_dir)
    considered = resolved.parts[:-1] if is_file else resolved.parts
    if SPEC_TREE_DIR_NAME not in considered:
        raise SpecTreePathError(
            f"case generation must write under a `{SPEC_TREE_DIR_NAME}/` directory "
            f"(e.g. {SPEC_TREE_DIR_NAME}/generated/<consumer>/<run-id>); "
            f"got {resolved}.\n"
            f"The `spec_tree` and `spec_tree_delete` effect ports declare target "
            f"`**/{SPEC_TREE_DIR_NAME}/**`, so a write -- or the metadir delete "
            "derived from it -- anywhere else is an undeclared effect.\n"
            "REMEDY: point --out at a path under a "
            f"{SPEC_TREE_DIR_NAME}/ directory and keep only exported artifacts "
            "(traces, reports) under your own report directory. A Test Graph node "
            f"generating into its build tree wants --out {SPEC_TREE_DIR_NAME}/"
            "generated/testgraph/<run-id>."
        )
    return resolved
