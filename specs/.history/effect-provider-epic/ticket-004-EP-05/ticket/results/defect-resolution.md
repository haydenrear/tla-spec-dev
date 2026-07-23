# EP-05 generic defect resolution

## DEF-001 — replay provenance

Replay construction now preserves `sys.executable` as an absolute path without
resolving a virtualenv symlink to its base interpreter. The regression creates
a temporary virtualenv, adds a module available only in that environment,
records a deterministic provider failure, changes working directory, and
replays exactly one point through the same virtualenv.

## DEF-002 — manifest parity

`load_manifest` now always uses the same constrained parser. Optional PyYAML
availability cannot select different semantics. Supported indented syntax
generates a byte-identical complete tree under normal Python and `python -S`.
Unsupported inline mappings fail closed with an instruction to use an indented
mapping instead of silently degrading typed methods.

## DEF-003 — generated signature conformance

After a provider scope enters and before adapter setup, every non-null binding
is checked against each generated Protocol method:

- parameter names and kinds;
- parameter annotations;
- return annotations.

Negative bindings with the correct method name but wrong arity, parameter
annotation, or return annotation all fail with a port/method-specific
diagnostic. Runtime validation does not execute methods to validate returned
values; generated contract tests and repository static typing remain the
behavior/type rungs.
