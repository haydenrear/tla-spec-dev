# Superseded diagnostic run

This run intentionally remains as failure evidence. Regeneration passed, but
the old repository-wide dirty-worktree audit rejected an unrelated root test
created by a concurrent agent before the HTTP validation started. The accepted
v3 run uses validation-start and post-campaign byte snapshots instead.
