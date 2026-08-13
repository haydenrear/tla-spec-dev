# CA-05 — suite, measured end to end at the reconciled tip

Command (NOT `README.md:35`, which omits `--with pyyaml`):

```
uv run --with pytest --with pyyaml -m pytest tests -q
```

## FINAL — reconciled onto `4302082` (CA-02 merged), at `4d6ec37`

```
FAILED tests/test_architecture_tags.py::test_the_same_tag_control_holds - Ass...
FAILED tests/test_goal_baseline_is_a_card.py::test_a_real_epic_plans_judged_baseline_cannot_be_re_opened
FAILED tests/test_source_citations.py::test_every_line_citation_resolves_to_the_line_it_cites[specs/current/spec_manifest.yaml]
FAILED tests/test_source_citations.py::test_every_line_citation_resolves_to_the_line_it_cites[specs/desired_program_model/spec_manifest.yaml]
FAILED tests/test_source_citations.py::test_every_line_citation_resolves_to_the_line_it_cites[specs/program_model/spec_manifest.yaml]
FAILED tests/test_ticket_retirement.py::test_repository_canonical_delivered_plan_has_matching_close_receipts
6 failed, 1539 passed in 1253.99s (0:20:53)
```

**6 reds — EXACTLY the post-CA-02 baseline, item for item, no more and no less.**

The baseline moved 7 -> 6 when CA-02 merged: it DELETED the pricer-grep red
with its subject rather than repairing it.

| red | status |
|---|---|
| `test_the_same_tag_control_holds` | DELIBERATE — `RM-06-DF-01` |
| `test_source_citations…[specs/current/spec_manifest.yaml]` | INHERITED, undeclared |
| `test_source_citations…[specs/desired_program_model/spec_manifest.yaml]` | INHERITED, undeclared |
| `test_source_citations…[specs/program_model/spec_manifest.yaml]` | INHERITED, undeclared |
| `test_ticket_retirement…delivered_plan_has_matching_close_receipts` | INHERITED, undeclared |
| `test_a_real_epic_plans_judged_baseline_cannot_be_re_opened` | `CA-00-DF-02` |

**None repaired, none silently touched, nothing attributable to CA-05.**

---

## Earlier runs, all recorded — a discarded run is evidence about method

| run | tree | result | why it is not the figure |
|---|---|---|---|
| 1 | `4616aad` | 8 failed / 1566 passed | **one red beyond baseline, MINE** — shipped `scripts/disposition.py` unregistered; the `registry-enumeration-coverage` tripwire caught it |
| 2 | `1a939c7` | 7 failed / 1568 passed | correct for the PRE-merge tree; superseded when CA-02 merged and the baseline moved to 6 |
| 3 | `4d6ec37` | **6 failed / 1539 passed** | **the figure** |

Run 1 is the one worth keeping: the charter defunds the suite as a FINDING
channel while keeping its regression-guard job, and on this ticket it did that
job, against this ticket, for one line of output.

---

## Instrument demonstrations at the reconciled tip

```
26 passed in 216.32s (0:03:36)
```

26 passed — every `failing` / `passing` / `blind_spot` slot reproduces,
including the three for `epic-disposition` whose `blind_spot` now demonstrates
SELF-ROUTING rather than the flattering closed-successor example.
