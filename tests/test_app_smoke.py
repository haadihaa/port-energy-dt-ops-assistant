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