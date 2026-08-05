#!/usr/bin/env python3
"""Scorecard scaffold, schema check, index, and history reader (scorecard_version 1).

Deliberately lives under examples/validation/ rather than scripts/: scripts/**
is IN MODEL per the plan's representation_scope, and eval harness is not program
surface. Putting it here keeps the model's surface unchanged.

  python3 score_tools.py scaffold <epic-dir> --example E --arms A,B,C --judges 2
  python3 score_tools.py check <dir-or-file>... [--require-filled]
  python3 score_tools.py index <epic-dir>
  python3 score_tools.py history --example E [--root DIR] [--write FILE]
  python3 score_tools.py audit [--root DIR]
  python3 score_tools.py seal <dir>...

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
import json
import pathlib
import random
import re
import subprocess
import sys
import tomllib
from datetime import date as _date

VERSION = 1
DIMS = ("D1", "D2", "D3", "D4", "D5")
NAMES = {
    "D1": "bug detection",
    "D2": "complexity",
    "D3": "modularity",
    "D4": "behavior preservation",
    "D5": "honesty",
}
CITE = re.compile(r"^[^\s:]+:\d+(-\d+)?$")

HERE = pathlib.Path(__file__).resolve()
REPO_ROOT = HERE.parents[3]
DEFAULT_RUBRIC = REPO_ROOT / "references/eval_scorecard.md"
DEFAULT_SCORECARD_ROOT = REPO_ROOT / "specs/results/scorecards"
LOG_NAME = "INSTRUMENT-LOG.toml"

# Never used as an opaque arm label: the arm names themselves. Labels prior
# rounds published are excluded dynamically -- see used_labels().
RESERVED_LABELS = set("ABC")
LABEL_POOL = "DEFGHJKLMNRSTUVWZ"

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


# --------------------------------------------------------------------------
# the rubric: one source of truth for the anchors
# --------------------------------------------------------------------------

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
        if sorted(anchors) != ["0", "1", "2", "3", "4"]:
            raise RubricError(f"{path}: {key} does not carry anchors 0-4 (got {sorted(anchors)})")
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
    missing = [d for d in DIMS if d not in dims]
    if missing:
        raise RubricError(f"{path}: no anchors parsed for {', '.join(missing)}")
    for key, dim in dims.items():
        if dim["name"] != NAMES[key]:
            raise RubricError(
                f"{path}: {key} is titled {dim['name']!r} but this tool knows it as "
                f"{NAMES[key]!r} -- the dimension key has drifted"
            )

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

    source = str(path.relative_to(REPO_ROOT)) if _under(path, REPO_ROOT) else str(path)
    rubric = {"source": source, "dimensions": dims,
              "scoring_rules": rules, "reading_rules": reading}
    rubric["digest"] = "sha256:" + hashlib.sha256(
        json.dumps({"dimensions": dims, "scoring_rules": rules},
                   sort_keys=True).encode()).hexdigest()[:16]
    return rubric


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

    if card.get("scorecard_version") != VERSION:
        err(f"scorecard_version must be {VERSION}, got {card.get('scorecard_version')!r}")

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

    missing = [d for d in DIMS if d not in dims]
    if missing:
        err(f"missing dimensions: {', '.join(missing)}")
    extra = [d for d in dims if d not in DIMS]
    if extra:
        err(f"unknown dimensions: {', '.join(extra)}")

    if rubric is not None and (card.get("rubric") or {}).get("digest"):
        got = card["rubric"]["digest"]
        if got != rubric["digest"]:
            msg = f"scaffolded against rubric digest {got}, current rubric is {rubric['digest']}"
            if status == "unfilled":
                err(msg + " -- re-scaffold before judging against a stale bar")
            else:
                notes.append(f"RUBRIC-DRIFT {where}: {msg}. A filled card is evidence and "
                             f"is not edited; see `history`/`audit` for how to read it.")

    running = 0
    for dim in DIMS:
        entry = dims.get(dim)
        if not isinstance(entry, dict):
            continue
        if entry.get("name") and entry["name"] != NAMES[dim]:
            err(f"{dim} is named {entry['name']!r}; this card version knows it as {NAMES[dim]!r}")
        if "anchors" in entry:
            keys = sorted(str(k) for k in (entry.get("anchors") or {}))
            if keys != ["0", "1", "2", "3", "4"]:
                err(f"{dim} carries inline anchors but not all of 0-4 (got {keys})")
        score = entry.get("score")
        if status == "unfilled":
            if score is not None:
                err(f"{dim} of an unfilled skeleton must have score null")
            continue
        if not isinstance(score, int) or isinstance(score, bool) or not 0 <= score <= 4:
            err(f"{dim} score must be an int 0-4, got {score!r}")
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
        # Rule 3: a 4 must name something the artifact refuses to claim.
        if score == 4 and not entry.get("refuses_to_claim"):
            err(f"{dim} scored 4 without refuses_to_claim -- rule 3")
        if not str(entry.get("rationale") or "").strip():
            err(f"{dim} has no rationale")

    if status != "unfilled":
        total = card.get("total")
        if total != running:
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

    out = [f"# Scorecards — {root.name}", ""]
    out.append("scorecard_version 1. See `references/eval_scorecard.md`.")
    out.append("")
    out.append("**Never average across examples.** `ex6_jenga` is a deliberately")
    out.append("incoherent fixture and is supposed to score low on D3; averaging it")
    out.append("with `ex4` produces a number about nothing. Nothing in this file is")
    out.append("computed across two examples.")
    out.append("")
    header = ("| example | arm | "
              + " | ".join(f"D{i+1} {NAMES['D' + str(i + 1)]}" for i in range(5))
              + " | total | contested |")
    out.append(header)
    out.append("|" + "---|" * 9)
    for example in sorted(by_example):
        for card in sorted(by_example[example], key=lambda c: (str(c.get("arm")), c["run_id"])):
            d = card["dimensions"]
            row = [example, str(card.get("arm") or "—")]
            row += [str(d[k]["score"]) for k in DIMS]
            row.append(f"**{card['total']}**/20")
            row.append(", ".join(card.get("contested") or []) or "—")
            out.append("| " + " | ".join(row) + " |")
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
        for m in re.finditer(r"^\|\s*`?([A-Z])`?\s*\|", p.read_text(), re.M):
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
    ap.add_argument("--unblinded", action="store_true",
                    help="DELIBERATELY skip blinding: emit real arm names as labels")
    ap.add_argument("--reason", default=None, help="required with --unblinded")
    args = ap.parse_args(argv)

    try:
        rubric = load_rubric(pathlib.Path(args.rubric))
    except RubricError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2

    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    if not arms:
        print("REFUSED: --arms names no arm", file=sys.stderr)
        return 2
    if args.judges < 1:
        print("REFUSED: --judges must be at least 1", file=sys.stderr)
        return 2

    epic_dir = pathlib.Path(args.epic_dir)
    scorecard_root = epic_dir.parent

    if args.unblinded:
        if not args.reason:
            print("REFUSED: --unblinded requires --reason. Blinding is the default and "
                  "undoing it is a deliberate, recorded act.", file=sys.stderr)
            return 2
        labels = list(arms)
    elif args.labels:
        labels = [x.strip() for x in args.labels.split(",") if x.strip()]
        if len(labels) != len(arms):
            print(f"REFUSED: {len(labels)} labels for {len(arms)} arms", file=sys.stderr)
            return 2
    else:
        taken = used_labels(scorecard_root) | RESERVED_LABELS | {a.upper() for a in arms}
        pool = [c for c in LABEL_POOL if c not in taken]
        if len(pool) < len(arms):
            print(f"REFUSED: only {len(pool)} unused opaque labels remain", file=sys.stderr)
            return 2
        rng = random.Random(args.seed) if args.seed is not None else random.SystemRandom()
        labels = rng.sample(pool, len(arms))

    run_date = args.run_date or _date.today().strftime("%Y%m%d")
    tag = _slug(args.run_tag) if args.run_tag else None

    def run_id(label: str, judge: int) -> str:
        return "-".join([run_date] + ([tag] if tag else []) + [label, f"p{judge}"])

    example_dir = epic_dir / _slug(args.example)
    planned: list[tuple[pathlib.Path, str]] = []
    for label in labels:
        for judge in range(1, args.judges + 1):
            rid = run_id(label, judge)
            d = example_dir / rid
            planned.append((d / "scorecard.json", _skeleton_json(args, rubric, label, judge, rid)))
            planned.append((d / "scorecard.md", _skeleton_md(args, rubric, label, judge, rid)))
            planned.append((d / "mechanical.json", _mechanical_json(args, label, rid)))
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


def _rubric_block(rubric: dict) -> dict:
    return {"source": rubric["source"], "digest": rubric["digest"],
            "scoring_rules": rubric["scoring_rules"]}


def _skeleton_json(args, rubric: dict, label: str, judge: int, rid: str) -> str:
    dims = {}
    for key in DIMS:
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
        dims[key] = entry
    card = {
        "scorecard_version": VERSION,
        "status": "unfilled",
        "epic": pathlib.Path(args.epic_dir).name,
        "example": args.example,
        "run_id": rid,
        "arm": label,
        "commit": "",
        "judge": {"model": "", "pass": judge, "blind_to_arm": not args.unblinded},
        "rubric": _rubric_block(rubric),
        "how_to_fill": [
            "Score the LOWEST anchor the artifact fully satisfies. Torn between two: "
            "take the lower and say why.",
            "Set `status` to \"filled\", `commit` to the sha the artifacts were scored "
            "at, and name your model in `judge.model`.",
            "`total` is the sum of the five scores; the schema check recomputes it.",
            "Leave `anchors` as scaffolded. They are read from the rubric so the bar "
            "and the score live in one file; editing them here forks the rubric "
            "silently, which is the drift this scaffold exists to remove.",
        ],
        "dimensions": dims,
        "total": None,
        "contested": [],
        "verdict": "",
    }
    return json.dumps(card, indent=2) + "\n"


def _skeleton_md(args, rubric: dict, label: str, judge: int, rid: str) -> str:
    out = [f"# Scorecard — {args.example}, artifact `{label}`, judge pass {judge}", ""]
    out.append(f"`run_id`: `{rid}` · scorecard_version {VERSION} · rubric "
               f"`{rubric['source']}` digest `{rubric['digest']}`")
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
    out.append("## The rules, in the file where the score is written")
    out.append("")
    for i, rule in enumerate(rubric["scoring_rules"], 1):
        out.append(f"{i}. {rule}")
    out.append("")
    out.append("**Score the LOWEST anchor the artifact fully satisfies; when torn "
               "between two, take the lower and say why.**")
    out.append("")
    out.append("## The mechanical block is recorded, never scored")
    out.append("")
    out.append("`mechanical.json` beside this file holds kill counts, complexity "
               "figures, case counts, determinism and runtime. It sits beside the "
               "judgement so a reader can see when the two disagree — **and a "
               "disagreement is a finding, not a rounding error.**")
    out.append("")
    for key in DIMS:
        d = rubric["dimensions"][key]
        out.append(f"## {key} — {d['name']}")
        out.append("")
        if d["question"]:
            out.append(f"*{d['question']}*")
            out.append("")
        if d.get("preamble"):
            out.append(d["preamble"])
            out.append("")
        for score in ("0", "1", "2", "3", "4"):
            out.append(f"- **{score}** — {d['anchors'][score]}")
        out.append("")
        if d["caveat"]:
            out.append(f"> {d['caveat']}")
            out.append("")
        out.append("**Score:** _(0–4)_")
        out.append("")
        out.append("**Citations** (`file:line`; required for any score ≥ 2, and a score "
                   "≥ 2 without one is capped at 1 by the schema check):")
        out.append("")
        out.append("-")
        out.append("")
        out.append("**Refuses to claim** (required and non-null for a score of 4):")
        out.append("")
        out.append("**Rationale:**")
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
    else:
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
        return {"path": path, "changes": [], "notes": [], "claims": [], "sealed": []}
    data = tomllib.loads(path.read_text())
    return {"path": path, "changes": data.get("change", []), "notes": data.get("note", []),
            "claims": data.get("claim", []), "sealed": data.get("sealed", [])}


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
        out.append("| run | round | arm | pass | D1 | D2 | D3 | D4 | D5 | total | commit | note |")
        out.append("|" + "---|" * 12)
        for r in era_rows:
            c = r["card"]
            d = c.get("dimensions") or {}
            if c.get("status") == "unfilled":
                scores, total = ["—"] * 5, "_unfilled_"
            else:
                scores = [str(d.get(k, {}).get("score", "?")) for k in DIMS]
                total = f"**{c.get('total')}**/20"
            marks = notes_by_card.get(r["key"], [])
            out.append("| " + " | ".join([
                f"`{c['run_id']}`", r["round"], str(c.get("arm") or "—"),
                str((c.get("judge") or {}).get("pass", "—")), *scores, total,
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
    """R-H3 repair vs improvement: no claim stays `current` across an unreaffirmed change."""
    out = []
    filed = _finding_ids()
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


AUDIT_CHECKS = {
    "R-H1": audit_rh1,
    "R-H2": audit_rh2,
    "R-H3": audit_rh3,
    "R-H4": audit_rh4,
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

COMMANDS = {
    "check": cmd_check,
    "index": cmd_index,
    "scaffold": cmd_scaffold,
    "history": cmd_history,
    "audit": cmd_audit,
    "seal": cmd_seal,
}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in COMMANDS:
        print(__doc__)
        return 2
    return COMMANDS[argv[0]](argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
