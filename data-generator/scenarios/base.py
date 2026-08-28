from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import pandas as pd


@dataclass
class ScenarioResult:
    name: str
    transactions: pd.DataFrame
    login_events: pd.DataFrame
    devices: pd.DataFrame
    customer_devices: pd.DataFrame
    fraud_cases: pd.DataFrame
    fraud_alerts: pd.DataFrame
    extra_customers: pd.DataFrame = field(default_factory=pd.DataFrame)
    extra_merchants: pd.DataFrame = field(default_factory=pd.DataFrame)


class FraudScenario(ABC):
    name: str

    @abstractmethod
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
        ...
