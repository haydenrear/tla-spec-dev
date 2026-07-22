# EP-06 independent agent validation

One agent was confined to each example directory after EP-05 landed. None
edited framework production code, another example, the shared runner, the
ticket workflow, or frozen EP-03 evidence.

## Atomic publisher

- Explicit-injection `FilesystemPort`; the filesystem semantics remain
  project-owned.
- Accepted fresh-agent run: `agent-ep06-atomic-v2`.
- 14 generated cases, 224 control points, 24/24 repeated mutant executions,
  12/12 exact replays, 392/392 cleanup checks, and 7/7 real filesystem
  outcomes in 9.71 seconds.
- Hand-written baseline: 10/12; generated outcome coverage supplied two
  missing detectors.

## Legacy payment HTTP

- Self-installed `PaymentHttpPort`; the provider yields `None` while a bounded
  project compatibility scope patches `requests.Session.send`.
- Accepted fresh-agent run: `agent-ep06-http-v3`.
- 112 generated cases, 1,792 control points, 12/12 mutants, 13/13 exact
  replays, 2,477/2,477 cleanup checks, and 56/56 child-process loopback cases
  in 41.04 seconds.
- EP-05 replay retained the project virtualenv and needed no site-packages
  import-root workaround. The handwritten baseline also killed 12/12, so the
  measured value is systematic coverage/isolation/replay rather than mutation
  score lift.

## Reminder worker

- Four explicit generated ports share one repository-owned correlated bundle
  and journal.
- Accepted fresh-agent run: `agent-ep06-reminder-v2`.
- 14 generated cases, 175 control points, 12/12 mutants, 12/12 exact replays,
  271/271 cleanup checks, and 7/7 real CLI cases in 6.25 seconds.
- Hand-written baseline: 8/12; generated semantic cases supplied four missing
  detectors. All mutants were killed in iteration zero, so later fuzz points
  currently measure robustness rather than additional discovery.

The detailed reviews are the three project-local `AGENT_REVIEW.md` files.
All agents independently recommended retaining the generic provider boundary
and not promoting their concrete filesystem, HTTP, clock, queue, outbox, or
notifier implementations into the framework library.
