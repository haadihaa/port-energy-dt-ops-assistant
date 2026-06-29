from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_route_smoke():
    response = client.get("/")
    assert response.status_code == 200
    assert "Port Energy Digital Twin Ops Assistant" in response.text


def test_scenarios_route_smoke():
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "scenario_id" in data[0]


def test_evaluate_custom_valid():
    payload = {
        "critical_load_kw": 40,
        "vessel_load_kw": 60,
        "other_load_kw": 0,
        "solar_kw": 10,
        "battery_charge_kwh": 5,
        "battery_max_kwh": 100,
        "grid_available": False,
        "backup_generator_kw": 20,
        "description": "Custom constrained scenario"
    }
    response = client.post("/api/evaluate-custom", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["scenario_id"] == "custom"
    assert "status" in data
    assert "summary" in data


def test_evaluate_custom_invalid_battery():
    payload = {
        "critical_load_kw": 40,
        "vessel_load_kw": 60,
        "other_load_kw": 0,
        "solar_kw": 10,
        "battery_charge_kwh": 120,
        "battery_max_kwh": 100,
        "grid_available": False,
        "backup_generator_kw": 20,
        "description": "Invalid battery scenario"
    }
    response = client.post("/api/evaluate-custom", json=payload)
    assert response.status_code == 422