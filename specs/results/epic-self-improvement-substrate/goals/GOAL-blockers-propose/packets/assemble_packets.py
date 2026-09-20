#!/usr/bin/env python3
"""Assemble the SI-08 improvement-card judge packets.

The card says the bytes a judge is served are RENDERED FROM PARSED STRUCTURE,
never read out of improvement_card.md -- because that file carries statements
about how its own dimensions have scored, which is a conclusion about the
instrument the judge is being asked to be.

So: parse the anchor bullets (`- **0** -- ...` .. `- **4** -- ...`) per
dimension and the numbered scoring rules, and serve ONLY those. Every bolded
editorial paragraph between the bullets is dropped.
"""
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path("/Users/hayde/IdeaProjects/wt-341-evaluation")
CARD = REPO / "skills/spec-double-2/references/improvement_card.md"
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/packets")
OUT.mkdir(parents=True, exist_ok=True)

card = CARD.read_text(encoding="utf-8")

# ----------------------------------------------------------- render the card
DIMS = {
    "I1": "reporting -- Did the blockers this work actually met get reported at all?",
    "I2": "proposal -- Did each report carry a proposed change, or only a description?",
    "I3": "disposition -- Was each proposal applied, or declined with a reason, on the record?",
    "I4": "attribution -- Was the anchor placed, and the model updated where it implied a change?",
    "I5": "honesty -- Does the work refuse to claim what its own artifacts do not show?",
}

anchors = {}
for dim in DIMS:
    m = re.search(rf"^### {dim} — .*?$(.*?)(?=^### |^## )", card, re.S | re.M)
    if not m:
        raise SystemExit(f"could not parse anchors for {dim}")
    bullets = re.findall(r"^- \*\*([0-4])\*\* — (.*?)(?=^- \*\*[0-4]\*\*|\Z)",
                         m.group(1), re.S | re.M)
    if len(bullets) != 5:
        raise SystemExit(f"{dim}: parsed {len(bullets)} rungs, expected 5")
    anchors[dim] = [(n, " ".join(t.split())) for n, t in bullets]

# non-vacuity: the parse must have found all five dimensions, five rungs each
assert len(anchors) == 5, f"parsed {len(anchors)} dimensions, expected 5"
assert all(len(v) == 5 for v in anchors.values()), "a dimension lost a rung"

rules_block = re.search(r"^## Scoring rules that make it hard to game$(.*?)^## ",
                        card, re.S | re.M).group(1)
rules = re.findall(r"^\d+\. \*\*(.*?)\*\*(.*?)(?=^\d+\. |\Z)", rules_block, re.S | re.M)
assert len(rules) == 8, f"parsed {len(rules)} scoring rules, expected 8"

lines = ["# The improvement card (rendered: anchors and scoring rules only)", "",
         "Five dimensions, each scored 0-4. THERE IS NO TOTAL; do not compute one.",
         "Score the LOWEST anchor the subject fully satisfies; when torn between",
         "two, take the lower and say why.", ""]
for dim, q in DIMS.items():
    lines += [f"## {dim} — {q}", ""]
    for n, text in anchors[dim]:
        lines.append(f"- **{n}** — {text}")
    lines.append("")
lines += ["## Scoring rules", ""]
for i, (head, body) in enumerate(rules, 1):
    lines.append(f"{i}. **{head}**{' '.join(body.split())}")
    lines.append("")
rendered_card = "\n".join(lines)
(OUT / "CARD-RENDERED.md").write_text(rendered_card, encoding="utf-8")

# ------------------------------------------------------------ the subjects
def backlog_rows(found_by_prefix):
    import yaml
    rows = []
    final = REPO / "specs/results/deferred_findings_final.yaml"
    d = yaml.safe_load(final.read_text(encoding="utf-8"))
    allrows = d if isinstance(d, list) else list(d.values())[0]
    for r in allrows:
        if str(r.get("found_by", "")).startswith(found_by_prefix):
            rows.append(r)
    part = REPO / f"specs/results/deferred/{found_by_prefix}.yaml"
    if part.is_file():
        p = yaml.safe_load(part.read_text(encoding="utf-8"))
        rows += p["findings"] if isinstance(p, dict) else p
    return rows

SUBJECTS = {
    "A": {"pr": 349, "ticket": "SI-01", "shape": "ticket"},
    "B": {"pr": 375, "ticket": "SI-15", "shape": "ticket"},
}

manifest = {}
for key, s in SUBJECTS.items():
    body = (OUT / f"PR-{s['pr']}-body.md").read_text(encoding="utf-8")
    commits = (OUT / f"PR-{s['pr']}-commits.txt").read_text(encoding="utf-8")
    rows = backlog_rows(s["ticket"])
    assert rows, f"{s['ticket']}: no backlog rows found -- non-vacuity failed"

    items, absent = ["pr_body", "commits", "deferred_findings_backlog_rows"], []
    for sec in ["## Skill changes proposed", "## Review input", "## Deferred findings"]:
        name = sec.strip("# ").lower().replace(" ", "_")
        (items if sec in body else absent).append(name)
    absent.append("close_summary")  # the epic agent closes spec tickets, not the ticket

    packet = [
        "=" * 70,
        f"SUBJECT: pull request #{s['pr']} (ticket {s['ticket']}), subject_shape=ticket",
        "=" * 70, "",
        "ITEM 1 — THE PULL REQUEST BODY, VERBATIM",
        "-" * 70, body, "",
        "ITEM 2 — THE SUBJECT'S OWN COMMITS (git log --stat)",
        "-" * 70, commits, "",
        "ITEM 3 — THE BACKLOG ROWS THIS SUBJECT FILED",
        "-" * 70, json.dumps(rows, indent=1, default=str), "",
        "ITEMS THAT DO NOT EXIST FOR THIS SUBJECT (absent, not withheld):",
        "  " + ", ".join(absent), "",
    ]
    if "## Skill changes proposed" not in body:
        packet.append("NOTE: this subject's body carries NO `## Skill changes proposed`\n"
                      "section. Its absence is DATA and is passed as absent.\n")
    (OUT / f"PACKET-{key}.md").write_text("\n".join(packet), encoding="utf-8")
    manifest[key] = {"pr": s["pr"], "ticket": s["ticket"], "items": items,
                     "absent": absent, "withheld": [],
                     "bytes": len("\n".join(packet)),
                     "backlog_row_ids": [r.get("id") for r in rows]}

# ------------------------------------------------------------ the prompt
PROMPT = """You are scoring one piece of software work against a fixed rubric.

STEP 1 — DISCLOSURE, AND DO THIS BEFORE YOU READ ANYTHING ELSE.
Report, verbatim and in full, every piece of project-specific context that was
placed in your context window before this prompt: any memory or MEMORY.md file,
any git status or recent-commit-subject block, any repository path, any skill or
plugin listing, any hook output, any system reminder naming a project. Quote the
actual bytes. If you received none of these, write exactly: DISCLOSURE: NONE.
Do not summarise -- quote. This disclosure is itself a measurement and a false
one invalidates the round.

STEP 2 — SCORE.
Below is a rubric of five dimensions (I1..I5), each scored 0-4, and then the
subject. Score the LOWEST rung the subject FULLY satisfies. There is no total;
do not compute one. Every score of 2 or higher must cite something a reader can
open -- a section heading in the body, a path, a commit sha, a backlog id.
A score of 2+ whose citations name nothing openable is capped at 1.
The denominator for I1 is the blockers THE WORK MET, which you estimate
yourself from the artifacts -- not the number the subject reports.
`none met` is a legitimate answer and is scored on the evidence for it, not on
the phrase.

OUTPUT: first your STEP 1 disclosure, then a fenced ```json block:
{"I1": {"score": N, "citations": ["..."], "rationale": "..."},
 "I2": {...}, "I3": {...}, "I4": {...}, "I5": {...}}
Then, after the JSON, three sentences on what you could NOT decide from the
packet you were given.

%%CARD%%

%%PACKET%%
"""

for key in SUBJECTS:
    packet = (OUT / f"PACKET-{key}.md").read_text(encoding="utf-8")
    text = PROMPT.replace("%%CARD%%", rendered_card).replace("%%PACKET%%", packet)
    for judge in ("1", "2"):
        (OUT / f"PROMPT-{key}{judge}.txt").write_text(text, encoding="utf-8")

(OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
print(json.dumps(manifest, indent=1))
print("rendered card bytes:", len(rendered_card))
for key in SUBJECTS:
    print(f"PROMPT-{key}1/{key}2 bytes:", (OUT / f"PROMPT-{key}1.txt").stat().st_size)
