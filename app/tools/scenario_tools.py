from __future__ import annotations

from typing import Any, Dict

from app.models import Scenario


def get_scenario_state(scenario: Scenario) -> Dict[str, Any]:
    demand = scenario.demand
    supply = scenario.supply

    total_demand_kw = (
        demand.critical_load_kw
        + demand.vessel_load_kw
        + demand.other_load_kw
    )

    battery_soc_pct = 0.0
    if supply.battery_max_kwh > 0:
        battery_soc_pct = round(
            (supply.battery_charge_kwh / supply.battery_max_kwh) * 100.0,
            2,
        )

    backup_generator_capacity_kw = getattr(
        supply,
        "backup_generator_capacity_kw",
        getattr(supply, "backup_generator_kw", 0.0),
    )
    backup_running_percentage = getattr(supply, "backup_running_percentage", 0.0)

    return {
        "scenario_id": scenario.scenario_id,
        "name": scenario.name,
        "description": scenario.description,
        "demand": {
            "critical_load_kw": demand.critical_load_kw,
            "vessel_load_kw": demand.vessel_load_kw,
            "other_load_kw": demand.other_load_kw,
            "total_demand_kw": total_demand_kw,
        },
        "supply": {
            "solar_kw": supply.solar_kw,
            "battery_charge_kwh": supply.battery_charge_kwh,
            "battery_max_kwh": supply.battery_max_kwh,
            "battery_soc_pct": battery_soc_pct,
            "grid_available": supply.grid_available,
            "max_grid_import_kw": supply.max_grid_import_kw,
            "backup_generator_capacity_kw": backup_generator_capacity_kw,
            "backup_running_percentage": backup_running_percentage,
            "backup_generator_kw": backup_generator_capacity_kw,
        },
    }