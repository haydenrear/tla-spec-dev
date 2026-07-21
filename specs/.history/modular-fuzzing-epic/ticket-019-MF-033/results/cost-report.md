# MF-033 — Cost report: making the effect oracle observe out-of-process work

**Ticket is also a cost probe.** The code is one deliverable; this writeup is
the other, and it is what decides the next tickets. Measured against epic tip
`67426dc`. Evidence in this directory: `effect-conformance-before.json`,
`effect-conformance-after.json` (produced by `observe_out_of_process.py`),
`tlc.txt`, `spec-unit.txt`, `pytest.txt`, `graph-*.txt`.

---

## 0. Headline

**Out-of-process filesystem observation is cheap, portable, and real — and it
does NOT get a shelling-out repo to a `clean` verdict, for a reason that will
not go away without expensive work.** The effect oracle now genuinely sees a
child process's filesystem effects and diffs them against the declared ports.
On this repo's own surface that moved a dead port to exercised and turned a
blanket "everything about the child is invisible" refusal into a precise
"filesystem observed; network unobserved". But the verdict is still
`unobservable`, because a filesystem snapshot diff cannot see a child's network
connections, and observing those needs either syscall capture (privileged,
non-portable) or in-process invocation of every adapter (the "large" axis
MF-028 already named). That residual is the answer the owner asked for.

---

## 1. What was made observable, and how

`scripts/effect_conformance.py` (the only production conflict key) gained a
second observer that reaches *across* the process boundary the in-process
`EffectSandbox` cannot cross:

- **`WorkingTreeObserver`** — snapshots a set of working-tree roots (file →
  size + mtime) *before* an execution window and diffs them *after*. A file that
  appeared or changed is a `filesystem.write`; a file that vanished is a
  `filesystem.delete`. It is pure stdlib (`os.stat`/`rglob`), needs no
  privileges, adds no dependency, and works **regardless of the child's
  runtime** — Python, java (TLC), or pytest all leave the same filesystem trace.
- **`OutOfProcessObservation`** — the positive-evidence record an observer
  leaves: which effect *types* it covered, over which root, how many effects it
  saw. `diff_effects` grew an `out_of_process=` parameter that consumes these.

This is added observability, not a weakened refusal (see §3).

## 2. The actual advisory verdict on this repository

Driver: `observe_out_of_process.py` runs the real, shelling-out
`ScaffoldProjectAdapter` (MF-028's measured case) through its real
`subprocess.run` spawn, twice, against the **real** five declared ports from
`specs/current/spec_manifest.yaml`. It uses a results-local driver and no
production-corpus binding (that is MF-023's surface); it exercises one action,
so the four ports belonging to other actions read as honest dead surface.

| | BEFORE (in-process sandbox only = MF-028 state) | AFTER (+ WorkingTreeObserver) |
|---|---|---|
| observed effects | 2 | 17 |
| child effects recovered out-of-process | 0 | **15** (all match `**/specs/**`) |
| `spec_tree` port | **dead** | **exercised** |
| process-boundary finding | blanket: "writes, deletes **and connections** invisible" | narrowed: "filesystem observed out-of-process; **network.connect, network.http, process.spawn** have no observer" |
| verdict | `unobservable` | `unobservable` (residual named precisely) |

Two of the three findings the oracle now produces are **real advisory signals
the sandbox alone could never have generated**:

- **`spec_tree` is no longer dead.** The child CLI wrote 15 files under
  `target-repo/specs/program_model/`; the diff recovered every one and matched
  it to the `**/specs/**` port.
- **A genuine gap.** The `ScaffoldProject` action declares `[spec_tree]` but not
  the `python3 tla_spec_dev.py` spawn it performs. The oracle correctly reports
  that spawn as an **undeclared effect (gap)** — the model is blind to the fact
  that this action shells out. That is exactly the "statement about the program"
  the doctrine wants surfaced.

The five ports, per the acceptance criterion (observed by a case, or honest
dead/unobservable — never deleted):

1. `spec_tree` — **observed** (15 out-of-process child writes).
2. `evidence_report` (`**/results/**`) — dead in this 1-action demo; exercised by
   `AnalyzeComplexity`/`AnalyzeCorpus`/`RunEffectConformance`/`RunKillTest`.
3. `cli_artifact` (`**/.venv/**`) — dead here; exercised by
   `BuildSkillCli`/`InstallLocalCli`.
4. `tlc_process` (`*java*`) — dead here; exercised by `AnalyzeComplexity`.
5. `test_process` (`*pytest*`) — dead here; exercised by
   `RunKillTest`/`RunSpecUnitTests`.

Declarations preserved; the dead findings are a statement about a reduced,
single-action demonstration corpus, not gamed away by deleting evidence.

## 3. MF-027 polarity survived — proven, not asserted

The risk of this ticket was that teaching the oracle to see child writes would
let it start *passing* runtimes it still cannot see. It does not. Tests in
`tests/test_effect_conformance.py::TestPolaritySurvivesOutOfProcessObservation`
pin every guard:

- **A spawn with no out-of-process evidence is unchanged** — still fully
  `unobservable` (the MF-027 default; all pre-existing MF-027 tests still pass).
- **Filesystem-only coverage still leaves the network unobservable** — observing
  the filesystem does *not* certify the network; the verdict stays
  `unobservable` and the residual is named.
- **Only positive coverage of _every_ axis discharges the boundary** — and a
  filesystem-only observer never reaches that, which is precisely why this repo
  stays unobservable. There is no flag that fakes it: `out_of_process` carries
  *observations*, and empty observations discharge nothing.
- A runtime refusal (JVM adapter) is untouched by filesystem coverage nearby.

`diff_effects` grew an *evidence* parameter, never a suppression one; `report.ok`
still consults only the finding lists; the CLI grew no downgrade flag. The full
508→526 repo suite is green (+14 MF-033 tests, 0 regressions).

## 4. What it cost, and how much generalizes — the owner's decision

**Cost of this ticket:** ~130 lines of production observer + evidence plumbing in
one file, ~120 lines of results-local driver, 14 tests. Conceptually small; no
new dependency; portable. The *observation mechanism* is cheap.

**How much reuses for the other four oracle actions — split into two claims:**

1. **The observation mechanism generalizes fully and cheaply.** Every oracle
   action (`RunEffectConformance`, `AnalyzeComplexity`, `AnalyzeCorpus`,
   `RunKillTest`, `RunSpecUnitTests`, `CloseTicket`) writes evidence into
   `**/results/**` or `**/specs/**` via a child process. `WorkingTreeObserver`
   sees those writes with zero new code — the same snapshot diff. So the
   *filesystem axis* of all of them is now observable.

2. **But that is not the thing that makes them case-executable, and that part
   does NOT generalize.** The 89.2% MF-032 measured is oracle actions whose
   after-state is a **verdict** (clean/gaps, a kill rate, a complexity score),
   not a filesystem tree. Observing that an oracle *wrote a report* tells you
   nothing about whether its *verdict* was right. Making an oracle's verdict
   case-comparable is **verdict projection** — read the verdict back out of the
   results artifact and compare it to the model's expected verdict — a different
   problem from effect observation, and MF-028 §4 already banded these HARD or
   BLOCKED for exactly that reason (each oracle's `apply()` is a multi-branch
   battery, not one transition). It is **N bespoke problems, one per oracle.**

**So the two questions the owner posed resolve cleanly:**

- *Does making the effect oracle produce a real signal generalize to the other
  four oracle actions?* **The observation half yes; the signal half no.** The
  cheap, general win (out-of-process filesystem observation) makes every oracle's
  filesystem effects visible. It does not make any oracle's *verdict*
  case-replayable — that is per-oracle projection work with no shared shape.

- *Is it worth chasing the remaining 90% to full case-execution, or should
  oracles be run advisorily?* **Run them advisorily.** Two independent walls
  make full case-execution a bad trade:
  - **The effect oracle itself cannot reach `clean` on any shelling-out repo**
    without network syscall capture (privileged, non-portable) or rewriting every
    adapter to invoke the CLI in-process (MF-028's "large" axis). The cheap
    observer gets you "filesystem observed, network named" and no further.
  - **The oracle *verdicts* are N separate projection problems**, and the payoff
    of solving them — a *blocking* conformance gate — is exactly what the
    2026-07-20 advisory reframe retired. Building verdict projection to feed a
    gate that no longer blocks is effort spent to reach a destination that was
    removed.

## 5. Recommendation

1. **Keep the cheap, general win.** `WorkingTreeObserver` is a real upgrade: the
   effect oracle now produces true filesystem signals (dead→exercised, gaps it
   could not see before) and names its residual precisely instead of refusing in
   a blanket way. Wire it into the production corpus run when MF-023 binds the
   corpus (out of scope here).
2. **Do not chase per-oracle verdict projection to make the 90%
   case-executable.** It does not generalize, and it targets a gate the reframe
   already made advisory.
3. **Run the oracles advisorily** — execute each and record its verdict as an
   advisory signal — rather than case-replaying it against a projected expected
   verdict. That is the honest reading of both this cost probe and
   `references/architecture_tractability.md`, "Advisory, Not Blocking".
4. If a `clean` effect-conformance verdict on a real shelling-out app is ever
   *required* (not just advisory), the only two roads are network syscall
   capture or in-process adapter invocation. Both are large; neither should be
   scoped until real-app validation (MF-037) shows the blocking gate is worth
   it.
