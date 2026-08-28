"""Fraud ring: same device used across multiple customers."""

from __future__ import annotations

import pandas as pd

from generators.base import new_id, utc_now
from scenarios.base import FraudScenario, ScenarioResult
from scenarios.helpers import append_rows, make_fraud_alert, make_fraud_case


class FraudRingScenario(FraudScenario):
    name = "fraud-ring"

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
        ring_customers = customers.sample(6, random_state=seed + 6)
        now = utc_now()

        shared_device = {
            "device_id": new_id("DEV"),
            "device_type": "DESKTOP",
            "os": "Windows",
            "browser": "Chrome",
            "fingerprint_hash": f"fp-{seed}-ring",
            "first_seen_at": now,
            "last_seen_at": now,
            "is_trusted": False,
        }

        fraud_txns = []
        alerts = []
        links = []
        total_loss = 0.0

        for i, (_, customer) in enumerate(ring_customers.iterrows()):
            cust_id = customer["customer_id"]
            merchant = merchants.sample(1, random_state=seed + i).iloc[0]
            amount = round(float(800 + i * 200), 2)
            total_loss += amount
            txn_id = new_id("TXN")

            links.append(
                {
                    "customer_id": cust_id,
                    "device_id": shared_device["device_id"],
                    "first_associated_at": now,
                    "last_used_at": now,
                    "is_primary": False,
                }
            )

            fraud_txns.append(
                {
                    "transaction_id": txn_id,
                    "customer_id": cust_id,
                    "merchant_id": merchant["merchant_id"],
                    "device_id": shared_device["device_id"],
                    "amount": amount,
                    "currency": "USD",
                    "status": "COMPLETED",
                    "transaction_type": "PURCHASE",
                    "merchant_category": merchant["category_code"],
                    "ip_address": "192.0.2.100",
                    "latitude": 51.5074,
                    "longitude": -0.1278,
                    "city": "London",
                    "country": "GB",
                    "is_fraud": True,
                    "fraud_scenario": self.name,
                    "created_at": now,
                }
            )
            alerts.append(make_fraud_alert(txn_id, cust_id, "CRITICAL"))

        case = make_fraud_case(
            ring_customers.iloc[0]["customer_id"],
            "Fraud Ring - Shared Device",
            "Same device fingerprint associated with 6 different customers making high-value purchases.",
            "FRAUD_RING",
            total_loss,
        )

        return ScenarioResult(
            name=self.name,
            transactions=append_rows(transactions, fraud_txns),
            login_events=login_events,
            devices=append_rows(devices, [shared_device]),
            customer_devices=append_rows(customer_devices, links),
            fraud_cases=pd.DataFrame([case]),
            fraud_alerts=pd.DataFrame(alerts),
        )
