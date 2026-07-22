from __future__ import annotations

import argparse
import json
from pathlib import Path

from application import AtomicPublisher
from conformance import RealFilesystem


def main() -> int:
    parser = argparse.ArgumentParser(description="Public CLI boundary for the atomic publisher example.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()
    filesystem = RealFilesystem(args.root, args.scenario)
    output = AtomicPublisher(filesystem).publish(filesystem.request())
    args.result.write_text(
        json.dumps(
            {
                "output": output,
                "record": filesystem.project_record(),
                "trace": filesystem.events,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
