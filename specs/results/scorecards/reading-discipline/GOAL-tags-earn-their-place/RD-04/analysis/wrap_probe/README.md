# DELIBERATE FAILING INPUTS. NOTHING HERE IS A CLAIM.

Five probe files for `RD-04-DF-01`. Four of them carry **the same true figure**:
on the example `ab_quota_ledger`, all 10 cards of the subject `arm_b` — the only
`ports-and-adapters` subject that example has — carry D3 = 4.

```
python3 examples/validation/scorecards/score_tools.py scope --path <this dir>/<file>
```

| file | the sentence | verdict |
|---|---|---|
| `same_line.md` | `…10 of 10 \`ports-and-adapters\` cards of \`ab_quota_ledger\`` | `UNREACHABLE` |
| `wrapped.md` | the same, wrapped after `10 of 10` | **`REFUTED`** |
| `qualifier_after_noun.md` | `…10 of 10 cards of the \`ports-and-adapters\` subject of \`ab_quota_ledger\`` | **`REFUTED`**, one line |
| `qualifier_in_aside.md` | `…10 of 10 cards, on the example \`ab_quota_ledger\`, of arm_b's subject` | **`REFUTED`**, one line |
| `no_dimension_token.md` | four counted figures, one naming `D3` and three naming their dimension **in words** | **"1 counted figure(s)"** — three are invisible |

## What they show

**The mechanism is PLACEMENT, not wrapping.** `scope` inspects a window of at
most three words immediately after the count. A narrowing word inside that window
is seen and the figure is `UNREACHABLE`. **The same narrowing word anywhere else
— after the card noun, in an aside, or on the next line — is invisible, and the
figure is refuted at example scope**, with 25 counterexamples named, every one of
them a card about a different subject.

The wrapping case was found first and stated too narrowly. The epic owner could
not reproduce it with different probe text and identified the broader class;
`qualifier_after_noun.md` and `qualifier_in_aside.md` were added to confirm it,
and `references/architecture_tags.md` §9.8 carries the corrected statement.

**`no_dimension_token.md` is RD-02's finding, reproduced here** because it
compounds with the above: `scope` is keyed on a `D[1-5]` token, so a counted
figure that names its dimension in words is never counted at all.

Together: **RD-01's headline is itself a scoped claim whose scope nobody stated.**
Its denominator is *figures carrying a dimension token*, not *counted figures*,
and its numerator can include refutations that are artifacts of placement rather
than false claims.

## Denominator rule

At the reconciled tip the repository-wide sweep reports **58 counted figures: 26
REFUTED, 11 COUNT-MOVED, 9 HOLDS, 12 UNREACHABLE.** Attributed:

| | RD-04's files | everything else |
|---|---|---|
| REFUTED | **4 — all four are probes in this directory** | 22 |
| HOLDS | 3 | 6 |
| UNREACHABLE | 3 | 9 |
| COUNT-MOVED | 0 | 11 |

**Every `REFUTED` this ticket adds is a probe in this directory** — a demonstrated
failing input, the same way `score_tools.py scope` itself ships exiting non-zero
on this repository's own record. **RD-04 discovered no new false claim in the
historical record**; that sweep is RD-03's job.

Do not delete these files to make a count go down. That is the move the workflow
forbids.
