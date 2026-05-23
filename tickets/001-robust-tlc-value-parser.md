# Robust TLC Value Parser

The current `generate_cases_from_tlc_dump.py` parser is pragmatic and handles
the DOT output used by the first program model. It should be replaced or
hardened before relying on richer specs.

Known gaps:

- nested records
- sequences
- tuples
- strings containing commas
- nested functions
- model values with unusual characters

Acceptance criteria:

- Add parser tests with representative TLC values.
- Preserve Python-native values for sets/functions/records/sequences.
- Fail with useful errors when a TLC value is outside the supported profile.
