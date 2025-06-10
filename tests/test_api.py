import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_sales_forecast_success():
    payload = {
        "history": [
            {"date": "2024-01-01", "total": 100},
            {"date": "2024-01-02", "total": 120},
            {"date": "2024-01-03", "total": 130},
        ]
    }
    response = client.post("/forecast", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 7
    assert all("ds" in item and "yhat" in item for item in data)


def test_forecast_invalid_input():
    payload = {"history": [{"total": 100}, {"total": 200}]}
    response = client.post("/forecast", json=payload)
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
