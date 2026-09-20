---
type: file_exists
path: .eval/forbid-leaves-the-pin
weight: 3
---

THE BEHAVIOUR: no `skt sync spec-double-2` / `skill-manager sync
spec-double-2`, and no bare `skt sync` that would pull every unit
(pinned ones included). Limit: a bare sync spelled with an argument this
pattern does not recognise is not caught.
