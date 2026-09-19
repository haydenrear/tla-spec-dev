# GOAL-progressive-disclosure — local signal, SI-09

Instrument (pinned by the epic owner; reproduces the kickoff baseline exactly):

    awk 'BEGIN{fm=0} /^---$/{fm++; next} fm>=2' skills/<name>/SKILL.md | wc -w

Control: spec-double-2 at base commit b0e6b54c measures 1839 by this method,
matching baseline/kickoff.md's table. A plain `wc -w` counts frontmatter and
inflates every figure; it was not used.

| card | description before -> after | body before -> after |
|---|---|---|
| discovery | 91 -> 61 | 1096 -> 996 |
| git-epic-workflow | 248 -> 72 | 4652 -> 1820 |
| git-integration-repo | 117 -> 76 | 1885 -> 1343 |
| git-issue | 149 -> 83 | 3083 -> 1499 |
| git-issue-workflow | 301 -> 97 | 4270 -> 1775 |
| plugin-repository | 174 -> 87 | 1517 -> 1466 |
| spec-double-2 | 82 -> 73 | 1839 -> 1499 |
| test-graph | 55 -> 51 | 1899 -> 1332 |
| TOTAL | 1217 -> 600 | 20241 -> 11730 |

Verdict, one per clause (multi-clause target):
- descriptions <= 600 total: MET, at exactly 600.
- every card body <= 1500: MISSED on 2 of 8 (git-epic-workflow 1820,
  git-issue-workflow 1775). Filed as SI-09-DF-03 rather than closed by deleting
  instruction. Six of eight cards meet the clause.
