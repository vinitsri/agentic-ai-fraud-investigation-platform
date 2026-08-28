import pandas as pd

from generators.customers import generate_customers
from generators.devices import generate_devices
from generators.login_events import generate_login_events
from generators.merchants import generate_merchants
from generators.transactions import generate_transactions
from scenarios.account_takeover import AccountTakeoverScenario


def test_account_takeover_injects_fraud() -> None:
    customers = generate_customers(10, seed=42)
    merchants = generate_merchants(20, seed=42)
    devices, customer_devices = generate_devices(customers, seed=42)
    transactions = generate_transactions(customers, merchants, customer_devices, count=100, seed=42)
    login_events = generate_login_events(customers, customer_devices, seed=42)

    scenario = AccountTakeoverScenario()
    result = scenario.inject(
        customers, merchants, devices, customer_devices, transactions, login_events, seed=42
    )

    fraud_txns = result.transactions[result.transactions["is_fraud"] == True]  # noqa: E712
    assert len(fraud_txns) >= 1
    assert fraud_txns.iloc[-1]["fraud_scenario"] == "account-takeover"
    assert len(result.fraud_alerts) == 1
    assert len(result.fraud_cases) == 1


def test_all_scenarios_registered() -> None:
    from scenarios import FRAUD_SCENARIOS, SCENARIO_REGISTRY

    assert len(FRAUD_SCENARIOS) == 7
    assert "normal" in SCENARIO_REGISTRY
    assert "fraud-ring" in SCENARIO_REGISTRY
