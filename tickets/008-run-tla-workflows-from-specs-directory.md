# Run TLA Workflows From Specs Directory

Status: Done

TLA workflows sometimes run from the project root. When that happens, relative
outputs such as `cases/` are written to the project root instead of under
`specs/`, which splits generated artifacts across locations and makes cleanup,
history capture, and adapter execution less predictable.

Make TLA execution location explicit. Running TLC, generating cases, and running
case adapters should either execute from `specs/` or resolve all spec-relative
outputs against `specs/`, regardless of the caller's current working directory.

The intuition is that `specs/` is the boundary for spec state. Generated cases,
TLC evidence, and transient model artifacts should stay inside that boundary so
the repository root remains orchestration-only.

Acceptance criteria:

- Invoking the TLA workflow from the project root writes generated cases under
  `specs/`.
- Invoking the same workflow from `specs/` produces the same artifact layout.
- No supported workflow creates or relies on a project-root `cases/` directory.
- Error messages include the resolved spec directory and output paths.
- Existing generated-case and adapter workflows keep working with the new path
  behavior.

Implementation:

- Added shared spec-relative path helpers in `scripts/spec_paths.py`.
- Updated `generate_cases_from_tlc_dump.py` so TLC runs with the spec directory
  as its working directory and relative output paths resolve under the spec
  directory unless the caller already supplied a path inside it.
- Updated `run_generated_case_adapters.py` with `--spec-dir` and
  spec-relative resolution for case packages, mappings, import roots, and work
  directories.
- Kept existing root-relative example paths working when they already point
  inside the resolved spec directory.
