# Generator parser dependency diagnostic

Fresh-checkout validation at integration commit `076a28d` exposed a real
dependency-sensitive contract-generation defect. The reminder manifest used
valid YAML inline maps for field types and port method command/result pairs.

- Xcode Python 3.9 with PyYAML 6.0 generated typed signatures such as
  `ClockPort.now(self, command: ReadClock) -> int`.
- Homebrew Python 3.14 without PyYAML, and explicitly with `-S`, used the
  constrained fallback parser. It treated each inline map as a scalar and
  generated `ClockPort.now(self) -> object`.
- The same source manifest therefore produced differences in `ports.py`,
  `types.py`, `fake.py`, `validators.py`, and `contract_tests.py`.

EP-03 resolves its own typed-effect fidelity without changing framework files:
the reminder manifest now spells all field and method maps in the fallback
parser's supported nested form. Its unit suite generates the whole contract
both in the active environment and under `python -S`, compares both trees
byte-for-byte with the committed tree, and inspects representative typed
signatures. The aggregate Test Graph additionally loads the normalized manifest
through both PyYAML and the fallback parser, compares every contract-generation
section, and explicitly checks all five no-result methods parse as null. Budgets
are excluded from this raw-tree equality because the constrained parser
represents `kill_rate_floor: 0.8` as a string while PyYAML uses a float; the
budget loader has a separate coercion path and the Python contract generator
does not consume budgets. This assertion catches generation differences that
happen to stringify into the same source without making a false whole-file
parser-equivalence claim.

The shared defect remains open as `DEF-002`: valid manifests outside this
project can still degrade silently depending on optional PyYAML availability.
The framework should either parse inline maps consistently or require a pinned
YAML implementation and fail closed.

The apparent reminder baseline flake found in the same checkout was not a
product defect. A diagnostic timing wrapper bypassed the shell's Python alias
and selected Python 3.9; `zip(..., strict=True)` correctly requires the
project's declared Python 3.10+. Exact documented commands under Python 3.14
passed repeatedly, so no runtime change was made for that diagnostic.
