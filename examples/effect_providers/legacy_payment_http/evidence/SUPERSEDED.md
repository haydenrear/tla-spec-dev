# Superseded and unscored evidence

The following retained artifacts do not contribute to the accepted experiment
result:

- `local-repetition-1.json`, `local-repetition-2.json`, and raw directories
  `local-repetition-1-scored/` and `local-repetition-2/` are superseded. Review
  found that PH-05 changed the initial idempotency key instead of only retry
  attempts, replay acceptance did not require the same structured nonzero
  failure, source provenance was absent, and the repetition digest was too
  narrow.
- Raw directories `local-repetition-1/` and `local-repetition-1-rerun/` are
  infrastructure failures already marked `infra_failed_unscored`.

The preregistration was not changed. Only
`reviewed-local-repetition-1.json`, `reviewed-local-repetition-2.json`, and
their same-named raw directories are accepted.
