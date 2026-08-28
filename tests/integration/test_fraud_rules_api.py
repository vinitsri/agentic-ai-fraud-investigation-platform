import os

import pytest
import requests

FRAUD_SERVICE_URL = os.getenv("FRAUD_SERVICE_URL", "http://localhost:8080")


@pytest.mark.integration
def test_fraud_service_health() -> None:
    try:
        response = requests.get(f"{FRAUD_SERVICE_URL}/api/v1/health", timeout=3)
    except requests.RequestException:
        pytest.skip("fraud-service not running")
    assert response.status_code == 200
    assert response.json()["service"] == "fraud-service"
