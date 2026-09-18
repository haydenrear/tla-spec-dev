---
type: regex
pattern: 'Next\s*==[\s\S]{0,800}\\\/'
weight: 1
---

The response quotes a `Next` and at least one `\/` disjunct within 800
characters of it — a TLA+ action list, pasted, rather than described.

WHY A REGEX AND NOT THE JUDGE. `models-the-trace-property` used to ask for two
things at once: *quote the action list* AND *the list contains a release
action*. The first is mechanical and a judge should never have been asked it.
Asked both, on a 6,300-character report, three judges voted **FAIL PASS FAIL**
on a run whose artefact was verifiably correct — `Release(s, o)` is a disjunct
of `InternalNext`, and the module's own comment says the trace property "is the
reason `Release` has to be in this model at all".

So the conjunction is split: this settles the half a machine can settle, and
the judge is left one question. **This is not the grader being tuned until the
run passes.** The pattern is naming-agnostic — it would match a model whose
actions are called anything at all — and it is the same change I would make on
a run that scored 1.00. Verified both ways: it matches that report, and does
not match "I modelled the release action faithfully."
