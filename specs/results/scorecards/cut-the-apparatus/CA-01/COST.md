# CA-01 — cost, with the basis named

`CL-04` proposed a `cost` block with `basis` and `value` three epics ago and
nothing has recorded one since, **because nothing asked**. Issue #255 asks.

**The basis is named first, because a token figure without one is the thing
`SV-05` §13 complained about.** Three components, and they are NOT the same
quality of measurement. They are reported separately and never summed into one
headline.

---

## A. Dispatched subagents — EXACT, harness-reported

Four probe agents, each reported by the harness on completion:

| arm | agent type | subagent tokens | tool uses | duration |
|---|---|---|---|---|
| A | `general-purpose` | 20,672 | 0 | 170 s |
| B | `Explore` | 13,258 | 0 | 154 s |
| C | `claude` | 20,779 | 0 | 171 s |
| D | `general-purpose` (judge-shaped) | 20,656 | 0 | 174 s |
| **total** | | **75,365** | **0** | **669 s** |

`basis: harness-reported subagent_tokens, summed over the four dispatched
probes.` `value: 75,365 tokens.`

Zero tool calls across all four — the probe forbade them, so this is pure
context-in / report-out.

## B. CLI arms — MEASURED BYTES, token figure ESTIMATED

Two separate `claude -p` processes. The harness does not report their token
usage back to this session, so **bytes are measured and tokens are an estimate**,
and the two must not be confused.

| arm | reply bytes | wall clock |
|---|---|---|
| `ARM-N` (neutral cell) | 45,192 | ~150 s |
| `ARM-O` (repo cwd) | 56,436 | ~170 s |
| **total** | **101,628** | |

`basis: measured reply bytes; tokens estimated at ~4 bytes/token for output,
plus an unmeasured input side (each arm received the full ~40-entry skill
listing and system prompt).` `value: ~25,000 output tokens, input side NOT
MEASURED.`

**The input side is the larger half and it is not measured.** Stated rather than
guessed, because guessing it is how a cost figure becomes decoration.

## C. This ticket agent's own session — NOT MEASURED

`basis: unavailable.` The token count for this session is not exposed to the
agent running in it, and no instrument in this repository computes one.

**Reported as unmeasured rather than estimated.** A plausible-looking number
invented here would be the same error `SV-05` §13 names, committed in the file
that exists to correct it.

Lower bound on the shape, since a shape is better than nothing: ~40 tool calls,
4 dispatched agents, 2 CLI subprocesses, 1 full repository test suite, 11
evidence files written.

---

## What it bought, per unit

The four probes at **75,365 tokens** produced:

- the measured inventory that decides `GOAL-blind-dispatch` clause (a);
- the correction of `SV-05-DF-02`'s *4 of 4* to a tier (`CA-01-DF-03`);
- two of the three real subjects the `R1` demonstration refuses;
- and the judge's own *"a live temptation to spread my scores to reproduce the
  known noise profile"* — the sharpest sentence in the ticket, produced by an
  agent, not by the operator.

**The channel is blind agents again**, which is where `SV-05` §8 recorded 8 of
26 findings. Five of this ticket's five filed findings came from reading agent
output or the harness's own text; **none came from the suite**, which for this
ticket produced no finding at all.

---

## The honest note on this file

A cost block that only ever records the cheap, exact component (A) and writes
"unmeasured" for the expensive one (C) will understate every future comparison.
**A is 75,365 tokens and is almost certainly the smallest of the three.** Whoever
next asks for a cost should ask for C first, and should fund the instrument that
can produce it — otherwise this block will be filed for a fourth epic and still
not say what the round cost.
