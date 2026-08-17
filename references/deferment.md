# Deferment policy

Epic tickets fail in a characteristic way: validation surfaces a real defect that
sits outside the ticket's declared slice, the agent fixes it, the fix breaks a
sibling surface, and the ticket expands until its evidence no longer describes
the semantic delta it was assigned. Deferment makes the alternative explicit —
the agent **reports** the finding and the epic owner decides when it becomes
work.

The policy is agreed once, at epic creation, and applies to every ticket agent
and to finalization.

## Scope classification

Before any finding can be deferred it must be classified. A finding is
**in scope** for the current ticket only when *all* of these hold:

- every file/surface the fix touches is covered by this ticket's
  `conflict_keys`;
- the fix changes no TLA+ action, invariant, or adapter mapping outside this
  ticket's declared semantic delta;
- the ticket's own desired model already implies the corrected behavior.

Anything else is **out of scope**, including: defects in already-promoted
sibling tickets, latent bugs the ticket merely exposed, missing coverage on
untouched surfaces, flaky infrastructure, and refactors the fix would be
"cleaner" with. Out-of-scope findings are candidates for deferment. In-scope
findings are simply the ticket's work — fix them and say nothing about
deferment.

A finding is **blocking** when the ticket's REQUIRED validation matrix cannot
pass without touching an out-of-scope surface. Blocking out-of-scope findings
are never silently deferred and never silently fixed: the agent stops and
returns the ticket to the epic owner (see *Escalation*).

## Policy record

Set once during planning, stored in `specs/desired_program_model/ticket_plan.yaml`
next to `schedule_revision`:

```yaml
deferment_policy:
  mode: batch            # batch | ask | inline
  blocking: escalate     # escalate | ask   (blocking findings only)
  budget: 5              # max deferred findings per ticket before the agent stops
  backlog: "specs/desired_program_model/deferred_findings.yaml"
```

Modes:

- **`batch`** (default, recommended) — the agent records every out-of-scope
  finding to the backlog and continues its assigned slice. No interruption, no
  inline fixes. The owner triages the backlog between waves and at finalization.
- **`ask`** — the agent records the finding, then asks the owner whether to open
  a ticket now or batch it. Use when the epic touches load-bearing surfaces and
  a latent defect changes the plan.
- **`inline`** — the agent may fix out-of-scope findings within its own conflict
  keys' blast radius, and must still record what it fixed and why. Use only for
  small epics with a single active ticket; it reintroduces the spiral in
  parallel waves.

`budget` is the anti-spiral guard and applies in every mode. When a ticket
accumulates more than `budget` out-of-scope findings, the agent stops
implementing, files the backlog entries, and reports that the ticket's premise
looks wrong. Repeated deferrals are a signal that the plan is off, not a queue
to drain.

The canonical plan is authoritative for the policy. Assignments mirror it for
readability, but a ticket agent re-reads the plan entry before acting on it, so
the owner may change the policy mid-epic without bumping `schedule_revision` or
invalidating dispatched assignments.

## Backlog format

`specs/desired_program_model/deferred_findings.yaml` is append-only. Agents add
entries; only the epic owner edits `disposition`.

```yaml
findings:
  - id: DEF-003                      # sequential, never reused
    found_by: "<ticket-id>"
    found_at_commit: "<sha>"
    schedule_revision: 3
    severity: blocking | major | minor
    surface:
      production: ["<path>"]
      tla: []
      adapters: []
      test_graph: []
    summary: "<one line: what is wrong>"
    reproduction: "<exact command + observed vs expected>"
    evidence: ["<path under the ticket evidence root>"]
    why_out_of_scope: "<which conflict key or semantic boundary it crosses>"
    suggested_fix: "<one line, or 'unknown'>"
    blast_radius: "<other tickets/surfaces a fix would touch>"
    disposition: pending             # pending | ticketed | wontfix | fixed-inline
    disposition_ticket: null         # spec ticket ID once promoted
```

An entry with no reproduction is not a finding, it is a hunch — do not file it.

## Ticket-agent behavior

1. Classify the finding. In scope → fix it as ordinary ticket work.
2. Out of scope and blocking → apply `deferment_policy.blocking`.
3. Out of scope and non-blocking → append a backlog entry, then follow
   `deferment_policy.mode`. In `batch`, continue. In `ask`, ask now-or-batch. In
   `inline`, fix only within the ticket's conflict keys and set
   `disposition: fixed-inline`.
4. Commit backlog entries with the ticket's normal commits. The backlog is
   planning data, not spec state: it never enters ticket-local `desired/` or
   `current/`, and it is never evidence for a ticket close.
5. Report deferred findings in the ticket PR body under a
   `## Deferred findings` heading, one line per ID.

A deferred finding never justifies weakening a REQUIRED validation entry,
loosening an invariant, marking a test skipped, or closing a ticket whose
equality gate fails.

## Escalation

When a blocking out-of-scope finding appears and `blocking: escalate`, the agent:

- stops implementation at the current commit;
- files the backlog entry with `severity: blocking`;
- pushes the branch without closing the spec ticket or opening a promotion PR;
- reports: the finding, the ticket it blocks, the surfaces a fix would touch,
  and which sibling tickets share those conflict keys.

The epic owner then either inserts a repair ticket ahead of it in the promotion
lane, rescopes the blocked ticket's conflict keys, or drops the ticket. The
agent does not make that call, and does not "unblock itself" by widening scope.

## Owner triage

Triage the backlog at two points.

**Between waves, when recommending the next issue.** Present pending findings
alongside the ready issue list so the owner sees defects and schedule together.
That presentation is a section of the wave review artifact, not a separate
message — `references/human-review.md` §3.5, where it sits next to the hot
spots, the overrides, and the goal trajectory that give each finding its weight:

| ID | Found by | Severity | Summary | Blast radius | Disposition |
| --- | --- | --- | --- | --- | --- |

For each pending finding, offer exactly three outcomes: promote it to a new
spec ticket now (new stable ID, dependency edges, wave, promotion order,
conflict keys, revalidated schedule, `schedule_revision` bump, new issue), keep
it batched for finalization, or close it `wontfix` with a recorded reason.
Recommend batching unless the finding blocks a planned ticket or grows more
expensive the longer it sits.

Promoting a finding is an ordinary plan change: add the ticket, rerun
`scripts/validate_epic_plan.py`, bump `schedule_revision`, re-render affected
assignments. Never retrofit a deferred fix into a dispatched ticket's scope.

**At finalization.** No pending findings may remain. Every entry ends as
`ticketed` (and merged), `wontfix` (with a reason), or `fixed-inline`. Findings
carried past the epic become issues on the default branch, referenced from the
epic PR body — deferring is a scheduling decision, not a way to lose defects.
