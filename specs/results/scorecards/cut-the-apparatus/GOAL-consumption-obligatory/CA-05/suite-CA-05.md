# CA-05 — suite, measured end to end (not derived)

Command (NOT `README.md:35`, which omits `--with pyyaml` and yields 12 phantom reds):

```
uv run --with pytest --with pyyaml -m pytest tests -q
```

## Final run, at `1a939c7`

```
FAILED tests/test_architecture_tags.py::test_the_same_tag_control_holds - Ass...
FAILED tests/test_goal_baseline_is_a_card.py::test_a_real_epic_plans_judged_baseline_cannot_be_re_opened
FAILED tests/test_price_removal.py::test_nothing_in_the_repository_invokes_the_pricer
FAILED tests/test_source_citations.py::test_every_line_citation_resolves_to_the_line_it_cites[specs/current/spec_manifest.yaml]
FAILED tests/test_source_citations.py::test_every_line_citation_resolves_to_the_line_it_cites[specs/desired_program_model/spec_manifest.yaml]
FAILED tests/test_source_citations.py::test_every_line_citation_resolves_to_the_line_it_cites[specs/program_model/spec_manifest.yaml]
FAILED tests/test_ticket_retirement.py::test_repository_canonical_delivered_plan_has_matching_close_receipts
7 failed, 1568 passed in 1166.35s (0:19:26)
```

**7 reds — EXACTLY the epic baseline, item for item, no more and no less.**

| red | status |
|---|---|
| `test_the_same_tag_control_holds` | DELIBERATE — `RM-06-DF-01` |
| `test_nothing_in_the_repository_invokes_the_pricer` | DELIBERATE — pricer grep |
| `test_source_citations…[specs/current/spec_manifest.yaml]` | INHERITED, undeclared |
| `test_source_citations…[specs/desired_program_model/spec_manifest.yaml]` | INHERITED, undeclared |
| `test_source_citations…[specs/program_model/spec_manifest.yaml]` | INHERITED, undeclared |
| `test_ticket_retirement…delivered_plan_has_matching_close_receipts` | INHERITED, undeclared |
| `test_a_real_epic_plans_judged_baseline_cannot_be_re_opened` | `CA-00-DF-02` |

**None repaired. None silently touched. Nothing attributable to CA-05.**

---

## First run, at `4616aad` — recorded because a discarded run is evidence about method

```
FAILED tests/test_architecture_tags.py::test_the_same_tag_control_holds - Ass...
FAILED tests/test_goal_baseline_is_a_card.py::test_a_real_epic_plans_judged_baseline_cannot_be_re_opened
FAILED tests/test_instrument_demonstrations.py::test_the_named_instruments_are_all_enumerated
FAILED tests/test_price_removal.py::test_nothing_in_the_repository_invokes_the_pricer
FAILED tests/test_source_citations.py::test_every_line_citation_resolves_to_the_line_it_cites[specs/current/spec_manifest.yaml]
FAILED tests/test_source_citations.py::test_every_line_citation_resolves_to_the_line_it_cites[specs/desired_program_model/spec_manifest.yaml]
FAILED tests/test_source_citations.py::test_every_line_citation_resolves_to_the_line_it_cites[specs/program_model/spec_manifest.yaml]
FAILED tests/test_ticket_retirement.py::test_repository_canonical_delivered_plan_has_matching_close_receipts
8 failed, 1566 passed in 1179.78s (0:19:39)
```

**8 failed — one beyond baseline, and it was MINE:**

```
test_instrument_demonstrations.py::test_the_named_instruments_are_all_enumerated
  1 executable(s) under a declared instrument root have no row in
  instruments.toml: ['scripts/disposition.py']
```

I shipped an instrument and did not register it. That is the
`registry-enumeration-coverage` tripwire — `SM-03`'s repair of `FI-04-DF-04` —
doing exactly its job, on its first opportunity, against a genuinely new
executable.

**Not a baseline red, so REPAIRED rather than declared-and-left**, by the remedy
the registry's own message prescribes: add a row, never extend a list.

**A channel result worth recording:** the charter defunds the suite as a
*finding* channel while keeping its regression-guard job. On this ticket the
suite did that job, against this ticket, and cost one line of output to read.

---

## Instrument demonstrations, all slots

```
26 passed in 225.68s (0:03:45)
```

26 passed — every `failing` / `passing` / `blind_spot` slot in the registry
reproduces, including the three added for `epic-disposition`.
