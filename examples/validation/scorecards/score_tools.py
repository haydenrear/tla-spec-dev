#!/usr/bin/env python3
"""Scorecard scaffold, schema check, index, and history reader (scorecard_version 3).

Deliberately lives under examples/validation/ rather than scripts/: scripts/**
is IN MODEL per the plan's representation_scope, and eval harness is not program
surface. Putting it here keeps the model's surface unchanged.

  python3 score_tools.py scaffold <epic-dir> --example E --arms A,B,C --judges 2
                                  [--card-version {1,2,3}]
  python3 score_tools.py serve [--card-version N] [--rubric F] [--out FILE]
  python3 score_tools.py check <dir-or-file>... [--require-filled]
  python3 score_tools.py index <epic-dir>
  python3 score_tools.py history --example E [--root DIR] [--write FILE]
  python3 score_tools.py audit [--root DIR]
  python3 score_tools.py seal <dir>...
  python3 score_tools.py contested [--root DIR] [--example E]
  python3 score_tools.py scope [--path P ...] [--format text|json]

`contested` and `scope` are RD-01's two additions and they answer the same
defect at two granularities: A CLAIM READ FORWARD WITHOUT BEING CHECKED.

`contested` computes scoring rule 5 instead of asking a judge to declare it. The
rule has said since version 1 that a spread greater than 1 across two blind
judges is contested; nothing ever computed it, every card ever written carries
`contested = []`, and `index` printed a dash on all four rows of the round where
D3 came out 2, 2, 3, 4. It also reports a TIER SPLIT -- a dimension where two
judge tiers do not overlap at all on the same artifact -- which is a fact about
the card that no field held.

`scope` executes R3: A CLAIM CARRIES ITS SCOPE. A figure of the form
"D<n> = k on N of N cards" is a statement about whichever examples produced
those N cards; when the population its own words denote is wider than the set it
was computed over, THE CLAIM IS WRONG EVEN WHEN EVERY NUMBER IN IT IS RIGHT.
`subtract-to-measure` was opened on such a figure, restated it four times, and
"verified" it with a script containing `if "ab_quota_ledger" not in f: continue`.
`scope` re-derives every such figure it can find against the cards on disk and
names the counterexamples. IT EXITS 1 ON THIS REPOSITORY'S OWN RECORD, and that
is its demonstrated failing input rather than a defect in it.

`serve` is the version 3 answer to a defect measured at FI-03: four judges were
dispatched with "references/eval_scorecard.md -- the rubric. Read it", and that
file also carries reading rules and prior results ABOUT THE FIVE DIMENSIONS THE
JUDGES WERE SCORING. Both v1 judges cited one of those paragraphs, unprompted,
as their reason for scoring D4 the way they did (FI-06-DF-04, FI-03-DF-02). A
judge must never be handed the finding they are the instrument for.

So the rubric a judge sees is RENDERED from the parsed structure of the file --
dimensions, anchors, caveats, scoring rules -- and nothing else. Every other
section is outside what the renderer emits, so a new section does not reach a
judge by default. `scaffold` writes the same bytes into `scorecard.md`, so there
is exactly ONE served surface, and every card records its digest.

`--card-version N` exists so a prior version of the card can be reproduced.
Changing the card requires re-scoring a prior example under BOTH versions, and a
tool that can only emit the current version makes that impossible -- so the
ability to scaffold the OLD card is part of the change rule, not a debugging
convenience. NOTE WHAT IT DOES NOT DO (FI-06-DF-11(c), open): it stamps the
requested version while reading every anchor and rule from the rubric it is
POINTED AT. Reproducing an old card means also pointing it at a frozen copy of
the old rubric, with `--rubric`.

`check` enforces the rules from references/eval_scorecard.md that can be
enforced mechanically. The ones that matter -- score artifacts not claims, prose
quality is never an input -- cannot be, which is why two blind judges exist.

`scaffold` exists because for two epics every card was hand-authored from the
rubric by whichever agent was judging, which is how a dimension key or the
`refuses_to_claim` requirement drifts. The anchors are READ FROM THE RUBRIC and
written INLINE into the skeleton, so there is one source of truth and the judge
reads the bar for a score in the same file where the score is written.
Blinding is the DEFAULT: arms are emitted under opaque labels and the mapping
goes to an unblinding file. Unblinded scoring must be asked for, with a reason.

`history` and `audit` exist because a sealed row can go stale without anyone
noticing. The eval instrument was repaired AFTER a round measured on it, and a
scorer comparing naively across that boundary would have compared two different
instruments and called the difference progress. See
`references/eval_scorecard.md`, "Reading history", rules R-H1..R-H4 -- every one
of which is implemented by `audit` rather than merely written down.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import pathlib
import random
import re
import subprocess
import sys
import tomllib
from datetime import date as _date

VERSION = 4
SUPPORTED_VERSIONS = (1, 2, 3, 4)

# The dimension whose top anchor carries two defensible readings, and the card
# version from which the reading is a recorded field rather than a private one.
# This is version 2's move applied to an anchor instead of to a practice:
# RECORD THE CHOICE, NEVER MANDATE IT. The bar did not move -- `anchors_digest`
# is byte-identical across versions 1, 2 and 3 and `check` recomputes it.
#
# It is required only at 3 and 4. Below that the two readings cannot differ:
# anchor 2 is "names its blind spots" and anchor 3 is "refuses rather than
# falsely certifies", and neither turns on what counts as an unflattering
# result.
ANCHOR_READING_DIM = "D5"
ANCHOR_READING_SCORES = (3, 4)
ANCHOR_READINGS = ("disclosure", "measured")

# The dimension whose TOP ANCHOR cannot be awarded from the evidence packet.
# D4's anchor 4 asks for "a deliberate behavior-breaking change ... shown to be
# CAUGHT -- the check is demonstrated to be capable of failing". A judge who
# executes one can say that; a judge reading a table is repeating a claim. This
# is not new guidance: it is the anchor's own text, made checkable, after
# PA-06-DF-06 measured four dimension-points moving on byte-identical trees
# because two judges privately chose to execute and nothing recorded it.
#
# D1 and D5 also moved, and they are deliberately NOT gated here. D1's anchor 4
# asks that the cases be model-derived and that the record name a class it
# cannot reach; D5's asks that the record contain an unflattering result.
# Neither needs the judge to run anything, so gating them would be inventing a
# requirement rather than executing one.
PRACTICE_GATED_DIMS = ("D4",)

DIMS = ("D1", "D2", "D3", "D4", "D5")
NAMES = {
    "D1": "bug detection",
    "D2": "complexity",
    "D3": "modularity",
    "D4": "behavior preservation",
    "D5": "honesty",
}
CITE = re.compile(r"^[^\s:]+:\d+(-\d+)?$")

# ---------------------------------------------------------------------------
# WHAT VERSION 4 REMOVED, and why none of the code above it could go with it
# ---------------------------------------------------------------------------
#
# `DIMS` is every dimension key that has ever been scored, and it stays five
# long forever: 73 sealed cards carry all five and `R-H4` says a sealed card is
# never edited, so every rule those cards were written under is still executed
# here. What version 4 changes is which dimensions a NEW card scores.
#
# D1 and D4 grade this project's toolchain rather than the artifact -- an anchor
# decision cites this repository's machinery in 38% of D1 rationales and 18% of
# D4 rationales against 4% on D2 -- and neither survives the trip to another
# project. D5 is orthogonal to architecture by measurement. All three keep their
# QUESTION as a recorded note and lose their NUMBER.
RETIRED_AT = 4
RETIRED_DIMS = ("D1", "D4", "D5")

#: The note key a retired dimension's question is recorded under.
NOTE_KEY = {dim: f"N-{dim}" for dim in RETIRED_DIMS}

#: The top of each dimension's scale, per card version. D2's anchor 4 gated the
#: one portable dimension on `D4 >= 3`, and D4's anchor 3 required a
#: model-derived check -- so the top of the dimension that travels was gated on
#: the clause that does not. Deleting the anchor costs the top of the scale, and
#: that cost is this dict rather than a sentence somewhere.
TOP_SCORE_V4 = {"D2": 3, "D3": 4}


def scored_dims(version: int) -> tuple[str, ...]:
    """The dimensions a card of this version carries a SCORE for."""
    if version >= RETIRED_AT:
        return tuple(d for d in DIMS if d not in RETIRED_DIMS)
    return DIMS


def note_dims(version: int) -> tuple[str, ...]:
    """The dimensions this version records as prose instead of scoring."""
    return RETIRED_DIMS if version >= RETIRED_AT else ()


def top_score(dim: str, version: int) -> int:
    """The highest anchor `dim` carries at this version. Rule 3 keys on it."""
    if version >= RETIRED_AT:
        return TOP_SCORE_V4.get(dim, 4)
    return 4

HERE = pathlib.Path(__file__).resolve()
REPO_ROOT = HERE.parents[3]
DEFAULT_RUBRIC = REPO_ROOT / "references/eval_scorecard.md"
DEFAULT_SCORECARD_ROOT = REPO_ROOT / "specs/results/scorecards"
LOG_NAME = "INSTRUMENT-LOG.toml"

# Never used as an opaque arm label: the arm names themselves. Labels prior
# rounds published are excluded dynamically -- see used_labels().
RESERVED_LABELS = set("ABC")
LABEL_POOL = "DEFGHJKLMNRSTUVWZ"

# RM-04, `RM-02-DF-01`. THE POOL RAN OUT: 17 characters, 13 published, `G J L V`
# left, and a round needing five arms was already refused.
#
# THE CONSTRAINT IS THE PROPERTY, NOT THE MECHANISM: a judge must not be able to
# connect a label to anything they could have seen before. Global single-
# character uniqueness was one way to get that and it has a bounded lifetime
# baked into a constant.
#
# What ships instead: a label is a STRING over the characters this repository
# has never published as a label, and the width grows when a width runs out. At
# width 2 that is `GG GJ GL GV JG ...` -- 16 labels; at width 3, 64; and so on
# without bound. TWO PROPERTIES, both exact rather than argued:
#
#   1. No label emitted from here has ever been published. Exclusion is on the
#      WHOLE STRING and `used_labels` reads whole strings.
#   2. No CHARACTER of a label emitted from here has ever been published on its
#      own either, so a judge who saw `T` in a prior round meets nothing that
#      shares a character with it.
#
# Width 1 is deliberately NOT offered even though four single characters remain.
# Spending them as labels would destroy the alphabet every wider label is built
# from -- four labels once, against sixteen and then sixty-four. That is the
# reason for the floor, and it is a reason rather than a preference.
MIN_LABEL_WIDTH = 2
MAX_LABEL_WIDTH = 4


def label_alphabet(published: set[str]) -> str:
    """The characters no prior round published as a label, and none reserved."""
    return "".join(c for c in LABEL_POOL
                   if c not in published and c not in RESERVED_LABELS)


def available_labels(published: set[str], needed: int) -> tuple[list[str], int]:
    """`(labels to draw from, width)` for a round needing `needed` arms.

    The narrowest width at or above `MIN_LABEL_WIDTH` that can serve the round.
    Returns `([], 0)` when no width up to `MAX_LABEL_WIDTH` can -- a refusal,
    never a fallback to a label somebody has already seen.
    """
    alphabet = label_alphabet(published)
    for width in range(MIN_LABEL_WIDTH, MAX_LABEL_WIDTH + 1):
        pool = ["".join(t) for t in itertools.product(alphabet, repeat=width)]
        pool = [x for x in pool if x not in published]
        if len(pool) >= needed:
            return pool, width
    return [], 0

# `current` is the only status that asserts a number NOW, so it is the only one
# R-H3 polices across an era boundary. The others each cost something to use:
# `sealed` says explicitly that the number is not read forward, `superseded`
# needs to name its successor, `known_wrong` needs a reason, `under_review`
# needs a filed finding id, and `refuted` needs to name who falsified it and on
# what -- so no status can park a number quietly.
#
# `refuted` is deliberately NOT a synonym for `known_wrong`. `known_wrong` is a
# MEASUREMENT that stopped being true. `refuted` is an ASSERTION SOMEONE MADE IN
# REVIEW that was then falsified from data -- typically a filed finding. Keeping
# them apart is the point: a finding that turned out to be wrong is evidence
# about the review process, and this project keeps its superseded numbers on the
# record with a pointer rather than erasing them. A `refuted` claim KEEPS its
# `filed_as`, so the finding it came from stays reachable from the ledger.
CLAIM_STATUSES = {"current", "sealed", "superseded", "known_wrong", "under_review",
                  "refuted"}


# RD-05. The third comparability axis lives in a sibling module because it has
# a subject of its own -- the declared scopes and the derivation over them --
# and because this file is already the longest thing in the eval harness.
# Loaded by path rather than by name: `score_tools.py` is executed as a script
# AND loaded by `spec_from_file_location` from the tests, and only one of those
# puts this directory on `sys.path`.
_ARCH_CACHE: dict = {}


def arch():
    """The `effect_boundary` module. See `architecture_tags.py`."""
    if "mod" not in _ARCH_CACHE:
        import importlib.util
        path = HERE.parent / "architecture_tags.py"
        spec = importlib.util.spec_from_file_location("_score_tools_arch", path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        _ARCH_CACHE["mod"] = module
    return _ARCH_CACHE["mod"]


# --------------------------------------------------------------------------
# the rubric: one source of truth for the anchors
# --------------------------------------------------------------------------

class BlindingError(Exception):
    """A scaffold that would hand a judge the identity of what they are judging.

    Separate from `RubricError` on purpose: `RubricError` is about the BAR --
    a stale digest, an absent anchor, a version that cannot be emitted -- and
    callers let it propagate. This one is about the ROUND, it is raised while a
    batch is being planned, and `cmd_scaffold` turns it into a refusal that
    writes nothing.
    """


class RubricError(Exception):
    pass


def load_rubric(path: pathlib.Path) -> dict:
    """Parse the anchors and the scoring rules out of references/eval_scorecard.md.

    The anchors are NOT duplicated in this file on purpose. A rubric copied into
    the tool is a rubric that drifts from the one the judges are pointed at, and
    drift is the defect this command exists to remove.
    """
    if not path.exists():
        raise RubricError(f"rubric not found: {path}")
    text = path.read_text()

    # The version the FILE declares. It decides which dimensions this rubric is
    # required to carry, so it is read before the dimension blocks are parsed --
    # a version 4 rubric carrying five dimension blocks is as wrong as a version
    # 3 one carrying two.
    m = re.search(r"^\*\*Scorecard version (\d+)\.\*\*", text, re.M)
    file_version = int(m.group(1)) if m else 1
    want_dims = scored_dims(file_version)

    questions: dict[str, str] = {}
    for m in re.finditer(r"^\|\s*\*\*(D[1-5])\*\*\s*\|\s*\*\*([^|]+?)\*\*\s*\|\s*([^|]+?)\s*\|",
                         text, re.M):
        questions[m.group(1)] = m.group(3).strip()

    dims: dict[str, dict] = {}
    sections = re.split(r"^### (D[1-5]) — (.+)$", text, flags=re.M)
    # sections == [pre, key, title, body, key, title, body, ...]
    for i in range(1, len(sections) - 2, 3):
        key, title, body = sections[i], sections[i + 1].strip(), sections[i + 2]
        body = body.split("\n## ")[0]
        anchors: dict[str, str] = {}
        items = re.split(r"^- \*\*([0-4])\*\* — ", body, flags=re.M)
        for j in range(1, len(items) - 1, 2):
            score, chunk = items[j], items[j + 1]
            anchors[score] = " ".join(re.split(r"\n\n", chunk)[0].split())
        want = [str(n) for n in range(top_score(key, file_version) + 1)]
        if sorted(anchors) != want:
            raise RubricError(
                f"{path}: {key} does not carry anchors {want[0]}-{want[-1]} "
                f"(got {sorted(anchors)})")
        caveat = ""
        tail = re.search(r"\n\n(\*\*[A-Z].+?)\Z", body, re.S)
        if tail:
            caveat = " ".join(tail.group(1).split())
        preamble = " ".join(re.split(r"^- \*\*[0-4]\*\* — ", body, flags=re.M)[0].split())
        dims[key] = {
            "name": title.lower(),
            "question": questions.get(key, ""),
            "preamble": preamble,
            "anchors": anchors,
            "caveat": caveat,
        }
    missing = [d for d in want_dims if d not in dims]
    if missing:
        raise RubricError(f"{path}: no anchors parsed for {', '.join(missing)}")
    retired = [d for d in dims if d not in want_dims]
    if retired:
        raise RubricError(
            f"{path}: declares scorecard version {file_version} and still serves anchors "
            f"for {', '.join(sorted(retired))}. A retired dimension is kept in the file "
            f"under `Retired anchors` -- where a person comparing two versions can read it "
            f"and a judge scoring under either cannot be served it.")
    for key, dim in dims.items():
        if dim["name"] != NAMES[key]:
            raise RubricError(
                f"{path}: {key} is titled {dim['name']!r} but this tool knows it as "
                f"{NAMES[key]!r} -- the dimension key has drifted"
            )

    # The recorded notes, parsed out of the file exactly as the anchors are, so
    # the prompt a judge is served for a note has ONE home -- the same reason
    # `tests/test_card_has_one_home.py` exists.
    notes: dict[str, dict] = {}
    nblock = re.search(r"^## The recorded notes\s*\n(.*?)(?=^## )", text, re.M | re.S)
    if nblock:
        for m in re.finditer(r"^- \*\*(N-D[1-5]) — ([^*]+?)\.\*\* (.+?)(?=\n- \*\*N-D|\n\n|\Z)",
                             nblock.group(1), re.M | re.S):
            notes[m.group(1)] = {"name": m.group(2).strip(),
                                 "prompt": " ".join(m.group(3).split())}
    want_notes = [NOTE_KEY[d] for d in note_dims(file_version)]
    absent = [n for n in want_notes if n not in notes]
    if absent:
        raise RubricError(
            f"{path}: declares scorecard version {file_version} and carries no `## The "
            f"recorded notes` entry for {', '.join(absent)}. A dimension that stopped "
            f"being scored keeps its QUESTION; dropping the question as well would be a "
            f"different removal from the one the version history declares.")

    rules_block = re.search(
        r"^## Scoring rules that make it hard to game\s*\n(.*?)(?=^## )", text, re.M | re.S)
    if not rules_block:
        raise RubricError(f"{path}: no 'Scoring rules that make it hard to game' section")
    rules = [" ".join(m.group(1).split()) for m in
             re.finditer(r"^\d+\.\s+(.+?)(?=^\d+\.\s|\Z)", rules_block.group(1), re.M | re.S)]
    if len(rules) < 5:
        raise RubricError(f"{path}: only {len(rules)} scoring rules parsed; expected the full list")

    reading = []
    reading_block = re.search(r"^## Reading history\s*\n(.*?)(?=^## )", text, re.M | re.S)
    if reading_block:
        for m in re.finditer(r"^### (R-H\d+) — (.+?)$", reading_block.group(1), re.M):
            reading.append({"id": m.group(1), "title": m.group(2).strip()})

    card_version = file_version

    versions = []
    vblock = re.search(r"^#{2,3} Version history\s*\n(.*?)(?=^#{1,3} |\Z)", text, re.M | re.S)
    if vblock:
        for row in re.finditer(
                r"^\|\s*\*{0,2}(\d+)\*{0,2}\s*\|\s*`(sha256:[0-9a-f]+)`\s*\|\s*(.+?)\s*\|\s*$",
                vblock.group(1), re.M):
            versions.append({"version": int(row.group(1)),
                             "anchors_digest": row.group(2),
                             "summary": row.group(3).strip()})

    source = str(path.relative_to(REPO_ROOT)) if _under(path, REPO_ROOT) else str(path)
    rubric = {"source": source, "dimensions": dims, "notes": notes,
              "card_version": card_version,
              "scoring_rules": rules, "reading_rules": reading, "versions": versions}
    # The notes enter the digest only where they exist. A version 1-3 rubric has
    # none, so its digest is byte-identical to what every sealed card recorded --
    # adding a key to the payload unconditionally would have re-based 73 sealed
    # cards' `rubric.digest` and reported the whole record as scaffolded against
    # a stale bar, which is a fact about this edit and not about any card.
    payload: dict = {"dimensions": dims, "scoring_rules": rules}
    if notes:
        payload["notes"] = notes
    rubric["digest"] = "sha256:" + hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]
    rubric["anchors_digest"] = anchors_digest(dims)
    # The whole file, served and unserved alike. `FI-03-DF-02` asked for exactly
    # this: a record that the rubric file changed AT ALL between two rounds that
    # are being compared. It is deliberately not the drift check -- a typo in a
    # section no judge reads must not invalidate a skeleton.
    rubric["file_sha256"] = "sha256:" + hashlib.sha256(text.encode()).hexdigest()[:16]
    return rubric


# --------------------------------------------------------------------------
# what a judge is served, and the digest over exactly those bytes
# --------------------------------------------------------------------------

# A "result about this card" is a claim that one of the five dimensions MOVED,
# HELD STILL, or is STABLE or NOISY -- the class of statement FI-03's judges
# were handed and then cited back, unprompted, as their reason for scoring the
# way they did.
#
# THIS IS A BACKSTOP AND IT IS NOT THE MECHANISM. The mechanism is that
# `served_rubric` renders parsed structure only, so a section of the rubric
# cannot reach a judge unless the renderer puts it there. This list cannot be
# complete: an author who writes "D5 wobbles" passes it. It exists because the
# two leaks it was built against were BOTH INSIDE the served surface -- rule 8's
# cross-reference to R-H5, and the scaffold's own judging-practice section,
# which told every version 2 judge that "D1, D4 and D5 all moved on unchanged
# input" -- where the renderer could not help.
RESULT_WORDS = re.compile(
    r"\b(mov(?:e|es|ed|ing)|movements?|unchanged|held\s+still|holds\s+still|"
    r"stable|stability|unstable|instability|nois(?:e|y)|deltas?)\b", re.I)
# The subject has to be a dimension or a dimension's score. "Any dimension where
# two judges differ by more than 1 is contested" is a scoring rule, not a result.
RESULT_SUBJECTS = re.compile(
    r"(\bD[1-5]\b|\bdimension[- ]points?\b|\bjudge[- ]scores?\b)")


def result_leaks(served: str) -> list[str]:
    """Lines of the served text that assert how a dimension has scored or moved."""
    bad = []
    for i, line in enumerate(served.splitlines(), 1):
        subject = RESULT_SUBJECTS.search(line)
        word = RESULT_WORDS.search(line)
        if subject and word:
            bad.append(f"line {i}: {subject.group(0)!r} with {word.group(0)!r} -- "
                       f"{' '.join(line.split())[:160]}")
    return bad


def served_rubric(rubric: dict, card_version: int = VERSION) -> str:
    """THE BYTES A JUDGE IS SERVED. Rendered from parsed structure ONLY.

    Nothing here reads the rubric file as text. Every line is either written in
    this function or came out of `load_rubric`'s parse of a dimension block or a
    numbered scoring rule -- so `## Reading history`, `## Version history`, the
    storage layout, the change rule and anything a later editor adds are outside
    the served surface by construction rather than by a rule someone remembers.
    """
    out = ["## The rubric you are scoring against", ""]
    if card_version >= 3:
        out.append("**This is the whole rubric, and it is reproduced here so the bar for a "
                   "score sits in the same file as the score.** Do NOT go and read "
                   "`references/eval_scorecard.md`. That file also carries reading rules "
                   "and prior results about these same dimensions, and a judge who "
                   "reads those is being handed conclusions about the instrument they are "
                   "the instrument for.")
        out.append("")
    out.append("### The scoring rules")
    out.append("")
    for i, rule in enumerate(rubric["scoring_rules"], 1):
        out.append(f"{i}. {rule}")
    out.append("")
    out.append("**Score the LOWEST anchor the artifact fully satisfies; when torn "
               "between two, take the lower and say why.**")
    out.append("")
    if card_version >= 2:
        out.append("### Judging practice — REQUIRED, and it is a field on the card")
        out.append("")
        out.append("**Did you seed a fault of your own and run it against this artifact, or "
                   "did you score the evidence packet?** Both are legal. Neither is the "
                   "right answer. What is not legal is leaving it unsaid.")
        out.append("")
        out.append("Fill `judging_practice` in `scorecard.json`: `executed_own_faults` true "
                   "or false, and `what_was_run` listing what you actually ran.")
        out.append("")
        if card_version < RETIRED_AT:
            out.append("**D4's anchor 4 is only awardable when this says `true`**, because "
                       "that anchor asks for a behavior-breaking change *shown to be "
                       "caught*, and a judge reading a table is repeating the artifact's "
                       "claim rather than checking it. If you did not run one, the highest "
                       "D4 you can support is 3 — say that the packet asserts it and you "
                       "did not verify it.")
        else:
            out.append("**No anchor is gated on your answer.** The anchor that was is a "
                       "recorded note now. Say what you ran because it is the variable "
                       "that moves scores, not because a rung depends on it.")
        out.append("")
    for key in scored_dims(card_version):
        d = rubric["dimensions"].get(key)
        if d is None:
            continue
        out.append(f"### {key} — {d['name']}")
        out.append("")
        if d["question"]:
            out.append(f"*{d['question']}*")
            out.append("")
        if d.get("preamble"):
            out.append(d["preamble"])
            out.append("")
        for score in sorted(d["anchors"]):
            out.append(f"- **{score}** — {d['anchors'][score]}")
        out.append("")
        if d["caveat"]:
            out.append(f"> {d['caveat']}")
            out.append("")
    served_notes = [NOTE_KEY[dim] for dim in note_dims(card_version)]
    if served_notes:
        out.append("## The recorded notes — REQUIRED, and they take no score")
        out.append("")
        out.append("**Answer each in your own words and cite `file:line` as you would for a "
                   "score.** There is no 0–4 here and there is no anchor ladder: these "
                   "questions were scored for three versions and the numbers were measured "
                   "not to mean the same thing twice. *\"I could not tell, and here is what "
                   "I looked at\"* is a correct answer; an empty note is not.")
        out.append("")
        for key in served_notes:
            note = (rubric.get("notes") or {}).get(key)
            if note is None:
                continue
            out.append(f"### {key} — {note['name']}")
            out.append("")
            out.append(note["prompt"])
            out.append("")
    return "\n".join(out)


def served_digest(rubric: dict, card_version: int = VERSION) -> str:
    return "sha256:" + hashlib.sha256(
        served_rubric(rubric, card_version).encode()).hexdigest()[:16]


def anchors_digest(dims: dict) -> str:
    """A digest over the ANCHORS ALONE, separate from the rubric digest.

    The rubric digest covers the anchors AND the scoring rules together, so it
    moves whenever either does -- which is right for "was this card scaffolded
    against a bar that has since changed" and useless for "did the version bump
    keep the old anchors". `Changing this card` requires keeping them, and a
    requirement nothing computes is a requirement that drifts.
    """
    return "sha256:" + hashlib.sha256(
        json.dumps({k: v["anchors"] for k, v in dims.items()},
                   sort_keys=True).encode()).hexdigest()[:16]


def version_history_problems(rubric: dict) -> list[str]:
    """The card's own change rule, executed.

    Bump the version, keep the old anchors, and say what changed. A version
    history that does not carry the CURRENT version, or whose row for it does
    not match the anchors actually in the file, is the card changing silently.
    """
    bad: list[str] = []
    versions = rubric.get("versions") or []
    if not versions:
        return [f"{rubric['source']}: declares no `## Version history` table, so a change to "
                f"this card cannot be told from a typo in it"]
    seen = {v["version"]: v for v in versions}
    current = rubric.get("card_version")
    if current not in seen:
        bad.append(f"{rubric['source']}: is scorecard version {current} and its version "
                   f"history has no row for {current}")
        return bad
    if seen[current]["anchors_digest"] != rubric["anchors_digest"]:
        bad.append(f"{rubric['source']}: version {current} declares anchors digest "
                   f"{seen[current]['anchors_digest']} but the anchors in this file digest to "
                   f"{rubric['anchors_digest']}. Either the anchors moved without a version "
                   f"bump, or the table is stale -- and both are the card changing silently.")
    for earlier in range(1, current):
        if earlier not in seen:
            bad.append(f"{rubric['source']}: version history drops version {earlier}. The old "
                       f"rows are kept so a historical comparison is not a guess.")
    return bad


def rubric_leak_problems(rubric: dict) -> list[str]:
    """A judge must never be handed the finding they are the instrument for.

    Run over the SERVED text, at every version the rubric can be served at, so a
    result written into a dimension caveat or a scoring rule is caught wherever
    it would reach a judge. It reports; `serve` and `scaffold` refuse.
    """
    bad: list[str] = []
    seen: set[str] = set()
    for cv in SUPPORTED_VERSIONS:
        for leak in result_leaks(served_rubric(rubric, cv)):
            if leak in seen:
                continue
            seen.add(leak)
            bad.append(f"{rubric['source']}: the text served to a judge asserts how one of "
                       f"these five dimensions has scored or moved -- {leak}")
    return bad


def _under(path: pathlib.Path, root: pathlib.Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


# --------------------------------------------------------------------------
# check
# --------------------------------------------------------------------------

def check(card: dict, where: str, rubric: dict | None = None,
          require_filled: bool = False) -> tuple[list[str], list[str]]:
    """Return (problems, notes)."""
    bad: list[str] = []
    notes: list[str] = []

    def err(msg: str) -> None:
        bad.append(f"{where}: {msg}")

    version = card.get("scorecard_version")
    if version not in SUPPORTED_VERSIONS:
        err(f"scorecard_version must be one of {list(SUPPORTED_VERSIONS)}, got {version!r}")
        version = VERSION

    status = card.get("status", "filled")
    if status not in {"filled", "unfilled"}:
        err(f"status must be 'filled' or 'unfilled', got {status!r}")
        status = "filled"
    dims = card.get("dimensions") or {}
    scored = [d for d in DIMS
              if isinstance(dims.get(d), dict) and dims[d].get("score") is not None]

    # A skeleton cannot smuggle a score past the schema by staying 'unfilled'.
    if status == "unfilled" and scored:
        err(f"status is 'unfilled' but {', '.join(scored)} carry a score -- set status "
            f"to 'filled' so the card is checked as a measurement")
        status = "filled"

    if status == "unfilled":
        notes.append(f"UNFILLED {where}: skeleton, not yet judged")
        if require_filled:
            err("card is still an unfilled skeleton and --require-filled was given")

    for field in ("epic", "example", "run_id", "commit", "judge", "dimensions", "verdict"):
        if status == "unfilled" and field in ("commit", "verdict"):
            continue
        if not card.get(field):
            err(f"missing required field {field!r}")
    judge = card.get("judge") or {}
    for field in ("model", "pass"):
        if field not in judge:
            err(f"judge.{field} is required")
    # RD-01: judge tier. DERIVED where derivation is possible -- the tier is
    # already written in the model id every card must carry -- and validated
    # where it is declared. `opus` judged D3 2, 2 and `sonnet` 4, 3 on the same
    # artifact while D2 agreed across tiers, and nothing surfaced that.
    for msg in tier_problems(card, where):
        bad.append(msg)
    if judge_tier(judge) == TIER_UNKNOWN and status != "unfilled":
        notes.append(f"TIER-UNKNOWN {where}: judge.model {judge.get('model')!r} names no "
                     f"tier this knows and the card declares none. The tier is a field of "
                     f"the card from RD-01; an unrecognised model is recorded here rather "
                     f"than guessed.")

    # RD-05, attack A5: a scope declared before scoring, and refused if it moved.
    # A card MAY carry no subject -- every card sealed before RD-05 does not, and
    # R-H4 forbids adding one -- but a card that names a subject must name a
    # DECLARED one and must carry that subject's scope unchanged. A scope change
    # is not an architecture change and must never be read as one.
    subject = card.get("subject")
    if isinstance(subject, dict):
        name = subject.get("name")
        try:
            declared = arch().load_subjects()
        except Exception as exc:                     # pragma: no cover - unreadable file
            notes.append(f"SUBJECTS-UNREADABLE {where}: {exc}")
            declared = {}
        # RM-04. A BLINDED CARD NAMES NO SUBJECT AND CARRIES NO DECLARED VALUE.
        # `subject.name` is a real arm identity -- RM-03's re-score cards are
        # labelled `T` and say `arm_b` -- and `declared_effect_boundary` is the
        # value of the axis D3 is compared on, which is the answer to the
        # dimension being scored. Neither may reach a judge.
        #
        # A5's defence survives intact and is what makes the omission safe: the
        # scope must still match a scope DECLARED before scoring, resolved here
        # by the scope itself rather than by a name. What is lost is the ability
        # to name WHICH declared subject when two declare the same scope, and
        # that is reported rather than guessed.
        if subject.get("blinded") is True:
            if name is not None:
                err(f"subject.name {name!r} on a card whose subject is blinded. A "
                    f"blinded card carries the scope and nothing that identifies it.")
            if "declared_effect_boundary" in subject:
                err("subject.declared_effect_boundary is present on a blinded card. "
                    "That field is the value of the axis D3 is compared on.")
            got = list(subject.get("scope") or [])
            matches = sorted(n for n, s in (declared or {}).items()
                             if list(s["scope"]) == got)
            if declared and not matches:
                err(f"subject.scope {got} matches no scope declared in subjects.toml. "
                    f"A scope is declared before scoring; a card cannot invent one "
                    f"afterwards, blinded or not.")
            elif len(matches) > 1:
                notes.append(f"SUBJECT-AMBIGUOUS {where}: scope {got} is declared by "
                             f"{matches}; a blinded card resolves by scope, so which "
                             f"one it is cannot be read off the card.")
        elif declared and name not in declared:
            err(f"subject.name {name!r} is not declared in subjects.toml. A scope is "
                f"declared before scoring; a card cannot invent one afterwards.")
        elif declared:
            want = list(declared[name]["scope"])
            got = list(subject.get("scope") or [])
            if got != want:
                err(f"subject.scope {got} does not match the declared scope of "
                    f"{name!r} ({want}). THE SCOPE MOVED. Four judges scored three "
                    f"different subjects of one artifact once already, and D3 came "
                    f"out 2, 2, 3, 4.")
            if subject.get("declared_effect_boundary") != declared[name]["declared"]:
                err(f"subject.declared_effect_boundary "
                    f"{subject.get('declared_effect_boundary')!r} does not match "
                    f"subjects.toml ({declared[name]['declared']!r}). A declaration "
                    f"refuses nothing and it is still not editable per card.")
    elif subject is not None:
        err(f"subject must be an object or null, got {type(subject).__name__}")

    want_dims = scored_dims(version)
    missing = [d for d in want_dims if d not in dims]
    if missing:
        err(f"missing dimensions: {', '.join(missing)}")
    extra = [d for d in dims if d not in want_dims]
    if extra:
        if version >= RETIRED_AT and all(d in RETIRED_DIMS for d in extra):
            err(f"{', '.join(sorted(extra))} carry a score on a version {version} card. "
                f"They are recorded notes from version {RETIRED_AT} -- put the answer in "
                f"`notes.N-{sorted(extra)[0]}` and leave the number out. Restoring the "
                f"number here would restore the dimension without a version bump.")
        else:
            err(f"unknown dimensions: {', '.join(extra)}")

    # From version 4 the three retired questions are still asked and still
    # required. Dropping the question as well would be a different removal from
    # the one the version history declares.
    if version >= RETIRED_AT and status != "unfilled":
        card_notes = card.get("notes")
        if not isinstance(card_notes, dict):
            err(f"missing required field 'notes'. From scorecard_version {RETIRED_AT} a card "
                f"records {', '.join(NOTE_KEY[d] for d in RETIRED_DIMS)} as prose instead of "
                f"scoring them, and rule 10 says an empty note is not a legal card.")
            card_notes = {}
        for dim in note_dims(version):
            key = NOTE_KEY[dim]
            entry = card_notes.get(key)
            if not isinstance(entry, dict):
                err(f"notes.{key} is missing -- rule 10")
                continue
            if not str(entry.get("note") or "").strip():
                err(f"notes.{key} is empty. 'I could not tell, and here is what I looked at' "
                    f"is a legal note; silence is not -- rule 10")
            for c in entry.get("citations") or []:
                if not CITE.match(str(c)):
                    err(f"notes.{key} citation {c!r} is not file:line or file:line-line")
        stray = [k for k in card_notes if k not in {NOTE_KEY[d] for d in RETIRED_DIMS}]
        if stray:
            err(f"unknown notes: {', '.join(sorted(stray))}")
    elif version < RETIRED_AT and card.get("notes") is not None:
        err(f"`notes` is not a field of a version {version} card -- it arrives with "
            f"version {RETIRED_AT}, where three dimensions stopped being scored")

    # scorecard_version 2: what the judge DID is a field, not a private choice.
    executed = None
    if version >= 2 and status != "unfilled":
        practice = card.get("judging_practice")
        if not isinstance(practice, dict):
            err("missing required field 'judging_practice'. From scorecard_version 2 a card "
                "records WHETHER THE JUDGE EXECUTED ITS OWN FAULTS and WHAT IT RAN, because "
                "that is the variable that moved four dimension-points on byte-identical "
                "trees and nothing recorded it.")
        else:
            executed = practice.get("executed_own_faults")
            if not isinstance(executed, bool):
                err("judging_practice.executed_own_faults must be true or false, got "
                    f"{executed!r} -- 'did you run anything against this artifact' has an "
                    "answer either way, and the unflattering answer is the useful one")
                executed = None
            ran = practice.get("what_was_run")
            if not isinstance(ran, list) or any(not str(x).strip() for x in ran):
                err("judging_practice.what_was_run must be a list of non-empty strings")
            elif executed is True and not ran:
                err("judging_practice says the judge executed its own faults and lists "
                    "nothing in `what_was_run` -- name what was run, or say it executed "
                    "nothing")
            elif executed is False and ran:
                notes.append(f"PRACTICE {where}: executed_own_faults is false but "
                             f"`what_was_run` lists {len(ran)} item(s); read them as things "
                             f"run that were not fault seeding")
            if executed is False:
                notes.append(f"PACKET-ONLY {where}: this judge scored the evidence packet and "
                             f"seeded no fault of its own. That is a legal card and it is "
                             f"recorded, never corrected.")

    if rubric is not None and (card.get("rubric") or {}).get("digest"):
        got = card["rubric"]["digest"]
        if got != rubric["digest"]:
            msg = f"scaffolded against rubric digest {got}, current rubric is {rubric['digest']}"
            if status == "unfilled":
                err(msg + " -- re-scaffold before judging against a stale bar")
            else:
                notes.append(f"RUBRIC-DRIFT {where}: {msg}. A filled card is evidence and "
                             f"is not edited; see `history`/`audit` for how to read it.")

    # scorecard_version 3: the digest over the bytes this judge was SERVED.
    # `digest` covers the parsed anchors and rules and was identical --
    # sha256:e33638087c4191da -- across six commits and a 2x growth of the rubric
    # file, all of which the judges were told to read in full (FI-03-DF-02,
    # FI-06-DF-11(b)). This one moves whenever what reaches a judge moves.
    if rubric is not None and version >= 3:
        block = card.get("rubric") or {}
        got_served = block.get("served_digest")
        want_served = served_digest(rubric, version)
        if not got_served:
            err("rubric.served_digest is required from scorecard_version 3 -- a card "
                "that does not record the bytes its judge was served cannot say whether "
                "another card was served the same ones")
        elif got_served != want_served:
            msg = (f"served against rubric {got_served}, the current rubric serves "
                   f"{want_served}")
            if status == "unfilled":
                err(msg + " -- re-scaffold: what a judge would read has changed")
            else:
                notes.append(f"SERVED-DRIFT {where}: {msg}. The bar this judge read is "
                             f"not the bar in the tree; a filled card is evidence and is "
                             f"not edited.")
        elif block.get("file_sha256") and rubric.get("file_sha256") \
                and block["file_sha256"] != rubric["file_sha256"]:
            notes.append(f"PROSE-DRIFT {where}: the rubric file changed "
                         f"({block['file_sha256']} -> {rubric['file_sha256']}) in a part "
                         f"NO JUDGE IS SERVED -- the served digest is unchanged. This is a "
                         f"prompt to go and look, never a violation.")

    running = 0
    for dim in DIMS:
        entry = dims.get(dim)
        if not isinstance(entry, dict):
            continue
        if entry.get("name") and entry["name"] != NAMES[dim]:
            err(f"{dim} is named {entry['name']!r}; this card version knows it as {NAMES[dim]!r}")
        top = top_score(dim, version)
        if "anchors" in entry:
            keys = sorted(str(k) for k in (entry.get("anchors") or {}))
            if keys != [str(n) for n in range(top + 1)]:
                err(f"{dim} carries inline anchors but not all of 0-{top} (got {keys})")
        score = entry.get("score")
        if status == "unfilled":
            if score is not None:
                err(f"{dim} of an unfilled skeleton must have score null")
            continue
        if not isinstance(score, int) or isinstance(score, bool) or not 0 <= score <= top:
            err(f"{dim} score must be an int 0-{top} on a version {version} card, "
                f"got {score!r}")
            continue
        running += score
        cites = entry.get("citations") or []
        # Rule 2: every score >= 2 cites file:line, or is capped at 1.
        if score >= 2:
            if not cites:
                err(f"{dim} scored {score} with NO citation -- rule 2 caps it at 1")
            for c in cites:
                if not CITE.match(str(c)):
                    err(f"{dim} citation {c!r} is not file:line or file:line-line")
        # Rule 3: a score at the TOP OF ITS SCALE must name something the
        # artifact refuses to claim. The top is 4 everywhere until version 4
        # deletes D2's anchor 4, at which point D2's top is 3 and the rule
        # follows the anchor rather than the literal number it used to be.
        if score == top and not entry.get("refuses_to_claim"):
            err(f"{dim} scored {score}, the top of its scale on a version {version} card, "
                f"without refuses_to_claim -- rule 3")
        # Rule 8 (scorecard_version 2): the one top anchor whose own text asks
        # the judge to run something.
        if version >= 2 and score == 4 and dim in PRACTICE_GATED_DIMS and executed is False:
            err(f"{dim} scored 4 while judging_practice.executed_own_faults is false. That "
                f"anchor asks for a behavior-breaking change SHOWN TO BE CAUGHT -- a judge "
                f"who executes one can say so; a judge reading a table is repeating the "
                f"artifact's claim. Score 3 and say the packet asserts it, or run one.")
        # scorecard_version 3: the one anchor with two defensible readings says
        # WHICH ONE it was scored under. The bar is unchanged and neither reading
        # is corrected -- what changes is that two judges who split can be read.
        if version >= 3 and dim == ANCHOR_READING_DIM and score in ANCHOR_READING_SCORES:
            reading = entry.get("anchor_reading")
            if reading not in ANCHOR_READINGS:
                err(f"{dim} scored {score} with anchor_reading {reading!r}; it must be one "
                    f"of {list(ANCHOR_READINGS)}. Anchor 4 asks for 'a result unflattering "
                    f"to the thing being scored' and that phrase has two defensible "
                    f"readings -- a disclosure the artifact makes about itself, or a "
                    f"result the artifact MEASURED against itself. Both are legal and "
                    f"neither is corrected; say which you used.")
        if not str(entry.get("rationale") or "").strip():
            err(f"{dim} has no rationale")

    if status != "unfilled":
        # `total` is not a field of a version 3 card. Four of its five terms
        # cannot carry a delta -- D2 has taken one value on every card ever
        # written about `ab_quota_ledger`, and D1, D4 and D5 each take a
        # different value from a different judge on the same bytes -- so a sum
        # over them moves most where the card reads worst. Versions 1 and 2
        # carry one and their arithmetic is still checked, because a sealed card
        # is never edited and a check that stops looking at it is a check that
        # stopped working.
        total = card.get("total")
        if version >= 3:
            if total is not None:
                err(f"total {total!r} is set on a version {version} card. There is no "
                    f"total from version 3: read a dimension, not a headline.")
        elif total != running:
            err(f"total {total!r} does not equal the sum of dimensions ({running})")
    return bad, notes


def load(path: pathlib.Path) -> list[tuple[pathlib.Path, dict]]:
    if path.is_file():
        return [(path, json.loads(path.read_text()))]
    return [(p, json.loads(p.read_text())) for p in sorted(path.rglob("scorecard.json"))]


def cmd_check(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="score_tools.py check")
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--require-filled", action="store_true",
                    help="treat an unfilled skeleton as a problem (use at workflow close)")
    ap.add_argument("--rubric", default=str(DEFAULT_RUBRIC))
    args = ap.parse_args(argv)

    try:
        rubric = load_rubric(pathlib.Path(args.rubric))
    except RubricError as exc:
        print(f"WARNING rubric unreadable, digest checks skipped: {exc}", file=sys.stderr)
        rubric = None

    cards, problems, notes = [], [], []
    if rubric is not None:
        problems.extend(version_history_problems(rubric))
        problems.extend(rubric_leak_problems(rubric))
    for arg in args.paths:
        cards.extend(load(pathlib.Path(arg)))
    if not cards:
        print("no scorecard.json found", file=sys.stderr)
        return 2
    unfilled = 0
    for path, card in cards:
        bad, note = check(card, str(path), rubric, args.require_filled)
        problems.extend(bad)
        notes.extend(note)
        if card.get("status") == "unfilled":
            unfilled += 1
    for line in notes:
        print(line)
    for line in problems:
        print(f"INVALID {line}")
    print(f"{len(cards)} scorecard(s) checked, {len(cards) - unfilled} filled, "
          f"{unfilled} unfilled skeleton(s), {len(problems)} problem(s)")
    return 1 if problems else 0


# --------------------------------------------------------------------------
# judge tier, contested, and the tier split
# --------------------------------------------------------------------------
#
# RD-01. Scoring rule 5 has said since version 1 that "any dimension where they
# differ by more than 1 is recorded as `contested`". NOTHING HAS EVER COMPUTED
# IT. Every card ever written carries `contested = []`, including the four
# `toolchain_removal` cards whose D3 came out 2, 2, 3, 4 -- a spread of 2 --
# where `index` printed a dash on all four rows.
#
# The reason it was never filled in is structural rather than careless, and it
# decides the design here: `contested` is a property of a JUDGE GROUP and no
# single judge can see it. Rule 5 also says the judges are blind to each other,
# so a field asking one judge to record how far they are from another asks for
# something that judge is forbidden to know. So it is COMPUTED, from the cards,
# on every read -- never declared. A declaration cannot manufacture one and,
# more importantly, cannot erase one: `EVAL-SUPPRESS` is this repository's own
# demonstration that a declared `verified: true` will be used to erase a
# measured kill if the shape of the record allows it.
#
# The card's `contested` field is retained because a sealed card is never
# edited (R-H4) and 49 of them carry it. It is read as a DECLARATION and
# compared against the computation; where they differ, the computation wins and
# the difference is reported.

TIER_WORDS = ("opus", "sonnet", "haiku")
TIER_UNKNOWN = "unknown"


def derived_tier(model: str | None) -> str | None:
    """The tier a model id names, or None when nothing in it names one.

    Derivation rather than declaration is deliberate: a field a judge fills in
    by hand is a field that can be filled in wrong, and the tier is already
    written in the model id every card is required to carry.
    """
    low = str(model or "").lower()
    hits = [t for t in TIER_WORDS if t in low]
    return hits[0] if len(hits) == 1 else None


def judge_tier(judge: dict | None) -> str:
    """The recorded tier if the card carries one, else the derived one."""
    judge = judge or {}
    declared = judge.get("tier")
    if isinstance(declared, str) and declared.strip():
        return declared.strip()
    return derived_tier(judge.get("model")) or TIER_UNKNOWN


def tier_problems(card: dict, where: str) -> list[str]:
    """A declared tier that contradicts the model id is a violation, not a note."""
    judge = card.get("judge") or {}
    declared = judge.get("tier")
    if not isinstance(declared, str) or not declared.strip():
        return []
    got = derived_tier(judge.get("model"))
    if got is not None and got != declared.strip():
        return [f"{where}: judge.tier is {declared!r} but judge.model "
                f"{judge.get('model')!r} names tier {got!r}. The tier is derived where "
                f"derivation is possible; a declaration that contradicts the model id is "
                f"the tag being used to say something the record does not."]
    return []


def group_key(root: pathlib.Path, path: pathlib.Path, card: dict) -> tuple[str, str, str]:
    """The unit rule 5 is about: the judges of ONE artifact, in ONE round.

    Not the epic FIELD -- `hexagonal-prompting-rerun`'s cards carry
    `epic = "hexagonal-prompting"`, so grouping by that field would put two
    different rounds' judges into one group and invent a spread. The round
    directory is what separates them on disk and it is what separates them here.
    """
    return (_round_of(root, path), str(card.get("example")), str(card.get("arm")))


def judge_groups(root: pathlib.Path, example: str | None = None) -> list[dict]:
    groups: dict[tuple[str, str, str], dict] = {}
    for path, card in load(root):
        if card.get("status") == "unfilled":
            continue
        if example and card.get("example") != example:
            continue
        key = group_key(root, path, card)
        g = groups.setdefault(key, {"key": key, "round": key[0], "example": key[1],
                                    "arm": key[2], "cards": [], "paths": []})
        g["cards"].append(card)
        g["paths"].append(path)
    return [groups[k] for k in sorted(groups)]


def _scores(group: dict, dim: str) -> list[tuple[dict, int]]:
    out = []
    for card in group["cards"]:
        entry = (card.get("dimensions") or {}).get(dim) or {}
        score = entry.get("score")
        if isinstance(score, int) and not isinstance(score, bool):
            out.append((card, score))
    return out


def contested_of(group: dict) -> dict[str, dict]:
    """Rule 5, computed: a spread greater than 1 across the judges of one artifact."""
    out: dict[str, dict] = {}
    for dim in DIMS:
        pairs = _scores(group, dim)
        if len(pairs) < 2:
            continue
        vals = [s for _, s in pairs]
        spread = max(vals) - min(vals)
        if spread > 1:
            out[dim] = {
                "spread": spread,
                "scores": vals,
                "by_judge": [(f"{(c.get('judge') or {}).get('model')}"
                              f"/pass {(c.get('judge') or {}).get('pass')}", s)
                             for c, s in pairs],
            }
    return out


def tier_split_of(group: dict) -> dict[str, dict]:
    """Dimensions where two judge tiers do not overlap at all on one artifact.

    Reported only when the tiers' score ranges are DISJOINT. An overlap is two
    tiers that agree as far as this can tell, and calling that a split would let
    the tag say something the numbers do not -- which is the suppression-key
    failure one level down.
    """
    out: dict[str, dict] = {}
    for dim in DIMS:
        pairs = _scores(group, dim)
        by_tier: dict[str, list[int]] = {}
        for card, score in pairs:
            by_tier.setdefault(judge_tier(card.get("judge")), []).append(score)
        by_tier.pop(TIER_UNKNOWN, None)
        if len(by_tier) < 2:
            continue
        ordered = sorted(by_tier.items(), key=lambda kv: (min(kv[1]), max(kv[1])))
        disjoint = all(max(ordered[i][1]) < min(ordered[i + 1][1])
                       for i in range(len(ordered) - 1))
        if not disjoint:
            continue
        means = {t: sum(v) / len(v) for t, v in by_tier.items()}
        lo, hi = ordered[0], ordered[-1]
        out[dim] = {
            "by_tier": {t: sorted(v) for t, v in by_tier.items()},
            "means": means,
            "points": round(means[hi[0]] - means[lo[0]], 2),
            "gap": min(hi[1]) - max(lo[1]),
            "lower": lo[0],
            "higher": hi[0],
        }
    return out


def cmd_contested(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="score_tools.py contested")
    ap.add_argument("--root", default=str(DEFAULT_SCORECARD_ROOT))
    ap.add_argument("--example")
    ap.add_argument("--format", choices=("text", "json"), default="text")
    ap.add_argument("--require-recorded", action="store_true",
                    help="exit 1 when a contested dimension has no `[[contested]]` entry "
                         "in INSTRUMENT-LOG.toml saying what was done about it")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root)
    groups = judge_groups(root, args.example)
    recorded = {(str(e.get("round")), str(e.get("example")), str(e.get("arm")),
                 str(e.get("dimension"))) for e in load_log(root)["contested"]}

    unrecorded = []
    report = []
    for g in groups:
        c, t = contested_of(g), tier_split_of(g)
        if not c and not t:
            continue
        report.append({"round": g["round"], "example": g["example"], "arm": g["arm"],
                       "judges": len(g["cards"]), "contested": c, "tier_split": t})
        unrecorded += [(g["round"], g["example"], g["arm"], dim) for dim in c
                       if (g["round"], g["example"], g["arm"], dim) not in recorded]
    if args.format == "json":
        print(json.dumps({"groups": len(groups), "reported": report,
                          "unrecorded": unrecorded}, indent=2, default=str))
        return 1 if (args.require_recorded and unrecorded) else 0

    print(f"# contested and tier splits over {root}")
    print(f"# {len(groups)} judge group(s); a group is one artifact judged in one round.")
    print("# `contested` is COMPUTED from the cards on every run -- rule 5, spread > 1.")
    print("# A tier split is reported only where the tiers' ranges are DISJOINT.")
    ncon = 0
    for r in report:
        print(f"\n## {r['round']} / {r['example']} / arm {r['arm']} "
              f"({r['judges']} judge(s))")
        for dim, info in r["contested"].items():
            ncon += 1
            print(f"  CONTESTED  {dim} spread {info['spread']} -- "
                  + ", ".join(f"{m} = {s}" for m, s in info["by_judge"]))
            print(f"             rule 5: adjudicate with a third pass that cites NEW "
                  f"evidence, never a re-read.")
            if (r["round"], r["example"], r["arm"], dim) not in recorded:
                print(f"             UNRECORDED: no `[[contested]]` entry in "
                      f"{LOG_NAME} says what was done about it.")
        for dim, info in r["tier_split"].items():
            by = "; ".join(f"{t} {v}" for t, v in sorted(info["by_tier"].items()))
            print(f"  TIER-SPLIT {dim} {by} -- disjoint, {info['higher']} higher by "
                  f"{info['points']} point(s)")
    if not report:
        print("\n  nothing contested and no tier split.")
    print(f"\n{ncon} contested dimension(s) over {len(groups)} judge group(s), "
          f"{len(unrecorded)} unrecorded")
    return 1 if (args.require_recorded and unrecorded) else 0


# --------------------------------------------------------------------------
# serve: what a judge is given, and the refusal that keeps a result out of it
# --------------------------------------------------------------------------

def cmd_serve(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="score_tools.py serve")
    ap.add_argument("--rubric", default=str(DEFAULT_RUBRIC))
    ap.add_argument("--card-version", type=int, default=VERSION, choices=SUPPORTED_VERSIONS)
    ap.add_argument("--out", default=None, help="write the served rubric here as well")
    ap.add_argument("--digest-only", action="store_true")
    args = ap.parse_args(argv)

    try:
        rubric = load_rubric(pathlib.Path(args.rubric))
    except RubricError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2

    served = served_rubric(rubric, args.card_version)
    leaks = result_leaks(served)
    if leaks:
        print("REFUSED: this rubric would hand a judge a result about the very "
              "dimensions they are scoring. Nothing was written.", file=sys.stderr)
        for leak in leaks:
            print(f"  {leak}", file=sys.stderr)
        print("A judge must never be handed the finding they are the instrument for. "
              "Move the statement out of the dimension blocks and the scoring rules; "
              "nothing else in the rubric file is served.", file=sys.stderr)
        return 3

    if args.digest_only:
        print(served_digest(rubric, args.card_version))
        return 0
    print(served)
    if args.out:
        p = pathlib.Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(served)
        print(f"wrote {p}", file=sys.stderr)
    print(f"served digest {served_digest(rubric, args.card_version)} "
          f"(card version {args.card_version}, rubric file "
          f"{rubric.get('file_sha256')})", file=sys.stderr)
    return 0


# --------------------------------------------------------------------------
# index
# --------------------------------------------------------------------------

def cmd_index(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="score_tools.py index")
    ap.add_argument("epic_dir")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.epic_dir)
    cards = [(p, c) for p, c in load(root) if c.get("status") != "unfilled"]
    by_example: dict[str, list[dict]] = {}
    for _, card in cards:
        by_example.setdefault(card["example"], []).append(card)

    # RD-01: `contested` is COMPUTED here, from the group of judges who scored
    # one artifact, and not read out of the card. Read out of the card it was
    # `[]` on every row this file has ever printed -- including the four rows of
    # a round where D3 came out 2, 2, 3, 4.
    grouped: dict[tuple[str, str, str], dict] = {}
    for path, card in cards:
        key = group_key(root, path, card)
        g = grouped.setdefault(key, {"key": key, "round": key[0], "example": key[1],
                                     "arm": key[2], "cards": [], "paths": []})
        g["cards"].append(card)
        g["paths"].append(path)
    groups = [grouped[k] for k in sorted(grouped)]
    computed: dict[int, dict[str, dict]] = {}
    for g in groups:
        con = contested_of(g)
        for card in g["cards"]:
            computed[id(card)] = con

    versions = sorted({c.get("scorecard_version") for _, c in cards
                       if c.get("scorecard_version")})
    out = [f"# Scorecards — {root.name}", ""]
    out.append("scorecard_version "
               + (", ".join(str(v) for v in versions) if versions else str(VERSION))
               + ". See `references/eval_scorecard.md`.")
    out.append("")
    out.append("**Never average across examples.** `ex6_jenga` is a deliberately")
    out.append("incoherent fixture and is supposed to score low on D3; averaging it")
    out.append("with `ex4` produces a number about nothing. Nothing in this file is")
    out.append("computed across two examples.")
    out.append("")
    out.append("**No total, from scorecard_version 3.** Four of its five terms cannot")
    out.append("carry a delta, so a sum over them moves most where the card reads")
    out.append("worst. Read a dimension.")
    out.append("")
    out.append("**`contested` is computed, never declared.** Scoring rule 5 — a spread")
    out.append("greater than 1 across the judges of one artifact — is re-derived from the")
    out.append("cards on every run. A card's own `contested` field is a declaration and")
    out.append("cannot manufacture one or erase one; where the two differ, the difference")
    out.append("is printed below the table.")
    out.append("")
    header = ("| example | arm | judge | tier | "
              + " | ".join(f"D{i+1} {NAMES['D' + str(i + 1)]}" for i in range(5))
              + " | contested |")
    out.append(header)
    out.append("|" + "---|" * 10)
    disagree: list[str] = []
    for example in sorted(by_example):
        for card in sorted(by_example[example], key=lambda c: (str(c.get("arm")), c["run_id"])):
            d = card["dimensions"]
            judge = card.get("judge") or {}
            con = computed.get(id(card), {})
            row = [example, str(card.get("arm") or "—"),
                   f"pass {judge.get('pass')}", judge_tier(judge)]
            # A version 4 card carries no D1, D4 or D5. `—` is the honest cell:
            # the question was asked and answered in `notes`, and there is no
            # number to put here. It is NOT a missing measurement.
            row += [str(d[k]["score"]) if isinstance(d.get(k), dict) else "—" for k in DIMS]
            row.append(", ".join(sorted(con)) or "—")
            out.append("| " + " | ".join(row) + " |")
            declared = sorted(card.get("contested") or [])
            if declared != sorted(con):
                disagree.append(
                    f"- `{example}` / {card['run_id']}: the card declares "
                    f"`contested = {declared}`; the cards compute "
                    f"`{sorted(con)}`. **The computation is the answer.** A sealed card is "
                    f"never edited (R-H4), so the declaration stays where it is and this "
                    f"line is the correction beside it.")
    out.append("")
    if disagree:
        out.append("### Declared `contested` against computed")
        out.append("")
        out.extend(disagree)
        out.append("")
    contested_rows = [(g, contested_of(g)) for g in groups]
    contested_rows = [(g, c) for g, c in contested_rows if c]
    out.append("### Contested — rule 5, computed")
    out.append("")
    if not contested_rows:
        out.append("None. No dimension has a spread greater than 1 in any judge group here.")
    for g, con in contested_rows:
        for dim, info in con.items():
            out.append(f"- **{g['example']} / arm {g['arm']}, {dim}** — spread "
                       f"{info['spread']}: "
                       + ", ".join(f"{m} = {s}" for m, s in info["by_judge"])
                       + ". Rule 5 asks for a third pass citing NEW evidence.")
    out.append("")
    split_rows = [(g, tier_split_of(g)) for g in groups]
    split_rows = [(g, s) for g, s in split_rows if s]
    out.append("### Tier splits")
    out.append("")
    out.append("A dimension where two judge tiers do not overlap at all on the same")
    out.append("artifact. Reported only where the ranges are DISJOINT — an overlap is two")
    out.append("tiers agreeing as far as this can tell.")
    out.append("")
    if not split_rows:
        out.append("None.")
    for g, spl in split_rows:
        for dim, info in spl.items():
            by = "; ".join(f"`{t}` {v}" for t, v in sorted(info["by_tier"].items()))
            out.append(f"- **{g['example']} / arm {g['arm']}, {dim}** — {by}; "
                       f"`{info['higher']}` higher by {info['points']} point(s).")
    out.append("")
    for example in sorted(by_example):
        for card in sorted(by_example[example], key=lambda c: c["run_id"]):
            out.append(f"- **{example}** ({card['run_id']}): {card['verdict']}")
    text = "\n".join(out) + "\n"
    (root / "INDEX.md").write_text(text)
    print(text)
    return 0


# --------------------------------------------------------------------------
# scaffold
# --------------------------------------------------------------------------

def used_labels(scorecard_root: pathlib.Path) -> set[str]:
    """Every arm label any round has already published, so none is reused.

    HP-06 used X/Y and published its key; EVAL-RERUN deliberately chose P/Q so a
    judge who stumbled into the sealed run could not read the arms off it. That
    was discipline. This makes it a mechanism.

    RM-04: labels are STRINGS, not characters, so both readers below match a run
    of upper-case letters rather than exactly one. A width-1 record still reads
    as width 1, so nothing about the sealed rounds changes -- the sealed record
    still yields the 13 published single characters it always did.
    """
    used: set[str] = set()
    if not scorecard_root.exists():
        return used
    for p in scorecard_root.rglob("scorecard.json"):
        try:
            arm = json.loads(p.read_text()).get("arm")
        except Exception:
            continue
        if isinstance(arm, str) and arm.strip():
            used.add(arm.strip().upper())
    for p in scorecard_root.rglob("UNBLINDING*.md"):
        for m in re.finditer(r"^\|\s*`?([A-Z]+)`?\s*\|", p.read_text(), re.M):
            used.add(m.group(1))
    return used


def _slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", text).strip("-")


def cmd_scaffold(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="score_tools.py scaffold")
    ap.add_argument("epic_dir")
    ap.add_argument("--example", required=True)
    ap.add_argument("--arms", required=True, help="comma-separated REAL arm names, e.g. A,B,C")
    ap.add_argument("--judges", type=int, default=2)
    ap.add_argument("--rubric", default=str(DEFAULT_RUBRIC))
    ap.add_argument("--run-date", default=None, help="YYYYMMDD; defaults to today")
    ap.add_argument("--run-tag", default=None, help="short tag inside the run id")
    ap.add_argument("--labels", default=None,
                    help="explicit opaque labels, comma-separated (testing / re-scaffold)")
    ap.add_argument("--seed", type=int, default=None, help="seed the label shuffle")
    ap.add_argument("--subject", default=None,
                    help="a subject declared in examples/validation/scorecards/"
                         "subjects.toml. Writes its SCOPE into the unfilled skeleton, "
                         "before any judge is dispatched; `check` then refuses a card "
                         "whose scope moved. A program that is one thing wrapping "
                         "another declares SEVERAL scoped subjects and scaffolds one "
                         "card per subject.")
    ap.add_argument("--unblinded", action="store_true",
                    help="DELIBERATELY skip blinding: emit real arm names as labels")
    ap.add_argument("--reason", default=None, help="required with --unblinded")
    ap.add_argument("--card-version", type=int, default=VERSION, choices=SUPPORTED_VERSIONS,
                    help="emit a card of this scorecard_version. The old version exists so "
                         "the discontinuity a version bump creates can be MEASURED by "
                         "re-scoring under both, which is the card's own change rule.")
    args = ap.parse_args(argv)

    try:
        rubric = load_rubric(pathlib.Path(args.rubric))
    except RubricError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2

    # A round may not begin by handing its judges the answer. Checked BEFORE any
    # path is planned, so nothing is written -- the same discipline as the
    # collision refusal below.
    leaks = result_leaks(served_rubric(rubric, args.card_version))
    if leaks:
        print("REFUSED: the rubric this would serve asserts how one of the five "
              "dimensions has scored or moved. Nothing was written.", file=sys.stderr)
        for leak in leaks:
            print(f"  {leak}", file=sys.stderr)
        print("A judge must never be handed the finding they are the instrument for. "
              "FI-03 dispatched four judges with the whole rubric file and both v1 "
              "judges cited a results paragraph back as their reason for scoring D4 the "
              "way they did.", file=sys.stderr)
        return 3

    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    if not arms:
        print("REFUSED: --arms names no arm", file=sys.stderr)
        return 2
    if args.judges < 1:
        print("REFUSED: --judges must be at least 1", file=sys.stderr)
        return 2

    epic_dir = pathlib.Path(args.epic_dir)
    scorecard_root = epic_dir.parent

    published = used_labels(scorecard_root)
    args._published = published
    reused: list[str] = []

    if args.unblinded:
        if not args.reason:
            print("REFUSED: --unblinded requires --reason. Blinding is the default and "
                  "undoing it is a deliberate, recorded act.", file=sys.stderr)
            return 2
        labels = list(arms)
    elif args.labels:
        labels = [x.strip().upper() for x in args.labels.split(",") if x.strip()]
        if len(labels) != len(arms):
            print(f"REFUSED: {len(labels)} labels for {len(arms)} arms", file=sys.stderr)
            return 2
        # RM-04. THE EXPLICIT PATH USED TO BYPASS THE EXCLUSION ENTIRELY. The
        # pool path has excluded every published label since HP-06; `--labels`
        # wrote whatever it was given, so the one route an operator reaches for
        # when the pool refuses was the one route with no check on it.
        #
        # IT IS A REASON, NOT A BAN, and the reason is what the record needed.
        # Reusing a label is sometimes correct and this project does it on
        # purpose: FI-03, SM-04 and RM-03 each re-scored ONE arm under two card
        # versions and kept its label, because two versions of the same arm
        # have to be readable as the same arm. What was wrong was that it cost
        # nothing and was recorded nowhere. So it now costs `--reason`, exactly
        # as undoing blinding does, and the reason is written into the key file.
        #
        # Deferred to after the collision check below, because re-scaffolding
        # over an existing path is a collision and that message is the more
        # useful one -- and a batch refused for a collision has, by definition,
        # published those labels itself.
        reused = sorted(x for x in labels if x in published or x in RESERVED_LABELS)
        args._reused = reused
    else:
        taken = published | RESERVED_LABELS | {a.upper() for a in arms}
        pool, width = available_labels(taken, len(arms))
        if not pool:
            print(f"REFUSED: no label width up to {MAX_LABEL_WIDTH} can supply "
                  f"{len(arms)} unpublished label(s) over the alphabet "
                  f"{label_alphabet(taken)!r}", file=sys.stderr)
            return 2
        rng = random.Random(args.seed) if args.seed is not None else random.SystemRandom()
        labels = rng.sample(pool, len(arms))

    run_date = args.run_date or _date.today().strftime("%Y%m%d")
    tag = _slug(args.run_tag) if args.run_tag else None

    def run_id(label: str, judge: int) -> str:
        return "-".join([run_date] + ([tag] if tag else []) + [label, f"p{judge}"])

    example_dir = epic_dir / _slug(args.example)
    planned: list[tuple[pathlib.Path, str]] = []
    try:
        for label in labels:
            for judge in range(1, args.judges + 1):
                rid = run_id(label, judge)
                d = example_dir / rid
                planned.append((d / "scorecard.json",
                                _skeleton_json(args, rubric, label, judge, rid)))
                planned.append((d / "scorecard.md",
                                _skeleton_md(args, rubric, label, judge, rid)))
                planned.append((d / "mechanical.json", _mechanical_json(args, label, rid)))
    except BlindingError as exc:
        print(f"REFUSED: {exc}\nNothing was written.", file=sys.stderr)
        return 3
    key_path = epic_dir / "UNBLINDING.md"
    planned.append((key_path, _unblinding_md(args, arms, labels, run_date, tag)))

    # Refuse to overwrite. A scaffold that clobbers a measurement is worse than
    # no scaffold. Check EVERY path before writing ANY of them.
    existing = [p for p, _ in planned if p.exists()]
    if existing:
        print("REFUSED: scaffolding here would overwrite an existing card.", file=sys.stderr)
        for p in existing:
            print(f"  exists: {p}", file=sys.stderr)
        print("Nothing was written -- not one file, not the ones that would not have "
              "collided. A scorecard is a measurement; move or rename the existing run, "
              "or scaffold under a different --run-tag.", file=sys.stderr)
        if key_path in existing:
            print(f"Note that {key_path.name} alone is enough to refuse the whole batch, "
                  "and that is deliberate: fresh random labels would otherwise write new "
                  "card directories beside a measurement and silently orphan its key.",
                  file=sys.stderr)
        return 3

    if reused and not args.reason:
        print(f"REFUSED: {reused} would reuse a label a prior round published (or a "
              f"reserved arm name). A judge who has seen that round can connect this "
              f"card to it, which is the whole of what blinding buys.\n"
              f"If the reuse is deliberate -- re-scoring one arm under two card "
              f"versions is the case this project actually has -- pass --reason and "
              f"it is written into UNBLINDING.md. Otherwise drop --labels and let "
              f"the pool draw. Nothing was written.", file=sys.stderr)
        return 2

    for p, text in planned:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    print(f"scaffolded {len(arms)} arm(s) x {args.judges} judge(s) = "
          f"{len(arms) * args.judges} card(s) for example {args.example!r}")
    for p, _ in planned:
        if p.name == "scorecard.json":
            print(f"  {p}")
    if args.unblinded:
        print(f"\n!! NOT BLINDED. Reason recorded in {key_path}: {args.reason}")
    else:
        print(f"\nBLINDED BY DEFAULT. Arms emitted as {', '.join(labels)}.")
        print(f"!! DO NOT GIVE THIS FILE TO ANY JUDGE: {key_path}")
    return 0


def _rubric_block(rubric: dict, card_version: int = VERSION) -> dict:
    """What the card records about the rubric it was scored against.

    Three digests, three questions, and only the middle one is about the bar a
    judge actually read:

    * `digest` -- the parsed anchors and scoring rules. `check` refuses a
      SKELETON scaffolded against a stale one, and notes drift on a filled card.
    * `served_digest` -- the EXACT bytes `served_rubric` emitted for this card.
      This is the one that answers "did the rubric change in any way that could
      reach this judge". It was added at SM-04 because `digest` was identical --
      `sha256:e33638087c4191da` -- across six commits and a 2x growth of the
      rubric file, every one of which the judges were told to read in full.
    * `file_sha256` -- the whole rubric file, served and unserved alike. Two
      cards whose served digests agree and whose file digests differ are
      `PROSE-DRIFT`: a prompt to go and look, never a violation.
    """
    block = {"source": rubric["source"], "digest": rubric["digest"],
             "scoring_rules": rubric["scoring_rules"]}
    if card_version >= 3:
        block["served_digest"] = served_digest(rubric, card_version)
        block["file_sha256"] = rubric.get("file_sha256")
    return block


#: A path segment that is a blind-round artifact directory, or that is itself
#: nothing but an upper-case label. `artifact_T` is the shape every blind round
#: in this repository has used.
_LABEL_IN_PATH = re.compile(r"(?:^|[_-])([A-Z]{1,3})$")


def scope_leaks_a_label(scope: list[str], published: set[str]) -> list[str]:
    """Which published arm labels does this declared scope spell out?

    RM-04. `subject.scope` is written into the card because a judge has to know
    what to read. Where the scope is a prior round's blind directory the PATH
    carries that round's label -- `.../blind/artifact_T` -- so a card labelled
    with anything at all still tells a judge which arm it is looking at as soon
    as they have seen the round that published `T`.
    """
    hits = []
    for path in scope:
        for segment in re.split(r"[/\\]", path):
            m = _LABEL_IN_PATH.search(segment)
            if m and m.group(1) in published:
                hits.append(f"{path!r} names the published label {m.group(1)!r}")
    return hits


def _subject_block(name: str | None, blinded: bool = False,
                   published: set[str] | None = None) -> dict | None:
    """The declared scope, copied out of `subjects.toml` into the skeleton.

    RM-04. **A BLINDED CARD CARRIES THE SCOPE AND NOTHING THAT IDENTIFIES IT.**
    Verified on the record: RM-03's re-score cards are labelled `T` while
    `subject.name` reads `arm_b` and `subject.declared_effect_boundary` reads
    `ports-and-adapters` -- the arm and the answer to the dimension, both in the
    file the judge is handed. A judge read it and disclosed it.

    So under blinding `name` and `declared_effect_boundary` are withheld and the
    real name goes to `UNBLINDING.md`, which judges are not given. The scope
    stays, because the judge has to be told what to read, and `check` resolves
    it BY SCOPE against `subjects.toml` -- attack A5's defence is that the scope
    was declared before scoring, and that is unchanged.

    Where the scope path itself spells a published label, nothing here can hide
    it and the scaffold REFUSES instead.
    """
    if not name:
        return None
    subjects = arch().load_subjects()
    if name not in subjects:
        raise RubricError(f"--subject {name!r} is not declared in "
                          f"{arch().DEFAULT_SUBJECTS}. A scope is DECLARED, never "
                          f"invented at scaffold time.")
    s = subjects[name]
    if not blinded:
        return {"name": name, "scope": list(s["scope"]),
                "declared_effect_boundary": s["declared"],
                "axis": arch().AXIS}
    leaks = scope_leaks_a_label(list(s["scope"]), published or set())
    if leaks:
        raise BlindingError(
            "a blinded card would carry an identifying subject. --subject "
            f"{name!r} declares a scope that spells a label a prior round "
            "published:\n  " + "\n  ".join(leaks) + "\n"
            "Withholding `subject.name` cannot hide it, because the path is what "
            "the judge is told to read. Scaffold this subject with `--unblinded "
            "--reason ...`, or copy the tree to a directory that names no "
            "published label. RM-03's round shipped this leak: cards labelled `T` "
            "carrying `arm_b` and `.../blind/artifact_T`, and a judge disclosed it.")
    return {"name": None, "blinded": True, "scope": list(s["scope"]),
            "axis": arch().AXIS}


def _skeleton_json(args, rubric: dict, label: str, judge: int, rid: str) -> str:
    # `--card-version N` alone reproduces the old SCHEMA against the NEW bar --
    # `FI-06-DF-11(c)`, open through three version bumps because it was operator
    # sequencing and nothing refused. From version 4 it cannot be missed by
    # accident on the dimensions: a rubric that no longer carries a dimension
    # cannot scaffold a version that scores it, and the error says which frozen
    # file to point at. It still refuses NOTHING about any artifact.
    absent = [k for k in scored_dims(args.card_version) if k not in rubric["dimensions"]]
    if absent:
        raise RubricError(
            f"cannot scaffold a version {args.card_version} card from "
            f"{rubric['source']}, which is scorecard version {rubric['card_version']} "
            f"and carries no anchors for {', '.join(absent)}. Reproducing an older card "
            f"means pointing at the older bar: pass "
            f"`--rubric examples/validation/scorecards/rubric_v3_frozen.md`.")
    dims = {}
    for key in scored_dims(args.card_version):
        d = rubric["dimensions"][key]
        entry = {
            "name": d["name"],
            "question": d["question"],
            "anchors": d["anchors"],
            "score": None,
            "citations": [],
            "rationale": "",
            "refuses_to_claim": None,
        }
        if d.get("preamble"):
            entry["read_first"] = d["preamble"]
        if d["caveat"]:
            entry["caveat"] = d["caveat"]
        if 3 <= args.card_version < RETIRED_AT and key == ANCHOR_READING_DIM:
            entry["anchor_reading"] = None
        dims[key] = entry
    card = {
        "scorecard_version": args.card_version,
        "status": "unfilled",
        "epic": pathlib.Path(args.epic_dir).name,
        "example": args.example,
        "run_id": rid,
        "arm": label,
        "commit": "",
        # `tier` is left empty on purpose. It is DERIVED from `model` wherever a
        # model id names one, so a judge who fills in `model` has filled in the
        # tier; the field exists so a model id that names no tier can be said
        # rather than guessed at. A declared tier that contradicts the model id
        # is a `check` failure -- the tag records what the record says, never
        # what someone would prefer it said.
        "judge": {"model": "", "tier": "", "pass": judge,
                  "blind_to_arm": not args.unblinded},
        # RD-05, attack A5. THE SCOPE IS WRITTEN BEFORE ANY JUDGE IS DISPATCHED
        # and it is copied from `subjects.toml`, so what the card is about is
        # fixed before the numbers exist. `check` refuses a card whose
        # `subject.scope` no longer matches the declared one. Choosing the scope
        # that carries the flattering tag is not hypothetical: it is what
        # produced `toolchain_removal` D3 = 4 on a card whose every citation is
        # to a fixture.
        #
        # It is `null` where the round declared no subject, which is every card
        # sealed before RD-05 and any round that declines to declare one. A card
        # with no subject is attributed through `subjects.toml`'s `labels` or
        # not at all, and an unattributed card enters no comparison.
        "subject": _subject_block(getattr(args, "subject", None),
                                  blinded=not args.unblinded,
                                  published=getattr(args, "_published", None)),
        "rubric": _rubric_block(rubric, args.card_version),
        "how_to_fill": [
            "Score the LOWEST anchor the artifact fully satisfies. Torn between two: "
            "take the lower and say why.",
            "Set `status` to \"filled\", `commit` to the sha the artifacts were scored "
            "at, and name your model in `judge.model`.",
            "Leave `anchors` as scaffolded. They are read from the rubric so the bar "
            "and the score live in one file; editing them here forks the rubric "
            "silently, which is the drift this scaffold exists to remove.",
        ],
        "dimensions": dims,
        "contested": [],
        "verdict": "",
    }
    if args.card_version < 3:
        card["total"] = None
        card["how_to_fill"].insert(
            2, "`total` is the sum of the five scores; the schema check recomputes it.")
    if args.card_version >= 2:
        card["judging_practice"] = {
            "executed_own_faults": None,
            "what_was_run": [],
            "note": ("REQUIRED from scorecard_version 2. Did you seed a fault of your own "
                     "and run it against this artifact, or did you score the evidence "
                     "packet? Both are legal and neither is the right answer; what is not "
                     "legal is leaving it unsaid. Say which, and list what you ran."
                     + (" D4's anchor 4 is only awardable when this says true, because "
                        "that anchor asks for a behavior-breaking change SHOWN TO BE "
                        "CAUGHT." if args.card_version < RETIRED_AT else
                        f" From version {RETIRED_AT} no anchor is gated on it; it is "
                        f"recorded because it is the variable that moves scores.")),
        }
        card["how_to_fill"].insert(2, (
            "Fill `judging_practice`: `executed_own_faults` true or false, and "
            "`what_was_run` listing what you ran. FALSE IS A LEGAL AND USEFUL ANSWER -- "
            "it is recorded, never corrected. Delete the `note` key once you have."))
    if 3 <= args.card_version < RETIRED_AT:
        card["how_to_fill"].append(
            f"If you score {ANCHOR_READING_DIM} at "
            f"{' or '.join(str(s) for s in ANCHOR_READING_SCORES)}, set "
            f"`dimensions.{ANCHOR_READING_DIM}.anchor_reading` to "
            f"{' or '.join(repr(r) for r in ANCHOR_READINGS)} -- which of the anchor's "
            f"two defensible readings you scored under. Both are legal and neither is "
            f"corrected; recording it is what lets a reader tell a disagreement about "
            f"the artifact from a disagreement about the anchor.")
    if args.card_version >= RETIRED_AT:
        card["notes"] = {
            NOTE_KEY[dim]: {
                "name": (rubric.get("notes") or {}).get(NOTE_KEY[dim], {}).get("name", ""),
                "question": (rubric.get("notes") or {}).get(NOTE_KEY[dim], {}).get("prompt", ""),
                "note": "",
                "citations": [],
            }
            for dim in note_dims(args.card_version)
        }
        card["how_to_fill"].append(
            "Answer every entry in `notes`. They take NO score -- these three questions "
            "were scored for three versions and the numbers were measured not to mean the "
            "same thing twice, so what is asked for is prose and citations. 'I could not "
            "tell, and here is what I looked at' is a legal note; an empty one is not.")
    return json.dumps(card, indent=2) + "\n"


def _skeleton_md(args, rubric: dict, label: str, judge: int, rid: str) -> str:
    """The file the judge reads and fills.

    Its rubric half is `served_rubric` verbatim -- the SAME bytes `serve` emits
    and the same bytes `rubric.served_digest` is taken over. One served surface,
    so a judge cannot be reading one rubric while the card records another.
    """
    out = [f"# Scorecard — {args.example}, artifact `{label}`, judge pass {judge}", ""]
    line = (f"`run_id`: `{rid}` · scorecard_version {args.card_version} · rubric "
            f"`{rubric['source']}` digest `{rubric['digest']}`")
    if args.card_version >= 3:
        line += f" · served `{served_digest(rubric, args.card_version)}`"
    out.append(line)
    out.append("")
    if args.unblinded:
        out.append(f"**NOT BLINDED.** This card was scaffolded with `--unblinded`: "
                   f"`{label}` is the real arm name. Reason on record: {args.reason}")
    else:
        out.append(f"**You are scoring artifact `{label}`.** That label is opaque on "
                   "purpose: it is not the arm name, and the mapping is not in this "
                   "directory. Do not go looking for it. If you learn which arm you "
                   "hold, say so in the verdict — a disclosed leak is recorded, never "
                   "grounds to discard a card.")
    out.append("")
    out.append("Fill in the score, the `file:line` citations and the rationale for each "
               "dimension below, and mirror them into `scorecard.json` beside this "
               "file. **The anchors are reproduced here so the bar for a score sits in "
               "the same file as the score.**")
    out.append("")
    # SM-06: this heading and paragraph used to restate the card's rule about the
    # mechanical block, in prose written HERE rather than parsed out of the
    # rubric -- so it sat outside `served_digest` and nothing compared it to the
    # card. Inverted as gap mutant M3 it moved no verdict anywhere in this
    # repository. The rule is served below with every other numbered rule,
    # straight out of the card; what stays here is the pointer to the FILE, which
    # the card does not carry.
    out.append("## The mechanical block")
    out.append("")
    out.append("`mechanical.json` beside this file holds kill counts, complexity "
               "figures, case counts, determinism and runtime. How to read it "
               "against your judgement is one of the numbered scoring rules below.")
    out.append("")
    out.append(served_rubric(rubric, args.card_version))
    if args.card_version >= 2:
        out.append("### Judging practice — your answer")
        out.append("")
        out.append("**Executed own faults:** _(true / false)_")
        out.append("")
        out.append("**What was run:**")
        out.append("")
        out.append("-")
        out.append("")
    out.append("## Your scores")
    out.append("")
    for key in scored_dims(args.card_version):
        top = top_score(key, args.card_version)
        out.append(f"### {key} — {NAMES[key]}")
        out.append("")
        out.append(f"**Score:** _(0–{top})_")
        out.append("")
        # SM-06: the citation bar is served above, parsed out of the card. This
        # label names the FORMAT and points at the rule; it does not restate it.
        out.append("**Citations** (`file:line` — the bar is in the scoring rules above):")
        out.append("")
        out.append("-")
        out.append("")
        out.append(f"**Refuses to claim** (required and non-null for a score of {top}):")
        out.append("")
        if 3 <= args.card_version < RETIRED_AT and key == ANCHOR_READING_DIM:
            out.append(f"**Anchor reading** (required at "
                       f"{' or '.join(str(s) for s in ANCHOR_READING_SCORES)}; "
                       f"{' or '.join('`%s`' % r for r in ANCHOR_READINGS)}):")
            out.append("")
        out.append("**Rationale:**")
        out.append("")
    if note_dims(args.card_version):
        out.append("## Your recorded notes — no score")
        out.append("")
        for dim in note_dims(args.card_version):
            key = NOTE_KEY[dim]
            out.append(f"### {key} — {NAMES[dim]}")
            out.append("")
            out.append("**Citations** (`file:line`):")
            out.append("")
            out.append("-")
            out.append("")
            out.append("**Note:**")
            out.append("")
    out.append("## Verdict")
    out.append("")
    out.append("_One sentence a reader can act on._")
    out.append("")
    out.append("## Disclosures")
    out.append("")
    out.append("_Anything you saw that you were not meant to see, anything you ran that "
               "changed the tree, and anything you REJECTED. For three rounds running "
               "the best finding in this project came from the last one, and zero came "
               "from re-running the suite._")
    out.append("")
    return "\n".join(out)


def _mechanical_json(args, label: str, rid: str) -> str:
    block = {
        "note": ("Measured figures. NEVER SCORED. Recorded beside the judgement so a "
                 "reader can see when measurement and judgement disagree -- and a "
                 "disagreement is a finding, not a rounding error."),
        "example": args.example,
        "arm": label,
        "run_id": rid,
        "commit": "",
        "figures": {
            "kills": {},
            "complexity_of_produced_code": {},
            "case_counts": {},
            "determinism": {},
            "runtime_seconds": None,
        },
        "reach": {"note": "Print reach beside every kill: executed of emitted, per "
                          "instrument, per action, with the skip rule named."},
    }
    return json.dumps(block, indent=2) + "\n"


def _unblinding_md(args, arms: list[str], labels: list[str], run_date: str, tag) -> str:
    out = ["# UNBLINDING KEY — DO NOT GIVE THIS FILE TO A JUDGE", ""]
    if args.unblinded:
        out.append("**THIS ROUND WAS SCAFFOLDED UNBLINDED, DELIBERATELY.**")
        out.append("")
        out.append(f"Reason on record: {args.reason}")
        out.append("")
        out.append("The labels below are the real arm names. Every number produced under "
                   "them is a non-blind judgement and must be labelled as such wherever "
                   "it is quoted.")
    if getattr(args, "_reused", None):
        out.append("")
        out.append(f"**LABELS REUSED ON PURPOSE: {', '.join(args._reused)}.** A prior "
                   f"round published {'them' if len(args._reused) > 1 else 'it'}, so a "
                   f"judge who has seen that round can connect these cards to it. "
                   f"Reason on record: {args.reason}")
    if not args.unblinded:
        out.append("Generated by `score_tools.py scaffold`. **Blinding is the default "
                   "here and is a mechanism, not discipline:** the cards were emitted "
                   "under opaque labels and this mapping was written to a file the "
                   "judges are not given.")
    out.append("")
    out.append(f"Example: `{args.example}` · scaffolded {run_date}"
               + (f" · tag `{tag}`" if tag else ""))
    out.append("")
    out.append("| scorecard `arm` | is | note |")
    out.append("|---|---|---|")
    for label, arm in zip(labels, arms):
        out.append(f"| `{label}` | **{arm}** | |")
    out.append("")
    if not args.unblinded:
        out.append("The labels are drawn from a pool that excludes every label any prior "
                   "round published, so a judge who stumbles into a sealed run cannot "
                   "read this round's arms off it.")
        out.append("")
    out.append("## What each judge could and could not see")
    out.append("")
    out.append("_Fill this in before the round closes: what was supplied, what was "
               "forbidden, and every disclosure a judge volunteered. A leak that is "
               "disclosed is recorded, never used as grounds to discard a card — "
               "discarding a card after seeing its score is the one move a round may "
               "not make._")
    out.append("")
    return "\n".join(out)


# --------------------------------------------------------------------------
# the instrument log, history and audit
# --------------------------------------------------------------------------

def _git(*argv: str) -> tuple[int, str]:
    try:
        p = subprocess.run(["git", "-C", str(REPO_ROOT), *argv],
                           capture_output=True, text=True)
        return p.returncode, p.stdout.strip()
    except Exception:
        return 127, ""


def _resolves(commit: str) -> bool:
    return bool(commit) and _git("rev-parse", "--verify", "--quiet", f"{commit}^{{commit}}")[0] == 0


def _commit_date(commit: str) -> str | None:
    rc, out = _git("show", "-s", "--format=%cI", commit)
    return out[:10] if rc == 0 and out else None


def _is_ancestor(older: str, newer: str) -> bool | None:
    """True/False, or None when ancestry cannot be decided in this tree."""
    if not (_resolves(older) and _resolves(newer)):
        return None
    return _git("merge-base", "--is-ancestor", older, newer)[0] == 0


def _touched(commit: str, paths: list[str]) -> list[str]:
    rc, out = _git("show", "--pretty=format:", "--name-only", commit)
    if rc != 0:
        return []
    changed = [line for line in out.splitlines() if line.strip()]
    hits = []
    for declared in paths:
        for f in changed:
            if f == declared or f.startswith(declared.rstrip("/") + "/"):
                hits.append(declared)
                break
    return hits


def load_log(root: pathlib.Path) -> dict:
    path = root / LOG_NAME
    if not path.exists():
        return {"path": path, "changes": [], "notes": [], "claims": [], "sealed": [],
                "movements": [], "contested": [], "demonstrations": []}
    data = tomllib.loads(path.read_text())
    return {"path": path, "changes": data.get("change", []), "notes": data.get("note", []),
            "claims": data.get("claim", []), "sealed": data.get("sealed", []),
            "movements": data.get("movement", []),
            "contested": data.get("contested", []),
            "demonstrations": data.get("demonstration", [])}


def card_date(card: dict) -> str | None:
    m = re.match(r"^(\d{4})(\d{2})(\d{2})", str(card.get("run_id") or ""))
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return _commit_date(str(card.get("commit") or "")) if card.get("commit") else None


def _after(change: dict, card_commit: str, cdate: str | None) -> tuple[bool, str]:
    """Was the card measured AFTER this instrument change? (answer, basis)"""
    anc = _is_ancestor(str(change["commit"]), card_commit) if card_commit else None
    if anc is not None:
        return anc, "ancestry"
    if cdate and change.get("date"):
        return (cdate > str(change["date"])), "date"
    return False, "UNVERIFIABLE"


def _round_of(root: pathlib.Path, path: pathlib.Path) -> str:
    try:
        return path.relative_to(root).parts[0]
    except ValueError:
        return path.parent.name


def collect_cards(root: pathlib.Path, example: str | None) -> list[dict]:
    rows = []
    for path, card in load(root):
        if example and card.get("example") != example:
            continue
        rows.append({"path": path, "card": card, "date": card_date(card),
                     "round": _round_of(root, path),
                     "key": f"{_round_of(root, path)}/{card.get('example')}/{card.get('run_id')}"})
    return rows


def _era_index(changes: list[dict], card_commit: str, cdate: str | None) -> int:
    return sum(1 for ch in changes if _after(ch, card_commit, cdate)[0])


def _commit_ts(commit: str) -> str:
    rc, out = _git("show", "-s", "--format=%cI", commit)
    return out if rc == 0 and out else ""


def _order_changes(changes: list[dict]) -> list[dict]:
    """Chronological. Committer timestamp first -- two changes can share a date
    and the order between them is exactly what an era boundary is about."""
    return sorted(changes, key=lambda ch: (_commit_ts(str(ch.get("commit"))) or
                                           str(ch.get("date") or ""),
                                           str(ch.get("date") or ""),
                                           str(ch.get("id"))))


def cmd_history(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="score_tools.py history")
    ap.add_argument("--example", required=True,
                    help="REQUIRED. History is per example; a number over more than one "
                         "example is a number about nothing.")
    ap.add_argument("--root", default=str(DEFAULT_SCORECARD_ROOT))
    ap.add_argument("--write", default=None, help="also write the rendering to this path")
    args = ap.parse_args(argv)

    root = pathlib.Path(args.root)
    log = load_log(root)
    changes = [c for c in _order_changes(log["changes"])
               if not c.get("affects") or args.example in c.get("affects", [])]
    rows = collect_cards(root, args.example)
    # An unfilled skeleton has no measurement, so it belongs to no era. It is
    # listed at the end rather than placed by the date it was scaffolded.
    pending = [r for r in rows if r["card"].get("status") == "unfilled"]
    rows = [r for r in rows if r["card"].get("status") != "unfilled"]
    if not rows and not changes:
        print(f"no rows and no instrument changes for example {args.example!r}", file=sys.stderr)
        return 2

    notes_by_card: dict[str, list[dict]] = {}
    for n in log["notes"]:
        about = str(n.get("about", ""))
        if about.startswith("card:"):
            notes_by_card.setdefault(about[5:], []).append(n)

    for r in rows:
        r["era"] = _era_index(changes, str(r["card"].get("commit") or ""), r["date"])
    rows.sort(key=lambda r: (r["era"], r["date"] or "", str(r["card"].get("arm")),
                             r["card"]["run_id"]))

    out: list[str] = [f"# Scorecard history — `{args.example}`", ""]
    out.append("Generated by `score_tools.py history --example "
               f"{args.example}`. Reading rules: `references/eval_scorecard.md`, "
               "**Reading history** (R-H1..R-H4), every one of which is executed by "
               "`score_tools.py audit`.")
    out.append("")
    out.append("**One example only.** Never average across examples: a deliberately "
               "incoherent fixture is *supposed* to score low on D3, and a mean over it "
               "is a number about nothing.")
    out.append("")
    out.append("**There is no total column, from scorecard_version 3.** Four of its five "
               "terms cannot carry a delta, and a sum over them moves most where the card "
               "reads worst. The `ver` column is the card version: rows on opposite sides "
               "of a version boundary are not comparable without saying so.")
    out.append("")
    out.append("**A row is comparable to another only on the same example AND across an "
               "unchanged instrument.** The bars below are instrument changes. Rows on "
               "opposite sides of one are not comparable until the change is named — and "
               "**a number that moved because the instrument was repaired is not "
               "improvement.**")
    out.append("")

    def render_rows(era_rows: list[dict]) -> None:
        if not era_rows:
            out.append("_(no rows measured in this era)_")
            out.append("")
            return
        out.append("| run | round | arm | pass | ver | D1 | D2 | D3 | D4 | D5 | commit | note |")
        out.append("|" + "---|" * 12)
        for r in era_rows:
            c = r["card"]
            d = c.get("dimensions") or {}
            if c.get("status") == "unfilled":
                scores = ["—"] * 5
            else:
                scores = [str(d.get(k, {}).get("score", "?")) for k in DIMS]
            marks = notes_by_card.get(r["key"], [])
            out.append("| " + " | ".join([
                f"`{c['run_id']}`", r["round"], str(c.get("arm") or "—"),
                str((c.get("judge") or {}).get("pass", "—")),
                str(c.get("scorecard_version") or "?"), *scores,
                f"`{str(c.get('commit') or '')[:7]}`",
                " ".join(f"**[{n['id']}]**" for n in marks) or "—"]) + " |")
        out.append("")
        seen: dict[str, dict] = {}
        for r in era_rows:
            for n in notes_by_card.get(r["key"], []):
                seen[n["id"]] = n
        for nid, n in seen.items():
            out.append(f"> **[{nid}] {str(n.get('kind', 'note')).upper()}"
                       + (f" — {n['field']}" if n.get("field") else "") + ".** "
                       + " ".join(str(n.get("why", "")).split()))
            out.append(">")
            out.append(f"> _recorded {n.get('recorded_at', '?')} by {n.get('by', '?')}. "
                       f"The sealed card is NOT edited; this note sits beside it._")
            out.append("")

    for era in range(len(changes) + 1):
        if era == 0:
            out.append("## Era 0 — before any recorded instrument change")
        else:
            ch = changes[era - 1]
            out.append(f"### ⟥ INSTRUMENT CHANGE — `{ch['id']}` ({ch.get('kind', 'change')}) "
                       f"@ `{str(ch['commit'])[:7]}` {ch.get('date', '')}")
            out.append("")
            out.append(" ".join(str(ch.get("summary", "")).split()))
            out.append("")
            if "verdicts_moved" in ch:
                scope = f" over {ch['verdicts_scope']}" if ch.get("verdicts_scope") else ""
                if ch["verdicts_moved"] == 0:
                    out.append(f"**Verdicts moved: ZERO**{scope}. The instrument changed and "
                               "no number did — read what the numbers MEAN across this bar, "
                               "not whether they moved.")
                else:
                    out.append(f"**Verdicts moved: {ch['verdicts_moved']}**{scope}. A number "
                               "that moved because the instrument was repaired is not "
                               "improvement.")
                out.append("")
            if ch.get("invalidates"):
                out.append("**Numbers this change is recorded as invalidating:** "
                           + "; ".join(ch["invalidates"]))
                out.append("")
            out.append("**ROWS ABOVE ARE NOT COMPARABLE TO ROWS BELOW.** Name this change "
                       "or do not compare.")
            out.append("")
            out.append(f"## Era {era} — after `{ch['id']}`")
        out.append("")
        render_rows([r for r in rows if r["era"] == era])

    if pending:
        out.append("## Scaffolded, not yet measured")
        out.append("")
        out.append("These carry no measurement, so they belong to no era and are not "
                   "placed above. They will land in the era current when their `commit` "
                   "is filled in.")
        out.append("")
        out.append("| run | round | arm | pass |")
        out.append("|" + "---|" * 4)
        for r in sorted(pending, key=lambda r: r["card"]["run_id"]):
            c = r["card"]
            out.append(f"| `{c['run_id']}` | {r['round']} | {c.get('arm') or '—'} | "
                       f"{(c.get('judge') or {}).get('pass', '—')} |")
        out.append("")

    by_key = {r["key"]: r["card"] for r in rows + pending}
    movements = [m for m in log["movements"]
                 if str(m.get("from_card")) in by_key or str(m.get("to_card")) in by_key]
    if movements:
        out.append("## The same artifact, scored twice — declared movements")
        out.append("")
        out.append("R-H5. Each row names two cards and is **re-derived from them on every "
                   "`audit`**, so it cannot go stale the way a sentence can. `readable` is "
                   "false whenever either end does not record what its judge DID — because "
                   "four dimension-points once moved on byte-identical trees and the "
                   "mechanism was the judging practice, not the artifact.")
        out.append("")
        out.append("| movement | dim | from | to | points | readable |")
        out.append("|" + "---|" * 6)
        def _score_of(key: str, dim: str):
            card = by_key.get(key) or {}
            return (card.get("dimensions") or {}).get(dim, {}).get("score")

        for m in movements:
            fk, tk = str(m.get("from_card")), str(m.get("to_card"))
            fs = _score_of(fk, str(m.get("dimension")))
            ts = _score_of(tk, str(m.get("dimension")))
            out.append("| " + " | ".join([
                f"`{m.get('id')}`", str(m.get("dimension")),
                f"`{fk.split('/')[-1]}` ({fs})", f"`{tk.split('/')[-1]}` ({ts})",
                f"**{int(m.get('points', 0)):+d}**",
                "yes" if m.get("readable") else "**no**"]) + " |")
        out.append("")
        for m in movements:
            if m.get("why"):
                out.append(f"> **`{m.get('id')}`.** " + " ".join(str(m["why"]).split()))
                out.append("")

    claims = [c for c in log["claims"] if c.get("example") in (args.example, "n/a")]
    if claims:
        out.append("## Claims about this example that are not scorecard rows")
        out.append("")
        out.append("A ledger sentence is a measurement too and goes stale the same way. "
                   "Status is `current` (asserted now, and policed), `sealed` (true of "
                   "its era, not read forward), `superseded` (names its successor), "
                   "`known_wrong` (a measurement that stopped being true, and names why), "
                   "`refuted` (an assertion someone made in review that was falsified "
                   "from data, and names who) or `under_review` (only legal with a filed "
                   "finding id). No status can park a number quietly.")
        out.append("")
        out.append("| claim | status | measured at | delta basis | says |")
        out.append("|" + "---|" * 5)
        for c in claims:
            status = str(c.get("status", "?"))
            extra = ""
            if status == "superseded" and c.get("superseded_by"):
                extra = f" → `{c['superseded_by']}`"
            if status == "under_review" and c.get("filed_as"):
                extra = f" ({c['filed_as']})"
            if status == "refuted":
                extra = f" by {c.get('refuted_by', '?')}"
                if c.get("filed_as"):
                    extra += f", filed as {c['filed_as']}"
            if status == "current" and c.get("reaffirmed_at"):
                extra = f", re-affirmed at `{str(c['reaffirmed_at'])[:7]}`"
            out.append("| " + " | ".join([
                f"`{c.get('id')}`", f"**{status}**{extra}",
                f"`{str(c.get('measured_at', ''))[:7]}` {c.get('date', '')}",
                str(c.get("delta_basis", "—")),
                " ".join(str(c.get("statement", "")).split())]) + " |")
        out.append("")
        notes_by_claim: dict[str, list[dict]] = {}
        for n in log["notes"]:
            about = str(n.get("about", ""))
            if about.startswith("claim:"):
                notes_by_claim.setdefault(about[6:], []).append(n)
        for c in claims:
            if c.get("why"):
                out.append(f"> **`{c['id']}`.** " + " ".join(str(c["why"]).split()))
                out.append("")
            for n in notes_by_claim.get(str(c.get("id")), []):
                out.append(f"> **[{n['id']}] {str(n.get('kind', 'note')).upper()}"
                           + (f" — {n['field']}" if n.get("field") else "")
                           + f", beside `{c['id']}`.** "
                           + " ".join(str(n.get("why", "")).split()))
                out.append("")

    text = "\n".join(out).rstrip() + "\n"
    print(text)
    if args.write:
        p = pathlib.Path(args.write)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        print(f"wrote {p}", file=sys.stderr)
    return 0


# --------------------------------------------------------------------------
# audit: the reading rules, executed
# --------------------------------------------------------------------------

VIOLATION = "VIOLATION"
OPEN = "OPEN"
UNVERIFIED = "UNVERIFIED"
OK = "OK"


def _finding_ids() -> set[str]:
    path = REPO_ROOT / "specs/desired_program_model/deferred_findings.yaml"
    if not path.exists():
        return set()
    return set(re.findall(r"^\s*-\s+id:\s*\"?([A-Za-z0-9_.-]+)\"?", path.read_text(), re.M))


def audit_rh1(ctx: dict) -> list[tuple[str, str]]:
    """R-H1 comparability: era boundaries must be real, and rows across one annotated."""
    out = []
    for ch in ctx["changes"]:
        cid, commit = ch.get("id"), str(ch.get("commit", ""))
        if not _resolves(commit):
            out.append((UNVERIFIED, f"change `{cid}`: commit {commit} does not resolve in "
                                    f"this tree; the era boundary is unverified"))
            continue
        paths = ch.get("paths") or []
        if not paths:
            out.append((VIOLATION, f"change `{cid}`: declares no instrument `paths`, so "
                                   f"nothing can check that it changed the instrument"))
            continue
        hits = _touched(commit, paths)
        if not hits:
            out.append((VIOLATION, f"change `{cid}`: commit {commit[:7]} touches NONE of its "
                                   f"declared instrument paths {paths} -- either the commit "
                                   f"or the paths are wrong"))
        else:
            out.append((OK, f"change `{cid}` @ {commit[:7]} touches {', '.join(hits)}"))
    noted = {str(n.get("about", ""))[5:] for n in ctx["notes"]
             if str(n.get("about", "")).startswith("card:")}
    for r in ctx["rows"]:
        c = r["card"]
        rel = [ch for ch in ctx["changes"]
               if not ch.get("affects") or c.get("example") in ch.get("affects", [])]
        later = []
        for ch in rel:
            after, basis = _after(ch, str(c.get("commit") or ""), r["date"])
            if basis == "UNVERIFIABLE":
                out.append((UNVERIFIED, f"card `{r['key']}`: cannot be placed relative to "
                                        f"`{ch['id']}` by ancestry or by date"))
            elif not after:
                later.append(str(ch["id"]))
        if later and r["key"] not in noted and c.get("status") != "unfilled":
            out.append((OPEN, f"card `{r['key']}`: measured before {', '.join(later)} and "
                              f"carries no note. It is not comparable to anything measured "
                              f"after; record WHICH number and WHY beside it."))
    out.extend(audit_rh1_architecture(ctx))
    return out


def audit_rh1_architecture(ctx: dict) -> list[tuple[str, str]]:
    """R-H1's THIRD CLAUSE (RD-05): the demonstration table, re-derived.

    R-H1 grew a third comparability axis rather than gaining an `R-H7`,
    deliberately: R-H5's own history is that an unnumbered rule with no check
    was added at close and `audit` rejected it within the minute, so a new
    `R-H` id is a promise to ship a check and folding into R-H1 inherits one
    that already runs.

    What is checked: every `[[demonstration]]` in the ledger is RE-DERIVED FROM
    THE CARDS, exactly as R-H5 re-derives `points` and R-H6 re-derives
    `contested`. An entry the cards no longer support is a VIOLATION, not a
    rounding error -- and a separation the cards DO support with no entry
    beside it is `OPEN`, because an undeclared authority is one nobody agreed
    to.
    """
    out: list[tuple[str, str]] = []
    declared = ctx.get("demonstrations") or []
    module = arch()
    subjects = module.load_subjects()
    derived = module.derive_subjects(subjects, REPO_ROOT)
    unmeasurable = [n for n, d in derived.items()
                    if d["derived"].endswith("unmeasurable")]
    if unmeasurable:
        out.append((UNVERIFIED, f"the {module.AXIS} axis could not be derived for "
                                f"{sorted(unmeasurable)} in this tree -- their declared "
                                f"scope is absent, so nothing about them is checked here"))
    rows = module.card_rows(ctx["root"])
    entries = {e["id"]: e for e in module.demonstration_table(rows, derived, subjects)}
    if len(unmeasurable) == len(derived):
        out.append((UNVERIFIED, "no declared scope resolves in this tree; the demonstration "
                                "table is not re-derivable here and nothing below is checked"))
        return out
    for entry in declared:
        eid = str(entry.get("id"))
        got = entries.get(eid)
        if got is None:
            out.append((VIOLATION,
                        f"`[[demonstration]]` `{eid}`: names no cell the cards produce. "
                        f"A stale authority row is worse than none, because a comparison "
                        f"gets refused on evidence nobody can find."))
            continue
        for field in ("separates", "dimension", "example"):
            if field in entry and entry[field] != got[field]:
                out.append((VIOLATION,
                            f"`[[demonstration]]` `{eid}`: declares {field} = "
                            f"{entry[field]!r}; the cards give {got[field]!r}."))
                break
        else:
            if entry.get("ranges") and {k: list(v) for k, v in entry["ranges"].items()} \
                    != got["ranges"]:
                out.append((VIOLATION,
                            f"`[[demonstration]]` `{eid}`: declares ranges "
                            f"{entry['ranges']}; the cards give {got['ranges']}."))
                continue
            if entry.get("tiers_measured") is not None \
                    and list(entry["tiers_measured"]) != got["tiers_measured"]:
                out.append((VIOLATION,
                            f"`[[demonstration]]` `{eid}`: declares tiers_measured "
                            f"{list(entry['tiers_measured'])}; the cards give "
                            f"{got['tiers_measured']}. A separation present in one tier "
                            f"and absent in the other is a fact about the tier."))
                continue
            verdict = "SEPARATES" if got["separates"] else "does not separate"
            null = " NULL-ENTAILED" if got["null_entailed"] else ""
            out.append((OK, f"`[[demonstration]]` `{eid}`: {got['dimension']} "
                            f"{'/'.join(got['values'])} {verdict} re-derived "
                            f"{got['ranges']}, population took "
                            f"{got['population_values']}{null}, tiers "
                            f"{got['tiers_measured']}"))
    undeclared = [e for e in entries.values()
                  if e["separates"] and e["id"] not in {str(d.get("id")) for d in declared}]
    for e in undeclared:
        out.append((OPEN, f"the cards support a separation on {e['dimension']} between "
                          f"{'/'.join(e['values'])} ({e['ranges']}) and no "
                          f"`[[demonstration]]` records it. Until one does the pair refuses "
                          f"nothing -- an authority nobody declared is not an authority."))
    for card in module.scope_drift(rows, subjects):
        out.append((OPEN, f"SCOPE-DRIFT card `{card['card']}`: attributed to subject "
                          f"`{card['declared_subject']}`, its own {card['dimension']} "
                          f"citations name `{card['cited_subject']}` "
                          f"{card['citation_counts']}. A scope change is not an "
                          f"architecture change and must never be read as one."))
    return out


def audit_rh2(ctx: dict) -> list[tuple[str, str]]:
    """R-H2 scope: nothing is asserted across more than one example."""
    out = []
    known = {r["card"].get("example") for r in ctx["all_rows"]}
    for c in ctx["claims"]:
        ex = c.get("example")
        if isinstance(ex, list):
            out.append((VIOLATION, f"claim `{c.get('id')}`: names {len(ex)} examples {ex}. "
                                   f"A number over more than one example is a number about "
                                   f"nothing."))
            continue
        if ex not in known and ex != "n/a":
            out.append((UNVERIFIED, f"claim `{c.get('id')}`: example {ex!r} has no scorecard "
                                    f"row in this tree"))
        else:
            out.append((OK, f"claim `{c.get('id')}` is scoped to one example ({ex})"))
    claim_ids = {c.get("id") for c in ctx["claims"]}
    for n in ctx["notes"]:
        about = str(n.get("about", ""))
        if about.startswith("card:") and about[5:] not in ctx["keys"]:
            out.append((VIOLATION, f"note `{n.get('id')}`: is about `{about[5:]}`, which is "
                                   f"not a card in this tree"))
        elif about.startswith("claim:") and about[6:] not in claim_ids:
            out.append((VIOLATION, f"note `{n.get('id')}`: is about claim `{about[6:]}`, "
                                   f"which is not declared"))
    return out


def audit_rh3(ctx: dict) -> list[tuple[str, str]]:
    """R-H3 repair vs improvement: what a change moved, and what stays `current` across it."""
    out = []
    filed = _finding_ids()
    # A repair declares how many verdicts it moved, so "nothing moved" is a
    # MEASURED statement rather than an absence. Zero is a real and important
    # answer: an instrument can get more honest without a single number
    # changing, and the rule "a number that moved because the instrument was
    # repaired is not improvement" has a converse the record has to be able to
    # say out loud.
    for ch in ctx["changes"]:
        if ch.get("kind") != "repair":
            continue
        cid = ch.get("id")
        scope = f" over {ch['verdicts_scope']}" if ch.get("verdicts_scope") else ""
        if "verdicts_moved" not in ch:
            why = str(ch.get("verdicts_unmeasurable") or "").strip()
            if why:
                out.append((OK, f"change `{cid}`: no verdict diff exists, and says why -- "
                                f"{why}"))
            else:
                out.append((OPEN, f"change `{cid}`: a repair declaring neither "
                                  f"`verdicts_moved` nor `verdicts_unmeasurable`. Whether "
                                  f"numbers moved is the first thing a reader of an era "
                                  f"boundary needs; 'nothing moved' has to be measured, and "
                                  f"'cannot be measured' has to be argued."))
        elif ch["verdicts_moved"] == 0:
            out.append((OK, f"change `{cid}`: repaired and moved ZERO verdicts{scope}. The "
                            f"instrument changed and no number did -- so read what the "
                            f"numbers MEAN, not whether they moved."))
        else:
            out.append((OK, f"change `{cid}`: moved {ch['verdicts_moved']} verdict(s){scope}. "
                            f"A number that moved because the instrument was repaired is not "
                            f"improvement."))
    for c in ctx["claims"]:
        cid, status = c.get("id"), c.get("status")
        if status not in CLAIM_STATUSES:
            out.append((VIOLATION, f"claim `{cid}`: status {status!r} is not one of "
                                   f"{sorted(CLAIM_STATUSES)}"))
        if status == "sealed":
            out.append((OK, f"claim `{cid}`: sealed -- true of its era, not read forward"))
        if status == "known_wrong" and not str(c.get("why", "")).strip():
            out.append((VIOLATION, f"claim `{cid}`: known_wrong with no `why`. Recording "
                                   f"WHICH number is half of it; WHY is the other half."))
        if status == "refuted":
            missing = [f for f in ("refuted_by", "why") if not str(c.get(f, "")).strip()]
            if missing:
                out.append((VIOLATION, f"claim `{cid}`: refuted with no "
                                       f"{' and no '.join('`%s`' % m for m in missing)}. "
                                       f"An assertion that was falsified stays on the "
                                       f"record WITH who falsified it and on what -- "
                                       f"deleting it would hide the review, not the error."))
            else:
                out.append((OK, f"claim `{cid}`: refuted by {c['refuted_by']}, kept on the "
                                f"record"))
        # `filed_as` is checked on EVERY status, not only under_review: a refuted
        # or discharged finding must stay reachable from the ledger.
        if c.get("filed_as") and c["filed_as"] not in filed:
            out.append((VIOLATION, f"claim `{cid}`: `filed_as = {c['filed_as']}` is not an "
                                   f"id in deferred_findings.yaml"))
        if status == "superseded" and not c.get("superseded_by"):
            out.append((VIOLATION, f"claim `{cid}`: status superseded with no "
                                   f"`superseded_by` -- superseded BY WHAT?"))
        if status == "under_review":
            if not c.get("filed_as"):
                out.append((VIOLATION, f"claim `{cid}`: `under_review` with no `filed_as`. "
                                       f"That status is only legal with a filed finding; "
                                       f"otherwise it parks a number quietly."))
            elif c["filed_as"] in filed:
                out.append((OK, f"claim `{cid}` is under review and filed as {c['filed_as']}"))
        if status != "current":
            continue
        if c.get("delta_basis") == "within_run":
            out.append((OK, f"claim `{cid}`: a within-run comparison (two instruments in one "
                            f"run), so no era boundary applies"))
            continue
        measured = str(c.get("measured_at", ""))
        rel = [ch for ch in ctx["changes"]
               if not ch.get("affects") or c.get("example") in ch.get("affects", [])]
        straddled = []
        for ch in rel:
            anc = _is_ancestor(str(ch["commit"]), measured)
            if anc is None:
                if c.get("date") and ch.get("date"):
                    anc = str(c["date"]) > str(ch["date"])
                else:
                    out.append((UNVERIFIED, f"claim `{cid}`: cannot be placed relative to "
                                            f"`{ch['id']}`"))
                    continue
            if not anc:
                reaff = str(c.get("reaffirmed_at", ""))
                if not (reaff and _is_ancestor(str(ch["commit"]), reaff)):
                    straddled.append(str(ch["id"]))
        if straddled:
            out.append((VIOLATION,
                        f"claim `{cid}`: SUPERSEDED-UNMARKED. Still `current`, measured at "
                        f"{measured[:7]}, but the instrument changed at "
                        f"{', '.join(straddled)} afterwards and nothing re-affirmed it. "
                        f"Re-affirm it, mark it superseded, or move it to `under_review` "
                        f"with a filed finding."))
        else:
            out.append((OK, f"claim `{cid}` is current and no unreaffirmed instrument change "
                            f"post-dates it"))
    return out


def audit_rh4(ctx: dict) -> list[tuple[str, str]]:
    """R-H4 seals: a sealed card is never edited."""
    out = []
    if not ctx["sealed"]:
        out.append((OPEN, "no sealed digests recorded; run `score_tools.py seal` so an edit "
                          "to a sealed card can be detected at all"))
    for s in ctx["sealed"]:
        p = REPO_ROOT / s["path"]
        if not p.exists():
            out.append((VIOLATION, f"sealed `{s['path']}` no longer exists"))
            continue
        got = "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()[:16]
        if got != s.get("sha256"):
            out.append((VIOLATION, f"sealed `{s['path']}` HAS BEEN EDITED "
                                   f"({s.get('sha256')} -> {got}). A sealed card is never "
                                   f"edited; record the correction beside it."))
        else:
            out.append((OK, f"sealed `{s['path']}` unchanged"))
    return out


def audit_rh5(ctx: dict) -> list[tuple[str, str]]:
    """R-H5 movement: a movement is a measurement only if the judging practice is recorded."""
    out = []
    by_key = {r["key"]: r["card"] for r in ctx["all_rows"]}
    if not ctx["movements"]:
        out.append((OPEN, "no `[[movement]]` is declared. D1, D4 and D5 are demonstrated to "
                          "move on unchanged input, so a cross-round movement that is not "
                          "recorded here is a number nothing re-derives."))
    for mv in ctx["movements"]:
        mid = mv.get("id")
        dim = str(mv.get("dimension", ""))
        if dim not in DIMS:
            out.append((VIOLATION, f"movement `{mid}`: dimension {dim!r} is not one of "
                                   f"{list(DIMS)}"))
            continue
        ends, ok = [], True
        for side in ("from_card", "to_card"):
            key = str(mv.get(side, ""))
            card = by_key.get(key)
            if card is None:
                out.append((VIOLATION, f"movement `{mid}`: `{side} = {key}` is not a card in "
                                       f"this tree"))
                ok = False
            elif card.get("status") == "unfilled":
                out.append((VIOLATION, f"movement `{mid}`: `{side} = {key}` is an unfilled "
                                       f"skeleton and carries no measurement"))
                ok = False
            else:
                ends.append((key, card))
        if not ok:
            continue
        (fkey, fcard), (tkey, tcard) = ends
        fscore = (fcard.get("dimensions") or {}).get(dim, {}).get("score")
        tscore = (tcard.get("dimensions") or {}).get(dim, {}).get("score")
        if not isinstance(fscore, int) or not isinstance(tscore, int):
            out.append((VIOLATION, f"movement `{mid}`: {dim} is unscored on one end "
                                   f"({fscore!r} -> {tscore!r})"))
            continue
        actual = tscore - fscore
        if "points" not in mv:
            out.append((VIOLATION, f"movement `{mid}`: declares no `points`. The number is "
                                   f"the measurement; a movement that does not state it "
                                   f"cannot be checked against the cards."))
            continue
        if int(mv["points"]) != actual:
            out.append((VIOLATION, f"movement `{mid}`: declares `points = {mv['points']}` but "
                                   f"the cards say {dim} went {fscore} -> {tscore} "
                                   f"({actual:+d}). A movement is re-derived from the cards "
                                   f"on every audit precisely so it cannot go stale."))
            continue
        unrecorded = [k for k, c in ends if not isinstance(c.get("judging_practice"), dict)]
        if "readable" not in mv:
            out.append((VIOLATION, f"movement `{mid}`: declares no `readable`. Whether this "
                                   f"movement can be read as a result at all is the first "
                                   f"thing about it, and it is not optional."))
            continue
        if mv["readable"] and unrecorded:
            out.append((VIOLATION,
                        f"movement `{mid}`: `readable = true` while {', '.join(unrecorded)} "
                        f"records no `judging_practice`. Four dimension-points moved on "
                        f"byte-identical trees because judges privately chose to execute "
                        f"their own faults and no card said so. NAME WHAT THE JUDGES DID OR "
                        f"DO NOT READ THE MOVEMENT."))
        elif unrecorded:
            out.append((OK, f"movement `{mid}`: {dim} {fscore} -> {tscore} ({actual:+d}), "
                            f"declared NOT readable -- {', '.join(unrecorded)} does not say "
                            f"what its judge did. Within demonstrated noise; not evidence of "
                            f"improvement either way."))
        else:
            out.append((OK, f"movement `{mid}`: {dim} {fscore} -> {tscore} ({actual:+d}), "
                            f"judging practice recorded at both ends -- readable."))
    return out


def audit_rh6(ctx: dict) -> list[tuple[str, str]]:
    """R-H6 contested: computed from the cards, never declared, and never dropped."""
    out = []
    groups = ctx["groups"]
    computed = {}
    for g in groups:
        con = contested_of(g)
        if con:
            computed[(g["round"], g["example"], g["arm"])] = con
        # A DECLARATION CANNOT MANUFACTURE ONE. `EVAL-SUPPRESS` is this
        # repository's demonstration that a declared verdict will be used to
        # erase a measured one; the same shape inverted -- declaring a dimension
        # contested that the cards do not support -- would let a judge park an
        # inconvenient score behind a flag nothing re-derives.
        for card in g["cards"]:
            declared = set(card.get("contested") or [])
            unsupported = sorted(declared - set(con))
            if unsupported:
                out.append((VIOLATION,
                            f"card `{g['round']}/{g['example']}/{card.get('run_id')}` "
                            f"declares {unsupported} contested and the judges of that "
                            f"artifact do not differ by more than 1 on "
                            f"{'it' if len(unsupported) == 1 else 'them'}. Contested is "
                            f"re-derived from the cards; a declaration cannot make one."))
    for entry in ctx["contested"]:
        key = (str(entry.get("round")), str(entry.get("example")), str(entry.get("arm")))
        dim = str(entry.get("dimension"))
        got = computed.get(key, {}).get(dim)
        if got is None:
            out.append((VIOLATION,
                        f"`[[contested]]` `{entry.get('id')}`: declares {dim} contested on "
                        f"{'/'.join(key)} and the cards do not. Either the entry is stale "
                        f"or the group is wrong -- and a stale adjudication record is worse "
                        f"than none, because it reads as one that happened."))
            continue
        if entry.get("spread") is not None and int(entry["spread"]) != got["spread"]:
            out.append((VIOLATION,
                        f"`[[contested]]` `{entry.get('id')}`: declares spread "
                        f"{entry['spread']} on {dim}; the cards give {got['spread']}. "
                        f"Re-derived on every run, exactly as R-H5 re-derives `points`."))
            continue
        if entry.get("scores") and [int(x) for x in entry["scores"]] != got["scores"]:
            out.append((VIOLATION,
                        f"`[[contested]]` `{entry.get('id')}`: declares scores "
                        f"{list(entry['scores'])}; the cards give {got['scores']}."))
            continue
        third = str(entry.get("third_pass") or "").strip()
        if not third:
            out.append((VIOLATION,
                        f"`[[contested]]` `{entry.get('id')}`: says nothing about the third "
                        f"pass rule 5 asks for. `none` is a legal and useful answer; "
                        f"silence is not."))
            continue
        out.append((OK, f"`[[contested]]` `{entry.get('id')}`: {dim} spread "
                        f"{got['spread']} re-derived, third pass: {third}"))
    declared_keys = {(str(e.get("round")), str(e.get("example")), str(e.get("arm")),
                      str(e.get("dimension"))) for e in ctx["contested"]}
    for key, con in sorted(computed.items()):
        for dim in con:
            if key + (dim,) not in declared_keys:
                out.append((OPEN,
                            f"`{'/'.join(key)}` {dim} is contested (spread "
                            f"{con[dim]['spread']}: {con[dim]['scores']}) and no "
                            f"`[[contested]]` entry records what was done about it. Rule 5 "
                            f"asks for a third pass citing NEW evidence; the flag firing "
                            f"with nothing beside it is the rule going unexecuted again."))
    if not computed:
        out.append((OK, "no judge group has a spread greater than 1 on any dimension"))
    return out


AUDIT_CHECKS = {
    "R-H1": audit_rh1,
    "R-H2": audit_rh2,
    "R-H3": audit_rh3,
    "R-H4": audit_rh4,
    "R-H5": audit_rh5,
    "R-H6": audit_rh6,
}


def run_audit(root: pathlib.Path) -> tuple[dict[str, list[tuple[str, str]]], dict]:
    log = load_log(root)
    all_rows = collect_cards(root, None)
    ctx = {
        "root": root,
        "changes": _order_changes(log["changes"]),
        "notes": log["notes"],
        "claims": log["claims"],
        "sealed": log["sealed"],
        "movements": log["movements"],
        "contested": log["contested"],
        "demonstrations": log["demonstrations"],
        "groups": judge_groups(root),
        "rows": all_rows,
        "all_rows": all_rows,
        "keys": {r["key"] for r in all_rows},
    }
    return {rid: fn(ctx) for rid, fn in AUDIT_CHECKS.items()}, ctx


def cmd_audit(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="score_tools.py audit")
    ap.add_argument("--root", default=str(DEFAULT_SCORECARD_ROOT))
    ap.add_argument("--rubric", default=str(DEFAULT_RUBRIC))
    ap.add_argument("--quiet-ok", action="store_true", help="hide the OK lines")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root)
    try:
        declared = [r["id"] for r in load_rubric(pathlib.Path(args.rubric))["reading_rules"]]
    except RubricError:
        declared = []

    results, ctx = run_audit(root)
    violations = 0
    print(f"# Reading-rule audit over {root}")
    print(f"# {len(ctx['rows'])} card(s), {len(ctx['changes'])} instrument change(s), "
          f"{len(ctx['claims'])} claim(s), {len(ctx['sealed'])} sealed digest(s)")
    for rid, findings in results.items():
        doc = (AUDIT_CHECKS[rid].__doc__ or "").splitlines()[0].strip()
        print(f"\n## {doc}")
        for level, msg in findings:
            if level == OK and args.quiet_ok:
                continue
            print(f"  {level:<10} {msg}")
            if level == VIOLATION:
                violations += 1
    unimplemented = [r for r in declared if r not in AUDIT_CHECKS]
    if unimplemented:
        print(f"\n  {VIOLATION:<10} the rubric declares {unimplemented} with no check here "
              f"-- a reading rule nothing executes will drift")
        violations += len(unimplemented)
    print(f"\n{violations} violation(s)")
    return 1 if violations else 0


# --------------------------------------------------------------------------
# scope: R3, a claim carries its scope
# --------------------------------------------------------------------------
#
# RD-01. `R-H2` forbids AVERAGING across examples. NOTHING FORBADE GENERALISING
# FROM ONE, and an entire epic was justified by "D2 = 2 on 27 of 27 cards" --
# true of `ab_quota_ledger` alone, written into the charter, the plan and the
# issue, repeated four times, and "verified" by a script containing
# `if "ab_quota_ledger" not in f: continue`. THE CHECK WAS SCOPED TO ONE EXAMPLE
# AND THE RESULT REPORTED AS A PROPERTY OF THE CARD.
#
# WHAT THIS REFUSES, AND WHAT IT DOES NOT. It refuses a CLAIM. It gates nothing
# about the code, no close path consults it, and it decides nothing about any
# artifact -- five epics of static checking on the product caught zero bugs and
# this is deliberately not a sixth. What it does is re-derive a figure from the
# cards on disk and print the cards that contradict it.
#
# HOW A CLAIM IS READ. At the scope ITS OWN WORDS carry. If the text beside the
# figure names an example the corpus knows, the figure is evaluated against that
# example's cards. If it names none, the population is every card -- because
# that is what "on 27 of 27 cards ever written" says. The scope window is the
# line the figure sits on plus the line before and the line after: a scope that
# is not beside the figure is a scope a reader does not have when they read it,
# which is precisely how the "27 of 27" figure travelled.
#
# WHAT IT CANNOT REACH IS COUNTED, NEVER DROPPED. `absent` and `checked, none
# found` are different claims and this project has been caught conflating them.
# Four reach limits are reported by name: an ANAPHORIC scope ("about this
# example"), an ARM-scoped figure (arm labels are round-local and opaque by
# design, so they cannot be resolved to a card set), a counted noun that is not
# cards, and a noun carrying a qualifier the corpus does not define.

# A counted figure is a dimension, a value bound to it, and a count. The binder
# has to be explicit: `| **D1** | 1 | 2 of 6 |` is a table of movement counts,
# not a claim that D1 = 1 on 2 of 6 cards, and the difference between them is
# that nothing in the table BINDS the 1 to D1.
_BIND = r"(?:(?<![A-Za-z])(?:is|are|at|scored|scores|remains?|stays?)(?![A-Za-z])|=|:|->|→)"
_VAL = r"[`*\"' (]{0,3}(?P<val>[0-4])[`*\"' )]{0,3}"
# The count has to be introduced as a SCOPE ("on", "for", "in", "across", ...)
# or sit immediately after the value. Without this, "23 of 27 cards are `3`.
# Moved 0 of 40 against EVAL-RERUN" reads as "D1 = 3 on 0 of 40" -- a figure
# nobody wrote, which would have inflated the count this ticket reports.
_GAP = r"(?P<gap>[\s`*(\[,;—–-]*(?:\b(?:on|for|in|across|over|among|of)\b[^\n.]{0,25}?[\s(\[`*])?)"
# `N of M`, spelled out. `2/2 -> 4` is this repository's notation for a MOVEMENT
# between two judge passes and it is not a count of anything.
_CNT = r"(?P<n>\d+)\s+of\s+(?P<m>\d+)"
_NOUN = r"[\s`*)\]]{0,4}(?P<noun>[A-Za-z][A-Za-z-]*(?:[ \t]+[A-Za-z-]+){0,2})?"

CLAIM_FORM_A = re.compile(r"D(?P<dim>[1-5])(?P<mid>[^\n]{0,60}?)" + _BIND + r"\s*" + _VAL
                          + _GAP + r"(?<![\d.])" + _CNT + _NOUN)
CLAIM_FORM_B = re.compile(
    r"D(?P<dim>[1-5])(?P<mid>[^\n]{0,70}?)(?<![\d.])" + _CNT
    + r"[\s`*]{0,3}(?P<noun>[A-Za-z][A-Za-z-]*(?:[ \t]+[A-Za-z-]+){0,2})?[\s`*]{0,3}"
    + _BIND + r"\s*" + _VAL)
_ANOTHER_DIM = re.compile(r"D[1-5]")
_ANAPHOR = re.compile(r"\bth(?:is|e\s+same)\s+(?:example|artifact|subject|card|"
                      r"example\s+family)\b", re.I)
_ARM = re.compile(r"\barms?\s+[A-Z]\b|`[A-Z]`\s*[/,]|\barm\s+`?[A-Z]`?\b")
_NONCARD_NOUN = re.compile(
    r"\b(mutants?|cells?|actions?|faults?|arms?|columns?|cases?|tests?|lines?|commits?|"
    r"predictions?|controls?|findings?|tickets?|epics?|dimension-points?|points?|"
    r"movements?|kills?|figures?|fixtures?|examples?|instruments?|subjects?)\b", re.I)
_CARD_NOUN = re.compile(r"^(cards?|scorecards?|judge-scores?|judges|rows?)$", re.I)
# Words that may sit beside a card noun without narrowing the population.
_OPEN_QUALIFIERS = {"ever", "written", "judged", "blind", "sealed", "the", "all", "filled",
                    "and", "so", "in", "of", "about", "with", "under", "that", "every",
                    "on", "are", "is", "to", "a", "an", "these", "those", "both", "no",
                    "not", "it", "its", "has", "have", "been", "there", "for", "from",
                    "by", "over", "across"}

#: What `scope` reads by default: the charters, the plan, the ledger and the
#: narrative results. `specs/.history/**` is deliberately OUT -- those are sealed
#: closed-snapshots of the same documents and sweeping them would report one
#: claim once per epic that ever snapshotted it, which is a denominator about
#: the archive rather than about the record.
#:
#: `references/*.md` IS in the set, and that includes the card itself. The
#: section of `references/eval_scorecard.md` that DECLARES this rule quotes the
#: unscoped figure it was written about, so this sweep refuses a claim inside
#: its own specification. That is the correct outcome rather than an oversight:
#: exempting the document that declares a rule from the rule is how three
#: unexecuted declarations got written into this repository already.
DEFAULT_SWEEP = (
    "*.md",
    "references/*.md",
    "specs/desired_program_model/*.yaml",
    "specs/results/scorecards/**/*.md",
    "specs/results/scorecards/INSTRUMENT-LOG.toml",
    "specs/results/complexity_ledger.json",
    "specs/results/skill_feedback.md",
)

REFUTED = "REFUTED"
COUNT_MOVED = "COUNT-MOVED"
HOLDS = "HOLDS"
UNREACHABLE = "UNREACHABLE"


def sweep_paths(root: pathlib.Path, patterns=DEFAULT_SWEEP) -> list[pathlib.Path]:
    seen, out = set(), []
    for pat in patterns:
        for p in sorted(root.glob(pat)):
            if not p.is_file() or ".history" in p.parts:
                continue
            if p not in seen:
                seen.add(p)
                out.append(p)
    return out


def find_claims(path: pathlib.Path, root: pathlib.Path) -> list[dict]:
    """Every counted figure of the form `D<n> = k on N of M` in one file."""
    try:
        lines = path.read_text(errors="replace").splitlines()
    except OSError:
        return []
    rel = str(path.relative_to(root)) if _under(path, root) else str(path)
    out = []
    for i, line in enumerate(lines, 1):
        seen = set()
        # Anchored at EVERY dimension token rather than scanned with finditer.
        # `- **D2 — STOP CITING IT** ... `D2 = 2` on **27 of 27** cards` matches
        # from the first D2 with the second one inside `mid`; a non-overlapping
        # scan then consumes the line and never tries the second, so discarding
        # the cross-dimension match silently discarded the claim with it.
        starts = [mm.start() for mm in _ANOTHER_DIM.finditer(line)]
        for form, rx in (("A", CLAIM_FORM_A), ("B", CLAIM_FORM_B)):
            for pos in starts:
                m = rx.match(line, pos)
                if m is None:
                    continue
                if _ANOTHER_DIM.search(m.group("mid")):
                    continue          # the value belongs to a later dimension
                if form == "A" and _ANOTHER_DIM.search(m.group("gap")):
                    continue
                key = (m.group("dim"), m.group("val"), m.group("n"), m.group("m"))
                if key in seen:
                    continue
                seen.add(key)
                window = "\n".join(lines[max(0, i - 2):i + 1])
                out.append({
                    "file": rel, "line": i, "form": form,
                    "dim": "D" + m.group("dim"), "value": int(m.group("val")),
                    "n": int(m.group("n")), "m": int(m.group("m")),
                    "noun": (m.group("noun") or "").strip(),
                    "span": " ".join(m.group(0).split()),
                    "near": line[m.start(): m.end() + 40],
                    "window": window,
                })
    return out


def _qualifiers(noun: str) -> list[str]:
    words = [w for w in re.split(r"[\s]+", noun) if w]
    return [w for w in words
            if not _CARD_NOUN.match(w) and w.lower() not in _OPEN_QUALIFIERS]


def evaluate_claim(claim: dict, cards: list[dict], examples: set[str]) -> dict:
    """Read the figure at the scope its own words carry, then re-derive it."""
    noun, near, window = claim["noun"], claim["near"], claim["window"]
    if noun and _NONCARD_NOUN.search(noun):
        return dict(claim, verdict=UNREACHABLE, reason="non-card noun",
                    detail=f"the counted noun is {noun!r}; this reads cards")
    quals = _qualifiers(noun)
    if quals:
        return dict(claim, verdict=UNREACHABLE, reason="unresolved qualifier",
                    detail=f"the counted noun narrows the population with {quals}, which "
                           f"names no example in this corpus")

    # A NAMED EXAMPLE BESIDE THE FIGURE SETTLES THE SCOPE, and it is looked for
    # before the two unresolvable forms. An anaphor somewhere in the window does
    # not make an explicitly named example ambiguous; reading it the other way
    # round moved SM-04's correctly scoped claim into the unreachable pile, and
    # a check that cannot see a claim doing the right thing cannot be trusted
    # when it says one is doing the wrong thing.
    named = sorted(e for e in examples if e in window)
    if named:
        population = [c for c in cards if c["example"] in named]
        scope = f"example {', '.join(named)}"
    else:
        if _ARM.search(near):
            return dict(claim, verdict=UNREACHABLE, reason="arm-scoped",
                        detail="the figure names an arm label. Arm labels are round-local "
                               "and opaque by design (scaffold draws them from a pool that "
                               "excludes every label a prior round published), so they "
                               "cannot be resolved to a card set here.")
        if _ANAPHOR.search(window):
            return dict(claim, verdict=UNREACHABLE, reason="anaphoric scope",
                        detail="the scope is carried by 'this example' or the like. It is a "
                               "scope, and it is not one this can resolve.")
        population = list(cards)
        scope = "UNSCOPED — read over every card, which is what its words say"
    if not population:
        return dict(claim, verdict=UNREACHABLE, reason="empty scope",
                    detail=f"no cards for {scope}")

    dim, value = claim["dim"], claim["value"]
    hits = [c for c in population
            if (c["dimensions"].get(dim) or {}).get("score") == value]
    misses = [c for c in population if c not in hits]
    # A card outside the value is a COUNTEREXAMPLE only where the claim is
    # universal -- `on N of N`. Where the claim already says `23 of 27` the
    # other four are the remainder it accounts for, and listing them as
    # counterexamples would be the check making the claim say more than it does.
    universal = claim["n"] == claim["m"]
    out = dict(claim, scope=scope, examples=named, population=len(population),
               hits=len(hits), counterexamples=misses if universal else [],
               off_value=len(misses))
    if universal and misses:
        return dict(out, verdict=REFUTED, reason="counterexample",
                    detail=f"{len(misses)} card(s) in the population its words denote do not "
                           f"carry {dim} = {value}")
    if not universal and (len(hits), len(population)) != (claim["n"], claim["m"]):
        moved = ("the numerator" if len(hits) != claim["n"] else "the denominator")
        return dict(out, verdict=REFUTED, reason="count",
                    detail=f"re-derives as {len(hits)} of {len(population)}, not "
                           f"{claim['n']} of {claim['m']} — {moved} moved")
    if len(population) != claim["m"]:
        return dict(out, verdict=COUNT_MOVED, reason="denominator",
                    detail=f"no counterexample, and the population is now {len(population)} "
                           f"rather than {claim['m']} — the denominator rose")
    return dict(out, verdict=HOLDS, reason="re-derived", detail="")


def run_scope(root: pathlib.Path, scorecard_root: pathlib.Path,
              paths: list[pathlib.Path] | None = None) -> list[dict]:
    cards = [c for _, c in load(scorecard_root) if c.get("status") != "unfilled"]
    examples = {str(c.get("example")) for c in cards}
    files = paths if paths is not None else sweep_paths(root)
    out = []
    for f in files:
        for claim in find_claims(f, root):
            out.append(evaluate_claim(claim, cards, examples))
    return out


def _card_id(card: dict) -> str:
    return f"{card.get('example')}/{card.get('run_id')}"


def cmd_scope(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="score_tools.py scope")
    ap.add_argument("--root", default=str(REPO_ROOT),
                    help="the tree whose record is swept")
    ap.add_argument("--scorecards", default=str(DEFAULT_SCORECARD_ROOT))
    ap.add_argument("--path", action="append", default=[],
                    help="sweep this file instead of the default record")
    ap.add_argument("--format", choices=("text", "json"), default="text")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root)
    paths = [pathlib.Path(p) for p in args.path] or None
    results = run_scope(root, pathlib.Path(args.scorecards), paths)

    if args.format == "json":
        print(json.dumps([{k: v for k, v in r.items() if k != "counterexamples"}
                          | {"counterexamples": [_card_id(c) for c in
                                                 r.get("counterexamples", [])]}
                          for r in results], indent=2, default=str))
        return 1 if any(r["verdict"] == REFUTED for r in results) else 0

    order = (REFUTED, COUNT_MOVED, HOLDS, UNREACHABLE)
    print("# R3 — a claim carries its scope")
    print("# A figure `D<n> = k on N of M cards` is read at the scope ITS OWN WORDS carry")
    print("# and re-derived against the cards on disk. Nothing here gates the product.")
    for verdict in order:
        rows = [r for r in results if r["verdict"] == verdict]
        print(f"\n## {verdict} — {len(rows)}")
        for r in rows:
            print(f"  {r['file']}:{r['line']}  {r['dim']} = {r['value']} on "
                  f"{r['n']} of {r['m']} {r['noun']}".rstrip())
            print(f"      as written: {r['span']!r}")
            if verdict == UNREACHABLE:
                print(f"      cannot reach: {r['reason']} — {r['detail']}")
                continue
            print(f"      scope: {r['scope']}  (population {r['population']}, "
                  f"{r['hits']} carry {r['dim']} = {r['value']})")
            if r["detail"]:
                print(f"      {r['detail']}")
            for c in r.get("counterexamples", [])[:12]:
                print(f"      counterexample: {_card_id(c)} "
                      f"{r['dim']} = {(c['dimensions'][r['dim']] or {}).get('score')} "
                      f"({(c.get('judge') or {}).get('model')}, "
                      f"tier {judge_tier(c.get('judge'))})")
            if len(r.get("counterexamples", [])) > 12:
                print(f"      ... and {len(r['counterexamples']) - 12} more")
    counts = {v: sum(1 for r in results if r["verdict"] == v) for v in order}
    print(f"\n{len(results)} counted figure(s): "
          + ", ".join(f"{counts[v]} {v}" for v in order))
    print("A claim this cannot reach is NOT a claim that holds. The two counts are "
          "separate on purpose.")
    return 1 if counts[REFUTED] else 0


# --------------------------------------------------------------------------
# seal
# --------------------------------------------------------------------------

def cmd_seal(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="score_tools.py seal")
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--root", default=str(DEFAULT_SCORECARD_ROOT))
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root)
    log = load_log(root)
    known = {s["path"]: s for s in log["sealed"]}
    new, drifted = [], []
    for arg in args.paths:
        base = pathlib.Path(arg)
        files = sorted(base.rglob("scorecard.*")) if base.is_dir() else [base]
        for f in files:
            if f.suffix not in {".json", ".md"}:
                continue
            rel = str(f.resolve().relative_to(REPO_ROOT))
            digest = "sha256:" + hashlib.sha256(f.read_bytes()).hexdigest()[:16]
            if rel in known:
                if known[rel].get("sha256") != digest:
                    drifted.append((rel, known[rel].get("sha256"), digest))
                continue
            new.append((rel, digest))
    if drifted:
        print("REFUSED: these are already sealed and their contents changed. A sealed card "
              "is never edited -- record the correction beside it instead.", file=sys.stderr)
        for rel, was, now in drifted:
            print(f"  {rel}: {was} -> {now}", file=sys.stderr)
        return 3
    if not new:
        print("nothing new to seal")
        return 0
    lines = ["", "# --- sealed digests appended by `score_tools.py seal` ---"]
    for rel, digest in new:
        lines += ["", "[[sealed]]", f'path = "{rel}"', f'sha256 = "{digest}"']
    with (root / LOG_NAME).open("a") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"sealed {len(new)} file(s) into {root / LOG_NAME}")
    return 0


# --------------------------------------------------------------------------

def cmd_tags(argv: list[str]) -> int:
    """The third comparability axis, printed. It refuses nothing and exits 0.

    `--compare A B` prints one pair, one line per dimension, and BOTH SCORE
    SETS ARE ON EVERY LINE INCLUDING THE INCOMPARABLE ONE. That is the whole
    anti-suppression invariant and it is executed here rather than promised:
    the verdict annotates the pair, and a tag can never reduce the set of
    printed numbers.
    """
    ap = argparse.ArgumentParser(prog="score_tools.py tags")
    ap.add_argument("--root", default=str(DEFAULT_SCORECARD_ROOT))
    ap.add_argument("--compare", nargs=2, default=None, metavar=("A", "B"),
                    help="two declared subjects of the same example")
    args = ap.parse_args(argv)
    module = arch()
    root = pathlib.Path(args.root)
    subjects = module.load_subjects()
    derived = module.derive_subjects(subjects, REPO_ROOT)
    rows = module.card_rows(root)
    entries = module.demonstration_table(rows, derived, subjects)
    if args.compare:
        a, b = args.compare
        unknown = [x for x in (a, b) if x not in subjects]
        if unknown:
            print(f"no declared subject {unknown} in "
                  f"{module.DEFAULT_SUBJECTS}", file=sys.stderr)
            return 2
        table = module.authority(entries)
        example = subjects[a]["example"]
        print(f"example: {example}")
        print(f"  {a} [{derived[a]['derived']}]   vs   {b} [{derived[b]['derived']}]")
        print()
        counts = {module.COMPARABLE: 0, module.INCOMPARABLE: 0, module.ABSENT: 0}
        for line in module.compare(rows, derived, subjects, example, a, b, table):
            counts[line["state"]] = counts.get(line["state"], 0) + 1
            print(f"{line['dimension']}  {a} {line['scores_a']}")
            print(f"    {b} {line['scores_b']}")
            print(f"    -> {line['state']} ({line['reason']})")
        print()
        print(f"incomparable pairs reported: {counts[module.INCOMPARABLE]}     "
              f"absent: {counts[module.ABSENT]}     comparable: {counts[module.COMPARABLE]}")
        return 0
    print(module.render_derive(subjects, derived))
    print()
    print(module.render_table(entries, module.same_tag_controls(rows, derived, subjects)))
    print()
    print(module.render_drift(module.scope_drift(rows, subjects), len(rows)))
    return 0


COMMANDS = {
    "check": cmd_check,
    "tags": cmd_tags,
    "index": cmd_index,
    "scaffold": cmd_scaffold,
    "serve": cmd_serve,
    "history": cmd_history,
    "audit": cmd_audit,
    "seal": cmd_seal,
    "contested": cmd_contested,
    "scope": cmd_scope,
}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in COMMANDS:
        print(__doc__)
        return 2
    return COMMANDS[argv[0]](argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
