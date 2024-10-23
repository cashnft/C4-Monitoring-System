# tests/test_logs.py
import pytest
from datetime import datetime

def test_create_log(client):
    payload = {
        "service": "test_service",
        "level": "INFO",
        "message": "This is a test log message",
        "timestamp": "2024-10-22 12:00:00"
    }
    response = client.post("/logs/", json=payload)
    assert response.status_code == 201

def test_get_logs(client):
    # First create a test log
    payload = {
        "service": "test_service",
        "level": "INFO",
        "message": "This is a test log message",
        "timestamp": "2024-10-22 12:00:00"
    }
    client.post("/logs/", json=payload)
    
    response = client.get("/logs/test_service")
    assert response.status_code == 200
    logs = response.get_json()
    assert isinstance(logs, list)
    assert len(logs) > 0