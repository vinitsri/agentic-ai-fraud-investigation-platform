from __future__ import annotations

import pandas as pd

from generators.base import new_id, seeded_faker, seeded_numpy


def generate_login_events(
    customers: pd.DataFrame,
    customer_devices: pd.DataFrame,
    seed: int = 42,
) -> pd.DataFrame:
    fake = seeded_faker(seed)
    rng = seeded_numpy(seed)

    device_by_customer = customer_devices.groupby("customer_id")["device_id"].first().to_dict()
    rows = []

    for _, customer in customers.iterrows():
        num_logins = int(rng.integers(3, 15))
        device_id = device_by_customer.get(customer["customer_id"])

        for _ in range(num_logins):
            rows.append(
                {
                    "login_id": new_id("LOGIN"),
                    "customer_id": customer["customer_id"],
                    "device_id": device_id,
                    "ip_address": fake.ipv4(),
                    "latitude": customer["home_latitude"],
                    "longitude": customer["home_longitude"],
                    "city": customer["home_city"],
                    "country": customer["home_country"],
                    "success": True,
                    "failure_reason": None,
                    "created_at": fake.date_time_between(start_date="-60d", end_date="now"),
                }
            )

    return pd.DataFrame(rows)
