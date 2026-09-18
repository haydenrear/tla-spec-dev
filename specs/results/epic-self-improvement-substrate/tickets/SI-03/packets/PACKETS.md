# SI-03 judge packets, derived from the artifacts rather than asserted

One row per probe subject. `items` is what a judge receives, `absent` is what
does not exist for that subject, `withheld` is what exists and was not passed.
The improvement card requires those three to be different fields; collapsing
`absent` into `withheld` is not a legal card.

| subject | PR | own commits | packet items | absent | withheld |
|---|---|---|---|---|---|
| SI-04 | #353 | 2 | pr_body, commits, skill_changes_proposed, review_input, deferred_findings | close_summary | — |
| SI-05 | #354 | 2 | pr_body, commits, skill_changes_proposed, review_input, deferred_findings | close_summary | — |
| SI-06 | #352 | 1 | pr_body, commits, skill_changes_proposed, review_input, deferred_findings | close_summary | — |
| SI-10 | #355 | 4 | pr_body, commits, skill_changes_proposed, review_input, deferred_findings | close_summary | — |
| SI-11 | #356 | 6 | pr_body, commits, skill_changes_proposed, review_input, deferred_findings | close_summary | — |

## What this table already shows, before any judge runs

**`close_summary` is absent for every subject, and that is structural rather
than sloppy.** This epic's `planning_rules.model_ownership_rule` reserves
`close ticket` to the epic agent, so no ticket agent in waves 1-4 wrote a spec
close-history entry at all. The card's packet definition names an item this
epic cannot produce. That is a property of the epic, not of the tickets, and a
judge must be told so rather than scoring five subjects down for it.

**All five subjects carry `## Skill changes proposed`, `## Review input` and
`## Deferred findings`.** The sections exist because SI-06 made them standard
mid-epic. A card scored only on these five would therefore have no negative
control at all -- which is exactly why the redaction pair in `NON-VACUITY.md`
exists rather than a search for a subject that happens to score 0.
