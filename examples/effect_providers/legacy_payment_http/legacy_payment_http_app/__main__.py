from __future__ import annotations

import argparse
import json

from .application import authorize_payment


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--payment-id", required=True)
    parser.add_argument("--amount", required=True, type=int)
    parser.add_argument("--idempotency-key", required=True)
    parser.add_argument("--base-url", required=True)
    args = parser.parse_args()
    result = authorize_payment(
        payment_id=args.payment_id,
        amount=args.amount,
        idempotency_key=args.idempotency_key,
        base_url=args.base_url,
    )
    print(json.dumps(result.as_dict(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

