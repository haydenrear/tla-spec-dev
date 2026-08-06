#!/usr/bin/env python3
"""Mechanical collapse of Sweep-2 raw hits to EXECUTABLE effect sites.

THE COLLAPSING RULE, stated once and applied by machine so a reader can
re-derive every collapsed table from the raw file:

  A raw hit is RETAINED iff, after Python tokenisation removes every comment
  and every string/docstring token, the matched pattern still matches the
  remaining source text of that physical line.

Nothing else is dropped. In particular no hit is dropped for being
"uninteresting"; type annotations, imports and local identifiers survive the
filter and are dispositioned in the report by group.

Non-Python in-model files (.tla, .cfg, .yaml) cannot be tokenised as Python;
every hit in them is a comment or a declaration by construction, so they are
collapsed to ZERO and counted separately as `nonpython_dropped`.

Usage: python3 collapse_effects.py <repo_root>
"""
import io
import re
import sys
import token
import tokenize
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

PATTERNS = {
    "filesystem": r"\b(open|Path|write_text|read_text|write_bytes|mkdir|makedirs|remove|unlink|rename|replace|copy|copytree|rmtree|tempfile|mkdtemp|NamedTemporaryFile)\b",
    "subprocess": r"\b(subprocess|Popen|run|call|check_output|check_call|system|execv|execve|spawn)\b",
    "network": r"\b(socket|connect|requests|urlopen|urlretrieve|urllib|httpx|aiohttp|HTTPConnection|curl|wget)\b",
    "environment": r"\b(environ|getenv|putenv|setdefault|argv|load_dotenv|expanduser|PATH)\b",
    "clock": r"\b(datetime|now|utcnow|today|time|monotonic|perf_counter|sleep|timestamp)\b",
    "randomness": r"\b(random|randint|choice|shuffle|sample|uuid|uuid4|secrets|urandom|token_hex)\b",
    "store": r"\b(sqlite3|psycopg|pymysql|redis|boto3|engine|session|cursor|execute|commit)\b",
    "destructive": r"\b(rmtree|unlink|os\.remove|os\.rmdir|shutil\.move|\.rename\(|os\.replace|truncate)\b",
}

_CODE_CACHE: dict[str, dict[int, str]] = {}


def code_lines(path: str) -> dict[int, str] | None:
    """Per-line source text with comments and string tokens blanked out."""
    if path in _CODE_CACHE:
        return _CODE_CACHE[path]
    if not path.endswith(".py"):
        _CODE_CACHE[path] = None
        return None
    text = (ROOT / path).read_text(encoding="utf-8")
    lines = {i: l for i, l in enumerate(text.splitlines(), 1)}
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        _CODE_CACHE[path] = lines
        return lines
    for t in toks:
        if t.type in (token.COMMENT, token.STRING) or t.type == getattr(token, "FSTRING_START", -1):
            (sr, sc), (er, ec) = t.start, t.end
            for ln in range(sr, er + 1):
                if ln not in lines:
                    continue
                s = lines[ln]
                a = sc if ln == sr else 0
                b = ec if ln == er else len(s)
                lines[ln] = s[:a] + " " * (b - a) + s[b:]
    _CODE_CACHE[path] = lines
    return lines


def main() -> int:
    summary = []
    for name, pat in PATTERNS.items():
        raw_path = HERE / f"effects-{name}.txt"
        if not raw_path.exists():
            continue
        rx = re.compile(pat)
        raw = [l for l in raw_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        kept, nonpy, comment_dropped = [], 0, 0
        per_file = Counter()
        for line in raw:
            m = re.match(r"^(.+?):(\d+):(.*)$", line)
            if not m:
                continue
            path, ln, _ = m.group(1), int(m.group(2)), m.group(3)
            cl = code_lines(path)
            if cl is None:
                nonpy += 1
                continue
            src = cl.get(ln, "")
            if rx.search(src):
                kept.append(f"{path}:{ln}:{src.strip()}")
                per_file[path] += 1
            else:
                comment_dropped += 1
        (HERE / f"effects-{name}-collapsed.txt").write_text("\n".join(kept) + "\n", encoding="utf-8")
        (HERE / f"effects-{name}-byfile.txt").write_text(
            "\n".join(f"{c}\t{f}" for f, c in per_file.most_common()) + "\n", encoding="utf-8"
        )
        summary.append(
            f"{name}\traw={len(raw)}\tcollapsed={len(kept)}\t"
            f"nonpython_dropped={nonpy}\tcomment_or_string_dropped={comment_dropped}\tfiles={len(per_file)}"
        )
    text = "\n".join(summary) + "\n"
    (HERE / "effects-collapse-summary.txt").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
