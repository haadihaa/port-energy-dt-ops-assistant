from fastapi import Request
from app.main import read_root, health_check, list_scenarios, get_scenario, evaluate_scenario_endpoint

def mock_request(method: str = "GET", path: str = "/") -> Request:
    """Helper to construct a minimal mock Starlette Request object."""
    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "headers": [],
    }
    return Request(scope)

def test_read_root():
    """Verify that the root route successfully returns the TemplateResponse."""
    req = mock_request("GET", "/")
    response = read_root(req)
    assert response.status_code == 200
    assert response.template.name == "index.html"

def test_health_check():
    """Verify the health endpoint response."""
    result = health_check()
    assert result == {"status": "healthy", "service": "port-energy-ops-assistant"}

def test_list_scenarios():
    """Verify scenarios can be listed from memory."""
    scenarios = list_scenarios()
    assert isinstance(scenarios, list)
    assert len(scenarios) > 0
    assert "scenario_id" in scenarios[0]

def test_get_scenario():
    """Verify retrieving a single scenario works and raises 404 for missing ones."""
    scenarios = list_scenarios()
    first_id = scenarios[0]["scenario_id"]
    
    scenario = get_scenario(first_id)
    assert scenario.scenario_id == first_id

def test_evaluate_scenario():
    """Verify the evaluation workflow runs successfully via the endpoint function."""
    scenarios = list_scenarios()
    first_id = scenarios[0]["scenario_id"]
    
    result = evaluate_scenario_endpoint(first_id)
    assert result.scenario_id == first_id
    assert result.status in ["success", "unmet_critical_load", "safety_failure"]
    assert result.recommendation is not None
