# Two ticket systems with similar names, and what actually differs

SI-26 requires both driven end to end and the difference stated, because an
agent that learned one will reach for the other's spelling.

## `tla-spec-dev ... ticket` — a SPEC ticket
A directory of model state under `specs/tickets/<ID>/`, holding `desired/`
(and optionally `current/`) TLA+ modules, a manifest and generated cases.
Created by `scaffold workflow <ID> "<title>"`, activated by `open ticket <ID>`,
validated by `run spec-unit-tests`, ended by `close ticket <ID>` or withdrawn
by `retire ticket <ID>`. It has no branch and no worktree. Its subject is a
MODEL.

## `skt ticket` — a WORKTREE ticket
A linked git worktree plus its own Skill Manager home. Created by
`skt ticket new <ID>`, inspected by `info`, enumerated by `list`/`sweep`,
torn down by `close` — which keeps the branch, because the work is not what is
being removed. Its subject is a CHECKOUT.

## Where the confusion bites
- Both spell the noun `ticket` and both take an ID in the same position.
- `close` means "record the model change" in one and "remove the worktree" in
  the other. `skt ticket close` deliberately KEEPS the branch; a reader who
  expects spec-ticket semantics reads that as work being discarded.
- `retire` exists only on the spec side — there is no withdrawing a worktree,
  you close it.
- `skt ticket new <ID> <base>` accepts a POSITIONAL base specifically so it
  agrees with `wt new <ID> <base>`; the spec side has no base at all.
- Measured in this gamut: `skt ticket list` from a non-repository exits 1 and
  says "not inside a git repository, or git could not list its worktrees" —
  a correct refusal that names its own fix, not a defect.
