"""New device fraud: first-seen device with unusual merchant."""

from __future__ import annotations

from datetime import timedelta

import pandas as pd

from generators.base import new_id, utc_now
from scenarios.base import FraudScenario, ScenarioResult
from scenarios.helpers import append_rows, make_fraud_alert, make_fraud_case, pick_victim


class NewDeviceFraudScenario(FraudScenario):
    name = "new-device-fraud"

    def inject(
        self,
        customers: pd.DataFrame,
        merchants: pd.DataFrame,
        devices: pd.DataFrame,
        customer_devices: pd.DataFrame,
        transactions: pd.DataFrame,
        login_events: pd.DataFrame,
        seed: int,
    ) -> ScenarioResult:
        victim = pick_victim(customers, seed + 4)
        cust_id = victim["customer_id"]
        now = utc_now()

        new_device = {
            "device_id": new_id("DEV"),
            "device_type": "MOBILE",
            "os": "Android",
            "browser": "Chrome Mobile",
            "fingerprint_hash": f"fp-{seed}-newdev",
            "first_seen_at": now - timedelta(minutes=2),
            "last_seen_at": now,
            "is_trusted": False,
        }

        risky_merchant = merchants[merchants["risk_score"] > 0.6].sample(1, random_state=seed).iloc[0]
        amount = round(float(victim["avg_transaction_amt"]) * 6, 2)

        fraud_txn = {
            "transaction_id": new_id("TXN"),
            "customer_id": cust_id,
            "merchant_id": risky_merchant["merchant_id"],
            "device_id": new_device["device_id"],
            "amount": amount,
            "currency": "USD",
            "status": "COMPLETED",
            "transaction_type": "PURCHASE",
            "merchant_category": risky_merchant["category_code"],
            "ip_address": "203.0.113.88",
            "latitude": victim["home_latitude"],
            "longitude": victim["home_longitude"],
            "city": victim["home_city"],
            "country": victim["home_country"],
            "is_fraud": True,
            "fraud_scenario": self.name,
            "created_at": now,
        }

        alert = make_fraud_alert(fraud_txn["transaction_id"], cust_id, "HIGH")
        case = make_fraud_case(
            cust_id,
            f"New Device Fraud - {cust_id}",
            "High-value purchase from previously unseen device at high-risk merchant.",
            "NEW_DEVICE_FRAUD",
            amount,
        )

        return ScenarioResult(
            name=self.name,
            transactions=append_rows(transactions, [fraud_txn]),
            login_events=login_events,
            devices=append_rows(devices, [new_device]),
            customer_devices=customer_devices,
            fraud_cases=pd.DataFrame([case]),
            fraud_alerts=pd.DataFrame([alert]),
        )
