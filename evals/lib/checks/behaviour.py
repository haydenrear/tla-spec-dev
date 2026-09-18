"""Does the program still do what its model says? EXIT CODE ONLY.

This module is executed with agent-authored code on its import path, so it is
run under `checks/nowrite.sb`, which denies every filesystem write. It
therefore CANNOT record its own verdict -- and that is the point. The verdict
is written by the hook, from this process's exit status, outside the sandbox.

Exit 0  the account survives into snapshot()
Exit 1  it does not, or the program could not be exercised at all
"""

from __future__ import annotations

import pathlib
import sys


def main() -> int:
    if not pathlib.Path("ecommerce_backend/domain.py").is_file():
        print("no ecommerce_backend/domain.py")
        return 1

    # A plain import, not spec_from_file_location: loading by path without
    # registering in sys.modules makes @dataclass die on
    # sys.modules[cls.__module__].__dict__, which once withheld the verdict for
    # the VERIFIER's bug from a workspace that may have been repaired.
    sys.path.insert(0, str(pathlib.Path.cwd()))
    try:
        from ecommerce_backend.domain import EcommerceStore
    except Exception as exc:
        print(f"domain.py does not import: {exc!r}")
        return 1

    try:
        backend = EcommerceStore()
        backend.create_account("acct-eval")
        snapshot = backend.snapshot()
    except Exception as exc:
        print(f"exercising the backend raised: {exc!r}")
        return 1

    if "acct-eval" not in repr(snapshot):
        print("create_account did not persist: the account is absent from snapshot()")
        return 1

    print("behaviour ok: the account survives into snapshot()")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
