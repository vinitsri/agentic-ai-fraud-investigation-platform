from generators.base import reset_id_generator
from generators.customers import generate_customers
from generators.pipeline import run_pipeline


def test_same_seed_produces_same_customers() -> None:
    reset_id_generator(42)
    df1 = generate_customers(100, seed=42)
    reset_id_generator(42)
    df2 = generate_customers(100, seed=42)
    assert df1.equals(df2)


def test_different_seed_produces_different_data() -> None:
    df1 = generate_customers(100, seed=42)
    df2 = generate_customers(100, seed=99)
    assert not df1.equals(df2)


def test_pipeline_stats(tmp_path) -> None:
    stats = run_pipeline(
        customers=50,
        transactions=500,
        merchants=20,
        fraud_rate=0.05,
        seed=42,
        output_dir=tmp_path,
    )
    assert stats["customers"] == 50
    assert stats["transactions"] >= 500
    assert stats["fraud_transactions"] > 0
    assert (tmp_path / "customers.csv").exists()
