# Coverage Audit Report

- **Epic / workflow:** `<workflow name>`
- **Scope source:** `specs/desired_program_model/ticket_plan.yaml` (lines `<n>-<m>`)
- **Model audited:** `specs/current/<Module>.tla` @ `<commit>`
- **Date:** `<YYYY-MM-DD>`
- **Verdict:** `PASS` | `FAIL` | `INCOMPLETE`

> This audit checks **completeness of what is modeled**, not fidelity. The four
> oracles are bounded to what is already represented and cannot see this class
> of defect. See `prompts/coverage_audit.md`.

---

## 0. Declared scope (quoted verbatim from the plan)

> Paraphrase is not acceptable. Quote the literal plan text with line numbers.
> If the plan declares no usable scope, HALT here and record that instead —
> the auditing agent does not choose the scope.

```yaml
# specs/desired_program_model/ticket_plan.yaml:<n>-<m>
<verbatim quoted text>
```

| Scope line | Covers |
|---|---|
| `ticket_plan.yaml:<n>` | `<what this line puts in scope>` |

**Escalations (ambiguous boundary):**

| Row | Why the plan text does not classify it |
|---|---|

---

## 1. Model representation index

| Kind | Name | `file:line` |
|---|---|---|
| Action | | |
| Port | | |
| Binding | | |

---

## 2. Sweep 1 — Program surface

**Enumeration:** `<command>` → raw count **N = _**; table rows **M = _**; `N == M`: ☐

| # | Module | In/Out | Plan line | Spec action(s) | Verdict | Evidence |
|---|---|---|---|---|---|---|

Verdicts: `represented` / `partial` (name the uncovered part) / `unrepresented`.
Default polarity is `unrepresented` — coverage is granted only on cited
positive evidence.

---

## 3. Sweep 2 — Effects, by category

One table per category. Record raw count, collapsed count, and the collapsing
rule for every category where false positives were removed.

### 3.1 Filesystem — raw `_`, collapsed `_`, rule: `<...>`

| # | Site | Effect | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|

### 3.2 Subprocess — raw `_`, collapsed `_`, rule: `<...>`

> A `process.spawn` port declares the spawn, not what the child did. Sites whose
> child performs its own effects are `partial` at best.

### 3.3 Network — raw `_`, collapsed `_`, rule: `<...>`

### 3.4 Environment — raw `_`, collapsed `_`, rule: `<...>`

### 3.5 Clock — raw `_`, collapsed `_`, rule: `<...>`

### 3.6 Randomness — raw `_`, collapsed `_`, rule: `<...>`

### 3.7 Persistent store — raw `_`, collapsed `_`, rule: `<...>`

---

## 4. Sweep 3 — Behaviors

One table per class. For grouped error paths: state the grouping rule, the raw
count, and the group count.

### 4.1 Error paths — raw `_`, groups `_`, grouping rule: `<...>`

| # | Behavior | Trigger | In/Out | Plan line | Spec action / invariant | Verdict |
|---|---|---|---|---|---|---|

### 4.2 Retries

### 4.3 Timeouts

### 4.4 Fallbacks

> Includes the recurring class: a guard that silently passes when its input is
> absent. The disabled path is a behavior.

### 4.5 Concurrency / interleaving

### 4.6 Config-driven branches

---

## 5. Sweep 4 — Views, reported separately

**A merged verdict is not acceptable.** If a view module does not exist, the
whole of that view's surface is unrepresented by construction — report it as
such, not as "N/A".

### 5.1 Internal — verdict: `_`

| Surface item | Verdict | Evidence |
|---|---|---|

### 5.2 External — verdict: `_`

| Surface item | Verdict | Evidence |
|---|---|---|

---

## 6. Dispositions

Only three exist. **No "justified" or "accept as-is" disposition is available
for an in-scope gap** — see `prompts/coverage_audit.md` §6.

### 6.1 In-scope gaps — HARD, block promotion

| # | Gap | Sweep | Disposition (`model it` \| `change the program`) | Proposed remediation (advisory) |
|---|---|---|---|---|

### 6.2 Out-of-scope inventory — does not gate

| # | Surface | Quoted plan line placing it out of scope |
|---|---|---|

### 6.3 Scope escalations — owner amends the plan, once

| # | Row | Plan line that should change | Argument |
|---|---|---|---|

---

## 7. Verdict

- In-scope gaps: **_**
- Out-of-scope inventoried: **_**
- Escalations: **_**
- **Verdict: `PASS` | `FAIL` | `INCOMPLETE`**

`FAIL` blocks promotion until every in-scope gap is closed by modeling it or
changing the program. `INCOMPLETE` is not a `PASS`.

---

## 8. Attestation

1. Row-count reconciliation per sweep (`N`, `M`, `N == M`):
2. **Surface NOT walked:**
3. Rows dispositioned from path/name rather than from reading code:
4. Rows whose scope was decided by reasoning rather than a quoted plan line:
5. Can a reader reproduce this row set from the recorded commands? ☐ yes ☐ no
6. **Findings about the prompt itself** (required — a way this procedure let a
   plausible report be produced without walking the surface is a more valuable
   result than a clean report):
