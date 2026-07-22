# Repeatable effect-provider validation contract

These projects are experimental consumers of the generic, agent-authored
`EffectProvider.bind(context)` contract. Their providers are evidence, not a
framework library.

Every project exposes the same CLI from the repository root, using the
project's dependency-bearing Python environment:

```bash
<project-python> examples/effect_providers/<project>/validate.py --run-id <unique-id>
```

The command must:

1. refuse to overwrite an existing
   `evidence/validation-runs/<unique-id>/` directory;
2. regenerate its TLA-derived contracts and cases with a 120-second timeout;
3. run its green control, fixed mutation catalog, exact replay, cleanup checks,
   focused tests, and real-boundary rung;
4. write raw artifacts below that run directory and finish by writing
   `result.json`; and
5. exit non-zero unless the common result has `status: "pass"`.

`result.json` is UTF-8, sorted, indented JSON with this common shape:

```json
{
  "schema_version": 1,
  "project": "project-directory-name",
  "run_id": "unique-id",
  "status": "pass",
  "command": ["python3", ".../validate.py", "--run-id", "unique-id"],
  "commit": "git HEAD used for the run",
  "provider_contract": {"name": "EffectProvider.bind", "version": 1},
  "seed": 20260721,
  "cases": {"generated": 0, "control_points": 0, "external": 0},
  "controls": {"passed": 0, "total": 0},
  "mutants": {"killed": 0, "total": 0},
  "replay": {"attempted": 0, "exact": 0, "interpreter": "..."},
  "cleanup": {"checked": 0, "clean": 0},
  "duration_seconds": 0.0,
  "usage_descriptor": {"path": "effect_provider_usage.yaml", "sha256": "..."},
  "oracle_findings": {
    "tla_owned": [],
    "provider_owned": [],
    "passive_external": []
  },
  "limitations": [],
  "artifacts": []
}
```

Counts are project-defined but must be honest and non-negative. A passing run
requires every control, mutant, replay, and cleanup check represented by those
counts to pass. `command` records the actual interpreter path so a virtualenv
run remains reproducible. `commit` identifies the source revision; project
artifacts may additionally record file digests when the run includes local
changes.

Each project also owns `effect_provider_usage.yaml`. It lists every generated
effect port and records its repository-local provider, binding style, state
scope, fuzz dimensions, assertions, cleanup mechanism, and known bypass
limits. This is review evidence only; the runtime does not load it.

Run one project, selected projects, or the complete suite with:

```bash
python3 examples/effect_providers/run_validations.py --project atomic_publisher --fresh-evidence
python3 examples/effect_providers/run_validations.py --all --fresh-evidence
python3 examples/effect_providers/run_validations.py --all --fresh-evidence --run-id review-20260722
```

The repository-level command selects the correct checked project environment,
gives every selected project a derived run id, validates both its structured
result and provider-usage descriptor, and writes a non-destructive aggregate beneath
`examples/effect_providers/evidence/validation-runs/`.
