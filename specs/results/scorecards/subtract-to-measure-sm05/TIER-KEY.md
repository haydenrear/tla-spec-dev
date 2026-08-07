# Judge model tier key — SM-05

**DO NOT GIVE THIS FILE TO ANY JUDGE.** It is the second axis of this round and
a judge who knows which tier they are is no longer a sample of that tier.

The tier is also self-recorded: every judge writes its own `judge.model` into its
card, so this file is a **prediction of** the assignment and the cards are the
**record of** it. If they disagree, the cards win and the disagreement is a
finding.

| subject | card | dispatched tier |
|---|---|---|
| toolchain removal | `toolchain_removal/20260807-sm05rm-K-p1` | **high** — `opus` |
| toolchain removal | `toolchain_removal/20260807-sm05rm-K-p2` | **high** — `opus` |
| toolchain removal | `toolchain_removal/20260807-sm05rm-K-p3` | **low** — `sonnet` |
| toolchain removal | `toolchain_removal/20260807-sm05rm-K-p4` | **low** — `sonnet` |
| greenfield fixture | `ab_quota_ledger/20260807-sm05gf-S-p1` | **high** — `opus` |
| greenfield fixture | `ab_quota_ledger/20260807-sm05gf-S-p2` | **high** — `opus` |
| greenfield fixture | `ab_quota_ledger/20260807-sm05gf-S-p3` | **low** — `sonnet` |
| greenfield fixture | `ab_quota_ledger/20260807-sm05gf-S-p4` | **low** — `sonnet` |

## What this axis can and cannot test

**Every one of the 41 cards this project has ever written was judged by
`claude-opus-5[1m]`.** The high tier here is therefore the *same* tier as all
prior rounds, which is what makes the greenfield arm comparable to them at all.

**The axis only runs DOWNWARD.** No judge stronger than the high tier is
available to this round. So:

- if the low tier scores a dimension the same as the high tier, that is evidence
  the dimension is pinned by something other than judging capacity **within the
  range tested**;
- if the low tier scores lower, judging capacity is implicated;
- **nothing measured here can say whether a judge stronger than
  `claude-opus-5[1m]` would score differently.** That question is not answerable
  with the judges this round has, and reporting it as answered would be false.

## The confound this design does not remove

Judge identity is **not** held constant across the two subjects. A judge who
scored both would learn the round's structure from the pair, which is the exact
contamination this round exists to avoid — so eight separate agents were used and
the subject-to-subject comparison carries a between-agent difference it cannot
separate from the subject. The tier is held constant across subjects; the
individual agent is not.
