# EP-04 skill validation

The repository skill was validated without updating the installed copy:

```text
skill-manager install file:///private/tmp/tla-spec-dev-99-ep04-agent-provider-interface --dry-run
```

Result: exit 0. Skill-manager resolved the local unit and produced an
eight-step dry-run plan with no changes. Installed-skill synchronization is
intentionally deferred until the epic lands on `main` so agents cannot observe
an unintegrated branch.
