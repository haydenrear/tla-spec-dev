# Promotion Must Not Destroy Files Unique To specs/current

Status: Open

Tracker: GitHub #22

Ticket promotion silently destroys regression coverage. This has fired on two
consecutive tickets and must be fixed before any further model refactor runs
the same gauntlet.

## Root cause

`promote_ticket_outputs` in `scripts/spec_evolution.py`:

```python
replace_tree(active_dir / "desired", specs_dir / "current")

def replace_tree(src, dst):
    if dst.exists():
        shutil.rmtree(dst)      # <-- destroys everything
    return merge_tree(src, dst)
```

`specs/current` is deleted wholesale and replaced by the ticket's `desired/`
tree. Because `desired/` is seeded from a different source than `current/`,
**any file that exists only in `specs/current` is destroyed** — no warning, no
failure, no record.

## Observed impact

- MF-012 (#12) and MF-020 (#21) both lost
  `specs/current/tests/test_current_ticket_workflow.py`.
- That file carried **MF-012's budgets retention test** — a *previous*
  ticket's regression coverage, destroyed by a *later* ticket's promotion.
- The file was **not in the history seal either**, so the working-tree copy
  was the only one in existence. Nothing would have recovered it.
- MF-020 additionally lost the `refinement-probe/` directory, so this affects
  directories as well as files.

Both losses were caught only because the ticket agents happened to notice and
restore by hand. The defect is silent by construction: a deleted test cannot
fail, so the suite reports green while getting smaller. That is the worst
possible failure mode for a repository whose entire purpose is mechanized
behavior retention.

## Acceptance criteria

- A file present in `specs/current` but absent from the ticket's `desired/`
  tree survives promotion — or promotion aborts, naming it. Choose one and
  document which; silent deletion is not an acceptable default for test files.
- Directories unique to `specs/current` are covered by the same rule, not just
  regular files.
- Close output enumerates every path promotion removed. No path is removed
  without a record.
- A regression test reproduces the original loss: seed a current-only test
  file, run promotion, assert it survives. It must fail against the pre-fix
  behavior — verify that it does, rather than assuming.
- The fix does not weaken the intended semantics: `specs/current` is still a
  whole-program working copy after promotion, not an accumulating union of
  every file any ticket ever produced. State explicitly how the two are
  reconciled.

## Note for the implementer

Consider whether the real defect is the asymmetry rather than the `rmtree`:
`open ticket` seeds `desired/` from one source while promotion overwrites
`current/` with it. Fixing the seeding may be the more honest repair, and may
subsume the deletion problem. Evaluate both and record why you chose one — a
guard that papers over an inconsistent seed is a weaker fix than making the
two ends agree.
