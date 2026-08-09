# RD-03 probe — what was run, verbatim

Nothing under `specs/results/scorecards/reading-discipline/blind/`,
`examples/validation/ab/`, or `scripts/` was written by this probe. Every tree
was copied to a scratch root and mutated there. This directory is the only path
in the repository this ticket wrote to.

Scratch root, referred to below as `$SCR`:

    /private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/daf0ac7d-2e56-422e-b6df-6330f27b6709/scratchpad/probe

Repo root, referred to below as `$REPO`:

    /Users/hayde/IdeaProjects/wt-epic-reading-discipline-RD-03

`python3` below is `/opt/homebrew/opt/python@3.14/bin/python3.14`. **This matters
and cost one whole run:** the first `run_corpus.sh` invocation resolved `python3`
to `/usr/bin/python3` (3.9.6) under a non-interactive shell and died on
`ModuleNotFoundError: No module named 'tomllib'` for all six trees. The
interpreter is pinned in `harness/run_corpus.sh` because of that.

## 0. Copy the trees (never mutate in place)

    for t in Z E N M F D; do
      cp -R $REPO/specs/results/scorecards/reading-discipline/blind/artifact_$t $SCR/trees/artifact_$t
    done

## 1. Baselines on unmutated code

    uv run --with pytest python -m pytest $SCR/trees/artifact_{Z,M,N,D}/test_quota_ledger.py -q -p no:cacheprovider
    uv run --with pytest python -m pytest $SCR/trees/artifact_{E,F}/tests -q -p no:cacheprovider

    cd $REPO && QUOTA_LEDGER_DIR=$SCR/trees/artifact_<T> QUOTA_LEDGER_IMPL=quota_ledger \
      uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q -p no:cacheprovider

Result: `21/22/37/39/39/39` own tests and `28` shared, green on all six.

## 2. Hand-written instrument columns (own-tests, shared-suite, shared-suite-fake)

    cd $SCR && python3 run_probe.py out

`harness/anchors.py` carries the per-tree re-anchoring; `harness/wit.py` carries
one semantic witness per mutant. Every `find` is checked to occur exactly once,
and every mutant is required to make its witness False on the pristine tree and
True on the mutated one before any instrument verdict is recorded.

`logs/run-1-superseded.log` is the FIRST run and is kept. Two witnesses in it
were over-specified relative to the catalogue's own `semantic` text and reported
holes that are not holes (`PA-M14` on artifact_Z; `FI-M15` on artifact_N,
artifact_D, artifact_E, artifact_F). Both corrections are recorded in the
witness docstrings in `harness/wit.py`, with what was wrong and why.
`logs/run-2-final.log` is the run every number in the report comes from. No
mutant was re-run selectively: the whole table was re-run.

## 3. Model-derived instrument columns

TLC is present at `$REPO/.skill-manager/bin/cli/tlc2`.

    cd $REPO && PATH="$REPO/.skill-manager/bin/cli:$PATH" python3 scripts/tla_spec_dev.py \
      --spec-root specs generate cases \
      examples/validation/ab/model/QuotaLedger.tla examples/validation/ab/model/QuotaLedger.cfg \
      --out $SCR/specs/corpus-whole --package quota_whole --view internal
    # exit 2 -- 43,128 cases over the declared cap of 200. It writes the corpus
    # anyway; this is HP-03-DF-02, still open, and is documented in
    # examples/validation/ab/eval/run_controls.py's own docstring.

    ... the same with `--negative-cases only --out $SCR/specs/corpus-neg --package quota_neg`
    # exit 0, 118 cases.

Then, per tree, through the epic's own driver:

    cd $REPO && PYTHONPATH=$SCR/bindings python3 examples/validation/ab/eval/run_controls.py \
      --label RD03-<TREE> --tree $SCR/trees/<TREE> --module-dir . --binding <BINDING> \
      --catalogue $SCR/catalogues/<TREE>.toml \
      --instrument corpus-whole=$SCR/specs/corpus-whole/spec-unit/quota_whole \
      --instrument corpus-neg=$SCR/specs/corpus-neg/spec-unit/quota_neg \
      --instrument map-silent=$SCR/specs/corpus-whole/spec-unit/quota_whole:silent \
      --instrument map-checking=$SCR/specs/corpus-whole/spec-unit/quota_whole:checking \
      --out $SCR/out/corpus/<TREE>.json

Bindings are in `bindings/`; they are new files written by this probe, not edits
to any existing instrument. A binding is not blind — writing one means reading
the tree — and that disclosure is inherited from `eval/reference_binding.py`.

`corpus-slice-res` and `corpus-slice-led` were NOT generated and are NOT
reported. They are about the case-module aspect split, which is not one of this
ticket's three questions.

## 4. Q2, the before/after pairs

    cd $SCR && python3 pairs.py

## 5. Product-surface probes

    cd $SCR && python3 crossdiff.py 400        # six-way differential bug oracle
    cd $SCR && python3 edges.py trees/<TREE>   # targeted edge cases
    cd $SCR && python3 fake_drift.py trees/artifact_{E,F}
    cd $SCR && python3 newline_tenant.py trees/<TREE>
    cd $SCR && python3 adapter_contract_check.py trees/artifact_{E,F}

    # the trees' own shipped instrument, run in a layout where it can find the
    # shared suite (it cannot find it from where the artifacts actually live)
    cd $SCR/mrepo/subjects/artifact_{N,D} && uv run --with pytest python mutation_check.py

    # artifact_F's coverage claim, reproduced
    cd $SCR/trees/artifact_F && uv run --with pytest --with coverage \
      python -m coverage run --branch --source=quota_ledger -m pytest tests -q -p no:cacheprovider
    uv run --with pytest --with coverage python -m coverage report -m

    # artifact_M's "the new test is load-bearing" claim, reproduced
    # (guard replaced with `if self._reservations:` in a scratch copy)

## 6. Merge

    cd $SCR && python3 merge_table.py     # -> results/MERGED-TABLE.json
