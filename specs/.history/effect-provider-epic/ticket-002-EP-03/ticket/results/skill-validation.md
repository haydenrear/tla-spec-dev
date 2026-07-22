# Branch-local skill validation

No global `skill-manager sync` was run.

Publish metadata dry-run at the final code/docs commit:

```text
OTEL_SDK_DISABLED=true skill-manager publish . --dry-run \
  --github-url=https://github.com/haydenrear/tla-spec-dev.git --ref=c46aef1

unit:         spec-double-compiler@0.1.0 (skill)
github_url:   https://github.com/haydenrear/tla-spec-dev.git
git_ref:      c46aef1
--dry-run: not registering
```

Local install-plan dry-run:

```text
OTEL_SDK_DISABLED=true skill-manager install \
  file:///private/tmp/tla-spec-dev-79-ep03-effect-provider-examples --dry-run

DRY RUN — no changes will be made
5 resolution/install effects, 1 cleanup effect, 2 post-plan effects
exit 0
```
