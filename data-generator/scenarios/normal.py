"""Normal baseline scenario - no fraud injection."""

from __future__ import annotations

import pandas as pd

from scenarios.base import FraudScenario, ScenarioResult


class NormalScenario(FraudScenario):
    name = "normal"

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
        return ScenarioResult(
            name=self.name,
            transactions=transactions,
            login_events=login_events,
            devices=devices,
            customer_devices=customer_devices,
            fraud_cases=pd.DataFrame(),
            fraud_alerts=pd.DataFrame(),
        )
