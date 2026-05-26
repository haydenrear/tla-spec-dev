# Runtime Requirements

This reference describes the runtime tools the installed skill expects. It is
not an installation guide; in normal use the skill has already been installed
and these dependencies are provided through its `skill-manager.toml`.

Declared CLI dependencies:

- `jinja2`
- `pytest`
- `tlc2`

The `tlc2` wrapper is installed by `skill-scripts/install-tlc2.sh`. It downloads
the TLA+ tools jar from the TLA+ GitHub releases at install time and requires a
local Java runtime.

Repository scripts are intentionally plain Python where possible. Some tests
and examples require `pytest`; TLC case generation requires `tlc2`.
