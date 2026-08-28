#!/usr/bin/env python3
"""Generate a single reproducible fraud scenario."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from generators.pipeline import run_single_scenario  # noqa: E402
from scenarios import SCENARIO_REGISTRY  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a single fraud scenario")
    parser.add_argument("--type", required=True, choices=list(SCENARIO_REGISTRY.keys()))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(ROOT.parent / "database" / "seed" / "scenarios"),
    )
    parser.add_argument("--load", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    result = run_single_scenario(args.type, seed=args.seed, output_dir=output_dir)

    print(f"Scenario '{args.type}' generated (seed={args.seed})")
    print(f"  transactions: {len(result.transactions)}")
    print(f"  fraud alerts: {len(result.fraud_alerts)}")
    print(f"  fraud cases: {len(result.fraud_cases)}")

    if args.load:
        from scripts.load_to_postgres import load_all  # noqa: E402

        counts = load_all(output_dir / args.type)
        print("Scenario loaded into PostgreSQL:")
        for key, value in counts.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
