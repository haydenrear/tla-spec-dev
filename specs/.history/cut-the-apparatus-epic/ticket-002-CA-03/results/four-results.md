# `GOAL-four-results-stand` — all four verified at CA-03's head

**CA-03 is the highest-risk ticket in this epic for this goal:** `score_tools.py`
produced all four results, and it is CA-03's only production conflict key.

**Verified by reading the sealed cards, not by reading the prose about them.**
Each figure below is recomputed from `scorecard.json` on disk.

---

## 1. Asking for an architecture changes the architecture — **REPRODUCES**

| card | arm | D3 |
|---|---|---|
| `hexagonal-prompting/…/20260804-owner-pre` | `A-control-reference` | **1** |
| `hexagonal-prompting/…/20260804-hp06-X-p1,p2` | `X` (with prompt) | **4, 4** |
| `hexagonal-prompting-rerun/…/20260804-rerun-P-p1,p2` | `P` | 2, 2 |
| `hexagonal-prompting-rerun/…/20260804-rerun-Q-p1,p2` | `Q` (with prompt) | **4, 4** |
| `ports-as-adapters/…/20260805-W-p1,p2` | `W` = **arm C** | **1, 1** |

**`1 → 4` on the prompt alone, replicated in the rerun, and the confound killed
directly**: arm C, a *longer* prompt carrying no architectural vocabulary, scores
**1/1**.

## 2. D3 separates architectures on more than one example — **REPRODUCES**

`eval_toolchain`, RM-04. D3 by arm and judge tier:

| arm | opus | sonnet | range |
|---|---|---|---|
| `GG` (ports-and-adapters) | 2 | 4 | **[2, 4]** |
| `JJ` (effectful) | 1 | 0 | **[0, 1]** |
| `LL` (effectful) | 1 | 0 | **[0, 1]** |

**Disjoint, both judge tiers on both sides.**

## 3. D3's v5 caveat discriminates — **REPRODUCES**

| round | artifact | v4 | v5 |
|---|---|---|---|
| `score-drives-validation-sv01-*` (`GL`) | **lacks** the single-observer property | D3 **4, 4** | D3 **4, 4** |
| `close-the-loop-cl03-v*` (`CL`) | **has** it | D3 **4, 4** | D3 **3, 3** |

The prediction was sealed at a timestamped commit before any judge ran. The
discount `SV-01` disclosed about itself (`SV-01-DF-01`, contaminated scratch
paths) stands unchanged — CA-03 neither repairs nor relies on it.

## 4. A score can produce a test and the re-score sees it — **REPRODUCES**

`score-drives-validation-sv04`, `toolchain_removal`, all v5:

| arm | D3 | D2 |
|---|---|---|
| `GL` (control) | **3, 3** | 2, 2 |
| `LG` (treatment, same bytes plus one file) | **4, 4** | 2, 2 |

**D2 flat at 2 across all four**, exactly as the baseline records.

---

## The instruments `RM-02` called the substrate's best export

| instrument | at CA-03's head |
|---|---|
| `serve` / the version-served double seal | `6281` bytes, `sha256:2d7d4a0506d9b259`, unchanged |
| `seal` | runs |
| `contested` | runs |
| `audit` (R-H1…R-H6) | **`0 violation(s)`** |
| `scope` (R3) | runs — `102 counted figure(s): 80 REFUTED, 0 COUNT-MOVED, 2 HOLDS, 20 UNREACHABLE` |
| the blinding mechanism | runs, and CA-03 extends what it records without weakening it |

**The blinding mechanism is the one CA-03 touched.** It withholds exactly what it
withheld before — `subject.name` and `declared_effect_boundary` are still absent
from a blinded card, asserted by
`test_a_blinded_card_carries_the_scope_and_nothing_that_identifies_it`, unchanged.
What is added is a record **outside** the card, in the file judges are not given,
of which round produced which label — the same class of secret as `UNBLINDING.md`
and kept in the same place: not in the judge's directory.
