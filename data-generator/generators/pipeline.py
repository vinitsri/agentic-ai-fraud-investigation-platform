from __future__ import annotations

from pathlib import Path

import pandas as pd

from generators.base import reset_id_generator
from generators.customers import generate_customers
from generators.devices import generate_devices
from generators.login_events import generate_login_events
from generators.merchants import generate_merchants
from generators.transactions import generate_transactions
from scenarios import FRAUD_SCENARIOS, SCENARIO_REGISTRY
from scenarios.base import ScenarioResult


def _export_frames(frames: dict[str, pd.DataFrame], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, df in frames.items():
        if df is not None and not df.empty:
            df.to_csv(output_dir / f"{name}.csv", index=False)


def run_pipeline(
    customers: int,
    transactions: int,
    merchants: int,
    fraud_rate: float,
    seed: int,
    output_dir: Path,
) -> dict[str, int]:
    reset_id_generator(seed)

    merchants_df = generate_merchants(merchants, seed=seed)
    customers_df = generate_customers(customers, seed=seed)
    devices_df, customer_devices_df = generate_devices(customers_df, seed=seed)
    transactions_df = generate_transactions(
        customers_df,
        merchants_df,
        customer_devices_df,
        count=transactions,
        seed=seed,
    )
    login_events_df = generate_login_events(customers_df, customer_devices_df, seed=seed)

    fraud_cases_parts: list[pd.DataFrame] = []
    fraud_alerts_parts: list[pd.DataFrame] = []

    for idx, scenario_name in enumerate(FRAUD_SCENARIOS):
        scenario = SCENARIO_REGISTRY[scenario_name]
        result = scenario.inject(
            customers_df,
            merchants_df,
            devices_df,
            customer_devices_df,
            transactions_df,
            login_events_df,
            seed=seed + 100 + idx,
        )
        transactions_df = result.transactions
        login_events_df = result.login_events
        devices_df = result.devices
        customer_devices_df = result.customer_devices
        if not result.fraud_cases.empty:
            fraud_cases_parts.append(result.fraud_cases)
        if not result.fraud_alerts.empty:
            fraud_alerts_parts.append(result.fraud_alerts)

    fraud_cases_df = (
        pd.concat(fraud_cases_parts, ignore_index=True) if fraud_cases_parts else pd.DataFrame()
    )
    fraud_alerts_df = (
        pd.concat(fraud_alerts_parts, ignore_index=True) if fraud_alerts_parts else pd.DataFrame()
    )

    frames = {
        "merchants": merchants_df,
        "customers": customers_df,
        "devices": devices_df,
        "customer_devices": customer_devices_df,
        "transactions": transactions_df,
        "login_events": login_events_df,
        "fraud_cases": fraud_cases_df,
        "fraud_alerts": fraud_alerts_df,
    }
    _export_frames(frames, output_dir)

    fraud_txn_count = int(transactions_df["is_fraud"].sum()) if not transactions_df.empty else 0
    _ = fraud_rate  # reserved for future weighted scenario sampling

    return {
        "customers": len(customers_df),
        "merchants": len(merchants_df),
        "devices": len(devices_df),
        "transactions": len(transactions_df),
        "login_events": len(login_events_df),
        "fraud_transactions": fraud_txn_count,
        "fraud_alerts": len(fraud_alerts_df),
        "fraud_cases": len(fraud_cases_df),
    }


def run_single_scenario(scenario_type: str, seed: int, output_dir: Path) -> ScenarioResult:
    reset_id_generator(seed)

    merchants_df = generate_merchants(50, seed=seed)
    customers_df = generate_customers(20, seed=seed)
    devices_df, customer_devices_df = generate_devices(customers_df, seed=seed)
    transactions_df = generate_transactions(
        customers_df, merchants_df, customer_devices_df, count=100, seed=seed
    )
    login_events_df = generate_login_events(customers_df, customer_devices_df, seed=seed)

    scenario = SCENARIO_REGISTRY[scenario_type]
    result = scenario.inject(
        customers_df,
        merchants_df,
        devices_df,
        customer_devices_df,
        transactions_df,
        login_events_df,
        seed=seed + 200,
    )

    scenario_dir = output_dir / scenario_type
    frames = {
        "merchants": merchants_df,
        "customers": customers_df,
        "devices": result.devices,
        "customer_devices": result.customer_devices,
        "transactions": result.transactions,
        "login_events": result.login_events,
        "fraud_cases": result.fraud_cases,
        "fraud_alerts": result.fraud_alerts,
    }
    _export_frames(frames, scenario_dir)
    return result
