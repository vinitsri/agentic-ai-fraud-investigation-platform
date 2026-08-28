"""Failed login attack: many failed attempts without successful transaction."""

from __future__ import annotations

from datetime import timedelta

import pandas as pd

from generators.base import new_id, utc_now
from scenarios.base import FraudScenario, ScenarioResult
from scenarios.helpers import append_rows, make_fraud_alert, make_fraud_case, pick_victim


class FailedLoginAttackScenario(FraudScenario):
    name = "failed-login-attack"

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
        victim = pick_victim(customers, seed + 5)
        cust_id = victim["customer_id"]
        now = utc_now()

        failed_logins = []
        for i in range(20):
            failed_logins.append(
                {
                    "login_id": new_id("LOGIN"),
                    "customer_id": cust_id,
                    "device_id": None,
                    "ip_address": f"198.51.100.{i + 1}",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "city": "New York",
                    "country": "US",
                    "success": False,
                    "failure_reason": "INVALID_PASSWORD",
                    "created_at": now - timedelta(minutes=30 - i),
                }
            )

        case = make_fraud_case(
            cust_id,
            f"Failed Login Attack - {cust_id}",
            "20 failed login attempts from rotating IPs within 30 minutes.",
            "FAILED_LOGIN_ATTACK",
            0.0,
        )

        return ScenarioResult(
            name=self.name,
            transactions=transactions,
            login_events=append_rows(login_events, failed_logins),
            devices=devices,
            customer_devices=customer_devices,
            fraud_cases=pd.DataFrame([case]),
            fraud_alerts=pd.DataFrame(),
        )
