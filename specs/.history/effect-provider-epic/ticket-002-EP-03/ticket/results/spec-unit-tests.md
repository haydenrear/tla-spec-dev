# Host spec-unit evidence

Command:

```text
python3 scripts/tla_spec_dev.py --spec-root specs run spec-unit-tests --ticket EP-03
```

Result on the final semantic tree:

- `specs/current`: 63 passed.
- `specs/tickets/EP-03/current`: 60 passed.
- Two targets validated; exit 0.

The later `c46aef1` change only makes an EP-03 Test Graph source portable during
node discovery; it does not touch either validated host model/adapter tree.
