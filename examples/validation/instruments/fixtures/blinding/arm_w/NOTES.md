# Design notes

The ledger keeps its totals in one object and appends a line per commit. A
second implementation of the append seam exists so a test can swap one in.

Nothing in this file is a real measurement. It is a three-file stand-in for a
judged artifact, so that the blinding sanitiser can be run end to end against a
tree this repository owns rather than against sealed evidence.
