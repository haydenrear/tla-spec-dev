#!/bin/bash
# CA run 5 — verify-by-diff enumeration: all Sweep 2/3 category patterns over
# exactly the surface files whose content changed since run 4 (400c51a..5f84937)
# plus the one added file. Unchanged files carry identical hits by content
# identity (surface diff = +ca4_classify.py only; git name-status = 5 modified
# surface files). Patterns: prompt Step-3 table + Step-4 classes, word-boundary
# anchored, JVM-extended (ProcessBuilder, catch/throw/throws, waitFor,
# synchronized) — matching run 4's stated extensions.
set -u
cd "$(dirname "$0")"
R5=.
R4=../sweep-raw-run4
names=(filesystem subprocess network environment clock randomness persistent_store behaviors_error behaviors_retry behaviors_timeout behaviors_fallback behaviors_concurrency behaviors_config)
pats=(
'\b(open|Path|write_text|read_text|write_bytes|mkdir|makedirs|remove|unlink|rename|replace|copy|copytree|rmtree|tempfile|mkdtemp|NamedTemporaryFile)\b'
'\b(subprocess|Popen|run|call|check_output|check_call|system|execv|execve|spawn|ProcessBuilder)\b'
'\b(socket|connect|requests|urlopen|urlretrieve|urllib|httpx|aiohttp|HTTPConnection|curl|wget)\b'
'\b(environ|getenv|putenv|setdefault|argv|load_dotenv|expanduser|PATH)\b'
'\b(datetime|now|utcnow|today|time|monotonic|perf_counter|sleep|timestamp)\b'
'\b(random|randint|choice|shuffle|sample|uuid|uuid4|secrets|urandom|token_hex)\b'
'\b(sqlite3|psycopg|pymysql|redis|boto3|engine|session|cursor|execute|commit)\b'
'\b(except|raise|try|catch|throw|throws)\b'
'\b(retry|backoff|attempt|max_tries)\b'
'\b(timeout|deadline|expires|TimeoutError|waitFor)\b'
'\b(fallback|default|ImportError)\b|or None'
'\b(thread|async|await|lock|Lock|concurrent|multiprocessing|synchronized)\b'
'\b(getenv|flag|enabled|config)\b|\.get\("|--no-|--allow'
)
ROOT=../../../..
for i in "${!names[@]}"; do
  n=${names[$i]}
  : > "$R5/changed_${n}.txt"
  while read -r f; do
    (cd "$ROOT" && /usr/bin/grep -nHE "${pats[$i]}" "$f") >> "$R5/changed_${n}.txt" || true
  done < "$R5/changed-files.txt"
  fresh=$(wc -l < "$R5/changed_${n}.txt" | tr -d ' ')
  raw="$R4/${n}.txt"; [ -f "$raw" ] || raw="$R4/${n#behaviors_}.txt"
  old=0
  if [ -f "$raw" ]; then
    old=$(head -5 "$R5/changed-files.txt" | while read -r f; do /usr/bin/grep -c "^${f}:" "$raw" || true; done | paste -sd+ - | bc)
  fi
  echo "$n fresh_over_changed_files=$fresh run4_over_same_5_files=$old raw_ref=$(basename "$raw")"
done
