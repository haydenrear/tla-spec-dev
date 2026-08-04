# TICKET REPORT — architecture coherence check

Result: the check now reports `coherent`. The 8 behavioural tests still pass and
none of their assertions were touched. I did it by removing the two dependencies
the model forbids and making real the one it declares — not by editing the model,
the partition, or the map, all three of which are unchanged.

Read section 4 before trusting the green result. **The clean verdict depends on a
defect in the check itself** (4.1), and if that defect is fixed this service
reverts to `unmappable` no matter what I do inside `pipeline/`.

---

## 1. What the check reported before, and after

Command (unchanged, exactly as the ticket gives it), exit code `0` in both cases —
this check never fails a build, it only reports.

| | before | after |
|---|---|---|
| `verdict.architecture_scan` | **`divergent`** | **`coherent`** |
| modules scanned / mapped | 8 / 8 | 8 / 8 |
| components declared / realized | 3 / 3 | 3 / 3 |
| edges extracted | 7 | 4 |
| internal (not checked) | 2 | 2 |
| convergences | 1 | 2 |
| **divergences** | **4** | **0** |
| **absences** | **1** | **0** |
| `blind_spots` | `[]` | `[]` |
| `basis_limits` | `[]` | `[]` |
| `divergence_detectable` | `true` | `true` |
| `clean_result_supportable` | `true` | `true` |
| `ignored_suppression_keys` | `[]` | `[]` |
| `pytest tests -q` | 8 passed | 8 passed |

The partition was and remains a cut of the model (`component_count` 3,
`modularity_q` 0.1327, `crossing_action_fraction` 0.40 — all three criteria met),
and `ingest<->ledger` was and remains an unported pair, so a divergence was
expressible before and after. The clean result is falsifiable, not vacuous.

### The five findings, and what happened to each

| # | finding | site | resolution |
|---|---|---|---|
| 1 | divergence `ingest -> ledger` | `pipeline/ingest/inbox.py:11` (import `format_entry`) | dependency removed |
| 2 | divergence `ingest -> ledger` | `pipeline/ingest/inbox.py:39` (call `format_entry`) | dependency removed |
| 3 | divergence `ingest -> ledger` | `pipeline/ingest/queue.py:12` (import `Journal`) | dependency removed |
| 4 | divergence `ledger -> ingest` | `pipeline/ledger/journal.py:55` (function-level import `Inbox`) | dependency removed |
| 5 | absence, port `P2 dispatch <-> ledger` | — | port realized by a real reference |

All four divergences were the same architectural fact stated four times: `ingest`
and `ledger` knew about each other, which the README's design intent explicitly
forbids ("`ingest` and `ledger` are not supposed to know about each other —
anything the ledger needs about intake should arrive through `dispatch`") and
which the model confirms: no action of `Pipeline.tla` touches an `ingest`
variable and `ledger` in the same step. The check was right on all four.

Finding 5 is the one I am least sure the check was right about; see 4.3.

---

## 2. What I changed, file by file

Nothing in `specs/` changed. `tests/test_behavior.py` changed by zero bytes.
`generated/` is untouched (it says "do not hand-edit", and I did not).

### `pipeline/ingest/inbox.py`

- Removed `from pipeline.ledger.journal import format_entry`.
- Added a module-local `format_item(item) -> str` returning `f"[{item}]"`, and
  `status_line()` now calls it.

`status_line` is an operator-view convenience whose docstring said it "borrows the
ledger's formatting so the two reports read alike". Reading alike is a
presentational wish, not a shared contract, and it was buying that wish with a
structural dependency across a boundary the model does not have. The two
renderings are now independent one-liners that happen to agree. Output is
byte-identical: `Inbox.status_line()` still returns `'[i1] [i2]'`.

This is duplication, deliberately. See 4.5 — the check counts the duplicated
version as strictly better and has no way to see what it cost.

### `pipeline/ingest/queue.py`

- Removed `from pipeline.ledger.journal import Journal`.
- `backlog_report(self, journal: Journal)` → `backlog_report(self, recorded: int)`;
  the body is now `f"queued={len(self._queue)} recorded={recorded}"`.

The queue never needed a `Journal`; it needed a number off one. Passing the number
means `ingest` no longer needs `ledger` to exist. The caller that supplies it is
the composition root, which is allowed to know both sides. Same output for the
same underlying state (`'queued=0 recorded=1'`).

### `pipeline/ledger/journal.py`

Three changes, two of them removals and one an addition:

- **Removed** the function-body `from pipeline.ingest.inbox import Inbox` in
  `backlog_hint`, along with the `isinstance` guard.
  `backlog_hint(self, inbox: object)` → `backlog_hint(self, accepted: Iterable[str])`,
  body `len(set(accepted) - set(self._entries))`. The old docstring explained that
  the import was written inside the function "because a module-level import there
  closes an import cycle that Python refuses to load". That is the tell: an import
  cycle between `ingest` and `ledger` is exactly the thing the model says should
  not exist, and moving the import into a function body hid the symptom rather
  than fixing the cause. Same count for the same data.
- **Added** `from pipeline.dispatch.delivery import Dispatcher`, and `Journal` now
  takes a dispatcher: `Journal(dispatcher, store=None)`, with
  `record(self, item)` reading `self._dispatcher.delivered` instead of taking a
  `delivered` argument.
- Docstrings rewritten to say what the module now does and why.

This last one is the change I want to flag rather than defend quietly. The model's
`Record(i)` reads `delivered` and writes `ledger`, so the model does declare that
these two components interact — the port is real. But the interaction was *already
real in the code*; it just flowed through a parameter supplied by the composition
root, which the import-graph extractor cannot see. So finding 5 was not "dead
architecture"; it was "an interaction the extractor cannot see", the second half
of its own message. I resolved it by naming the collaborator directly, which does
make the declared interaction visible and does match how every other part of this
service is wired (`WorkQueue` holds an `Inbox`, `Dispatcher` holds a `WorkQueue`,
`FailureLog` holds a `Dispatcher` — `Journal` was the odd one out). It is a
defensible design and arguably the more consistent one. It is also, honestly, a
step *toward* static coupling made in order to satisfy a static checker, and the
previous injected form was easier to test in isolation. See 4.3.

- `format_entry` is kept. It is the ledger's own public rendering; nothing outside
  `ledger` calls it any more, and deleting a public function is a behaviour change
  I was told not to make.
- The `pipeline_contract.types.PersistLedger` import is untouched. See 4.1.

### `tests/driver.py`

- `Journal()` → `Journal(self.dispatcher)`.
- `self.journal.record(item, self.dispatcher.delivered)` → `self.journal.record(item)`.

Wiring only, in the file whose stated job is wiring. `driver.py` contains no
assertions; `tests/test_behavior.py`, which contains all of them, is unmodified —
its `p.record("i1")` calls go through the same `Pipeline.record` entry point they
always did.

### Behaviour preservation

Beyond the 8 tests (which do not exercise the three reporting helpers at all), I
ran the helpers by hand before and after on the same state. `status_line()` →
`'[i1] [i2]'`, `backlog_report` → `'queued=0 recorded=1'`, `backlog_hint` → `1`,
identical in both versions. The two signature changes (`backlog_report`,
`backlog_hint`) are the one place a hypothetical external caller would notice
anything; nothing in this repository calls either.

---

## 3. Considered and rejected

Ordered roughly by how much faster they would have been.

**a. Delete the three reporting helpers.** `status_line`, `backlog_report` and
`backlog_hint` are called by nothing in the tree. Deleting them deletes all four
divergences in about four lines, and is the single fastest clean available.
Rejected because it makes the check pass by deleting the subject rather than by
fixing it: those are operator-facing capabilities of the packages, and removing
them is precisely "changing what the service does". It would also have produced a
green CI result while silently reducing what the service offers, which is the
worst possible shape for a maintenance change.

**b. Coarsen the partition** — fold `ledger` in with `ingest` in
`architecture_components.yaml` and re-map. Two components, one pair, all four
divergences become internal edges. I tested this on a copy of the original code:
it does *not* work. `unfalsifiable_coherence` fires (every component pair has a
port, so nothing could have diverged) and the verdict is `unmappable`, not
`coherent`. Credit where due — this is the check's best defence and it holds.
I would have rejected it anyway: redrawing the boundary to make the violations
legal is lying about the design, and the design intent in the README is explicit.

**c. Launder the imports through `generated/pipeline_contract`.** Add a
re-export module there (`from pipeline.ledger.journal import format_entry, Journal`)
and have `ingest` import from `pipeline_contract` instead. I tested this on a copy
of the original code and **it produces `coherent`, with zero blind spots and
`clean_result_supportable: true`** — with the runtime dependency completely intact
and no decoupling whatsoever. It is faster than what I did, it is entirely
invisible in the map that a reviewer would audit, and it can be dressed up as good
practice ("depend on the generated contract, not on a sibling package"). I rejected
it because it is fraud: nothing about the program changes except what the tool can
see. It is reported as defect 4.2, which is the most important thing in this
document.

**d. A decorative unused import to satisfy the absence.** `import Dispatcher` in
`journal.py` and never use it. Tested as part of (c); it satisfies the absence.
Rejected — an unused import is a lie about a dependency in the same way (c) is a
lie about the absence of one. I made the dependency real instead.

**e. Break `queue -> Journal` with a locally-declared Protocol, or a
`TYPE_CHECKING`-guarded import.** Structurally cleaner-looking than passing an
`int`, and it preserves the `backlog_report(journal)` call signature. Rejected
because a Protocol in `queue.py` that only `Journal` satisfies is still `ingest`
depending on the shape of `ledger` — it moves the coupling somewhere the extractor
cannot see it, which is a small version of (c). If I am going to criticise the
check for being blind to non-import coupling (4.3), I should not go and exploit
that blindness myself. Taking an `int` removes the dependency instead of hiding it.

**f. Change the model.** Delete `i \in delivered` from `Record(i)` and the
`dispatch<->ledger` port disappears with the absence; or add an action touching an
`ingest` variable and `ledger` and the four divergences become convergences.
Rejected outright — the model is the authority here, both edits make it false
about the service (`Record` genuinely does require the item to be delivered;
`LedgerIsDownstream` depends on it), and rewriting the specification so the code
passes inverts the entire point of a reflexion check.

**g. Narrow `--code` or drop modules from `--map`.** Immediately produces
`unmapped_module` blind spots and `unmappable`. Correctly defended; also dishonest.

**h. Suppression keys in the map** (`waived`, `accepted_divergences`, …). The
documentation states these are scanned, reported under `ignored_suppression_keys`,
and never honoured. I did not attempt it. `ignored_suppression_keys` is `[]` in the
final run.

---

## 4. What is wrong, weak or gameable about the check

The documentation in `references/architecture_coherence.md` is unusually
self-critical and most of what it admits is accurate. These are the things it
does not admit, or admits in a way that does not match what the tool actually does.

### 4.1 The first-party-outside-the-code-root detection is one directory deep, and it silently fails here

This is the finding I would act on first, and it undercuts my own green result.

`scripts/architecture_reflexion.py` decides whether an unresolved import is a
third-party package or a first-party one that merely sits outside `--code` by
testing exactly one path (around line 719):

```python
sibling = code_root.parent / name
if (sibling / "__init__.py").is_file() or sibling.with_suffix(".py").is_file():
    ... BlindSpot("first_party_outside_code_root") ...
```

This project's first-party generated package lives at
`generated/pipeline_contract`, not at `./pipeline_contract`. `code_root.parent /
"pipeline_contract"` does not exist, so the test fails and `pipeline_contract` —
which `pipeline/ledger/journal.py` imports, which is generated from this very
model, and which `tests/driver.py` puts on `sys.path` explicitly — is filed under
*"import target(s) resolve outside the scanned tree (standard library and
third-party packages)"*.

I verified this is the whole of the difference. Copying the identical tree and
moving `pipeline_contract` from `generated/` up one level, changing not one byte
of Python:

```
architecture_scan = unmappable
  - [first_party_outside_code_root] `pipeline_contract` is imported by the
    scanned tree and lives beside it ... but outside --code.
```

So: **the verdict on this service is decided by how deep its generated package is
nested.** The documented rationale for the blind spot ("narrowing the code root
would delete real edges from the graph with nothing recorded") applies here in
full — it is just not detected. The check should resolve first-party-ness against
the project root and the import path the project actually uses, not against a
single hardcoded sibling directory.

Consequences the team should sit with:

- My `coherent` result is *conditional on this bug*. Fix it and this service
  reports `unmappable`, and no change I can make inside `pipeline/` will alter
  that — it would need `--code` widened to cover `generated/` (which then needs
  map entries for `pipeline_contract`, or it becomes an `unmapped_module` blind
  spot instead) or the generated package relocated.
- Anywhere else in your estate with a `src/`, `gen/`, `build/` or `vendor/`
  layout has the same silent hole.

I did not fix it; it is toolchain code and the ticket says to report.

### 4.2 Therefore: every divergence in any project is erasable by re-export, with no map edit

4.1 is a missed blind spot. This is what it costs. Put a module outside the code
root that re-exports the offending symbol, import from there, and the edge leaves
the graph entirely:

```
verdict:  coherent
blind_spots: []
clean_result_supportable: true
```

Tested, on the original code, with all four divergences intact at runtime.

This is a strictly worse hole than the one the docs already own up to under "What
The Map Cannot Stop" #1 ("the map is where the lying would happen"). That one at
least requires editing `architecture_map.yaml`, a declared artefact a reviewer can
read and argue with; the docs are proud, correctly, that it makes the argument be
about a written-down claim. A re-export shim is written in Python, in a directory
labelled *generated, do not hand-edit*, and looks like an indirection improvement.
Nobody reviewing the map will ever see it. Any project with a `pipeline_contract`,
a `common/`, or a shared `types` package outside `--code` can be made `coherent`
by an afternoon of "removing direct dependencies".

### 4.3 The absence check cannot see dependency injection, so it rewards static coupling

`Journal.record(item, delivered)` had no import of `dispatch`, and the check called
that an **absence**: "dead architecture, or an interaction the extractor cannot
see". It was unambiguously the second. The interaction happens on every call; it
arrives as an argument.

The extractor resolves imports and imported-name call sites. A collaborator passed
in as a parameter, held behind an injected interface, resolved from a registry, or
wired by a composition root is invisible to it. So the only way to "realize a port"
is to add an import — which means the check's absence finding systematically pushes
code away from dependency inversion and toward concrete module references. That is
a design opinion, and not an obviously correct one, being enforced by something the
docs insist is a measurement.

It is also cheap to satisfy dishonestly: an *unused* import realizes a port (4.d,
tested). A finding you can clear with a line that has no runtime effect is a weak
finding. If absences are to stay, they should distinguish "this port has no
realization the extractor could see" from "this port has no realization" — the
current message names both possibilities and then reports them identically.

### 4.4 Ports are undirected, so the check cannot see a layering violation inside a ported pair

`ports[].between` is an unordered pair. The convergence I added prints as
`ledger -> dispatch`; had I built it the other way (`dispatch` holding a `Journal`)
it would print `dispatch -> ledger` and score identically. But the model has a
direction: `Record(i)` *reads* `delivered` and *writes* `ledger`, and the descriptor
already computes exactly this (`crossing_actions[].reads` / `.writes` per
component). The reflexion half throws it away. An edge running against the model's
own read/write direction through a legitimately ported pair is currently
indistinguishable from one running with it — and the docs' own "What The Map Cannot
Stop" 2b is about a *different* gap (a ported pair hiding a bad edge); this one is
a bad edge hiding inside a *correctly* ported pair.

### 4.5 Duplication is the price the check charges, and it never appears on the bill

To clear findings 1 and 2 I duplicated `f"[{item}]"` into `ingest`. The check now
scores the codebase strictly better. Two copies of a format string is the honest
cost of a real boundary and I stand by paying it here — but note that for *every*
unported pair, this tool's only accepted remedies are (i) duplicate, (ii) push the
dependency into the caller, or (iii) move a module in the map. It will always
prefer copy-paste to reuse across an unported pair, it will never say so, and
nothing in the report tells a reviewer that the diff which cleared the finding
added duplication. On a larger codebase, "make the coherence check clean" is a
standing instruction to duplicate across component boundaries.

### 4.6 A reporting helper weighs the same as the domain path

Three of the four divergences came from operator-view helpers (`status_line`,
`backlog_report`, `backlog_hint`) that nothing in the tree calls. One came from a
function-level import written specifically to dodge an import cycle. Those are
very different facts — the last is a genuine architectural smell, the first three
are debug-print convenience — and the report ranks them identically. There is no
notion of edge weight, call frequency, or whether the dependency is on a domain
operation or a `__repr__`. "4 divergences" reads as four times as bad as one, and
here it was really one architectural fact stated four times.

### 4.7 Smaller things

- `__init__.py` files count toward "scanned 8 Python module(s); the map places 8
  of them" while carrying no edges. Three of this project's eight modules are
  package markers. The coverage figure sounds stronger than it is.
- The "Out of scope" line lumps `__future__`, `typing` and `pipeline_contract`
  together and labels all three "standard library and third-party packages".
  `pipeline_contract` is neither; it is generated from the very model being
  checked. That mislabeling is the user-visible surface of 4.1, and it is the
  line a reader would have to notice to catch the problem.
- `crossing_action_fraction <= 0.5` is measured at 0.40 here on 5 actions — two
  of them cross. One more crossing action would be 0.60 and the partition would
  stop being a cut. On a five-action model the criterion has a granularity of 20
  percentage points, and small models will flip across it for reasons that have
  nothing to do with their architecture.

### 4.8 What works, stated because it is the point of the exercise

The `unfalsifiable_coherence` defence stopped the cheapest attack I tried (3.b) and
stopped it correctly, with a message that explains itself. `divergence_detectable`
being printed *above* the findings, and the basis travelling inside the verdict
object, meant I could tell at a glance that the green result was falsifiable rather
than vacuous. Every divergence carried a `file:line` I could paste, and all four
were true. The check found a real import cycle that a comment in the source had
rationalised. Its diagnosis of this codebase was correct; my complaints are all
about what it additionally lets through.

---

## 5. Friction with the tooling and its documentation

- **The README's test command does not run.** `python3 -m pytest tests -q` fails
  with `No module named pytest` on this machine — only the pinned venv has it. The
  ticket supplied the right interpreter; the project README does not mention that
  one is needed.
- **`--components` is effectively mandatory, and the docs present it as optional.**
  `references/architecture_coherence.md` describes an `EMERGENT` partition as the
  default. Running the check without `--components` exits 2:
  `maps modules onto component(s) the model does not have: dispatch, ingest,
  ledger. The model's components are: C1, C2.` Any project with a human-written
  map is refused, because emergent components are named `C1`/`C2`. That is
  correct behaviour and an excellent error message; the docs should just say the
  two flags come as a set, the way they say `--code` and `--map` do.
- **Documented artefacts that do not exist in this checkout.** The reference
  points at `tests/test_architecture_reflexion.py` (the toolchain checkout has no
  `tests/` directory), at
  `specs/.history/architectural-coherence-epic/ticket-002-AC-02/results/dogfood-findings.txt`,
  and at a `tla-spec-dev analyze architecture` CLI (only
  `scripts/architecture_reflexion.py` ships here). None blocked me; all cost time
  to chase.
- **`spec_manifest.yaml` is named as a source of truth by files that ship without
  it.** Every file in `generated/pipeline_contract/` has a header reading
  `Source of truth: - Pipeline.tla - spec_manifest.yaml`, and the reference
  documents `architecture:` living in that manifest. There is no
  `spec_manifest.yaml` anywhere in this project. I lost time looking for it before
  concluding `--components` is the only route.
- **Missing `--map` produces a bare argparse error** (`the following arguments are
  required: --map`), exit 2. Correct code, but the docs promise a considered usage
  error explaining why half a reflexion check is refused; the tool just declines
  to parse. Minor, and the exit code is right.
- **The absence message asks a question it has the data to answer.** "dead
  architecture, or an interaction the extractor cannot see" — for `P2` it was
  certainly the latter, and the remedy the phrasing nudges you toward (add code
  until the edge appears) is the opposite of what a reviewer looking at
  `Journal.record(item, delivered)` would advise. See 4.3.
- **No `--version`, no digest of the tool itself in the report.** The report
  records `basis.map_digest` and `basis.architecture_digest` so the map and the
  model are pinned, but nothing identifies which build of the extractor produced
  the verdict. Given 4.1 — where a verdict flips on extractor behaviour rather
  than on the code — a stored `coherent` from an older build cannot be compared
  with one from a newer build.
