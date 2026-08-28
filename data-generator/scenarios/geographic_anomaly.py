"""Geographic anomaly: transaction far from customer's home location."""

from __future__ import annotations

import pandas as pd

from generators.base import new_id, utc_now
from scenarios.base import FraudScenario, ScenarioResult
from scenarios.helpers import append_rows, make_fraud_alert, make_fraud_case, pick_victim


class GeographicAnomalyScenario(FraudScenario):
    name = "geographic-anomaly"

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
        victim = pick_victim(customers, seed + 3)
        cust_id = victim["customer_id"]
        device_id = customer_devices[customer_devices["customer_id"] == cust_id]["device_id"].iloc[0]
        merchant = merchants.sample(1, random_state=seed).iloc[0]
        now = utc_now()
        amount = round(float(victim["avg_transaction_amt"]) * 4, 2)

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
            "ip_address": "198.18.0.99",
            "latitude": -33.8688,
            "longitude": 151.2093,
            "city": "Sydney",
            "country": "AU",
            "is_fraud": True,
            "fraud_scenario": self.name,
            "created_at": now,
        }

        alert = make_fraud_alert(fraud_txn["transaction_id"], cust_id, "HIGH")
        case = make_fraud_case(
            cust_id,
            f"Geographic Anomaly - {cust_id}",
            f"Transaction in Sydney, AU while customer home is {victim['home_city']}, {victim['home_country']}.",
            "GEOGRAPHIC_ANOMALY",
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
