# taskq

A tiny task queue CLI. Tasks move `pending -> running -> done`; at most two
tasks run at once; duplicate names are rejected. State persists in
`taskq.json` (override with `TASKQ_STATE`).

```bash
python3 taskq.py add build
python3 taskq.py start build
python3 taskq.py finish build
python3 taskq.py list
```

Run the tests:

```bash
uv run --with pytest -m pytest tests -q
```

This project has no spec workflow yet.
