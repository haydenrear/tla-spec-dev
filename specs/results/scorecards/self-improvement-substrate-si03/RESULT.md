# SI-03 probe round — does the improvement card discriminate?

**These are owner tracking passes (`pass: 0`). They decide nothing.** One judge,
not blind, scoring a redaction pair this ticket built. `SI-08` runs the
two-blind-judge rounds that decide `GOAL-blockers-propose`. What this round is
for is the narrower question the ticket owes: **does the card separate a PR that
reported its blockers and proposed changes from one that did not?**

## The subjects

One real subject, in two halves — not two subjects, because two different PRs
differ in a hundred ways and none of them would be attributable to the card.

| arm | packet |
|---|---|
| `full` | PR #352 (SI-06), the complete body: 208 lines, `## Skill changes proposed`, `## Review input`, `## Deferred findings` |
| `redacted` | the same body with exactly those first two sections removed: 159 lines |

The pair is verified to differ in nothing else —
`../../epic-self-improvement-substrate/tickets/SI-03/packets/NON-VACUITY.md`:
**0 lines added** by the redaction, 48 removed, and **0 removed lines belonging
to any other section**.

## The scores

| | I1 reporting | I2 proposal | I3 disposition | I4 attribution | I5 honesty |
|---|---|---|---|---|---|
| `full` | **3** | **2** | **3** | **0** | **3** |
| `redacted` | **0** | **0** | **0** | **0** | **2** |

## What separates, and what deliberately does not

**The three dimensions those sections carry collapse to 0.** That is the card
doing the only job this round asks of it.

**`I4` is 0 on BOTH halves, and that is the result that makes the other three
readable.** The redaction removed no attribution, because there was none to
remove: a case-insensitive sweep for `unmodeled|attribut|<Module>.|action each
defect` over the full body returns **zero** hits, while the same sweep returns
one on PR #353 and one on PR #356 — so the search is not vacuous and the absence
is a fact about this subject rather than about the grep. Had every dimension
fallen, this pair would have been measuring **packet size**, which is precisely
the vacuous-control failure `SI-10` shipped once and caught itself.

**`I5` falls by one rung rather than to 0, and the reason is locatable.** The one
place the subject stated what it had *not* established is line 136 of the full
body — *"suspicion only, not reproduced … I did not establish why … rather than
trusting my account"* — and that line lives inside `## Review input`. It is
verified absent from the redacted half. What survives still cites committed
evidence paths, which is the rung below.

## What this round does NOT show

- **Nothing about whether the numbers are right.** One non-blind judge, and the
  judge wrote the card. Two blind judges agreeing within 1 is `SI-08`'s
  measurement, not this one's.
- **Nothing about any other subject.** This is one ticket PR of one wave of one
  epic. `R-H2`'s reasoning applies unchanged: a figure computed here is a figure
  about `si-06-pr352` and about no wider population.
- **Nothing about the eval card.** The two cards share no dimension and no row
  of one is comparable to a row of the other.
- **`I4 = 0` is not a criticism of SI-06 specifically.** It is the more
  interesting finding that the *epic* asks every ticket to attribute defects to
  a TLA+ action in its PR, and this one — a careful ticket by every other
  measure on this card — did not. Whether that generalises is exactly what a
  real round over several subjects would answer.

## The contamination note

**NOT BLIND**, in three separate ways, each recorded on the cards themselves
rather than discounted: the judge is this ticket's author and built the
redaction; there is one judge rather than two, at `pass: 0`; and the dispatch was
an ordinary in-session one rooted at the repository, which
`references/blind_dispatch.md` measures as *the* failing configuration — no
neutral cell, no `--safe-mode`, so the operator's memory and the commit log were
in context before the packet was opened.

Stating it is the obligation that page ends on: **stop calling a round blind that
is not.**
