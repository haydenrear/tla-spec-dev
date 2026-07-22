# EP-05 validation summary

- Focused provider/parser/replay suite: 83 passed.
- Repository suite: 614 passed.
- Spec units: current 63 passed; ticket current 60 passed.
- TLC: no error; 5,619,356 generated, 231,621 distinct, depth 25.
- `specWorkflow-20260722-231129-034ad51e`: 8/8 nodes and 64/64
  assertions passed.
- `cliWorkflow-20260722-231150-32493c00`: 2/2 nodes and 41/41
  assertions passed.
- Skill-manager local install dry-run: exit 0, no mutation.

The replay regression executes from another working directory using a
dependency-bearing temporary virtualenv. The manifest regression compares all
generated package files with and without site packages. Three signature
negative controls prove failure occurs before adapter setup.
