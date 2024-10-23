# tests/test_traces.py
import pytest
from datetime import datetime

def test_create_trace(client):
    payload = {
        "trace_id": "abc123",
        "service": "test_service",
        "operation": "test_operation",
        "duration": 15.5,
        "timestamp": "2024-10-22 12:00:00"
    }
    response = client.post("/traces/", json=payload)
    assert response.status_code == 201

def test_get_trace(client):
    # First create a test trace
    payload = {
        "trace_id": "abc123",
        "service": "test_service",
        "operation": "test_operation",
        "duration": 15.5,
        "timestamp": "2024-10-22 12:00:00"
    }
    client.post("/traces/", json=payload)
    
    response = client.get("/traces/abc123")
    assert response.status_code == 200
    traces = response.get_json()
    assert isinstance(traces, list)
    assert len(traces) > 0