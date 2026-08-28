"""High-value fraud: transaction amount far exceeds customer average."""

from __future__ import annotations

import pandas as pd

from generators.base import new_id, seeded_numpy, utc_now
from scenarios.base import FraudScenario, ScenarioResult
from scenarios.helpers import append_rows, make_fraud_alert, make_fraud_case, pick_victim


class HighValueFraudScenario(FraudScenario):
    name = "high-value-fraud"

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
        rng = seeded_numpy(seed)
        victim = pick_victim(customers, seed)
        cust_id = victim["customer_id"]
        device_id = customer_devices[customer_devices["customer_id"] == cust_id]["device_id"].iloc[0]
        merchant = merchants[merchants["risk_score"] > 0.5].sample(1, random_state=seed).iloc[0]
        now = utc_now()
        amount = round(float(rng.uniform(5000, 15000)), 2)

        fraud_txn = {
            "transaction_id": new_id("TXN"),
            "customer_id": cust_id,
            "merchant_id": merchant["merchant_id"],
            "device_id": device_id,
            "amount": amount,
            "currency": "USD",
            "status": "COMPLETED",
            "transaction_type": "PURCHASE",
            "merchant_category": merchant["category_code"],
            "ip_address": "198.51.100.10",
            "latitude": victim["home_latitude"],
            "longitude": victim["home_longitude"],
            "city": victim["home_city"],
            "country": victim["home_country"],
            "is_fraud": True,
            "fraud_scenario": self.name,
            "created_at": now,
        }

        alert = make_fraud_alert(fraud_txn["transaction_id"], cust_id, "CRITICAL")
        case = make_fraud_case(
            cust_id,
            f"High Value Fraud - {cust_id}",
            f"Transaction of ${amount} exceeds customer average of ${victim['avg_transaction_amt']}.",
            "HIGH_VALUE_FRAUD",
            amount,
        )

        return ScenarioResult(
            name=self.name,
            transactions=append_rows(transactions, [fraud_txn]),
            login_events=login_events,
            devices=devices,
            customer_devices=customer_devices,
            fraud_cases=pd.DataFrame([case]),
            fraud_alerts=pd.DataFrame([alert]),
        )
