# order_hub

A small order processor built around one shared hub. Orders are placed and
shipped (never more shipped than ordered, at most 3 open), a retry sweep runs
at most twice, and an audit log counts every operation up to a cap that stops
the world.

The TLA+ model lives in `specs/program_model/OrderHub.tla` with its cfg and
`spec_manifest.yaml`. Run the tests:

```bash
uv run --with pytest -m pytest tests -q
```

Model-check with the tla-spec-dev toolchain's `run_tlc.sh`, and scan with
`analyze complexity`.
