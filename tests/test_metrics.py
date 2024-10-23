# tests/test_metrics.py
import pytest
from datetime import datetime

def test_create_metric(client):
    payload = {
        "service": "test_service",
        "metric_type": "CPU",
        "value": 75.5,
        "timestamp": "2024-10-22 12:00:00"
    }
    response = client.post("/metrics/", json=payload)
    assert response.status_code == 201

def test_get_metrics(client):
    # First create a test metric
    payload = {
        "service": "test_service",
        "metric_type": "CPU",
        "value": 75.5,
        "timestamp": "2024-10-22 12:00:00"
    }
    client.post("/metrics/", json=payload)
    
    response = client.get("/metrics/test_service")
    assert response.status_code == 200
    metrics = response.get_json()
    assert isinstance(metrics, list)
    assert len(metrics) > 0