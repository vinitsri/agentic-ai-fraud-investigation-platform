from __future__ import annotations

import pandas as pd

from generators.base import new_id, seeded_faker, seeded_numpy, utc_now


def generate_devices(
    customers: pd.DataFrame, seed: int = 42
) -> tuple[pd.DataFrame, pd.DataFrame]:
    fake = seeded_faker(seed)
    rng = seeded_numpy(seed)

    device_rows = []
    link_rows = []

    device_types = ["MOBILE", "DESKTOP", "TABLET"]
    os_options = {"MOBILE": ["iOS", "Android"], "DESKTOP": ["Windows", "macOS"], "TABLET": ["iOS", "Android"]}
    browsers = {"MOBILE": ["Safari Mobile", "Chrome Mobile"], "DESKTOP": ["Chrome", "Firefox", "Safari"]}

    for _, customer in customers.iterrows():
        num_devices = int(rng.integers(2, 5))
        for idx in range(num_devices):
            device_type = device_types[int(rng.integers(0, len(device_types)))]
            os_name = os_options[device_type][int(rng.integers(0, len(os_options[device_type])))]
            browser = browsers.get(device_type, [None])[0] if device_type != "TABLET" else "Safari"
            first_seen = fake.date_time_between(
                start_date=customer["account_created_at"], end_date="now"
            )
            device_id = new_id("DEV")

            device_rows.append(
                {
                    "device_id": device_id,
                    "device_type": device_type,
                    "os": os_name,
                    "browser": browser,
                    "fingerprint_hash": fake.sha256()[:64],
                    "first_seen_at": first_seen,
                    "last_seen_at": utc_now(),
                    "is_trusted": idx == 0,
                }
            )

            link_rows.append(
                {
                    "customer_id": customer["customer_id"],
                    "device_id": device_id,
                    "first_associated_at": first_seen,
                    "last_used_at": utc_now(),
                    "is_primary": idx == 0,
                }
            )

    return pd.DataFrame(device_rows), pd.DataFrame(link_rows)
