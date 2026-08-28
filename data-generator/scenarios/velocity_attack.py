"""Velocity attack: many transactions in a short time window."""

from __future__ import annotations

from datetime import timedelta

import pandas as pd

from generators.base import new_id, utc_now
from scenarios.base import FraudScenario, ScenarioResult
from scenarios.helpers import append_rows, make_fraud_alert, make_fraud_case, pick_victim


class VelocityAttackScenario(FraudScenario):
    name = "velocity-attack"

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
        victim = pick_victim(customers, seed + 2)
        cust_id = victim["customer_id"]
        device_id = customer_devices[customer_devices["customer_id"] == cust_id]["device_id"].iloc[0]
        now = utc_now()

        fraud_txns = []
        alerts = []
        total_amount = 0.0

        for i in range(12):
            merchant = merchants.sample(1, random_state=seed + i).iloc[0]
            amount = round(float(150 + i * 25), 2)
            total_amount += amount
            txn_id = new_id("TXN")
            fraud_txns.append(
                {
                    "transaction_id": txn_id,
                    "customer_id": cust_id,
                    "merchant_id": merchant["merchant_id"],
                    "device_id": device_id,
                    "amount": amount,
                    "currency": "USD",
                    "status": "COMPLETED",
                    "transaction_type": "PURCHASE",
                    "merchant_category": merchant["category_code"],
                    "ip_address": "192.0.2.50",
                    "latitude": victim["home_latitude"],
                    "longitude": victim["home_longitude"],
                    "city": victim["home_city"],
                    "country": victim["home_country"],
                    "is_fraud": True,
                    "fraud_scenario": self.name,
                    "created_at": now - timedelta(minutes=5 - i // 3),
                }
            )
            alerts.append(make_fraud_alert(txn_id, cust_id, "HIGH"))

        case = make_fraud_case(
            cust_id,
            f"Velocity Attack - {cust_id}",
            "12 transactions within 5 minutes indicating card testing or automated fraud.",
            "VELOCITY_ATTACK",
            total_amount,
        )

        return ScenarioResult(
            name=self.name,
            transactions=append_rows(transactions, fraud_txns),
            login_events=login_events,
            devices=devices,
            customer_devices=customer_devices,
            fraud_cases=pd.DataFrame([case]),
            fraud_alerts=pd.DataFrame(alerts),
        )
