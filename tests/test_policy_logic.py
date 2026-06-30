import pytest
from fastapi import Request

from app.main import (
    read_root,
    health_check,
    list_scenarios,
    get_scenario,
    evaluate_scenario_endpoint,
    evaluate_custom_scenario,
    CustomScenarioRequest,
)

VALID_STATUSES = [
    "success",
    "unmet_critical_load",
    "safety_failure",
    "insufficient_information",
    "emergency_action_required",
    "supervisor_action_required",
]


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
    """Verify retrieving a single scenario works."""
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
    assert result.status in VALID_STATUSES
    assert result.recommendation is not None or result.status == "insufficient_information"


def test_evaluate_custom_scenario():
    """Verify the custom evaluation workflow runs successfully."""
    payload = CustomScenarioRequest(
        critical_load_kw=40,
        vessel_load_kw=60,
        other_load_kw=0,
        solar_kw=10,
        battery_charge_kwh=5,
        battery_max_kwh=100,
        grid_available=False,
        backup_generator_capacity_kw=20,
        backup_running_percentage=30,
        description="Custom constrained scenario",
    )

    result = evaluate_custom_scenario(payload)
    assert result.scenario_id == "custom"
    assert result.status in VALID_STATUSES
    assert result.recommendation is not None or result.status == "insufficient_information"


def test_custom_request_rejects_backup_running_below_30():
    with pytest.raises(ValueError):
        CustomScenarioRequest(
            critical_load_kw=40,
            vessel_load_kw=60,
            other_load_kw=0,
            solar_kw=10,
            battery_charge_kwh=5,
            battery_max_kwh=100,
            grid_available=False,
            backup_generator_capacity_kw=20,
            backup_running_percentage=20,
            description="Invalid backup running percentage",
        )


def test_custom_scenario_passed_status():
    payload = CustomScenarioRequest(
        critical_load_kw=20,
        vessel_load_kw=10,
        other_load_kw=5,
        solar_kw=40,
        battery_charge_kwh=50,
        battery_max_kwh=100,
        grid_available=True,
        backup_generator_capacity_kw=0,
        backup_running_percentage=30,
        description="Comfortably supplied scenario",
    )

    result = evaluate_custom_scenario(payload)
    assert result.status == "success"
    assert result.recommendation is not None


def test_custom_scenario_warning_or_partial_supply():
    payload = CustomScenarioRequest(
        critical_load_kw=20,
        vessel_load_kw=60,
        other_load_kw=20,
        solar_kw=10,
        battery_charge_kwh=5,
        battery_max_kwh=100,
        grid_available=True,
        backup_generator_capacity_kw=0,
        backup_running_percentage=30,
        description="Non-critical demand pressure scenario",
    )

    result = evaluate_custom_scenario(payload)
    assert result.status in VALID_STATUSES
    assert result.recommendation is not None or result.status == "insufficient_information"


def test_custom_scenario_supervisor_or_emergency_condition():
    payload = CustomScenarioRequest(
        critical_load_kw=80,
        vessel_load_kw=50,
        other_load_kw=10,
        solar_kw=0,
        battery_charge_kwh=0,
        battery_max_kwh=100,
        grid_available=False,
        backup_generator_capacity_kw=20,
        backup_running_percentage=30,
        description="Severely constrained no-grid scenario",
    )

    result = evaluate_custom_scenario(payload)
    assert result.status in [
        "unmet_critical_load",
        "safety_failure",
        "insufficient_information",
        "emergency_action_required",
        "supervisor_action_required",
    ]


def test_custom_scenario_insufficient_information_when_inputs_are_ambiguous():
    payload = CustomScenarioRequest(
        critical_load_kw=0,
        vessel_load_kw=0,
        other_load_kw=0,
        solar_kw=0,
        battery_charge_kwh=0,
        battery_max_kwh=100,
        grid_available=False,
        backup_generator_capacity_kw=0,
        backup_running_percentage=30,
        description="Minimal-input edge case",
    )

    result = evaluate_custom_scenario(payload)
    assert result.status in VALID_STATUSES