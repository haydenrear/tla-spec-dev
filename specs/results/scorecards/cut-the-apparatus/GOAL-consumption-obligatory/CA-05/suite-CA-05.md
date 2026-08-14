# CA-05 — suite at the RECONCILED epic tip, measured end to end

```
uv run --with pytest --with pyyaml -m pytest tests -q
```

## Final, merged with `e379d6b` (CA-01..CA-04 all in)

```
FAILED tests/test_architecture_tags.py::test_the_same_tag_control_holds - Ass...
FAILED tests/test_goal_baseline_is_a_card.py::test_a_real_epic_plans_judged_baseline_cannot_be_re_opened
FAILED tests/test_instrument_demonstrations.py::test_every_declared_path_exists
FAILED tests/test_instrument_demonstrations.py::test_every_fast_demonstration_reproduces
FAILED tests/test_source_citations.py::test_every_line_citation_resolves_to_the_line_it_cites[specs/current/spec_manifest.yaml]
FAILED tests/test_source_citations.py::test_every_line_citation_resolves_to_the_line_it_cites[specs/desired_program_model/spec_manifest.yaml]
FAILED tests/test_source_citations.py::test_every_line_citation_resolves_to_the_line_it_cites[specs/program_model/spec_manifest.yaml]
FAILED tests/test_ticket_retirement.py::test_repository_canonical_delivered_plan_has_matching_close_receipts
8 failed, 1483 passed in 1342.81s (0:22:22)
```

**8 reds — EXACTLY the epic-tip baseline, item for item. ZERO attributable to CA-05.**

### The baseline moved 6 -> 8 when CA-04 merged, and I MEASURED that rather than assuming it

CA-04 deleted `scripts/kill_test.py` and `scripts/run_kill_test.py` and left
two `instruments.toml` rows pointing at them. It **declared both reds itself**
under `CA-04-DF-04` (*"TWO NEW SUITE REDS, DECLARED AND NOT REPAIRED"*).

My first instinct was that they were mine, from my `instruments.toml` merge
resolution. **They were not, and I checked instead of arguing:** a detached
worktree at `e379d6b`, this branch not involved —

```
$ git worktree add --detach <tmp> e379d6b && pytest tests/test_instrument_demonstrations.py -q
2 failed, 24 passed in 260.70s
FAILED test_every_declared_path_exists
FAILED test_every_fast_demonstration_reproduces
```

**Same two, at the tip, without me.** `CA-01`'s reviewer caught this project
publishing a DERIVED baseline once; deriving this one would have made the same
mistake and would have blamed CA-04's reds on myself.

| red | status |
|---|---|
| `test_the_same_tag_control_holds` | DELIBERATE — `RM-06-DF-01` |
| `test_every_declared_path_exists` | **INHERITED from CA-04**, declared in `CA-04-DF-04` |
| `test_every_fast_demonstration_reproduces` | **INHERITED from CA-04**, declared in `CA-04-DF-04` |
| `test_source_citations…` ×3 | INHERITED, undeclared |
| `test_ticket_retirement…close_receipts` | INHERITED, undeclared |
| `test_a_real_epic_plans_judged_baseline_cannot_be_re_opened` | `CA-00-DF-02` |

**None repaired, none silently touched.**

---

## All runs, including the superseded ones

| run | tree | result | note |
|---|---|---|---|
| 1 | `4616aad` | 8 / 1566 | one red beyond baseline, **MINE** — unregistered instrument, caught by the registry tripwire |
| 2 | `1a939c7` | 7 / 1568 | correct pre-merge; superseded |
| 3 | `4d6ec37` | 6 / 1539 | correct after CA-02; superseded |
| 4 | reconciled tip | **8 / 1483** | **the figure** — baseline moved to 8 with CA-04 |

Fewer tests pass in run 4 than run 3 (1483 vs 1539) because **CA-04 deleted test
files**, not because anything regressed.
