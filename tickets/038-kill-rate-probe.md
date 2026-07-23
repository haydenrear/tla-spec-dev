# Probe: Do The Generated Cases Catch Real Bugs?

Status: Open

**Investigation ticket. The deliverable is a measured kill rate, not a feature.**
This answers the one question the whole fuzzing value-proposition rests on, and
it has never been answered against a runnable corpus.

## Why

The kill test (MF-016) is the only instrument that measures whether generated
cases catch bugs. It has **never produced a real number on this repository** —
its one worked example was synthetic (4/7 on a toy model), and against the real
corpus it `control_failed` because no case could execute. MF-031/MF-032 changed
that: **~10% of the corpus now executes** (the filesystem-mutating commands).

So the decisive experiment is finally possible: seed bugs into the production
behavior those runnable cases exercise, run the cases, and measure how many
bugs the cases catch.

If the cases catch the bugs, model-derived conformance testing has teeth and
"case advising" is a real offering. If they don't, the cases are too shallow —
and we learn that now, cheaply, instead of after shipping.

## The measurement

1. **Establish a green control first.** Run the unmutated, runnable corpus
   against the real adapters. It MUST pass. If the control is not green, the
   kill rate is meaningless (MF-016's own safeguard) — report that as the result
   and stop; a corpus that fails unmutated cannot measure anything.
2. **Seed a spread of realistic bugs** into the production CLI behavior the
   runnable adapters exercise (`ScaffoldProject`, `ScaffoldWorkflow`,
   `RecordBudgets`, `OpenTicket`, `InstallLocalCli`,
   `UpdateTicketDesired/Current`). Not only trivial ones. Include:
   - obvious: writes the wrong file, emits the wrong output;
   - subtle: an off-by-one in a count, a plausible-but-wrong phase value, a
     budget default set to a neighbouring number, a dropped field.
   The subtle bugs are the real test — trivial-only seeding inflates the rate.
3. **Run the generated cases against each mutant.** A mutant is *killed* if some
   case's oracle (output conformance, projected-state conformance, effect
   conformance) catches the divergence.
4. **Report the kill rate**, which mutants were killed vs survived, and — the
   analytical payoff — **what each survivor says about why the cases missed it**
   (wrong oracle, unchecked field, coverage gap, the case never exercises that
   path).

## The honest-outcome rule

**A low kill rate is a valid, valuable result. Do not tune it.** Do not seed
only catchable bugs, do not lower a threshold, do not delete a survivor. If the
cases catch 2 of 10, the answer is "the cases are shallow" and that is exactly
what the owner needs to know. This epic has repeatedly found the self-critical
result beats the tidy one — MF-016 nearly shipped a spurious perfect kill rate
and caught itself; hold that standard.

## Acceptance criteria

- A green control run on the runnable corpus, or an honest report that the
  control is not green and why.
- At least ~10 seeded bugs across the runnable adapters, spanning obvious and
  subtle, each a real behavioral change (not a syntax break).
- A measured kill rate with the kill/survive status of every seeded bug.
- For each survivor, the reason the cases missed it.
- A plain recommendation: is model-derived conformance testing worth shipping as
  "case advising", based on the number — and if the cases are shallow, what
  would deepen them (more oracles, richer projection, the Hypothesis arm).

## Out of scope

Building the Hypothesis random-generation arm. Chasing the 90% of the corpus
that does not execute (owner decided against it, MF-033). Fixing whatever the
probe reveals — this measures, it does not repair. Report, do not fix.

## Note

Use MF-016's existing kill-test machinery (`kill_test.py`, `control_run`)
pointed at the runnable corpus and real adapters, rather than the synthetic
example. MF-034 owns the corpus-OOM problem; use the reduced runnable subset and
say so, so the rate is read against the right denominator.
