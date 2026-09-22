---
type: regex
pattern: '\[plugins\.tla-spec-dev\]'
weight: 2
---

Reads the final response only: the corrected manifest declares
   `[plugins.tla-spec-dev]` (the fixture has no carrier entry, so the report
   says to add one).

   SI-18 MOVED THE CARRIER. This pattern was `\[plugins\.skt\]`, and skt is a
   contained skill of tla-spec-dev now — so `[plugins.skt]` names a unit that is
   no longer published, and its coordinate still resolves to the standalone the
   migration removes. Rewarding it would have trained the duplicate back in.
