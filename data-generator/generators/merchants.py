from __future__ import annotations

import pandas as pd

from generators.base import MCC_CATEGORIES, new_id, seeded_faker, seeded_numpy


def generate_merchants(count: int, seed: int = 42) -> pd.DataFrame:
    fake = seeded_faker(seed)
    rng = seeded_numpy(seed)

    rows = []
    for i in range(count):
        mcc_code, mcc_name, base_risk = MCC_CATEGORIES[i % len(MCC_CATEGORIES)]
        risk = round(float(min(1.0, max(0.0, base_risk + rng.uniform(-0.1, 0.1)))), 4)
        rows.append(
            {
                "merchant_id": new_id("MER"),
                "name": fake.company(),
                "category_code": mcc_code,
                "category_name": mcc_name,
                "risk_score": risk,
                "country": fake.country_code(),
            }
        )

    return pd.DataFrame(rows)
