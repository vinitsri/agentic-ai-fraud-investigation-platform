#!/usr/bin/env python3
"""Generate synthetic fraud dataset."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from generators.pipeline import run_pipeline  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic fraud data")
    parser.add_argument("--customers", type=int, default=1000)
    parser.add_argument("--transactions", type=int, default=10000)
    parser.add_argument("--merchants", type=int, default=200)
    parser.add_argument("--fraud-rate", type=float, default=0.03)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(ROOT.parent / "database" / "seed" / "generated"),
    )
    parser.add_argument("--load", action="store_true", help="Load into PostgreSQL after generation")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    stats = run_pipeline(
        customers=args.customers,
        transactions=args.transactions,
        merchants=args.merchants,
        fraud_rate=args.fraud_rate,
        seed=args.seed,
        output_dir=output_dir,
    )

    print(f"Generated dataset (seed={args.seed}):")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    if args.load:
        from scripts.load_to_postgres import load_all  # noqa: E402

        counts = load_all(output_dir)
        print("Data loaded into PostgreSQL:")
        for key, value in counts.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
