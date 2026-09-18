# SI-03 evals — UNMEASURED, and a 0.00 here is not a score

The issue's regression list says *"`examples/agent_integration/eval-plugin` both
cases with the checkout's shim on `PATH`"*. **That instruction is stale**: `SI-10`
replaced the shim-and-override lane with `evals/run.sh`, seven cases, one per
nested skill, run against this checkout in one command. I ran the current lane,
not the one the issue names, and say so here rather than reporting a run that
does not exist.

## What I ran, and what happened

The two cases belonging to the skill whose references this ticket changes:

```bash
evals/run.sh --case catch-the-drift
evals/run.sh --case scaffold-a-program-model
```

Both **refused to run**, identically:

```
error: the Docker (~/.docker, DOCKER_CONFIG) credential store on this machine
holds a symbolic link inside it, so the Bash sandbox cannot reliably exclude
it — a Bash-granting evaluation cannot run here
✗ catch-the-drift            score 0.00  (1 run)  $0.00
✗ scaffold-a-program-model   score 0.00  (1 run)  $0.00
```

Full transcript: `evals-spec-double-2.txt`.

## Why the 0.00 is reported as `unmeasured` and not as a result

**`$0.00` and `score 0.00` in the same row is the tell.** No model was invoked;
the harness refused before the agent existed. A 0.00 that means *the case never
started* and a 0.00 that means *the agent failed the case* are different claims,
and this repository's own record is full of the damage done by conflating a
refusal with a measurement — it is the same shape as a check whose negative
result is indistinguishable from not having looked.

So: **`unmeasured`, with the reason.** Not a zero, and not silently omitted.

## This is a known finding, already filed, and I did not re-file it

`SI-10-DF-01` (major, `pending`) records exactly this:

> Three of the seven eval cases grant Bash, and on a machine with Docker Desktop
> a Bash-granted run refuses unless HOME points at a scratch home that copies
> `~/.docker/config.json` and SYMLINKS `~/Library/Keychains` … the refusal
> message is byte-identical.

Mine is byte-identical to the message that finding quotes, on the same machine
class, one wave later. **That is corroboration, not a new finding**, so no
fifty-ninth row was appended to a 58-row cumulative file that `SI-07` is also
appending to in this same wave — concurrent appends to that file's end produced
every conflict in wave 3.

## What this costs this ticket, stated plainly

**Little, and the reason is not an excuse.** These two cases ask whether an agent
can scaffold a program model and find model/program drift. This ticket changes a
judged rubric, a second card file, and a scorecard tool under
`examples/validation/`. Neither case exercises `score_tools.py`, the card files,
or the new card kind — the eval lane has no case about the scorecard at all.

**That gap is worth naming**: the instrument this epic uses to decide its own
goals is the one surface its eval lane does not cover. Recorded here rather than
filed, for the same no-new-row reason above.
