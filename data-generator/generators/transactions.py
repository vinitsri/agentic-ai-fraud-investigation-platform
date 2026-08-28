from __future__ import annotations

import pandas as pd

from generators.base import new_id, seeded_faker, seeded_numpy


def generate_transactions(
    customers: pd.DataFrame,
    merchants: pd.DataFrame,
    customer_devices: pd.DataFrame,
    count: int,
    seed: int = 42,
) -> pd.DataFrame:
    fake = seeded_faker(seed)
    rng = seeded_numpy(seed)

    device_by_customer = customer_devices.groupby("customer_id")["device_id"].first().to_dict()

    rows = []
    for _ in range(count):
        customer = customers.sample(1, random_state=int(rng.integers(0, 2**31))).iloc[0]
        merchant = merchants.sample(1, random_state=int(rng.integers(0, 2**31))).iloc[0]
        device_id = device_by_customer.get(customer["customer_id"])

        avg = float(customer["avg_transaction_amt"])
        amount = round(float(rng.lognormal(mean=max(0.5, avg / 100), sigma=0.5)), 2)
        amount = min(max(amount, 1.0), avg * 3)

        txn_time = fake.date_time_between(start_date="-90d", end_date="now")

        rows.append(
            {
                "transaction_id": new_id("TXN"),
                "customer_id": customer["customer_id"],
                "merchant_id": merchant["merchant_id"],
                "device_id": device_id,
                "amount": amount,
                "currency": "USD",
                "status": "COMPLETED",
                "transaction_type": "PURCHASE",
                "merchant_category": merchant["category_code"],
                "ip_address": fake.ipv4(),
                "latitude": customer["home_latitude"],
                "longitude": customer["home_longitude"],
                "city": customer["home_city"],
                "country": customer["home_country"],
                "is_fraud": False,
                "fraud_scenario": None,
                "created_at": txn_time,
            }
        )

    return pd.DataFrame(rows)
