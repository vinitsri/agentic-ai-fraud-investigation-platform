"""Load generated CSV files into PostgreSQL."""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

TABLE_ORDER = [
    "merchants",
    "customers",
    "devices",
    "customer_devices",
    "transactions",
    "login_events",
    "fraud_cases",
    "fraud_alerts",
]


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "fraud_platform"),
        user=os.getenv("POSTGRES_USER", "fraud_user"),
        password=os.getenv("POSTGRES_PASSWORD", "change_me_in_production"),
    )


def _clean_value(value):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    return value


def load_csv(conn, table: str, csv_path: Path) -> int:
    if not csv_path.exists():
        return 0

    df = pd.read_csv(csv_path, keep_default_na=False, na_values=[""])
    if df.empty:
        return 0

    df = df.where(pd.notnull(df), None)
    cols = ", ".join(df.columns)
    placeholders = ", ".join(["%s"] * len(df.columns))
    sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"

    rows = [tuple(_clean_value(v) for v in row) for row in df.itertuples(index=False, name=None)]

    with conn.cursor() as cur:
        for row in rows:
            cur.execute(sql, row)
    conn.commit()
    return len(rows)


def load_all(data_dir: Path) -> dict[str, int]:
    conn = get_connection()
    counts: dict[str, int] = {}
    try:
        for table in TABLE_ORDER:
            counts[table] = load_csv(conn, table, data_dir / f"{table}.csv")
    finally:
        conn.close()
    return counts


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "data_dir",
        nargs="?",
        default=str(Path(__file__).resolve().parents[2] / "database" / "seed" / "generated"),
    )
    cli_args = parser.parse_args()
    results = load_all(Path(cli_args.data_dir))
    for table, count in results.items():
        print(f"{table}: {count}")
