import os

import psycopg2
import pytest

TABLES = [
    "customers",
    "transactions",
    "devices",
    "merchants",
    "login_events",
    "fraud_alerts",
    "fraud_cases",
    "investigation_reports",
    "agent_runs",
    "analyst_decisions",
]


@pytest.fixture
def db_conn():
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            dbname=os.getenv("POSTGRES_DB", "fraud_platform"),
            user=os.getenv("POSTGRES_USER", "fraud_user"),
            password=os.getenv("POSTGRES_PASSWORD", "change_me_in_production"),
        )
    except psycopg2.OperationalError:
        pytest.skip("PostgreSQL not available")
    yield conn
    conn.close()


@pytest.mark.integration
def test_all_tables_exist(db_conn) -> None:
    with db_conn.cursor() as cur:
        for table in TABLES:
            cur.execute(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)",
                (table,),
            )
            assert cur.fetchone()[0], f"Table {table} missing"


@pytest.mark.integration
def test_pgvector_extension(db_conn) -> None:
    with db_conn.cursor() as cur:
        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        row = cur.fetchone()
        assert row is not None
        assert row[0] == "vector"
