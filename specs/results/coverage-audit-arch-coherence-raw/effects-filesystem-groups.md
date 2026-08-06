| Group | Distinct effect semantics | Raw hits | in-scope hits | ESCALATION hits |
|---|---|---|---|---|
| `FS-D` | DESTRUCTIVE: delete / rename / overwrite-in-place of a real path | 54 | 36 | 18 |
| `FS-W` | WRITE/CREATE: creates or overwrites a file or directory | 828 | 603 | 225 |
| `FS-T` | TEMP WORKDIR: creates a temporary tree | 34 | 29 | 5 |
| `FS-R` | READ / PATH CONSTRUCTION: no mutation of the filesystem | 933 | 555 | 378 |
| `FS-N` | LEXICAL ONLY: token matched prose, a str/list method, or an identifier | 2060 | 1157 | 903 |
