"""Account takeover: failed logins, new device, foreign high-value transaction."""

from __future__ import annotations

from datetime import timedelta

import pandas as pd

from generators.base import new_id, seeded_numpy, utc_now
from scenarios.base import FraudScenario, ScenarioResult
from scenarios.helpers import append_rows, make_fraud_alert, make_fraud_case, pick_victim


class AccountTakeoverScenario(FraudScenario):
    name = "account-takeover"

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
        victim = pick_victim(customers, seed + 1)
        cust_id = victim["customer_id"]
        now = utc_now()

        failed_logins = []
        for i in range(5):
            failed_logins.append(
                {
                    "login_id": new_id("LOGIN"),
                    "customer_id": cust_id,
                    "device_id": None,
                    "ip_address": "203.0.113.55",
                    "latitude": 48.8566,
                    "longitude": 2.3522,
                    "city": "Paris",
                    "country": "FR",
                    "success": False,
                    "failure_reason": "INVALID_PASSWORD",
                    "created_at": now - timedelta(minutes=10 - i),
                }
            )

        atk_device = {
            "device_id": new_id("DEV"),
            "device_type": "MOBILE",
            "os": "Android",
            "browser": "Chrome Mobile",
            "fingerprint_hash": f"fp-{seed}-ato",
            "first_seen_at": now - timedelta(minutes=5),
            "last_seen_at": now,
            "is_trusted": False,
        }

        success_login = {
            "login_id": new_id("LOGIN"),
            "customer_id": cust_id,
            "device_id": atk_device["device_id"],
            "ip_address": "203.0.113.55",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "city": "Paris",
            "country": "FR",
            "success": True,
            "failure_reason": None,
            "created_at": now - timedelta(minutes=3),
        }

        high_risk_merchant = merchants[merchants["risk_score"] > 0.7].sample(1, random_state=seed).iloc[0]
        amount = round(float(rng.uniform(2000, 8000)), 2)
        fraud_txn = {
            "transaction_id": new_id("TXN"),
            "customer_id": cust_id,
            "merchant_id": high_risk_merchant["merchant_id"],
            "device_id": atk_device["device_id"],
            "amount": amount,
            "currency": "USD",
            "status": "COMPLETED",
            "transaction_type": "PURCHASE",
            "merchant_category": high_risk_merchant["category_code"],
            "ip_address": "203.0.113.55",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "city": "Paris",
            "country": "FR",
            "is_fraud": True,
            "fraud_scenario": self.name,
            "created_at": now,
        }

        alert = make_fraud_alert(fraud_txn["transaction_id"], cust_id, "CRITICAL")
        case = make_fraud_case(
            cust_id,
            f"Account Takeover - {cust_id}",
            "Multiple failed logins followed by login from new device in foreign location.",
            "ACCOUNT_TAKEOVER",
            amount,
        )

        return ScenarioResult(
            name=self.name,
            transactions=append_rows(transactions, [fraud_txn]),
            login_events=append_rows(login_events, failed_logins + [success_login]),
            devices=append_rows(devices, [atk_device]),
            customer_devices=customer_devices,
            fraud_cases=pd.DataFrame([case]),
            fraud_alerts=pd.DataFrame([alert]),
        )
