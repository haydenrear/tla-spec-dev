# The artifact was not copied, renamed or regenerated. It is the same file.

**Verified, not assumed.** A stability measurement whose subject moved is not a
stability measurement, and "byte-identical" has been asserted in this project
before it was checked.

## 1. The judges scored the sealed trees IN PLACE

FI-03's judges were pointed at
`specs/results/scorecards/ports-as-adapters/blind/artifact_{T,U,W}/` — the very
directories PA-06's judges read. **No copy was made, so no copy could drift.**

The git tree object for that directory is unchanged from the commit that
recorded it to the commit FI-03 branched from:

| commit | `blind/` tree object |
|---|---|
| `8878cd5` — PA-06, the commit that recorded the blind copies | `2947d07077e7281c4354ac077ef32cd3e1173be5` |
| `51fe73d` — FI-03's parent | `2947d07077e7281c4354ac077ef32cd3e1173be5` |
| `HEAD` at scoring time | `2947d07077e7281c4354ac077ef32cd3e1173be5` |

`git log --oneline -- specs/results/scorecards/ports-as-adapters/blind/` returns
exactly one commit, `8878cd5`. The working tree was clean over that path
throughout.

Per-file digests, recorded so a future reader can check without git:

```
ce8f65aed7dda1f61cdfab38baef4fcac56d1cced08fae3d540ff97a8ef92f3c  artifact_T/EVIDENCE.md
1f45c347f181b58579dc4d83e81d7683a1ba169e0f1839d62226c3d0304714fb  artifact_T/NOTES.md
818e941e3d01b961a703b8a23d0705009e832325b5f91d6f9a3bc3716fdb9a53  artifact_T/quota_ledger/__init__.py
fe9ebd5558cbcf7cdc286aaba75467177053a22d0ee121cc6283555ba032e567  artifact_T/quota_ledger/domain.py
5aadad3196596464ed8a3409d845d4c7767e528445c66d1d8e81b9f878530a3f  artifact_T/quota_ledger/file_journal.py
019ecdb1c03dde8a0dfc6554157575d8a23efeb27cdb74b23d2ad3418802ddef  artifact_T/quota_ledger/memory_journal.py
afcb9792e156f4d8979c4e12ce8a5327600425d00c7cb39a330081a34cbc0c99  artifact_T/tests/test_ledger.py
b399477065b84a8279b770274f256618d2c26deea078aa1714fd19079b1d8852  artifact_U/EVIDENCE.md
3a9493f611e9d211a4c701b69617b4b10f2d08f03120164255a9454edfebdb26  artifact_U/NOTES.md
213b2a5e27c6ec281b7d4c353e4d39d029fe152f49eae187c05fc2fa29458ca3  artifact_U/quota_ledger.py
94434f26e1c3ecbfd37382608e3401f4cbaa99d4339aaeaabf7ff197cecfe26c  artifact_U/test_quota_ledger.py
98d548cf89ee423774867522e9cb437873fd6adcf4cf3169dd48e5c338ac0973  artifact_W/EVIDENCE.md
293345b4083efaeb1a5176bd0c5ec0af68f451626c0ca1368e0aeff3f5d95437  artifact_W/NOTES.md
6f1af243890fd2ad109887cb46f6a3d8976a783bbd40bef8da3392da70699de3  artifact_W/quota_ledger.py
4da00df44eba13db8a6fdbd372300e0870305938723fc8d5c7145c5f82c214fa  artifact_W/test_extra.py
```

## 2. The arm sources behind them are unchanged since EVAL-RERUN

The blind copies are sanitised renderings of `examples/validation/ab/arm_{a,b}`.
Those two trees are byte-identical from the round EVAL-RERUN judged to this one:

| commit | `arm_a` | `arm_b` |
|---|---|---|
| `b3a0199` — EVAL-RERUN | `4e99660…` | `01a8ca3…` |
| `930fa57` — the sha PA-06's cards record | `4e99660…` | `01a8ca3…` |
| `8878cd5` — PA-06's own commit | `4e99660…` | `01a8ca3…` |
| `51fe73d` — FI-03's parent | `4e99660…` | `01a8ca3…` |

So the chain PA-06 asserted — *"sealed predecessor artifact, byte-identical to
the one EVAL-RERUN judged"* — holds at the tree-object level across all four
commits, and FI-03 is scoring the same bytes a third time.

## 3. The labels were REUSED, deliberately, and it cost something

`score_tools.py scaffold` refuses to reuse an arm label any prior round
published, precisely so a judge who stumbles into a sealed run cannot read the
arms off it. FI-03 overrode that with `--labels T,U,W`.

**The reason is that the alternative was worse.** Relabelling requires copying
the trees and substituting the label inside each `EVIDENCE.md`, which are five
edits per packet — and the packet is part of what is scored. A measurement whose
whole premise is byte-identity cannot begin by editing the subject. Reusing the
label leaves the artifact untouched and puts FI-03's judges in **exactly** the
blinding position PA-06's judges were in: same labels, same key file, same
forbidden list.

**What it costs:** PA-06's `UNBLINDING.md` and `RESULTS.md` now map `T`, `U` and
`W` to arms. Both files were on the forbidden list and both judges reported not
opening them, but the exposure is real and it did not exist for PA-06's own
judges. Recorded here rather than argued away.

## 4. What is NOT byte-identical, and it matters

**The rubric changed between PA-06's judging and FI-03's, and the rubric digest
did not notice.** `references/eval_scorecard.md` gained the "Known instability
of this card" section at `d3f483d`, *after* PA-06's judges scored at `8878cd5`.
Its parsed digest is `sha256:e33638087c4191da` on **both** sides, because the
digest covers the anchors and the numbered scoring rules and nothing else.

Both FI-03 v1 judges cited that section, unprompted, as a reason for how they
judged. So the "v1" arm below re-scores the card **as it stands today**, which
is what the ticket asked for — and it is not a replication of the card PA-06's
judges held. Filed as `FI-03-DF-02`.
