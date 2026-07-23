# Runtime Protocol conformance diagnostic

The generated Python Protocol declarations carry typed commands and results,
but `@runtime_checkable` checks only structural method presence. This command
was run against the committed atomic contract:

```text
env PYTHONPATH=examples/effect_providers/atomic_publisher/specs/program_model/generated python3 - <<'PY'
from atomic_publisher_contract.ports import FilesystemPort
class Malformed:
    def read(self): pass
    def write(self): pass
    def replace(self): pass
    def delete(self): pass
print(isinstance(Malformed(), FilesystemPort))
PY
```

Observed output: `True`. The malformed binding has the four names but accepts no
command and declares no result. Consequently, the atomic test's positive
`isinstance(binding, FilesystemPort)` assertion is a useful shape preflight but
is not runtime typed-signature enforcement.

EP-03 keeps this visible as `DEF-003`. A follow-up should generate explicit
signature/annotation conformance and add a static type-check rung; documentation
must distinguish typed declarations from what Python enforces at runtime.
