---
type: file_exists
path: "specs/program_model/spec_manifest.yaml"
weight: 1
---

The spec tree the toolchain produces, identified by the manifest that names its
ports, invariants and finite model -- not by "some .tla file is present".

THE EARLIER VERSION OF THIS GRADER GLOBBED `specs/program_model/*.tla` AND WAS
SATISFIED BY A SCRATCH FILE. The first scored run wrote `Probe.tla`:

    Init == x = 0
    Next == x' = (x + 1) % 3

-- a toolchain smoke test about a counter mod 3, with nothing to do with the
fixture -- and the case reported 0.50 as though half the work had been done.
A manifest is not proof of a good model either, but it cannot be produced by
scribbling one module while checking that TLC runs.
