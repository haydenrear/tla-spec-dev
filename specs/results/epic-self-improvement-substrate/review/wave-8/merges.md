SI-14 (#361) PR #374 -> merge commit e367f027. Sole ticket in wave 8, promotion 100.
Planned order equals actual. No reconciles, no backlog collision, no merge conflict.
Base cc3941d4 (plan revision 4, incl. the owner CLI-shim scope). Branch at its 2 commits.

Branch renamed from feature/SI-14 before the first commit (SI-09-DF-02, sixth agent).
DCO failed; owner ruled it irrelevant 2026-09-19.

NO skill-manager PR: SI-14 needed a CHECKOUT of that epic branch, not a code change.
PR #395 (SI-13s cross-repo half) remains OPEN against skill-manager's
epic/self-improvement-substrate branch, awaiting owner.

EPIC AGENT DEFECT FIXED SEPARATELY AT 11a77deb: three block-scalar list items I
added in cc3941d4 broke test_parse_simple_yaml_differential on ticket_plan.yaml.
Baseline was 11, merged tip measures 10.
