# modular-fuzzing epic — handoff to the next epic owner

You are taking over as **epic owner** of `epic/modular-fuzzing`. Read this
before touching anything.

---

## 1. Why this epic exists

`tla-spec-dev` claims that a program's complexity can be *measured* from a TLA+
model, *minimized* by architecture rather than by lowering standards, and that
the minimization is *safe* because a constraint set catches you cheating.

The epic mechanizes that claim. Doctrine lives in
`references/modular_fuzzing.md` and `references/architecture_tractability.md`;
the latter's **"No Degenerate Escapes"** section is the governing law and
outranks any older conflicting text.

Five rules, from the repository owner:

1. **Complexity is pushed out, not accommodated.** When a measurement is bad,
   the architecture changes — not the measurement, not the thing measured.
2. **The tools inform the architecture.** Their output is input to a design
   decision, never a number to satisfy by other means.
3. **Never game a metric by removing evidence.** No dropping, filtering,
   suppressing, or silencing — not even with a recorded rule.
4. **The diagram is a faithful representation of the program.** If the program
   cannot be represented, **the program changes.** No third option.
5. **The diagram has strict complexity limits.** Caps are hard gates. Raising
   one is an explicit recorded decision, never a flag or fallback.

**A rule with an escape hatch is not a rule.** If you find yourself writing "or
record a justification", "unless overridden", "falls back to", or "when
present" into a gate — write the failure instead.

---

## 2. Where it actually stands

**15 tickets merged and accepted. 10 remain.** The plan
(`specs/desired_program_model/ticket_plan.yaml`) is the source of truth; GitHub
issues mirror it.

The epic built four oracles, a complexity analyzer, per-program budgets, a
mechanized ledger with anti-gaming, and a coverage audit. **All of that works.**

Then MF-023 pointed the finished toolchain at this repository — and the
substrate underneath the gates did not hold:

- **`analyze complexity` does not resolve `EXTENDS`.** It uses it as a *parse
  terminator*, so a decomposed model is scored on a fraction of itself. Fewer
  variables means a smaller bound, so **the error always points at PASS.** The
  epic's binding gate silently disables itself on the architecture `SKILL.md`
  mandates.
- **No adapter could execute a generated case.** All 16 implement
  `apply(target_repo, ...)`; the corpus path calls `run(case, ...)`. Three of
  four oracles produced no signal at all.
- Two adapters (`UpdateTicketDesired`, `UpdateTicketCurrent`) **do not exist**,
  blocking 72.5% of the corpus.
- `analyze corpus` is **OOM-killed by the corpus it exists to catch**. Every
  corpus figure recorded in this epic came from a reduced config.
- `max_component_actions: 8` is **unsatisfiable by any partition** of this
  model. It counts commands, not coupling.

**This is the epic working, not failing.** MF-019's ledger refused the close,
MF-026's audit returned FAIL, MF-016's control run refused to report a
flattering kill rate, and the agent declined to self-merge because its
authorization was conditional on a green matrix. The gates caught a broken
substrate before it shipped.

Two spikes then replaced guesswork with measurement: **MF-028** found
before-state materialization is cheap (`setup_phase` is an ordinal, so a
before-state is a command *prefix*), and **MF-029** proved action parameters are
recoverable from the state pair with no model change at all.

---

## 3. What to run, in order

Strictly serialized — each ticket's `promotion_predecessor` must be merged
before the next branches.

| Order | Ticket | Issue | Why it matters |
|---|---|---|---|
| 86 | **MF-030** Resolve `EXTENDS` | #55 | **Do this first.** Until it's fixed the gate passes on exactly the architecture MF-023 produces. |
| 87 | MF-031 Two missing adapters | #56 | 72.5% of the corpus is blocked by absence. |
| 88 | MF-032 Case execution, remaining 15 | #57 | 2 trivial / 4 moderate / 5 hard / 4 blocked. **Do not extrapolate MF-028's ~29-line figure** — it holds for 2 adapters and not the hard ones. |
| 89 | MF-033 Out-of-process effect observation | #58 | `run()` alone does **not** restore oracle 3. Second axis, absent from the original plan. |
| 90 | MF-034 Stream the corpus | #59 | Last thing between the toolchain and a full-scale run. |
| 91 | MF-035 Silent default + alpha model pick | #60 | Two bounded defects. Neither may be fixed by adding a flag. |
| 92 | MF-036 Component-metric decision | #61 | **Design decision — needs owner approval. Do not change the doctrine unilaterally.** |
| 95 | MF-023 Decompose by dogfooding (retry) | #30 | Open PR #50 holds the prior attempt. Don't duplicate it. |
| 96 | **MF-037 Three validation projects** | #62 | See §6 — this is the point. |

---

## 4. How to work

**Dispatch sub-agents. Do not implement tickets yourself.** One at a time,
because the promotion chain is serialized.

For each ticket:

1. **Render the assignment block into the issue before dispatching.** Most
   issues currently carry scheduling only. The block needs `plan_commit` (the
   current epic tip), `schedule_revision`, `promotion_predecessor`,
   `feature_branch`, `worktree`, the validation matrix, **and the
   repository-owner deviation note authorizing self-merge**. Omitting that note
   once already caused an agent to correctly refuse to merge.
2. **Dispatch via the `git-issue-workflow` skill in epic mode.** Tell the agent
   the issue body is authoritative — if your brief and the issue disagree, the
   issue wins. Agents have correctly overridden briefs twice.
3. **Verify independently when it lands.** Re-run the suites yourself; check the
   load-bearing claims against the repo. Do not accept a report at face value.
4. **Hand it to the repository owner for review.** Do not close the issue
   yourself — the owner reviews after you do.

### Standing constraints — all non-negotiable

- **Never merge to `main`.** It sits at `da0a7ff` and must stay there.
- **Never run `skill-manager sync`** or update `$SKILL_MANAGER_HOME`.
- **Never invoke `tla-spec-dev` from PATH** — it execs the installed clone at
  `da0a7ff`, containing none of this epic's work. Use
  `python3 scripts/tla_spec_dev.py --spec-root specs ...`.
- **Run pytest with `--with pyyaml`** or the YAML-validity guard skips silently.
- **The spec-case execution deferral has ENDED.** It applied through MF-022;
  from MF-028 onward, runs are expected.
- **Carry `max_distinct_states: 500000` and its rationale comments** through
  each ticket's `desired/` and verify post-promotion. That block lives only in
  `specs/current/spec_manifest.yaml`, which promotion overwrites — the SF-003
  blind spot (#32).
- **Validate the plan YAML after every edit.** It has been broken twice, once
  by the epic owner. `tests/test_spec_yaml_valid.py` guards it now.

---

## 5. Epic-owner mistakes to avoid repeating

The previous owner made six spec-level errors. Every one was caught by a ticket
agent, not by review:

1. Propagated a **−13.1% projection** as a target; it required deleting a real
   transition.
2. Gated a **static bound against `max_distinct_states`** — incommensurable
   quantities, ~400× apart.
3. Wrote **self-contradictory acceptance criteria** into MF-022.
4. Told a ticket the **732-case corpus was committed**; `git ls-files` says 0.
5. Created **#38 without an assignment block**, so its agent correctly refused
   to self-merge.
6. Said **"thirteen labels"**; there are 14 plus `Stutter`.

The pattern: a plausible figure asserted without checking what it meant. **Tell
every agent your brief may be wrong and the issue is authoritative.** Two agents
have corrected briefs; both were right.

---

## 6. The goal: MF-037

Everything above is preparation for this.

MF-023 dogfoods against `tla-spec-dev` itself — **one shape**. Real users arrive
with others. MF-037 scaffolds three example projects and dispatches **real
agents doing real tickets** against them:

1. **Scaffold-only** — the entry path a new user hits first.
2. **Ticket workflow** — like `examples/distributed_history`. Note
   `run_distributed_history_validation.py --mode local` currently **cannot
   complete** (its External model is refused by the complexity gate, verified
   pre-existing), so that must be resolved first.
3. **A deliberately over-complex project** — where the agent must **lower** the
   complexity of the diagram.

The third is the sharpest test in the entire epic, and the only falsifiable one:

> **Complexity must go DOWN while behavior is retained. An agent that raises a
> budget, waives a gate, or reaches for an override instead has FAILED THE
> VALIDATION — not the example.**

Define expected behavior **before** dispatching, so "as expected" is a
prediction rather than a post-hoc reading. Run each example more than once;
divergence between runs is itself a finding about instruction determinism. File
toolchain findings rather than fixing them inline — the validation is a
measurement, and fixing while measuring destroys it.

The owner's rationale, in their words: *"correctness the first time is worth a
bit of extra validation."* Every gate this epic built has value **only** insofar
as it changes what agents actually do. MF-037 is where that gets tested.

---

## 7. After the epic

A report and a set of visualizations of what the epic did. The material is
already dense: the `notes:` block in `ticket_plan.yaml` is a full chronological
record, and each ticket has a complexity ledger under
`specs/.history/modular-fuzzing-epic/*/results/`. Natural series include the
state-space and declared-bound trajectory, budget utilization against caps, the
six spec-level errors and how each surfaced, and the measured reductions that
were deliberately **refused** — MF-027 turned down 47%, MF-016 turned down
26.2%, both because the reduction would have cost a boundary.

That last series is the epic's real thesis: **a toolchain that refuses its own
flattering numbers.**
