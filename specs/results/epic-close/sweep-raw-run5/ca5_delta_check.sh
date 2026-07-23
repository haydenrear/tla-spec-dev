#!/bin/bash
# Fixed-pattern content-delta check: run-5 patterns applied to BOTH the 400c51a
# (run-4) content and the 5f84937 (run-5) content of the five modified surface
# files, plus the added file. For a fixed pattern, hit deltas can come only
# from content deltas — this isolates CD-11's edits from pattern variance.
set -u
cd "$(dirname "$0")"
ROOT=../../../..
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
modified=(scripts/new_ticket_workflow.py tests/test_kill_test.py specs/current/tests/test_tla_spec_dev_kill_test_adapter.py specs/desired_program_model/tests/test_tla_spec_dev_kill_test_adapter.py specs/program_model/tests/test_tla_spec_dev_kill_test_adapter.py)
added=specs/results/epic-close/sweep-raw-run4/ca4_classify.py
for i in "${!names[@]}"; do
  n=${names[$i]}; p=${pats[$i]}
  o=0; w=0
  for f in "${modified[@]}"; do
    oc=$( (cd "$ROOT" && git show "400c51a:$f") | /usr/bin/grep -cE "$p" ); o=$((o+oc))
    nc=$( (cd "$ROOT" && /usr/bin/grep -cE "$p" "$f") ); w=$((w+nc))
  done
  ac=$( (cd "$ROOT" && /usr/bin/grep -cE "$p" "$added") )
  echo "$n old5=$o new5=$w delta_modified=$((w-o)) added_file=$ac"
done
