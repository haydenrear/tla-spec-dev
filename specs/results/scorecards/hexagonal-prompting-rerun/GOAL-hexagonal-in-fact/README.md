# GOAL-hexagonal-in-fact — the run record

| | |
|---|---|
| **baseline** | D3 = 1 / 1–2 / 3 / 1 / 0–1 across the predecessor's five fixtures. **Only one reached 3 and nothing ever reached 4.** |
| **measured** | **Arm B (the hexagonal + minimize-complexity ask): D3 = 4 from both judges.** Arm A (the ordinary ask): **2 from both.** |
| **target** | the prompt arm scores D3 ≥ 3 from both judges on the majority of produced artifacts, with at least one 4 |
| **verdict** | **`met`** |

## What the judges did, rather than what they read

Both arm-B judges refused to take the artifact's word for its own structure and
executed the swap.

- **The declared one-line swap was performed.** `quota_ledger/__init__.py:39` is
  the only composition point; replacing `FileJournal(ledger_path)` with
  `InMemoryJournal()` leaves the whole 28-case shared contract green with
  `domain.py` **byte-identical** — one judge confirmed with `diff -r` — and the
  ledger file provably never created.
- **Runtime call topology, not import topology.** One judge instrumented
  `builtins.open`; the other used an audit hook plus a stub port. With the fake
  bound, a full domain cycle opens **zero** files; with the real adapter, every
  `open` originates in `file_journal.py`. Rejections produce no `append` at all.
- **The parity suite was checked for the hole HP-02's pilot found** in an earlier
  draft of this prompt — `scenario(fake) == scenario(real)`, which cannot fail
  for any fault in the rules. It is not present: `--collect-only` shows 50 of 53
  cases running against both wirings, each asserting a literal expected value.

Arm A's D3 = 2 was also tested rather than inferred. Both judges tried the swap
and it does not exist: the constructor takes a path and instantiates
`_LedgerFile` itself, so passing a duck-typed fake with the right
`append`/`lines` surface raises `TypeError`, and the only working substitution
is monkeypatching a module-private name. The I/O seam is real and confined —
every file operation lives in one small class and nowhere else — which is why it
is a 2 and not a 1.

## This is the second consecutive round to reach D3 = 4, and it still cannot be attributed to hexagonality

The confound is unchanged and reproduces to the decimal: **16 lines unique to
arm A's prompt against 105 unique to arm B's — 6.6×**, on 38 shared lines.

**This round cannot separate "hexagonal guidance helped" from "a longer, more
specific ask helped" any better than the last one could.** The result is that
the D3 = 4 replicated on a fresh pair of artifacts from a fresh pair of agents;
the cause is still unmeasured, and a third arm — same length, same specificity,
no ports — is the only thing that would settle it. This epic does not run one.

## The cost side, replicated and extended

HP-06 found that the port creates a region no shared oracle reaches. This round
reproduces it and adds a second instance from a different channel:

- **The fake is verified by nothing outside arm B's own tests.** The seeded
  catalogue's mutants all live in the domain or the file adapter; nothing in any
  shared instrument executes `memory_journal.py`.
- **The blind author found a real defect there and deliberately did not seed
  it**: `InMemoryJournal.records()` returns its internal list, violating the port
  contract `memory_journal.py` itself writes down. It excluded it because arm A
  has no counterpart and a one-armed mutant turns a kill rate into two
  denominators — and recommended it be promoted later *as an asymmetric probe*,
  because it is the only fault it found that lives entirely on a surface arm B's
  architecture creates and arm A's does not.
- **A judge independently found the two implementations of the port are not
  contract-equivalent**: `'A\nB'` and `''` round-trip differently through the
  file adapter and the fake. That falsified a claim the artifact makes about
  itself and is why its D5 stopped at 3 on that card.

**So the structure's measured effect this round is: it earned a 4, it caught
nothing extra (76 of 76 comparable kill cells identical to the control arm), and
it introduced one class of fault that only exists because the port exists.**

## And the one measurable consequence of the architecture that nothing exercises

From the blind author's REJECTED section, which is again the most valuable
thing in the round:

> The two artifacts make opposite choices about ordering the durable write
> against the in-memory update, each argues for its choice in its notes, and
> **nothing in this fixture can price the difference** — the requirement
> specifies no write failure. Arm B *could* be made to price it, by injecting a
> raising `Journal`; arm A has no injection seam at all.

That is the clearest thing the port buys on this feature, it is a testability
benefit rather than a detection benefit, and **the fixture does not measure it.**
Seeding it is the single highest-value change to this catalogue.
