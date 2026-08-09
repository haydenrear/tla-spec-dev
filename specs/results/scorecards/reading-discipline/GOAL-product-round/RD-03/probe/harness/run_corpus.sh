#!/bin/bash
# RD-03 model-derived column. One run per tree, four instruments.
set -u
SCR=/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/daf0ac7d-2e56-422e-b6df-6330f27b6709/scratchpad/probe
REPO=/Users/hayde/IdeaProjects/wt-epic-reading-discipline-RD-03
WHOLE=$SCR/specs/corpus-whole/spec-unit/quota_whole
NEG=$SCR/specs/corpus-neg/spec-unit/quota_neg
mkdir -p $SCR/out/corpus
for pair in "artifact_Z binding_Z" "artifact_M binding_Z" "artifact_N binding_N" \
            "artifact_D binding_N" "artifact_E binding_E" "artifact_F binding_E"; do
  set -- $pair; TREE=$1; BIND=$2
  echo "===== $TREE / $BIND ====="
  ( cd $REPO && PYTHONPATH=$SCR/bindings /opt/homebrew/opt/python@3.14/bin/python3.14 examples/validation/ab/eval/run_controls.py \
      --label RD03-$TREE \
      --tree $SCR/trees/$TREE --module-dir . --binding $BIND \
      --catalogue $SCR/catalogues/$TREE.toml \
      --instrument corpus-whole=$WHOLE \
      --instrument corpus-neg=$NEG \
      --instrument map-silent=$WHOLE:silent \
      --instrument map-checking=$WHOLE:checking \
      --out $SCR/out/corpus/$TREE.json ) > $SCR/out/corpus/$TREE.stdout 2>&1
  echo "exit=$?"
  tail -5 $SCR/out/corpus/$TREE.stdout
done
