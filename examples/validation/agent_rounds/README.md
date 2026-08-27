# Agent ergonomics rounds — a reusable judged round for "is this easy to use?"

**The subject is the TOOLCHAIN, not an artifact.** `references/eval_scorecard.md`
scores an artifact's architecture on five dimensions. This round scores
something else: **how much an agent pays to get a correct result out of
`tla-spec-dev`.** Different instrument, different question, and it must not be
confused with the card — see §6.

---

## 1. What is measured, and why it is round trips rather than tokens

**The primary metric is ROUND TRIPS TO GREEN: how many times the agent had to
invoke a command, read a refusal, and try again before the operation succeeded.**

Tokens are recorded and are the BUDGET, not the score. Two reasons:

1. **Tokens are a property of the model as much as of the toolchain.** A round
   trip is a property of the toolchain: it happens because the tool answered
   one question at a time when it could have answered three.
2. **A token count cannot be acted on.** `F-01` in `FRICTION-LEDGER.md` says
   *"three sequential refusals, one file, all three knowable on the first
   read"* — that names a change. *"4,000 tokens"* does not.

**Tokens are the interception mechanism.** A task that blows its budget is
STOPPED and recorded as `BUDGET-EXCEEDED`, which is a result, not a failure of
the round.

## 2. The budget, and what happens at the ceiling

Every task declares `budget_steps` and `budget_seconds`. On exceeding either:

- the agent is **stopped**, not allowed to continue;
- the transcript up to that point is **kept** — it is the most valuable
  transcript in the round, because it is the one where the toolchain was
  hardest to use;
- the task is recorded `BUDGET-EXCEEDED` with the last command attempted.

**A BUDGET-EXCEEDED row is the headline of its round, not an omission.** The
loop the owner asked for is: *run cheap, read what the agent did, make the
change, iterate.* That loop is fed by the stopped transcripts.

## 3. The task set is DECLARATIVE and lives in `tasks.toml`

Each task declares what the agent is asked, what counts as done (a command that
returns 0, checked by the harness and not by the agent), and its budget.

**A task never tells the agent HOW.** The whole measurement is what the agent
has to discover. A task that names the flag it needs has measured nothing.

## 4. The arms — what makes this a JUDGED round rather than a stopwatch

Round trips are counted mechanically. What needs judging is **why** a round trip
happened, and that is a reading of the transcript:

| verdict | meaning |
|---|---|
| `TOOL-COULD-HAVE-SAID` | the information the agent lacked was already known to the tool at that moment |
| `DOC-COULD-HAVE-SAID` | it was in a reference page the agent had no reason to open |
| `IRREDUCIBLE` | the agent had to supply a judgement or a value nothing could have known |

**`TOOL-COULD-HAVE-SAID` is the actionable class and the only one that becomes a
change.** `IRREDUCIBLE` is the floor: a round whose trips are all irreducible is
a round with nothing to fix, and reporting that honestly is the point of having
the third value.

**Two blind judges, per `references/eval_scorecard.md`'s dispatch rules.** The
judge is handed the transcript and the task, and **not** the friction ledger —
handing a judge the answers is the one thing a measurement may not do.

## 5. Reusability — what makes a round re-runnable

- **Tasks are versioned in `tasks.toml`** with a `schema_version`. Comparing two
  rounds across a task edit is an instrument change and `R-H1` applies.
- **The toolchain under test is pinned by commit**, recorded per round. This is
  the axis the round exists to move, so it is never inferred.
- **The agent's model and effort are recorded.** A round-trip count compared
  across two models is not a fact about the toolchain.
- **A round is sealed like a scorecard round** and never edited (`R-H4`).

## 6. What this round may NOT claim

- **It does not score the five dimensions and does not touch the card.**
  `serve` byte cost: 0.
- **It does not measure whether the toolchain is CORRECT.** The test graph and
  the suite do that. A task can be completed quickly against a tool that is
  wrong.
- **It does not compare across task-set versions without saying so.**
- **`n=1` is not a measurement.** Round 0 (`FRICTION-LEDGER.md`) is one agent
  that had read the source for hours, so its costs are LOWER BOUNDS on the
  friendliest possible case.

## 7. The loop this feeds

```
run round  ->  read the stopped and expensive transcripts
           ->  file each trip as TOOL-COULD-HAVE-SAID / DOC / IRREDUCIBLE
           ->  price the fix BEFORE making it        (bug_attribution.md §7)
           ->  make the change
           ->  re-run the SAME tasks and report the delta with its denominator
```

**The change list this produces is the input to attribution**, and each entry is
a CATCH whose `channel` is this round. That is how "where are our problems"
becomes an answer rather than an impression.
