#!/bin/sh
# The fixture the agent is pointed at, placed BEFORE the session starts.
#
# `run_agent_integration.py` did this in `build_workspace`. It is nine lines
# here because the harness no longer has to own the workspace, the config dir,
# the credentials or the cleanup -- `plugin eval` gives each case a throwaway
# workspace with a fresh CLAUDE_CONFIG_DIR and HOME.
set -eu
cp "${EVAL_CASE_DIR:-.}/../../../fixture/shortlink.py" ./shortlink.py
cp "${EVAL_CASE_DIR:-.}/../../../fixture/test_shortlink.py" ./test_shortlink.py
git init -q -b main .
git config user.email harness@tla-spec-dev.invalid
git config user.name "eval harness"
git add -A
git commit -q -m "shortlink: the program, and the tests that hold it up"
