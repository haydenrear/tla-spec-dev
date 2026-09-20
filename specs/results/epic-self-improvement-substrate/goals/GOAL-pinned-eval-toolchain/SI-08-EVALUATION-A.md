# `GOAL-pinned-eval-toolchain` — Evaluation A (SI-08), frozen reading

**Measured 2026-09-20 at base `2131cdad`.**
Instrument, as the plan names it: *"the suite's own run record, plus a read of
the case scaffold: the pinned ref must appear in the repository, not only in a
run log."*

> **Baseline (45a42b54).** 0 of the loop's runs record a toolchain version. skt
> resolves from the operator's live home at gitRef `main` (gitHash `286a3694`,
> installed 2026-09-14), and `main` is a moving target; nothing in either harness
> pins it, asks for it, or writes it next to a score.
>
> **Target.** every full-suite run records the skt ref it used; the ref is pinned
> in the repository rather than resolved from the operator's home; the runner asks
> which version before a full run and refuses to guess silently.

---

## Clause 2 — "the ref is pinned in the repository rather than resolved from the operator's home"

### VERDICT: **MET**, and the pin demonstrably changes which bytes run.

`evals/lib/toolchain.lock.toml` exists in the repository and pins **commits, not
branches** — `toolchain.py` refuses anything that is not 40 hex characters:

| unit | pinned commit | `ref_when_pinned` |
|---|---|---|
| `skt` | `286a3694a815c6f6a9e76bffcb03a1fd8100cce3` | `main` |
| `skill-manager` | `6ffacb88ff968aafadaa464811a77be7f3ddffd1` | `epic/self-improvement-substrate` |

I ran the materialiser (`materialise --check-drift`, exit **0**, record at
`toolchain-run-record.json`). It fetched both units, **verified the checked-out
HEAD IS the pinned commit** (`verified_head == pinned_commit` for both), and
reported drift on both refs:

```
drift: skill-manager: epic/self-improvement-substrate HAS MOVED to d27601417293
       since the pin at 6ffacb88ff96 -- the pin is doing its job
drift: skt: main HAS MOVED to 0f3807811e1d since the pin at 286a3694a815
       -- the pin is doing its job
```

**This is the decisive measurement for the clause, and it is not a claim about
the future.** The record's `ambient_home_would_have_used` field says the
operator's home today resolves skt at **`0f3807811e1d`** (installed
2026-09-18) — while the pin ran **`286a3694a815`**. The two differ. So the pin
is not decorative: on this machine, on this day, pinned and ambient are already
*different code*, and the baseline's "moving target" has measurably moved twice
since the lock file was written.

The CLI's own self-report corroborates it rather than being taken on our word:
`skill-manager 0.28.1+g6ffacb88ff96`, `build: 6ffacb88ff96 (detached)` — against
the operator's brew install at plain `0.28.1`.

## Clause 3 — "the runner asks which version before a full run and refuses to guess silently"

### VERDICT: **MET**, and both halves were exercised, not only read.

Read of `evals/run.sh:171-212` — four branches, and the ask is the only one that
is interactive:

| condition | behaviour |
|---|---|
| `--toolchain-ref <c>` | uses it, announces **"(recorded as an OVERRIDE)"** |
| `SI14_TOOLCHAIN_REF` set | same, announced as an override |
| full suite **and** a tty (`[ "$case_glob" = '*' ] && [ -t 0 ]`) | **THE ASK** — prints the pin, prints that the operator's home would have used something else, and reads an answer |
| full suite, no tty | takes the pin and says so loudly: *"Nothing was guessed"* |
| single case | defaults to the pin and **names it** |

**Exercised, not inferred:**

- **The refusal fires.** `toolchain.py materialise --ref no-such-ref-si08-probe`
  → exit **1**: *"'no-such-ref-si08-probe' does not resolve on
  https://github.com/haydenrear/skt.git. Refusing to run against a toolchain
  nobody can name."*
- **An override is recorded as an override.** `materialise --ref main` → exit 0,
  resolved to `0f3807811e1d`, and the record marks it
  `"ref_source": "OVERRIDE: operator asked for 'main'"` rather than "pinned"
  (`toolchain-override-record.json`). This is the half that makes "the runner
  asked and I answered something else" visible afterwards instead of
  indistinguishable from the pin.

**One honest caveat.** The interactive ask is gated on `[ -t 0 ]` and every run
this ticket made was non-interactive, so **the tty branch was read and not
executed.** What was executed is the no-tty branch, the override branch and the
refusal. A human at a terminal running the full suite is unverified by this
ticket.

## Clause 1 — "every full-suite run records the skt ref it used"

### VERDICT: **MET for the run that exists — 1 of 1 — and the denominator was 0 until this ticket made it 1.**

The metric is *"eval runs whose recorded evidence names the exact skt ref they
ran against, over eval runs performed"*. Measured at the base:

- `evals/results/` **did not exist**. No run record had ever been written.
- **61 eval cases are in `evals/` and NONE had been scored.** SI-14 shipped the
  pin without running a scored case through it, so nothing proved a pinned ref
  reached a score. The ratio was **0 / 0**.

**This ticket ran one scored case to close that gap** (`RUN-ATTEMPT.md`, with the
cost): `./evals/run.sh --case use-the-front-door` — 1 case, 1 run, **$0.54**,
106 s, score **0.67**. It wrote
`evals/results/toolchain/20260920T164507Z.json`, schema
`si14.toolchain-run-record.v1`, naming `skt 286a3694a815` and
`skill-manager 6ffacb88ff96` with `verified_head == pinned_commit` for both, and
staged the pinned skt's skills into the view. **So the ratio is now 1 / 1.**

**Three limits on that verdict, and they are not small:**

1. **The ref is not next to the score.** `aggregate-result.json`, the artifact
   carrying the 0.67, contains **zero** occurrences of `toolchain`, `pinned`, or
   either sha. The record is a *sibling* joined to the score by **nothing but
   timestamp proximity** (`20260920T164507Z` vs run dir `2026-09-20T16-45-12-045Z`),
   sharing no run id. `SI-08-DF-05`.
2. **The run record is gitignored** (`.gitignore:32` → `evals/results/`), so a
   run does not persist its own record in the repository. The *pin* is committed
   and that is what the goal's harness requires; the *records* are not.
   `SI-08-DF-06`. Copies of both artifacts are preserved in `first-scored-run/`.
3. **One run is not "every run".** 1 of 1 is a ratio of one. 60 of the 61 cases
   remain unscored, and **a pinned ref has still not been shown to MOVE a
   score** — that needs the same case at two refs, ~$1.08, not run.

---

## Summary

| clause | baseline | measured | verdict |
|---|---|---|---|
| ref pinned in the repo, not the home | 0 pinned; `main` moving | 2 units pinned by 40-hex commit; HEAD verified; ambient home already diverged (`0f380781` vs pinned `286a3694`) | **MET** |
| runner asks, refuses to guess | nothing asks | ask branch present; refusal **exercised** (exit 1); override **exercised** and recorded as an override | **MET** (tty branch read, not executed) |
| every full-suite run records the ref | 0 of N; `evals/results/` absent, 61 cases, 0 ever scored | **1 of 1** — this ticket ran the suite's first scored case ($0.54) and it wrote a `si14.toolchain-run-record.v1` naming both pinned commits | **MET for the one run**, with three limits: the ref is not in the score artifact, the record is gitignored, and 60 of 61 cases remain unscored |

**The honest one-line reading of this goal:** the pin is real, committed,
verified and demonstrably different from what the operator's home would have
supplied — and as of today exactly **one** scored run has ever been put through
it.
