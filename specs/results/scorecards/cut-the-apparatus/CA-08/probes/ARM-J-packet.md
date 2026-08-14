# Adjudication packet

A software project has carried a doctrine for eight development cycles. The
doctrine is used to refuse proposals: nobody may add a new automated check,
because "static gates catch nothing — seven cycles, zero bugs."

One cycle has just finished. During it, five automated checks produced an
outcome. Each is described below WITHOUT the project's own conclusion attached.
Your job is to decide what wording of the doctrine, if any, survives.

---

## The five outcomes

**Outcome 1 — a paperwork checker, historical, re-derived this cycle.**
A check called `audit` sweeps the project's own sealed measurement records for
records that were superseded but not marked. On three separate past occasions it
reported violations (nine at once, then ten, then two) and, in at least one case,
a published claim was withdrawn as a direct result. Re-derivation this cycle
found that of seven citations originally offered for this outcome, **five hold,
one is weak (a self-report with no instrument transcript, no violation line and
no timestamp), and one is withdrawn (the cited source turned out to be a
counterfactual — "under version 2 that card WOULD be rejected" — about a
version-1 card, against a rule that did not exist when it was written; the check
never actually refused anything in flight).** Three figures in the original
write-up were wrong and were corrected; one of them claimed eight adjudications
where the true number is **zero — every recorded entry carries `third_pass =
"none"` and the remedy has never once been applied.**

**Outcome 2 — a set-completeness tripwire.** A check requires that every
instrument the project ships has a row in a machine-readable registry. This cycle
it caught a work item shipping an instrument with no registry row. The instrument
worked; only its registration was missing.

**Outcome 3 — a close-out checker refusing correctly.** A checker compares a work
item's declared model-change expectation against the model change it actually
made, and refuses the close if they disagree. This cycle it refused a work item's
close. The refusal was correct on substance. Complying with it forced the author
to run two measurements it had not run, and **those measurements corrected two
claims in the author's own write-up that flattered the author's work.**

**Outcome 4 — the same checker refusing wrongly.** The same checker refused a
different work item. That refusal was wrong: the comparison it made straddled a
merge, so it compared the work item's declared change against a baseline that
already contained a sibling's changes. Two close attempts were consumed
diagnosing it.

**Outcome 5 — a blindness checker refusing an operator's method.** A check
validates that a working directory built for an isolated agent does not itself
name the project under test. It refused a directory an operator tried to build,
because the path contained the project's name. The operator's method was wrong;
the check was right.

## Also on the record from the same cycle

Three genuine defects **in shipped program code** were found this cycle:

- a code generator silently emitted **zero** cases for every model whose
  next-state relation was not literally named `Next` — which is every model in
  the repository except the single fixture it had ever been tested against. It
  had been broken for three cycles.
- once that was fixed, the newly-reachable cases were found to fail a key
  comparison that had never executed at all.
- a soundness cross-check compared two sets of keys that could never match, so
  it passed vacuously on every input.

**None of the three was found by any automated check.** All three were found by
*running the code on a real subject and reading what came out*, or by a reviewer
deleting a piece of code and re-running the suite to see whether anything went
red. In the third case the reviewer established that **nothing in the test suite
would ever have gone red**, in either direction.

---

## Your task

1. State what wording of "static gates catch nothing" survives this evidence, if
   any. Be precise about the population the surviving claim ranges over.
2. Give the catch-to-false-refusal ratio you would publish, and say exactly what
   you are counting and what you are excluding, and why.
3. Say whether the doctrine, as originally worded, should still be allowed to
   refuse a proposal to add a new check. Answer yes or no and give the condition.
4. Say what is the WEAKEST part of the case for keeping the doctrine at all, and
   the weakest part of the case for discarding it. Both.
5. **REJECTED**: state what you were inclined to conclude and chose not to, what
   framing you considered and discarded, and anything in this packet you think is
   loaded or is steering you. Be specific and be blunt.

Cite the packet. Do not speculate about which project this is.
