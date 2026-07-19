# Coverage Audit — sub-agent prompt (MF-026)

**Dispatch this file verbatim as the prompt for a sub-agent.** It is the
end-of-epic completeness gate: after every mechanism ticket has landed and
**before** final end-to-end integration. See `references/coverage_audit.md` for
the doctrine and the gate semantics; this file is the executable procedure.

---

## What you are being asked to find

You are **not** checking whether the model is correct about what it models.
Four oracles already do that, and every one of them is bounded to what is
already represented:

| Oracle | Bounded to |
|---|---|
| Output conformance | cases that exist |
| Projected-state conformance | cases that exist |
| Effect conformance | the corpus — generated *from the model* |
| Mutation kill test | faults seeded one per port and one per invariant — modeled boundaries only |

Unmodeled program surface is never generated into a case, never adapted, never
mutated. **A subsystem with no representation is invisible to all four gates,
and all four report green.**

Your job is the complement: find program surface, effects, and behaviors that
the model **does not represent at all**. Fidelity and completeness are
independent; a green oracle run tells you nothing about your question.

---

## The failure mode this prompt exists to prevent

There is **no tooling** behind this audit — that is a deliberate owner
decision, and it has a consequence you must take seriously. A prompt that says
"look for uncovered behavior" returns whatever the agent happened to notice,
formatted as if it were a survey. That output is worse than no audit, because
it *reads* like completeness.

So the discipline is structural, and it is not optional:

> **Every table's row set is produced by a command, not by your attention.**

You run the enumeration command, you record its raw output count, and your
table carries **exactly that many rows**. A row you did not write is a row you
did not consider, and the row-count check catches it. If you find yourself
deciding which files are "worth including", you have already failed — include
them and disposition them.

**If you cannot enumerate a surface mechanically, say so in the Attestation
and mark the sweep INCOMPLETE.** An honest INCOMPLETE is a useful result. A
plausible-looking table over a surface you sampled is a fabrication.

---

## Step 0 — Read the scope from the plan. Do not choose it.

**You do not decide what is in scope.** An agent that picks its own scope can
define every gap out of existence, which would make this gate worthless. The
scope is a boundary decision the owner already made and recorded.

Read it from the epic plan:

1. Open `specs/desired_program_model/ticket_plan.yaml`.
2. Locate the workflow-level scope declaration — the `service_catalog` block
   (`existing_boundaries`, `desired_boundaries`, `adapter_boundaries`,
   `known_gaps`) and each in-flight ticket's `implementation_scope`.
3. **Quote the literal text verbatim into your report**, with the file path and
   line numbers. Paraphrase is not acceptable: a paraphrased scope is a scope
   you rewrote.

### The closure rule — read this before classifying a single row

The common real case is not "no scope" or "vague scope". It is a **partial**
scope: a precise inclusion list that names some files and says nothing about the
rest. Run 1 met exactly this — 15 of 160 files named, no exclusion rule — and
the prompt did not say whether naming `scripts/foo.py` scopes `scripts/`. The
auditor's first pass assumed directory closure (**103 in-scope / 57
escalations**); strict exact-path matching gave **15 / 145**. Same plan, same
agent, **88 rows — 55% of the surface — moved by an unstated convention**, and
both readings produce a confident-looking report.

**The rule, so that temperament does not decide it:**

> **An `implementation_scope` entry naming a FILE scopes that file only.
> Directory closure counts only when the plan writes a directory — a trailing
> slash or an explicit glob. Anything else is an ESCALATION, never an
> inference.**

This deliberately produces *more* escalations, and that is correct. An
escalation is one sentence for the owner to write once; an inferred scope is a
silent decision that redefines the gate. **When the plan's silence is
load-bearing, surface it — do not resolve it.**

**HALT conditions.** Stop and report rather than proceeding if:

- the plan declares no scope, or the declaration is too vague to classify a
  given module in or out;
- you find yourself needing to *interpret* the boundary to decide a row's
  disposition; or
- the scope as written does not cover surface you can plainly see.

In every one of those cases the correct output is: **"the plan's scope
declaration is insufficient to run this gate — the owner must amend it."**
Do not substitute your judgment. Do not classify ambiguous surface as
out-of-scope to make the sweep tractable. An ambiguous row is escalated, not
resolved.

Record for each row you will later classify: `in-scope` or `out-of-scope`, and
**which quoted plan line put it there**. A row whose classification cannot be
traced to a quoted plan line is an escalation, not a classification.

---

## Step 1 — Establish the model's representation index

Before any sweep, build the list of what the model *claims* to represent, so
each sweep row can be matched against it.

```bash
# Every action in each view. The `(\(.*\))?` is REQUIRED: without it the regex
# silently omits every PARAMETERIZED definition -- i.e. almost exactly the set
# of real actions -- and an index built from the remainder marks nearly the whole
# program `unrepresented` in a way that looks rigorous. (Run-1 finding.)
grep -nE '^[A-Za-z_][A-Za-z0-9_]*(\(.*\))? ==' specs/current/*.tla

# Declared ports and effects
grep -n 'ports\|effects\|channel' specs/current/spec_manifest.yaml

# Action-to-adapter bindings. DISCOVER these paths; do not assume them. Layouts
# differ, and a hardcoded `cat` of a nonexistent file yields an empty index that
# reads as "nothing is bound".
find . -name 'actions.yml' -o -name 'testgraph_bindings.yml' | grep -v '^./examples/'
```

Verify the index is non-empty and plausible before continuing. **An empty or
suspiciously small index means the enumeration failed, not that the model is
empty** — an index of 3 actions for a program with 9 CLI subcommands is a
symptom, not a finding. Fix the enumeration and re-derive.

Record the action list, the port list, and the binding list with `file:line`.
These are the only things a row may be mapped *to*. **You may not invent a
mapping**: if a module's behavior "would naturally fall under" an action that
does not name it, that is `partial` at best, and you say why.

---

## Step 2 — Sweep 1: Program surface

**Row set (run this; do not curate the result):**

```bash
# Establish SURFACE once. Every later sweep derives its paths from this list --
# see the warning below.
git ls-files '*.py' | sort > /tmp/ca-surface-py.txt
wc -l < /tmp/ca-surface-py.txt
```

Adapt the glob to the project's languages (`*.java`, `*.kt`, `*.kts`, `*.sh`,
`*.ts`, …) and run one enumeration per language. Record **each command and its
raw count**.

**On filters.** You may exclude `tests/` and vendored trees, but **state every
filter and check it against the declared scope first.** A filter is a scope
decision wearing a shell flag. Run-1 finding: `grep -v '^specs/'` dropped
`specs/…/production_adapters.py`, which the plan names as an explicit adapter
boundary, while keeping `examples/**/specs/**`, which nothing scopes — the
filter excluded in-scope surface and admitted escalation surface. If a filter
would drop a path any plan line names, do not apply it.

Then produce a table with **exactly** that many rows — one per file:

| # | Module (`path`) | In/Out of scope | Plan line | Spec action(s) representing it | Verdict | Evidence (`file:line`) |
|---|---|---|---|---|---|---|

**Verdict vocabulary — these three and no others:**

- `represented` — a named spec action covers this module's behavior. Cite the
  action and its `file:line`.
- `partial` — some behavior is represented, some is not. **You must name the
  unrepresented part.** `partial` without a named uncovered behavior is not a
  verdict, it is a hedge; convert it to `unrepresented`.
- `unrepresented` — no spec action covers it.

**Default polarity: `unrepresented`.** Coverage is granted only on positive
evidence — a named action, cited. A module you could not confidently map is
`unrepresented`, not "probably covered". This is the same polarity MF-027
established for the effect oracle: absence of evidence is never evidence of
coverage.

Close the sweep with: `enumerated N = <count>, table rows M = <count>, N == M`.

---

## Step 3 — Sweep 2: Effects, by category

Enumerate **by category** so the sweep is checkable rather than
impressionistic. A single "I looked for side effects" pass is exactly the
impressionistic result this gate rejects. Run each of these separately, record
each command with its raw count, and give **each category its own table**.

> **Search the surface Sweep 1 enumerated — never a hardcoded subdirectory.**
> The commands below use `$SURFACE`, which is Sweep 1's file list. Run-1 finding:
> when these patterns were pinned to `scripts/ spec_double_compiler/`, they
> covered 30 of 160 files and returned **233 fewer hits**, missing *every*
> network call in the repository and the only spawn primitive behind the Test
> Graph nodes. The report would have said "0 real network effects" — true of the
> searched subdirectory, false of the program. A sweep narrower than the surface
> it claims to cover is the impressionistic result with a command attached.

```bash
SURFACE=$(cat /tmp/ca-surface-*.txt)   # every file Sweep 1 enumerated
```

**Write each category's raw output to a file and cite it in the report:**

```bash
mkdir -p results/sweep-raw
grep -nE "<pattern>" $SURFACE > results/sweep-raw/<category>.txt; wc -l < results/sweep-raw/<category>.txt
```

The row-count reconciliation is otherwise **self-reported**, and a self-reported
check is only as strong as the agent's willingness to fail itself. The raw file
makes `N` an artifact a reviewer can recount.

Patterns are **word-boundary anchored** (`grep -nE`, `\b`). Unanchored substrings
produced a 95% false-positive rate in run 1 — `lock` matching `_parse_block`
turned 4 real concurrency sites into 81 raw hits. Both failure directions follow
from that: an agent that dispositions raw hits publishes a 95%-noise table, and
an agent that collapses hard discards the 4 real sites with the 77 fake ones.

| Category | Enumeration pattern (run against `$SURFACE`) |
|---|---|
| Filesystem | `\b(open\|Path\|write_text\|read_text\|write_bytes\|mkdir\|makedirs\|remove\|unlink\|rename\|replace\|copy\|copytree\|rmtree\|tempfile\|mkdtemp\|NamedTemporaryFile)\b` |
| Subprocess | `\b(subprocess\|Popen\|run\|call\|check_output\|check_call\|system\|execv\|execve\|spawn)\b` |
| Network | `\b(socket\|connect\|requests\|urlopen\|urlretrieve\|urllib\|httpx\|aiohttp\|HTTPConnection\|curl\|wget)\b` |
| Environment | `\b(environ\|getenv\|putenv\|setdefault\|argv\|load_dotenv\|expanduser\|PATH)\b` |
| Clock | `\b(datetime\|now\|utcnow\|today\|time\|monotonic\|perf_counter\|sleep\|timestamp)\b` |
| Randomness | `\b(random\|randint\|choice\|shuffle\|sample\|uuid\|uuid4\|secrets\|urandom\|token_hex)\b` |
| Persistent store | `\b(sqlite3\|psycopg\|pymysql\|redis\|boto3\|engine\|session\|cursor\|execute\|commit)\b` |

Extend the pattern set for the project's other languages — `File(`,
`ProcessBuilder`, `HttpClient`, `System.getenv` and their equivalents. A category
searched only in Python, in a repository that is not only Python, is a category
you did not sweep.

Per category:

| # | Site (`file:line`) | Effect performed | In/Out of scope | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|

**Verdicts:** `declared` (a port in `spec_manifest.yaml` covers it, cited) /
`undeclared` / `partial` (declared port covers some of what the site does —
name the rest).

Two rules that are not negotiable here:

- **A `process.spawn` port declares the spawn, not what the child did.** Every
  subprocess site whose child performs its own effects is `partial` at best,
  with the child's effects listed as unrepresented — even when the spawn itself
  matches a declared port. This is MF-027's process-boundary finding; do not
  re-collapse it.
- **A site in a non-Python runtime the effect sandbox cannot observe is
  `undeclared` until proven otherwise**, and you note that the shipped oracle
  could not have seen it either. `unobservable` is not `clean`.

If a grep returns hits you judge to be false positives (a `time.` in a comment,
a `datetime` in a docstring), you may collapse them — but you must record the
raw count, the collapsed count, **and the collapsing rule**, so a reviewer can
re-derive your table from the raw output. An uncounted collapse is
indistinguishable from a skipped row.

### High-volume categories: group, never sample

A category can legitimately return hundreds of hits. Run 1 hit 225 filesystem
rows and correctly refused to fake per-site disposition — but the prompt gave it
no sanctioned alternative, so a category that was *swept* had to be reported
INCOMPLETE. That gap is what pressures the next agent toward a curated table
presented as an enumeration.

So, explicitly permitted, on the same terms Step 4 grants error paths:

> **You may disposition a category by GROUP rather than per-site, provided you
> (a) state the grouping rule as a rule, (b) report raw count and group count,
> (c) account for every raw hit in exactly one group, and (d) disposition every
> group.**

Group by **distinct effect semantics** — "writes under the spec tree", "reads
manifest", "creates a temp workdir" — never by file, never by convenience, and
never by "the interesting ones". The test: **a reader applying your stated rule
to the raw output must land on your groups.** If you cannot state the rule that
way, you are sampling, and the honest output is INCOMPLETE.

Destructive effects (delete, rename, overwrite, truncate) are **always
enumerated per-site**, never grouped. They are the category where a single
missed site is a data-loss defect, and they are few enough everywhere that
volume is never the excuse.

---

## Step 4 — Sweep 3: Behaviors

These are the ones a happy-path-shaped model reliably misses. A model built
from the successful path through a system will pass all four oracles while
representing none of this.

**Row set:**

```bash
grep -rn "except\|raise\|try:" --include='*.py' scripts/ spec_double_compiler/ | wc -l
grep -rn "retry\|backoff\|attempt\|max_tries" --include='*.py' scripts/ spec_double_compiler/
grep -rn "timeout\|deadline\|expires\|TimeoutError" --include='*.py' scripts/ spec_double_compiler/
grep -rn "fallback\|default\|or None\|except.*pass\|ImportError" --include='*.py' scripts/ spec_double_compiler/
grep -rn "thread\|async \|await \|lock\|Lock()\|concurrent\|multiprocessing" --include='*.py' scripts/ spec_double_compiler/
grep -rn "if.*config\|getenv\|\.get(\"\|flag\|enabled\|--no-\|--allow" --include='*.py' scripts/ spec_double_compiler/
```

One table per behavior class — **error paths, retries, timeouts, fallbacks,
concurrency/interleaving, config-driven branches** — each with:

| # | Behavior | Trigger (`file:line`) | In/Out of scope | Plan line | Spec action / invariant | Verdict |
|---|---|---|---|---|---|---|

Error paths will usually be too numerous to enumerate one-per-`except`. That is
allowed **only** if you group them by *distinct failure semantics* (not by
file), state the grouping rule, give the raw count and the group count, and
disposition every group. A grouping you cannot state as a rule is a sample.

Pay specific attention to the class this doctrine keeps rediscovering: **a
guard that silently passes when its input is absent.** A config-driven branch
that disables a check when a key is missing is a behavior; if the model does
not represent the disabled path, that is a gap, and a consequential one.

---

## Step 5 — Sweep 4: Both views, separately

Internal and External get **separate tables and separate verdicts**. A merged
verdict is not acceptable output for this gate. A behavior may be represented
in one view and absent from the other, and merging hides exactly that.

- **Internal** — component detail: internal actions, component state, the
  interleaving between components.
- **External** — the public input surface and the observable projection: what a
  caller can drive and what a caller can see.

| View | Surface item | Verdict | Evidence (`file:line`) |
|---|---|---|---|

**If the project has only one view module**, that is itself a Sweep-4 finding
of the highest order: every behavior belonging to the missing view is
unrepresented by construction, and you report the whole External (or Internal)
surface as unrepresented rather than reporting the single module as complete.
Do not report "N/A — single module". A single module is not a merged view; it
is a missing one.

---

## Step 6 — Dispositions and the verdict

For every row marked `unrepresented`, `undeclared`, or `partial`, assign
exactly one disposition:

| Disposition | When | Gates? |
|---|---|---|
| **Model it** | In-scope gap. Propose the model addition. | **YES — hard** |
| **Change the program** | In-scope gap better closed by removing the behavior. Propose the change. | **YES — hard** |
| **Inventory it** | Out of scope per a quoted plan line. Record and move on. | No |

### There is no fourth disposition.

**FORBIDDEN for any in-scope gap** — do not emit these, in any wording:

- "justified"
- "accept as-is"
- "acceptable risk"
- "known limitation" (as a disposition; as a *fact* it belongs in the row's
  description, but the disposition is still model-it or change-it)
- "out of contract"
- "deferred" / "tracked separately" as a substitute for a disposition
- "low priority", "not worth modeling", "unlikely in practice"
- an out-of-scope classification you reached by reasoning rather than by
  quoting a plan line

**Why this is absolute.** A gate whose findings can each be closed by a
recorded justification is the out-of-contract suppression that was purged from
MF-013, rebuilt one level up. **One reviewable boundary decision is a boundary;
N per-finding justifications are an escape hatch.** The scope is declared once,
in the plan, and reviewed once. It is never waived per finding. See "No
Degenerate Escapes" in `references/architecture_tractability.md`.

If you believe an in-scope gap genuinely should not be modeled, you do **not**
have a disposition for it. What you have is an argument that the *plan's scope
is wrong* — say that, name the plan line you think should change, and escalate.
The owner amends the boundary, once, visibly. You do not resolve it row-by-row.

**Remediation is advisory; the gap is not.** You propose *how* to close each
gap; the owner approves, adjusts, or vetoes the approach. The *existence* of an
in-scope gap is not negotiable and not yours to waive.

### Verdict

- **PASS** — zero in-scope gaps. Out-of-scope inventory may be non-empty.
- **FAIL** — one or more in-scope gaps. Promotion is blocked until each is
  closed by modeling it or changing the program.
- **INCOMPLETE** — you could not walk some surface. **This is not a PASS.**
  Name precisely what you did not walk and why.

---

## Step 7 — Attestation (required; the report is invalid without it)

Answer all of these explicitly. Under-claiming here is correct behavior; this
section exists so the report's own reliability is legible to its reader.

1. For each sweep: the enumeration command, its raw count N, the table row
   count M, and whether `N == M`. Any inequality must be explained.
2. **What surface did you NOT walk?** Name it. "None" is an assertion you are
   making on the record.
3. Which rows did you disposition from a file path or name rather than from
   reading the code? **Give a per-sweep count of rows-READ versus
   rows-INFERRED**, then list the inferred ones. These are your least reliable
   rows.

   This exists because the row-count discipline has a known side effect: it
   successfully prevents *silent sampling*, but it creates pressure toward
   shallow rows, which is a quieter failure. A sweep of 160 rows where 76 were
   dispositioned from filename is a different artifact from one where all 160
   were read, and the reader is entitled to know which they have. Reporting a
   high inferred count is not a failure — concealing it is.
4. Did you at any point decide a row's scope by reasoning instead of by quoting
   a plan line? If yes, list those rows — they are escalations, not
   classifications.
5. **Could a reader reproduce this report's row set from the commands you
   recorded?** If not, the sweep is INCOMPLETE regardless of what the tables
   say.
6. **Findings about this prompt.** If following it let you produce a
   plausible-looking report without actually walking the surface, say so
   plainly and name the step that permitted it. That finding is more valuable
   than a clean report, and reporting it is an explicit requirement — not a
   discretionary courtesy.

---

## Output

Fill in `templates/coverage_audit_report.md`. Write it to the ticket's evidence
directory, and record the verdict in the complexity ledger's `coverage_audit`
block so that an epic which skipped this audit is visible rather than silent.

---

## Validation status of this prompt — read before trusting it

**Run 1 (MF-026, 2026-07-19, against this repository):** verdict `INCOMPLETE`,
19 in-scope gaps, 145 of 160 rows escalated. Report:
`specs/.history/**/MF-026/results/coverage_audit_report.md`.

That run was the prompt's validation, and it found real defects in it. Fixed
here in response: the parameterized-action regex, the hardcoded manifest paths,
Sweep 2/3 searching a narrower surface than Sweep 1 enumerated (which hid 233
hits including every network call), unanchored patterns at a 95% false-positive
rate, the missing grouping allowance for high-volume categories, the scope
closure rule, and the read-vs-inferred attestation.

**Known-open, and NOT fixed by any wording change:**

> **The row-count reconciliation is self-reported.** `N == M` is an assertion the
> auditing agent makes about its own diligence. Run 1 reported `N ≠ M` against
> itself three times — which is the behavior this prompt wants — but nothing
> *forces* that. An agent willing to write a curated table and claim it was
> enumerated is not stopped by any paragraph here.

Writing the raw output to `results/sweep-raw/` narrows this, because a reviewer
can recount. It does not close it. **Closing it requires a mechanical inventory
that produces the row set independently of the agent** — tracked as the
follow-up to MF-026. Until that exists, this gate's strength is bounded by the
honesty of the agent running it, and a reader of any report produced here should
treat §8 as the load-bearing section rather than the tables.

The prompt-only deliverable was an accepted tradeoff, not an oversight. This
paragraph is what keeps it from being mistaken for a guarantee.
