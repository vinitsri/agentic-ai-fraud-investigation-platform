from __future__ import annotations

import uuid
from datetime import datetime, timezone

import numpy as np
from faker import Faker


_id_counter = 0
_id_seed = 42


def reset_id_generator(seed: int) -> None:
    """Reset deterministic ID sequence for reproducible datasets."""
    global _id_counter, _id_seed
    _id_counter = 0
    _id_seed = seed


def new_id(prefix: str) -> str:
    global _id_counter
    _id_counter += 1
    token = uuid.uuid5(uuid.NAMESPACE_DNS, f"{_id_seed}:{prefix}:{_id_counter}").hex[:12].upper()
    return f"{prefix}-{token}"


def seeded_faker(seed: int) -> Faker:
    fake = Faker(["en_US", "en_GB", "en_CA"])
    Faker.seed(seed)
    return fake


def seeded_numpy(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


MCC_CATEGORIES = [
    ("5411", "Grocery Stores", 0.1),
    ("5812", "Restaurants", 0.15),
    ("5814", "Fast Food", 0.12),
    ("5541", "Gas Stations", 0.2),
    ("5311", "Department Stores", 0.18),
    ("5732", "Electronics", 0.35),
    ("5999", "Misc Retail", 0.25),
    ("6011", "ATM Cash", 0.45),
    ("4829", "Money Transfer", 0.75),
    ("7995", "Gambling", 0.85),
    ("5944", "Jewelry", 0.55),
    ("4111", "Transportation", 0.2),
]
