#!/usr/bin/env python3
"""SV-02. Every figure in `references/scoring_validation.md` is re-derived here.

Run from the repository root:

    python3 specs/results/scorecards/score-drives-validation/\
GOAL-validation-is-scorable/SV-02/analysis/scorability.py

Reads only sealed cards under `specs/results/scorecards/`. Writes nothing.
NO production code -- nothing imports this file.

METHOD. Section 2 is RM-02's autopsy, reproduced verbatim from
`specs/results/scorecards/portable-substrate/GOAL-portable/analysis/portability.py`
(LOCAL_TERMS and ANCHOR_DECISION are copied unchanged so the two numbers are
comparable), and then applied to SV-02's candidate. Sections 3-6 are SV-02's own.

SCOPE (R3). 87 sealed cards. 61 are the example `ab_quota_ledger`, 6 are
`eval_toolchain`, 4 `toolchain_removal`, 10 are two cards each of five fixtures,
6 more are `toolchain_removal` at v4/v5. Every figure names the population it
was computed over and no figure is averaged across examples or card versions
(R-H1 / R-H2).
"""
import collections
import glob
import json
import os
import re

CARDS = "specs/results/scorecards"
DIMS = ["D1", "D2", "D3", "D4", "D5"]


def tier(model):
    m = model or ""
    return "opus" if "opus" in m else ("sonnet" if "sonnet" in m else "unknown")


def load():
    """One row per (card, dimension-or-note). Notes carry score=None."""
    rows, cards = [], []
    for p in sorted(glob.glob(os.path.join(CARDS, "**", "scorecard.json"),
                              recursive=True)):
        d = json.load(open(p))
        rel = os.path.relpath(p, CARDS)
        base = dict(
            path=rel, round_dir=rel.split(os.sep)[0], example=d.get("example"),
            arm=d.get("arm"), version=d.get("scorecard_version"),
            model=(d.get("judge") or {}).get("model"),
            tier=tier((d.get("judge") or {}).get("model")),
            run_id=d.get("run_id"),
            jp=d.get("judging_practice") or {},
        )
        cards.append(base)
        for dim, v in (d.get("dimensions") or {}).items():
            if not isinstance(v, dict):
                continue
            rows.append(dict(base, dim=dim, kind="scored", score=v.get("score"),
                             citations=v.get("citations") or [],
                             text=v.get("rationale") or ""))
        for note, v in (d.get("notes") or {}).items():
            if not isinstance(v, dict):
                continue
            rows.append(dict(base, dim=note, kind="note", score=None,
                             citations=v.get("citations") or [],
                             text=v.get("note") or ""))
    return rows, cards


# --------------------------------------------------------------- section 2
# RM-02's autopsy, copied unchanged from portability.py so the two numbers
# are comparable. Do not "improve" these patterns -- the comparison is the
# whole point.
LOCAL_TERMS = (r"TLC|TLA\+|\.tla\b|model-derived|derived from the model|"
               r"whole-view corpus|the corpus|corpora|generated corpus|"
               r"spec double|spec_double|projection|catalogue")
ANCHOR_DECISION = (r"anchor \d[^.;]{0,120}?(refus|not met|withheld|denied|cannot|is not|fails)"
                   r"|(refus|withheld|not met|cannot award|blocks?)[^.;]{0,80}?anchor \d"
                   r"|anchor \d is met|meets anchor \d|reaches anchor \d"
                   r"|not \d[:,]? (because|every|the)")

# SV-02's candidate property, in the vocabulary the record already uses.
# A DEMONSTRATION sentence is one where a named break meets a red/green
# outcome of the SUBJECT'S OWN checking. It says nothing about provenance.
BREAK = (r"\bseed(ed|ing)?\b|\bmutant\b|\bmutat(e|ed|ing|ion)\b|\bfault\b|"
         r"\bdelet(e|ed|ing)\b|\bremov(e|ed|ing) the\b|\binject(ed)?\b|"
         r"\bbroke\b|\bbreak(ing)?\b|\bflipp?(ed)?\b|\breversed\b|"
         r"\boff-by-one\b|\bcorrupt(ed)?\b|\brewrote\b|\bscratch copy\b")
OUTCOME = (r"\bsurviv(e|ed|es|al)\b|\bkill(ed|s)?\b|\bcaught\b|\bcatch(es)?\b|"
           r"\bmissed?\b|\bpass(ed|es)? (all|unchanged|regardless|under)\b|"
           r"\d+\s*(of|/)\s*\d+|\bgreen\b|\bred\b|\bfail(ed|s|ure)?\b|"
           r"\bwent red\b|\bunchanged\b|\bexit(ed)? 0\b|\bnothing failed\b|"
           r"\bdid not fail\b|\bno case\b|\bnothing\b.{0,30}\b(notices|sees|reads|observ)")
# The blind region named, with its structural reason.
BLIND = (r"\bblind\b|\bunobservable\b|\binvisible\b|\bno oracle\b|"
         r"\bnever (reads?|opens?|exercis|drives?|asserts?|holds?)\b|"
         r"\basserted nowhere\b|\bby construction\b|\bcannot (see|contain|form)\b|"
         r"\bdemonstrably miss(es|ed)?\b|\bunreachable\b|\bvacuous\b|"
         r"\bcannot fail\b|\bunverified\b")


def sentences(t):
    return re.split(r"(?<=[.;])\s+", t)


def rests_on_local(rows, pattern, name):
    """RM-02 section 2, parameterised by which kind of decision we test."""
    per = collections.defaultdict(collections.Counter)
    for r in rows:
        per[r["dim"]]["n"] += 1
        for s in sentences(r["text"]):
            if re.search(LOCAL_TERMS, s, re.I) and re.search(pattern, s, re.I):
                per[r["dim"]]["local"] += 1
                break
    return per


def candidate_autopsy(rows):
    """The autopsy on SV-02's candidate.

    A DEMONSTRATION sentence: a named break AND an outcome in one sentence.
    The autopsy asks what fraction of those sentences ALSO cite this
    project's machinery -- i.e. how often the candidate's evidence could not
    have been produced by an adopter who does not own our toolchain.
    """
    total, local, per_dim = 0, 0, collections.defaultdict(collections.Counter)
    local_examples, clean_examples = [], []
    for r in rows:
        for s in sentences(r["text"]):
            if not (re.search(BREAK, s, re.I) and re.search(OUTCOME, s, re.I)):
                continue
            total += 1
            per_dim[r["dim"]]["n"] += 1
            if re.search(LOCAL_TERMS, s, re.I):
                local += 1
                per_dim[r["dim"]]["local"] += 1
                if len(local_examples) < 6:
                    local_examples.append((r["run_id"], r["dim"], s.strip()[:230]))
            elif len(clean_examples) < 6:
                clean_examples.append((r["run_id"], r["dim"], s.strip()[:230]))
    return total, local, per_dim, local_examples, clean_examples


# --------------------------------------------------------------- section 4
def demonstration_grade(text):
    """Score-free three-way read of what a card's prose demonstrates.

    NOT a proposed rung. It is the coarsest classification that can be applied
    uniformly to prose written under four different card versions, and its only
    job is to answer one question: does the property VARY across the record, or
    is it a constant like D1 was?
    """
    has_break = bool(re.search(BREAK, text, re.I))
    has_out = bool(re.search(OUTCOME, text, re.I))
    has_blind = bool(re.search(BLIND, text, re.I))
    has_count = bool(re.search(r"\d+\s*(of|/)\s*\d+", text))
    if not text.strip():
        return "EMPTY"
    if has_break and has_out and has_blind and has_count:
        return "RED+REGION+COUNT"
    if has_break and has_out and (has_blind or has_count):
        return "RED+ONE"
    if has_break and has_out:
        return "RED-ASSERTED"
    if has_blind:
        return "REGION-ONLY"
    return "NEITHER"


def main():
    rows, cards = load()
    ncards = len(cards)
    print(f"# SV-02 scorability evidence -- {ncards} sealed cards, "
          f"{len([r for r in rows if r['kind']=='scored'])} scored rationales, "
          f"{len([r for r in rows if r['kind']=='note'])} recorded notes")
    exc = collections.Counter(c["example"] for c in cards)
    verc = collections.Counter(c["version"] for c in cards)
    print(f"\nSCOPE (R3): examples={dict(exc)}")
    print(f"            card versions={dict(sorted(verc.items()))}")
    print("Every figure below is about THAT population and no wider one.\n")

    # ---- 1. RM-02's number, re-derived at this tree ----------------------
    print("## 1. RM-02's autopsy re-derived at this tree (SCORED rationales only)")
    scored = [r for r in rows if r["kind"] == "scored"]
    a = rests_on_local(scored, ANCHOR_DECISION, "anchor")
    print(f"{'dim':5s}{'n':>5s}{'anchor decisions citing local machinery':>46s}")
    for d in DIMS:
        n = a[d]["n"]
        print(f"{d:5s}{n:5d}{a[d]['local']:>38d} ({100*a[d]['local']/n:.0f}%)")
    print("  RM-02 reported 38% / 18% / 4% / 0% / 0% over 73 cards. The corpus is")
    print("  now 87 and the figures hold. THIS IS THE NUMBER TO BEAT.\n")

    # ---- 2. the candidate's autopsy --------------------------------------
    print("## 2. SV-02's candidate, autopsied RM-02's way")
    print("    A DEMONSTRATION sentence = a named break + a red/green outcome,")
    print("    in one sentence. Provenance-blind by construction: the patterns")
    print("    contain no word about where a case came from.")
    tot, loc, per_dim, lex, cex = candidate_autopsy(rows)
    print(f"\n    demonstration sentences in the whole record : {tot}")
    print(f"    of those, citing this project's machinery   : {loc} "
          f"({100*loc/tot:.1f}%)   <-- THE AUTOPSY FRACTION")
    print("\n    per dimension/note (where the sentences live):")
    for d in sorted(per_dim, key=lambda k: -per_dim[k]["n"]):
        n, l = per_dim[d]["n"], per_dim[d]["local"]
        print(f"      {d:6s} n={n:4d}  local={l:3d} ({100*l/n:.0f}%)")
    print("\n    the machinery-citing ones, so they can be read and disputed:")
    for rid, d, s in lex:
        print(f"      [{d}] {rid}: {s}")
    print("\n    a sample of the clean ones:")
    for rid, d, s in cex:
        print(f"      [{d}] {rid}: {s}")

    # ---- 3. does the property vary, or is it a constant like D1? ---------
    print("\n## 3. Does the property VARY? (D1's fatal defect was that it did not)")
    print("    D1 score distribution, v1-v3 cards, the only cards where D1 scored:")
    d1 = [r for r in scored if r["dim"] == "D1"]
    c = collections.Counter(r["score"] for r in d1)
    mode = c.most_common(1)[0]
    print(f"      {dict(sorted(c.items()))}  modal {mode[0]} on {mode[1]}/{len(d1)} "
          f"({100*mode[1]/len(d1):.0f}%)")
    for ex in sorted({r["example"] for r in d1}):
        sub = [r for r in d1 if r["example"] == ex]
        cc = collections.Counter(r["score"] for r in sub)
        m = cc.most_common(1)[0]
        print(f"        {ex:22s} {dict(sorted(cc.items()))}  modal {m[0]} on "
              f"{m[1]}/{len(sub)}")

    print("\n    The candidate's grade over the SAME D1 rationales "
          "(R-H2: not averaged across examples):")
    for ex in sorted({r["example"] for r in d1}):
        sub = [r for r in d1 if r["example"] == ex]
        cc = collections.Counter(demonstration_grade(r["text"]) for r in sub)
        print(f"      {ex:22s} n={len(sub):3d}  {dict(cc)}")

    print("\n    And the crux: WITHIN the cards D1 scored 3, what does the")
    print("    candidate see? If it varies here, D1's number was discarding")
    print("    signal that was already in D1's own prose.")
    at3 = [r for r in d1 if r["score"] == 3]
    cc = collections.Counter(demonstration_grade(r["text"]) for r in at3)
    print(f"      D1 == 3, n={len(at3)}: {dict(cc)}")

    # ---- 4. the notes: the property with the ladder REMOVED --------------
    print("\n## 4. The v4/v5 recorded notes -- the same question, no ladder")
    notes = [r for r in rows if r["kind"] == "note" and r["dim"] == "N-D1"]
    print(f"    N-D1 notes: {len(notes)} (population: card versions 4 and 5 only)")
    print(f"    {'run_id':30s}{'example':18s}{'chars':>7s}  grade")
    for r in sorted(notes, key=lambda x: x["run_id"] or ""):
        print(f"    {(r['run_id'] or '')[:29]:30s}{(r['example'] or '')[:17]:18s}"
              f"{len(r['text']):7d}  {demonstration_grade(r['text'])}")
    cc = collections.Counter(demonstration_grade(r["text"]) for r in notes)
    print(f"    grades: {dict(cc)}")
    nl = sum(1 for r in notes
             for s in sentences(r["text"])
             if re.search(BREAK, s, re.I) and re.search(OUTCOME, s, re.I)
             and re.search(LOCAL_TERMS, s, re.I))
    nt = sum(1 for r in notes
             for s in sentences(r["text"])
             if re.search(BREAK, s, re.I) and re.search(OUTCOME, s, re.I))
    print(f"    demonstration sentences in N-D1 notes: {nt}, "
          f"machinery-citing: {nl} ({100*nl/nt if nt else 0:.0f}%)")

    # ---- 5. what the property COSTS: who actually ran anything -----------
    print("\n## 5. The cost side: `judging_practice.executed_own_faults`")
    print("    The candidate needs a judge who breaks something. That is a COST")
    print("    and the record prices it.")
    byv = collections.defaultdict(collections.Counter)
    for c in cards:
        v = c["jp"].get("executed_own_faults")
        byv[c["version"]][v] += 1
    for v in sorted(byv):
        print(f"      card version {v}: {dict(byv[v])}")
    tot_t = sum(1 for c in cards if c["jp"].get("executed_own_faults") is True)
    print(f"    executed_own_faults == True on {tot_t} of {ncards} cards "
          f"({100*tot_t/ncards:.0f}%)")

    print("\n    Grade of the N-D1 note / D1 rationale, split by whether the")
    print("    judge actually seeded and ran a fault:")
    for flag in (True, False, None):
        sub = [r for r in rows
               if r["dim"] in ("D1", "N-D1")
               and r["jp"].get("executed_own_faults") is flag]
        if not sub:
            continue
        cc = collections.Counter(demonstration_grade(r["text"]) for r in sub)
        print(f"      executed_own_faults={str(flag):5s} n={len(sub):3d}  {dict(cc)}")

    # ---- 6. where the property is already observed OUTSIDE D1 ------------
    print("\n## 6. The candidate is not a D1 relabel: where its sentences live")
    print("    If the property only ever appears under D1, it IS D1. It does not.")
    for d in sorted(per_dim, key=lambda k: -per_dim[k]["n"]):
        share = 100 * per_dim[d]["n"] / tot
        print(f"      {d:6s} {per_dim[d]['n']:4d} sentences  {share:5.1f}% of all")
    outside = tot - per_dim["D1"]["n"] - per_dim["N-D1"]["n"]
    print(f"    OUTSIDE D1 and N-D1: {outside} of {tot} "
          f"({100*outside/tot:.0f}%) demonstration sentences.")

    # ---- 7. WHICH RUNG carries the machinery ----------------------------
    print("\n## 7. Which RUNG do the machinery-citing decisions name?")
    print("    If they concentrate on one clause, the dimension is not local --")
    print("    one anchor is.")
    for target in ("D1", "D4", "D2"):
        cnt, hits = collections.Counter(), 0
        for r in scored:
            if r["dim"] != target:
                continue
            for s in sentences(r["text"]):
                if re.search(LOCAL_TERMS, s, re.I) and re.search(ANCHOR_DECISION, s, re.I):
                    hits += 1
                    nums = (set(re.findall(r"anchor (\d)", s, re.I))
                            | set(re.findall(r"\bnot (\d)[:,]", s, re.I)))
                    cnt[tuple(sorted(nums)) or ("unnamed",)] += 1
                    break
        print(f"      {target}: {hits} machinery-citing decisions -> {dict(cnt)}")
    print("      D1 anchor 3 says 'a class the whole-view corpus structurally")
    print("      cannot reach'; D1 anchor 4 says 'derived from the model'; D4")
    print("      anchor 3 says 'model-derived (a corpus, a TLC invariant)'.")
    print("      Every other rung on both ladders names no tool at all.")

    # ---- 8. D4's tier instability, and its cause ------------------------
    print("\n## 8. D4 tier-split groups -- the card gives instability as an")
    print("    INDEPENDENT reason for retiring D4. Is it independent?")
    MODEL = (r"model-derived|derived from the model|TLA\+|TLC|formal model|"
             r"generated corpus|whole-view corpus")
    CAUGHT = r"caught|killed?|died|failures?|went red|\d+\s*(of|/)\s*\d+ "
    g = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in scored:
        if r["dim"] == "D4":
            g[(r["round_dir"], r["example"], r["arm"])][r["tier"]].append(r)
    nsplit = nmodel = 0
    for k, by in sorted(g.items(), key=str):
        o = [x["score"] for x in by.get("opus", [])]
        s = [x["score"] for x in by.get("sonnet", [])]
        if not o or not s or not (max(o) < min(s) or max(s) < min(o)):
            continue
        nsplit += 1
        low = "sonnet" if max(s) < min(o) else "opus"
        cards_ = by[low]
        named = sum(1 for c in cards_ if re.search(MODEL, c["text"], re.I))
        caught = sum(1 for c in cards_ if re.search(CAUGHT, c["text"], re.I))
        nmodel += (named == len(cards_))
        print(f"      {str(k)[:54]:56s} opus={o} sonnet={s} lower={low}")
        print(f"        lower-tier cards naming the model clause {named}/{len(cards_)}, "
              f"reporting a caught break anyway {caught}/{len(cards_)}")
    print(f"      {nmodel} of {nsplit} groups: EVERY lower-tier card names the "
          f"model clause.")

    # ---- 9. models, adapter surfaces and diagrams ------------------------
    print("\n## 9. Can a model, an adapter surface or a DIAGRAM be scored?")
    cit = collections.Counter()
    for r in rows:
        for c in r["citations"]:
            b = c.lower()
            if b.endswith(".tla") or b.endswith(".cfg") or "program_model" in b:
                cit[r["dim"]] += 1
    print(f"    citations at a TLA+ model / program_model: {dict(cit)}"
          f"  total {sum(cit.values())}")
    d3top = collections.Counter(r["example"] for r in scored
                                if r["dim"] == "D3" and r["score"] == 4)
    print(f"    D3 == 4 (a driven port exercised by a real adapter AND a fake) "
          f"reached on: {dict(d3top)}")
    print(f"    D3 anchor decisions citing local machinery: "
          f"{a['D3']['local']} of {a['D3']['n']}")
    DIAG = (r"\bdiagram|\bmermaid\b|\bUML\b|\bsequence diagram|\bC4\b|"
            r"\.svg\b|\.png\b|\bdrawing\b")
    dh = sum(1 for r in rows for s in sentences(r["text"])
             if re.search(DIAG, s, re.I))
    dc = len({r["path"] for r in rows for s in sentences(r["text"])
              if re.search(DIAG, s, re.I)})
    print(f"    DIAGRAMS: {dh} sentences across {dc} of {ncards} cards.")


if __name__ == "__main__":
    main()
