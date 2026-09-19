# Is the moved text still reachable? (the check the goal actually needs)

A reference map nothing reads is not progressive disclosure, so reachability was
measured, not assumed.

1. FILE-LEVEL. A sweep over all 8 cards extracted every references/, prompts/
   and templates/ citation and resolved each against the owning skill's
   directory. Frontmatter is stripped first, because `skill-imports:` path
   fields name OTHER units' pages and would otherwise produce false alarms. A
   citation whose line names another skill is resolved against that skill.
   RESULT: 156 links scanned, 0 broken. The sweep asserts it scanned >0 links,
   so "clean" cannot mean "looked at nothing".

2. SECTION-LEVEL. A file that exists with the cited heading missing fails just
   as silently, so the 4 section citations were checked separately:
     git-issue-workflow -> worktrees.md  §The exit codes `wt new` refuses with  OK
     git-issue-workflow -> worktrees.md  §Resolving `wt` when `skt` is absent   OK
     git-epic-workflow  -> worktree-lifecycle.md §The front door                OK
     git-integration-repo -> git-issue-workflow/SKILL.md §Reaching a by-hand
       route is itself a finding                                                OK
   The last is cited by four pages, so the rewrite keeps it as a real heading.

3. DESTINATION-CARRIES-THE-TEXT. Before dropping detail from a card, the target
   page was checked for the facts being dropped. skill-homes.md already carried
   the launch shims / gitignored / copy semantics; complete.md already carried
   the close-out gate and --force; plan-and-schedule.md already carried
   promotion_order, conflict keys and wave. worktrees.md did NOT carry `wt new`
   exits 3/7/79 - so that text was APPENDED there rather than merely cited,
   which is the difference between moving instruction and deleting it.
