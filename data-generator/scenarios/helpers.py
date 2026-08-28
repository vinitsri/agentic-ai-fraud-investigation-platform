from __future__ import annotations

from datetime import timedelta

import pandas as pd

from generators.base import new_id, utc_now


def make_fraud_alert(
    transaction_id: str,
    customer_id: str,
    severity: str = "HIGH",
) -> dict:
    now = utc_now()
    return {
        "alert_id": new_id("ALERT"),
        "transaction_id": transaction_id,
        "customer_id": customer_id,
        "status": "OPEN",
        "severity": severity,
        "rule_triggered": None,
        "ml_fraud_probability": None,
        "triggered_at": now,
        "resolved_at": None,
    }


def make_fraud_case(
    customer_id: str,
    title: str,
    description: str,
    fraud_type: str,
    amount: float,
) -> dict:
    now = utc_now()
    return {
        "case_id": new_id("CASE"),
        "customer_id": customer_id,
        "title": title,
        "description": description,
        "fraud_type": fraud_type,
        "status": "CONFIRMED",
        "total_loss_amount": amount,
        "currency": "USD",
        "resolution_notes": "Synthetic historical case for RAG and investigation reference.",
        "detected_at": now,
        "resolved_at": now + timedelta(days=2),
    }


def pick_victim(customers: pd.DataFrame, seed: int) -> pd.Series:
    return customers.sample(1, random_state=seed).iloc[0]


def append_rows(df: pd.DataFrame, rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return df
    return pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
