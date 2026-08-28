from __future__ import annotations

import pandas as pd

from generators.base import new_id, seeded_faker, seeded_numpy


def generate_customers(count: int, seed: int = 42) -> pd.DataFrame:
    fake = seeded_faker(seed)
    rng = seeded_numpy(seed)

    rows = []
    for _ in range(count):
        account_age_days = int(rng.integers(30, 3650))
        created = fake.date_time_between(start_date=f"-{account_age_days}d", end_date="now")
        avg_amt = round(float(rng.uniform(15, 250)), 2)

        rows.append(
            {
                "customer_id": new_id("CUST"),
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": fake.unique.email(),
                "phone": fake.phone_number()[:20],
                "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=80),
                "account_status": "ACTIVE",
                "account_created_at": created,
                "home_country": fake.country_code(),
                "home_city": fake.city(),
                "home_latitude": round(float(fake.latitude()), 6),
                "home_longitude": round(float(fake.longitude()), 6),
                "avg_transaction_amt": avg_amt,
            }
        )

    return pd.DataFrame(rows)
