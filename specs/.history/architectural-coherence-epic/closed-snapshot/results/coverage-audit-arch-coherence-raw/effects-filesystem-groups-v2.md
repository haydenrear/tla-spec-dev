| Group | Distinct semantics | Raw | IN-MODEL | out-of-model | ESCALATION |
|---|---|---|---|---|---|
| `FS-D` | DESTRUCTIVE: delete / rename / overwrite-in-place of a real path | 54 | 9 | 33 | 12 |
| `FS-W` | WRITE/CREATE: creates or overwrites a file or directory | 828 | 76 | 580 | 172 |
| `FS-T` | TEMP WORKDIR: creates a temporary tree | 34 | 2 | 32 | 0 |
| `FS-R` | READ / PATH CONSTRUCTION: no mutation of the filesystem | 933 | 201 | 513 | 219 |
| `FS-N` | LEXICAL ONLY: token matched prose, a str/list method, or an identifier | 2060 | 537 | 1129 | 394 |
